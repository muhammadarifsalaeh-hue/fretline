#!/usr/bin/env python3
"""Fit review-only MakeHuman guitar poses using the actual GLB skin.

The runtime accepts absolute LOCAL bone rotations.  This script keeps the
exported translations/scales and computes restRotation * anatomicalDelta.
No pose produced here is independently reviewed or certified collision-free.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
FINGERS = ("index", "middle", "ring", "little", "thumb")
NUMBERS = {"thumb": 1, "index": 2, "middle": 3, "ring": 4, "little": 5}
GAUGES = np.array([.25, .33, .46, .66, .91, 1.32])


def unit(a):
    return a / np.linalg.norm(a)


def fret_x(f):
    return 648 * (1 - 2 ** (-f / 12))


def string_z(s, x):
    return (s - 3.5) * (35 + 17 * x / 648) / 5


def board_top(z):
    return -z * z / 700


def back_y(x, z):
    half = (43 + 11 * np.clip(x / 324, 0, 1)) / 2
    return board_top(z) - 5 - 16 * np.sqrt(np.maximum(0, 1 - (z / half) ** 2))


def string_y(s, x):
    radius = GAUGES[s - 1] / 2
    a = board_top(string_z(s, 0)) + 1.4 + radius
    b = board_top(string_z(s, 324)) + 3.0 + radius
    return a + (b - a) * x / 324


def wood_depth(p):
    """Positive interior depth, conservative D-neck solid and board union."""
    x, y, z = p.T
    half = (43 + 11 * np.clip(x / 324, 0, 1)) / 2
    return np.maximum(0, np.minimum.reduce((board_top(z) - y, y - back_y(x, z),
                                            half - abs(z), x + 9, 330 - x)))


class Rig:
    def __init__(self, path, palmar_sign=-1):
        self.data = json.loads(Path(path).read_text())
        self.bones = self.data["boneRestData"]
        self.by_name = {b["name"]: i for i, b in enumerate(self.bones)}
        self.parents = [self.by_name.get(b["parentName"], -1) for b in self.bones]
        self.rest_local = np.array([b["localMatrix"] for b in self.bones])
        self.rest_world = np.array([b["worldMatrix"] for b in self.bones])
        self.rest_q = np.array([b["rotation"] for b in self.bones])
        self.mesh = next(m for m in self.data["meshes"] if "Hand" in m["name"])
        self.positions = np.array(self.mesh["positions"])
        self.normals = np.array(self.mesh["normals"])
        self.joints = np.array(self.mesh["joints"], dtype=int)
        self.weights = np.array(self.mesh["weights"])
        self.joint_bones = np.array([self.by_name[n] for n in self.mesh["skinJointNames"]])
        self.inverse_bind = np.array(self.mesh["inverseBindMatrices"])
        self.triangles = np.array(self.mesh["indices"], dtype=int).reshape(-1, 3)
        self.ph = np.column_stack((self.positions, np.ones(len(self.positions))))
        # Prebind each weighted vertex in bone space, preserving original indices.
        self.bound = np.einsum("nvij,nj->nvi", self.inverse_bind[self.joints], self.ph)
        self.landmarks = self.mesh["fingerSurfaceLandmarks"]
        f = self.rest_world[self.by_name["finger3-1.L"], :3, 3]
        w = (self.rest_world[self.by_name["finger5-1.L"], :3, 3] -
             self.rest_world[self.by_name["finger2-1.L"], :3, 3])
        self.forward = unit(f)
        self.width = unit(w - self.forward * np.dot(w, self.forward))
        self.palmar = unit(np.cross(self.forward, self.width)) * palmar_sign
        # Only a proper rotation: source forward/width/dorsal normal map
        # to guitar +Z/+X/+Y. Confirmed textured-native palm is negative F×W.
        src = np.column_stack((self.width, np.cross(self.forward, self.width), self.forward))
        self.initial_rot = src.T
        self.flex_axes = {}
        self.spread_axes = {}
        for finger in FINGERS:
            for segment in range(1, 4):
                n = f"finger{NUMBERS[finger]}-{segment}.L"
                r = self.rest_world[self.by_name[n], :3, :3]
                self.flex_axes[n] = unit(r.T @ np.cross(r[:, 1], self.palmar))
                self.spread_axes[n] = unit(r.T @ self.palmar)
        # Flesh patches are chosen by their displacement toward the palmar side.
        self.patch_ids = {}
        self.patch_side = {}
        for finger in FINGERS:
            lm = self.landmarks[finger]
            choices = [(np.dot(np.array(lm[k]["centerMeters"]) - np.array(lm["boneHeadMeters"]),
                               self.palmar), k) for k in ("surfaceSidePositive", "surfaceSideNegative")]
            side = max(choices)[1]
            self.patch_ids[finger] = np.array(lm[side]["vertexIndices"], dtype=int)
            self.patch_side[finger] = side
            if finger != "thumb":
                bi = self.by_name[f"finger{NUMBERS[finger]}-3.L"]
                inv = np.linalg.inv(self.rest_world[bi])
                local = self.ph @ inv.T
                candidates = np.flatnonzero((local[:, 1] > .007) &
                    (np.linalg.norm(local[:, [0, 2]], axis=1) < .013))
                peak = local[candidates, 1].max()
                candidates = candidates[(local[candidates, 1] > peak - .005) &
                    ((self.normals[candidates] @ self.palmar) > .15)]
                direction = unit(self.rest_world[bi, :3, 1] * .8 + self.palmar * .6)
                ranking = self.normals[candidates] @ direction
                self.patch_ids[finger] = candidates[np.argsort(ranking)[-8:]]
                self.patch_side[finger] = "far-distal-flesh-cap"
        self.sample_ids = np.unique(np.r_[np.arange(0, len(self.positions), 6),
                                          *self.patch_ids.values()])
        dominant = self.joint_bones[self.joints[np.arange(len(self.joints)), self.weights.argmax(1)]]
        self.finger_vertex_ids = {}
        for finger in FINGERS:
            names = [f"finger{NUMBERS[finger]}-{i}.L" for i in range(1, 4)]
            self.finger_vertex_ids[finger] = np.flatnonzero(np.isin(dominant, [self.by_name[n] for n in names]))
        self.finger_triangles = {f: self.triangles[np.any(np.isin(self.triangles, ids), axis=1)]
                                 for f, ids in self.finger_vertex_ids.items()}
        distal_ids = np.flatnonzero(np.isin(dominant, [self.by_name[f"finger{n}-3.L"] for n in range(1,6)]))
        self.distal_triangles = self.triangles[np.any(np.isin(self.triangles, distal_ids), axis=1)]

    def rotations(self, params):
        q = self.rest_q.copy()
        for i, finger in enumerate(FINGERS):
            mcp, spread, pip, dip = params[6 + 4*i:10 + 4*i]
            for segment, angle in enumerate((mcp, pip, dip), 1):
                name = f"finger{NUMBERS[finger]}-{segment}.L"
                delta = Rotation.from_rotvec(self.flex_axes[name] * angle)
                if segment == 1:
                    delta = Rotation.from_rotvec(self.spread_axes[name] * spread) * delta
                    if finger == "thumb" and len(params) > 26:
                        delta = delta * Rotation.from_rotvec(np.array([0., 1., 0.]) * params[26])
                bi = self.by_name[name]
                q[bi] = (Rotation.from_quat(self.rest_q[bi]) * delta).as_quat()
        return q

    def fk(self, params):
        q = self.rotations(params)
        local = self.rest_local.copy()
        local[:, :3, :3] = Rotation.from_quat(q).as_matrix() * np.array([b["scale"] for b in self.bones])[:, None, :]
        result = np.zeros_like(local)
        ready = set()
        def visit(i):
            if i in ready:
                return
            p = self.parents[i]
            if p >= 0:
                visit(p)
                result[i] = result[p] @ local[i]
            else:
                result[i] = local[i]
            ready.add(i)
        for i in range(len(self.bones)):
            visit(i)
        root_rot = Rotation.from_rotvec(params[3:6]).as_matrix() @ self.initial_rot
        root_matrix = np.eye(4)
        root_matrix[:3, :3] = root_rot * 1000
        root_matrix[:3, 3] = params[:3]
        return root_matrix @ result, q, root_rot

    def skin(self, world, ids=None):
        ids = np.arange(len(self.positions)) if ids is None else np.asarray(ids)
        mats = world[self.joint_bones[self.joints[ids]]]
        return np.einsum("nv,nvij,nvj->ni", self.weights[ids], mats[:, :, :3], self.bound[ids])

    def skin_normals(self, world, ids):
        ids = np.asarray(ids)
        mats = world[self.joint_bones[self.joints[ids]]] @ self.inverse_bind[self.joints[ids]]
        n = np.einsum("nv,nvij,nj->ni", self.weights[ids], mats[:, :, :3, :3], self.normals[ids])
        return n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-10)

    def skin_mesh(self, world, mesh):
        positions = np.column_stack((np.array(mesh["positions"]), np.ones(len(mesh["positions"]))))
        joints = np.array(mesh["joints"], dtype=int)
        weights = np.array(mesh["weights"])
        inverse_bind = np.array(mesh["inverseBindMatrices"])
        joint_bones = np.array([self.by_name[n] for n in mesh["skinJointNames"]])
        mats = world[joint_bones[joints]] @ inverse_bind[joints]
        return np.einsum("nv,nvij,nj->ni", weights, mats[:, :, :3], positions)

    def lower_surface(self, points, finger, x, z):
        ids = self.finger_triangles[finger]
        tri = points[ids]
        a = tri[:,1][:,[0,2]]-tri[:,0][:,[0,2]]
        b = tri[:,2][:,[0,2]]-tri[:,0][:,[0,2]]
        c = np.array([x,z])-tri[:,0][:,[0,2]]
        det = a[:,0]*b[:,1]-a[:,1]*b[:,0]
        good = abs(det)>1e-9
        u = np.divide(c[:,0]*b[:,1]-c[:,1]*b[:,0],det,out=np.zeros(len(det)),where=good)
        v = np.divide(a[:,0]*c[:,1]-a[:,1]*c[:,0],det,out=np.zeros(len(det)),where=good)
        valid = good&(u>=0)&(v>=0)&(u+v<=1)
        y = tri[:,0,1]+u*(tri[:,1,1]-tri[:,0,1])+v*(tri[:,2,1]-tri[:,0,1])
        if not valid.any():
            return None
        index = np.flatnonzero(valid)[np.argmin(y[valid])]
        return {"positionMm":[float(x),float(y[index]),float(z)],"triangleVertexIndices":ids[index].tolist(),
                "barycentric":[float(1-u[index]-v[index]),float(u[index]),float(v[index])]}


def string_polyline(s, targets):
    pressed = next((t for t in targets if t["string"]==s),None)
    out = [[0,string_y(s,0),string_z(s,0)]]
    if pressed:
        for x in [fret_x(pressed["fret"])-4,fret_x(pressed["fret"])]:
            z=string_z(s,x);out.append([x,board_top(z)+1+GAUGES[s-1]/2+.025,z])
    out.append([330,string_y(s,330),string_z(s,330)])
    return np.array(out)


def polyline_distance(points, line):
    result=np.full(len(points),np.inf)
    for a,b in zip(line[:-1],line[1:]):
        edge=b-a;t=np.clip((points-a)@edge/(edge@edge),0,1)
        result=np.minimum(result,np.linalg.norm(points-(a+t[:,None]*edge),axis=1))
    return result


def c_targets():
    return [{"finger": f, "string": s, "fret": n,
             "positionMm": [float(x := fret_x(n) - 4), float(board_top(z := string_z(s, x)) + 1 + GAUGES[s-1]), float(z)]}
            for f, s, n in (("index", 2, 1), ("middle", 4, 2), ("ring", 5, 3))]


def initial_parameters():
    x = np.zeros(26)
    x[:3] = (65, 18, -65)
    for i in range(4):
        x[6+4*i:10+4*i] = np.deg2rad((65, 0, 100, 45))
    x[22:26] = np.deg2rad((15, -25, 20, 20))
    return x


def bounds():
    lo = np.r_[[-30, -90, -125], [-1.4]*3, np.tile(np.deg2rad([0, -35, 5, 0]), 4), np.deg2rad([-40, -70, -15, -10])]
    hi = np.r_[[180, 35, -20], [1.4]*3, np.tile(np.deg2rad([110, 35, 130, 95]), 4), np.deg2rad([70, 70, 80, 85])]
    return lo, hi


def residual(rig, params, targets, collision_weight=0, natural=False, surface_contacts=False):
    world, _, root_rot = rig.fk(params)
    patches = {f: rig.skin(world, ids) for f, ids in rig.patch_ids.items()}
    out = []
    all_points = rig.skin(world) if surface_contacts else None
    for t in targets:
        finger = t["finger"]
        if surface_contacts:
            out.extend((patches[finger].mean(axis=0)[[0,2]] - np.array(t["positionMm"])[[0,2]]) * 2)
            hit=rig.lower_surface(all_points,finger,t["positionMm"][0],t["positionMm"][2])
            y=hit["positionMm"][1] if hit else patches[finger].mean(axis=0)[1]
            out.append((y-t["positionMm"][1]-.075)*2)
        else:
            out.extend((patches[finger].mean(axis=0) - t["positionMm"]) * 2)
        n = rig.skin_normals(world, rig.patch_ids[finger]).mean(axis=0)
        # Pad faces strings, with some permitted side tilt.
        out.extend((n - np.array([0, -1, 0])) * 12)
    # Keep the unused little finger curled safely outside the edge.
    little = patches["little"].mean(axis=0)
    out.extend(np.maximum(0, np.array([0., 6., 12.]) - little) * np.array([0., .4, 0.]))
    # A thumb behind the neck is expected, with pad facing approximately +Y.
    thumb = patches["thumb"].mean(axis=0)
    out.extend((thumb - np.array([params[0] - 8, -23, 0])) * np.array([.08, .3, .12]))
    if natural and not surface_contacts:
        out.extend((thumb - np.array([params[0] - 8, -23, -3])) * np.array([.08, 1.2, 1.2]))
        tn = rig.skin_normals(world, rig.patch_ids["thumb"]).mean(axis=0)
        out.extend((tn - np.array([0, 1, 0])) * 6)
    # Regularize wrist orientation and adjacent finger distribution.
    out.extend(params[3:6] * .25)
    for i in range(4):
        m, s, p, d = params[6+4*i:10+4*i]
        out.append((d - p * .55) * .3)
        out.append(s * .1)
        out.append(max(0, m+p+d-np.deg2rad(200)) * 3)
        if natural:
            out.extend((np.array([m, p, d])-np.deg2rad([45,65,25])) * 2)
    if collision_weight:
        points = rig.skin(world, rig.sample_ids)
        out.extend(wood_depth(points) * collision_weight)
        # Open strings 1 and 3 must be clear at every sampled skin vertex.
        for s in (1, 3):
            px = np.clip(points[:, 0], 0, 330)
            dist = np.sqrt((points[:, 1] - string_y(s, px))**2 +
                           (points[:, 2] - string_z(s, px))**2 + (points[:, 0]-px)**2)
            out.extend(np.maximum(0, GAUGES[s-1]/2 + .45 - dist) * collision_weight)
        if surface_contacts:
            tri=all_points[rig.distal_triangles]
            sp=np.concatenate((all_points[::3],tri.mean(axis=1),(tri[:,0]+tri[:,1])/2,
                               (tri[:,1]+tri[:,2])/2,(tri[:,2]+tri[:,0])/2))
            for s in range(1,7):
                clearance=polyline_distance(sp,string_polyline(s,targets))-GAUGES[s-1]/2
                out.extend(np.maximum(0,.05-clearance)*collision_weight)
    return np.array(out)


def audit(rig, params, targets):
    world, _, _ = rig.fk(params)
    points = rig.skin(world)
    wd = wood_depth(points)
    metrics = {"skinVerticesAudited": len(points), "woodInteriorVertexCount": int((wd > .25).sum()),
               "maximumWoodVertexPenetrationMm": float(wd.max()), "padContacts": [], "openStrings": []}
    for t in targets:
        pad = rig.skin(world, rig.patch_ids[t["finger"]]).mean(axis=0)
        normal = rig.skin_normals(world, rig.patch_ids[t["finger"]]).mean(axis=0)
        metrics["padContacts"].append({**t, "actualPositionMm": pad.tolist(),
            "errorMm": float(np.linalg.norm(pad-t["positionMm"])), "meanOutwardNormal": normal.tolist(),
            "originalVertexIndices": rig.patch_ids[t["finger"]].tolist(), "patchSide": rig.patch_side[t["finger"]]})
        metrics["padContacts"][-1]["actualLowerSurfaceAtTargetXZ"]=rig.lower_surface(points,t["finger"],t["positionMm"][0],t["positionMm"][2])
    for s in (1, 3):
        px = np.clip(points[:, 0], 0, 330)
        dist = np.sqrt((points[:, 1] - string_y(s, px))**2 + (points[:, 2] - string_z(s, px))**2 + (points[:, 0]-px)**2) - GAUGES[s-1]/2
        metrics["openStrings"].append({"string": s, "minimumVertexClearanceMm": float(dist.min()),
                                       "skinVerticesWithinHalfMm": int((dist < .5).sum())})
    metrics["anatomicalAnglesDegrees"] = {f: dict(zip(("mcpFlex", "mcpSpread", "pipFlex", "dipFlex"),
                                                     np.rad2deg(params[6+4*i:10+4*i]).tolist())) for i, f in enumerate(FINGERS)}
    if len(params) > 26:
        metrics["anatomicalAnglesDegrees"]["thumb"]["cmcAxialRotation"] = float(np.rad2deg(params[26]))
    metrics["thumbPadPositionMm"] = rig.skin(world, rig.patch_ids["thumb"]).mean(axis=0).tolist()
    metrics["thumbPadNormal"] = rig.skin_normals(world, rig.patch_ids["thumb"]).mean(axis=0).tolist()
    metrics["triangleIntersectionAudit"] = "pending"
    metrics["selfCollisionAudit"] = "pending"
    metrics["fourViewVisualReview"] = "pending"
    metrics["allMeshWoodSamples"] = []
    for mesh in rig.data["meshes"]:
        mp = points if mesh is rig.mesh else rig.skin_mesh(world, mesh)
        tri = mp[np.array(mesh["indices"], dtype=int).reshape(-1,3)]
        surface_samples = np.concatenate((mp, tri.mean(axis=1), (tri[:,0]+tri[:,1])/2,
                                          (tri[:,1]+tri[:,2])/2, (tri[:,2]+tri[:,0])/2))
        depth = wood_depth(surface_samples)
        metrics["allMeshWoodSamples"].append({"mesh": mesh["name"], "sampleCount": len(depth),
            "samplesInsideOverQuarterMm": int((depth>.25).sum()), "maximumInteriorDepthMm": float(depth.max()),
            "scope": "Actual LBS vertices, triangle centroids and edge midpoints against conservative analytical study-neck volume; not an exact triangle/wood proof."})
    return metrics


def write_candidate(rig, params, targets, path):
    world, quaternions, root_rot = rig.fk(params)
    candidate = {"chordId": "C", "root": {"positionMm": params[:3].tolist(), "quaternion": Rotation.from_matrix(root_rot).as_quat().tolist()},
                 "bones": {b["name"]: {"quaternion": quaternions[i].tolist()} for i,b in enumerate(rig.bones)},
                 "targets": targets, "audit": {"collisionPassed": False, "metrics": audit(rig, params, targets)},
                 "reviewed": False, "status": "needs-review", "reason": {
                     "th": "ท่ามือจากตัวแก้สมการบนผิวโมเดลจริง ยังรอตรวจการชนและตรวจภาพสี่มุมโดยผู้ตรวจอิสระ",
                     "en": "A numerical candidate fitted to actual skinned flesh patches; triangle collisions and independent four-view review remain pending."},
                 "assetSha256": rig.data["sha256"], "rigSignature": "|".join(sorted(rig.by_name)),
                 "solverParameters": params.tolist(), "palmarNormalSource": rig.palmar.tolist()}
    Path(path).write_text(json.dumps(candidate, indent=2) + "\n")
    return candidate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rig", default=str(ROOT/"docs/practice-trainer/models/authoring/rig-data.json"))
    ap.add_argument("--output", default="/tmp/fretline-trainer-pose/C-candidate.json")
    ap.add_argument("--seed", default=None)
    ap.add_argument("--iterations", type=int, default=180)
    ap.add_argument("--collision-weight", type=float, default=.7)
    ap.add_argument("--palmar-sign", type=int, default=-1)
    ap.add_argument("--natural", action="store_true", help="Include thumb opposition and finger-shape priors")
    ap.add_argument("--dense-collision", action="store_true", help="Use every original skin vertex during fitting")
    ap.add_argument("--conservative", action="store_true", help="Distribute flexion and relax unused little finger")
    ap.add_argument("--surface-contacts", action="store_true", help="Fit actual triangle surface at contact and reject all six string tubes")
    ap.add_argument("--freeze-thumb", action="store_true", help="Keep a previously reviewed thumb configuration")
    args = ap.parse_args()
    rig = Rig(args.rig, args.palmar_sign)
    if args.dense_collision:
        rig.sample_ids = np.arange(len(rig.positions))
    x = initial_parameters() if args.seed is None else np.array(json.loads(Path(args.seed).read_text())["solverParameters"])
    targets = c_targets()
    low, high = bounds()
    if args.natural:
        if len(x) == 26:
            x = np.r_[x, 0.]
        low, high = np.r_[low, -1.4], np.r_[high, 1.4]
        # A wrist may extend sideways below the high-e edge without a hard
        # arbitrary 125mm cutoff. Pose review still decides acceptability.
        low[2] = -180
        low[3] = -1.8
        high[4:6] = 1.8
        high[6:22:4] = np.deg2rad(100)
        low[8:22:4] = np.deg2rad(15)
        x = np.clip(x, low+1e-8, high-1e-8)
    if args.conservative:
        high[8:18:4] = np.deg2rad(70)
        low[9:18:4] = np.deg2rad(10)
        low[18:22] = np.deg2rad([0, -10, 15, 5])
        high[18:22] = np.deg2rad([10, 10, 35, 15])
        low[22:26] = np.deg2rad([-20, -55, -10, -5])
        high[22:26] = np.deg2rad([60, 55, 60, 65])
        if len(x) > 26:
            low[26], high[26] = np.deg2rad([-60, 60])
        x = np.clip(x, low+1e-8, high-1e-8)
    if args.freeze_thumb:
        low[22:]=x[22:]-1e-8
        high[22:]=x[22:]+1e-8
    stages = (0, args.collision_weight) if args.seed is None else (args.collision_weight,)
    for weight in stages:
        result = least_squares(lambda p: residual(rig, p, targets, weight, args.natural,args.surface_contacts), x,
                               bounds=(low, high), max_nfev=args.iterations, x_scale="jac", ftol=1e-6)
        x = result.x
        candidate = write_candidate(rig, x, targets, args.output)
        print(json.dumps({"output": args.output, "collisionWeight": weight, "cost": result.cost,
                          "evaluations": result.nfev, "metrics": candidate["audit"]["metrics"]}), flush=True)


if __name__ == "__main__":
    main()
