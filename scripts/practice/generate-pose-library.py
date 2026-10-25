#!/usr/bin/env python3
"""Generate review-only candidates for every central chord on one actual rig.

Imports the C solver's FK/LBS implementation rather than approximating the hand
with points or capsules. Ordinary contacts use its distal flesh patches. Barres
use separate closest barycentric points on the entire index palmar skin, with
all inclusive strings retained even when another finger frets above the barre.
Nothing produced by this numerical authoring tool is automatically verified.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("fretline_c_pose_solver", Path(__file__).with_name("solve-hand-poses.py"))
solver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solver)
FINGERS = solver.FINGERS
FINGER_BY_NUMBER = {1: "index", 2: "middle", 3: "ring", 4: "little"}


def central_chords():
    """Run the source module, including its own validation; no duplicated list."""
    program = "import {PRACTICE_CHORDS} from './src/features/practice/data/chords.js'; process.stdout.write(JSON.stringify(PRACTICE_CHORDS));"
    return json.loads(subprocess.check_output(["node", "--input-type=module", "-e", program], cwd=ROOT, text=True))


def targets_for(chord):
    targets = []
    for barre in chord["barres"]:
        for string in range(barre["fromString"], barre["toString"] - 1, -1):
            targets.append(target(FINGER_BY_NUMBER[barre["finger"]], string, barre["fret"],
                                  "barre", chord["frets"][6-string]))
    for index, fret in enumerate(chord["frets"]):
        if not fret:
            continue
        string, finger = 6 - index, chord["fingers"][index]
        if any(b["finger"] == finger and b["fret"] == fret and
               b["toString"] <= string <= b["fromString"] for b in chord["barres"]):
            continue
        targets.append(target(FINGER_BY_NUMBER[finger], string, fret, "fingertip", fret))
    return targets


def target(finger, string, fret, kind, sounding_fret):
    x = solver.fret_x(fret) - 4
    return {"finger": finger, "string": string, "fret": fret, "kind": kind,
            "underHigherFrettedString": kind == "barre" and sounding_fret is not None and sounding_fret > fret,
            "positionMm": [float(x), float(solver.board_top(solver.string_z(string, x)) + 1 + solver.GAUGES[string-1]),
                           float(solver.string_z(string, x))]}


def nearest_triangle(point, triangles):
    """Nearest real triangle point and barycentric weights (vectorized)."""
    a, b, c = triangles[:, 0], triangles[:, 1], triangles[:, 2]
    u, v, w = b-a, c-a, point-a
    uu, uv, vv = np.einsum("ij,ij->i", u, u), np.einsum("ij,ij->i", u, v), np.einsum("ij,ij->i", v, v)
    wu, wv = np.einsum("ij,ij->i", w, u), np.einsum("ij,ij->i", w, v)
    den = uu*vv-uv*uv
    safe = np.where(np.abs(den) < 1e-16, 1, den)
    s, t = (wu*vv-wv*uv)/safe, (wv*uu-wu*uv)/safe
    bary = np.column_stack((1-s-t, s, t))
    projected = a+s[:, None]*u+t[:, None]*v
    valid = (bary.min(axis=1) >= 0) & (den > 1e-16)
    points, weights = [projected], [bary]
    distances = [np.where(valid, ((projected-point)**2).sum(axis=1), np.inf)]
    for first, second in ((0, 1), (1, 2), (2, 0)):
        start, delta = triangles[:, first], triangles[:, second]-triangles[:, first]
        length2 = np.einsum("ij,ij->i", delta, delta)
        ratio = np.clip(np.einsum("ij,ij->i", point-start, delta)/np.maximum(length2, 1e-16), 0, 1)
        p = start+ratio[:, None]*delta
        b = np.zeros((len(triangles), 3)); b[:, first] = 1-ratio; b[:, second] = ratio
        points.append(p); weights.append(b); distances.append(((p-point)**2).sum(axis=1))
    ds = np.stack(distances)
    region, tri = np.unravel_index(ds.argmin(), ds.shape)
    return int(tri), weights[region][tri], points[region][tri], float(np.sqrt(ds[region, tri]))


class LibraryFitter:
    def __init__(self, rig):
        self.rig = rig
        self.patch_ids = np.concatenate([rig.patch_ids[f] for f in FINGERS])
        self.patch_slices = {f: slice(i*8, (i+1)*8) for i, f in enumerate(FINGERS)}
        self.base_sample_ids = np.unique(np.r_[np.arange(0, len(rig.positions), 16), self.patch_ids])
        self.sample_ids = self.base_sample_ids
        palm_forward = rig.positions @ rig.forward
        self.palm_ids = np.flatnonzero((palm_forward > .025) & (palm_forward < .08))
        self.palmar_triangles = {}
        self.cap_triangles = {}
        for finger in FINGERS:
            membership = np.zeros(len(rig.positions), dtype=bool)
            membership[rig.finger_vertex_ids[finger]] = True
            triangles = rig.triangles[np.all(membership[rig.triangles], axis=1)]
            palmar = (rig.normals[triangles].mean(axis=1) @ rig.palmar) > .05
            self.palmar_triangles[finger] = triangles[palmar]
            cap_membership = np.isin(rig.triangles, rig.patch_ids[finger]).any(axis=1)
            self.cap_triangles[finger] = rig.triangles[cap_membership]

    def correspondences(self, params, targets):
        world, _, _ = self.rig.fk(params)
        points = self.rig.skin(world)
        correspondences = []
        for contact in targets:
            if contact["kind"] != "barre":
                correspondences.append(None)
                continue
            triangles = self.palmar_triangles[contact["finger"]]
            tri, bary, _, _ = nearest_triangle(np.array(contact["positionMm"]), points[triangles])
            correspondences.append((triangles[tri], bary))
        return correspondences

    def residual(self, params, chord, targets, correspondences, collision_weight):
        rig = self.rig
        world, _, _ = rig.fk(params)
        patch = rig.skin(world, self.patch_ids)
        normal = rig.skin_normals(world, self.patch_ids)
        out = []
        for contact, correspondence in zip(targets, correspondences):
            finger = contact["finger"]
            if correspondence is None:
                actual = patch[self.patch_slices[finger]].mean(axis=0)
                outward = normal[self.patch_slices[finger]].mean(axis=0)
                out.extend((actual-contact["positionMm"]) * 2)
                out.extend((outward-np.array([0, -1, 0])) * 6)
            else:
                ids, bary = correspondence
                actual = bary @ rig.skin(world, ids)
                # Distinct points along one finger, never one cap reused six times.
                out.extend((actual-contact["positionMm"]) * 2)
        thumb = patch[self.patch_slices["thumb"]].mean(axis=0)
        desired_thumb = np.array([np.mean([t["positionMm"][0] for t in targets]), -23, -3])
        out.extend((thumb-desired_thumb) * np.array([.08, 1.2, 1.2]))
        thumb_normal = normal[self.patch_slices["thumb"]].mean(axis=0)
        out.extend((thumb_normal-np.array([0, 1, 0])) * 6)
        out.extend(params[3:6] * .12)
        out.extend(np.maximum(0, np.array([params[2]+45, params[1]-22])) * .4)
        used = {t["finger"] for t in targets}
        for i, finger in enumerate(FINGERS[:4]):
            mcp, spread, pip, dip = params[6+4*i:10+4*i]
            out.extend([(dip-pip*.55)*.25, spread*.12,
                        max(0, mcp+pip+dip-np.deg2rad(205))*2])
            if not (chord["barres"] and finger == "index"):
                out.extend((np.array([mcp, pip, dip])-np.deg2rad([45, 65, 25]))*1.5)
            if finger not in used:
                center = patch[self.patch_slices[finger]].mean(axis=0)
                out.extend([max(0, 6-center[1])*.2, (mcp-np.deg2rad(35))*.2])
        if collision_weight:
            points = rig.skin(world, self.sample_ids)
            out.extend(solver.wood_depth(points) * collision_weight)
            for string in chord["openStrings"]:
                px = np.clip(points[:, 0], 0, 330)
                distance = np.sqrt((points[:, 1]-solver.string_y(string, px))**2 +
                                   (points[:, 2]-solver.string_z(string, px))**2 + (points[:, 0]-px)**2)
                out.extend(np.maximum(0, solver.GAUGES[string-1]/2+.5-distance)*collision_weight)
        return np.asarray(out)

    def bounds(self, chord):
        low, high = solver.bounds()
        low[0], high[0], low[2] = -30, 260, -180
        low[3], high[4], high[5] = -1.8, 1.8, 1.8
        high[6:22:4] = np.deg2rad(100)
        low[8:22:4] = np.deg2rad(15)
        if chord["barres"]:
            # The index is longitudinally straight enough to cross strings.
            low[6:10] = np.deg2rad([0, -35, 0, 0])
            high[6:10] = np.deg2rad([55, 35, 25, 20])
            low[3], high[3] = -.9, .9
        return np.r_[low, -1.4], np.r_[high, 1.4]

    def seed(self, chord, targets, c_seed):
        params = np.array(c_seed, dtype=float)
        if len(params) == 26:
            params = np.r_[params, 0]
        if chord["barres"]:
            barre = chord["barres"][0]
            x = solver.fret_x(barre["fret"])-4
            params[:6] = [x+31, 16, -123, -.05, .12, 0]
            params[6:10] = np.deg2rad([8, 0, 3, 2])
            params[22:26] = np.deg2rad([10, 40, 45, 30])
            for i in range(1, 4):
                params[6+4*i:10+4*i] = np.deg2rad([65, 0, 90, 45])
        else:
            params[0] += np.mean([t["positionMm"][0] for t in targets]) - np.mean([t["positionMm"][0] for t in solver.c_targets()])
        low, high = self.bounds(chord)
        return np.clip(params, low+1e-7, high-1e-7)

    def fit(self, chord, targets, seed, evaluations):
        params = seed.copy(); low, high = self.bounds(chord)
        stages = [(0, evaluations), (.9, max(10, evaluations//2))]
        if chord["barres"]:
            stages = [(0, max(10, evaluations//2)), (0, max(10, evaluations//2)), (.9, max(10, evaluations//2))]
        stats = []
        for weight, count in stages:
            correspondences = self.correspondences(params, targets)
            if weight:
                world, _, _ = self.rig.fk(params)
                full_skin = self.rig.skin(world)
                self.sample_ids = np.unique(np.r_[self.base_sample_ids, np.flatnonzero(solver.wood_depth(full_skin) > 0)])
            result = least_squares(lambda p: self.residual(p, chord, targets, correspondences, weight),
                                   params, bounds=(low, high), max_nfev=count, x_scale="jac",
                                   ftol=3e-5, xtol=3e-5, gtol=3e-5)
            params = result.x
            stats.append({"collisionWeight": weight, "evaluations": result.nfev,
                          "cost": float(result.cost), "success": bool(result.success), "termination": result.message})
        self.sample_ids = self.base_sample_ids
        return params, stats

    def audit(self, params, chord, targets):
        rig = self.rig
        world, _, _ = rig.fk(params)
        points = rig.skin(world)
        depth = solver.wood_depth(points)
        patch = rig.skin(world, self.patch_ids)
        normals = rig.skin_normals(world, self.patch_ids)
        contacts = []
        for contact in targets:
            finger = contact["finger"]
            triangles = self.palmar_triangles[finger] if contact["kind"] == "barre" else self.cap_triangles[finger]
            tri, bary, actual, error = nearest_triangle(np.array(contact["positionMm"]), points[triangles])
            indices = triangles[tri]
            actual_normal = bary @ rig.skin_normals(world, indices)
            actual_normal /= max(np.linalg.norm(actual_normal), 1e-10)
            entry = {**contact, "actualPositionMm": actual.tolist(), "errorMm": error,
                     "surfaceTriangleVertexIndices": indices.tolist(), "surfaceBarycentric": bary.tolist(),
                     "surfaceOutwardNormal": actual_normal.tolist(),
                     "surfaceRegion": "whole-finger-palmar-skin" if contact["kind"] == "barre" else "far-distal-flesh-cap"}
            if contact["kind"] != "barre":
                anchor = patch[self.patch_slices[finger]].mean(axis=0)
                entry.update({"patchAnchorPositionMm": anchor.tolist(),
                              "patchAnchorErrorMm": float(np.linalg.norm(anchor-contact["positionMm"])),
                              "patchVertexIndices": rig.patch_ids[finger].tolist(),
                              "meanOutwardNormal": normals[self.patch_slices[finger]].mean(axis=0).tolist()})
            contacts.append(entry)
        opens = []
        for string in chord["openStrings"]:
            px = np.clip(points[:, 0], 0, 330)
            clearance = np.sqrt((points[:, 1]-solver.string_y(string, px))**2 +
                                (points[:, 2]-solver.string_z(string, px))**2 + (points[:, 0]-px)**2)-solver.GAUGES[string-1]/2
            opens.append({"string": string, "minimumVertexClearanceMm": float(clearance.min()),
                          "skinVerticesWithinHalfMm": int((clearance < .5).sum())})
        gaps = []
        for i, first in enumerate(FINGERS[:4]):
            for second in FINGERS[i+1:4]:
                ids1, ids2 = rig.finger_vertex_ids[first], rig.finger_vertex_ids[second]
                distance = cKDTree(points[ids1]).query(points[ids2], k=1)[0]
                gaps.append({"fingers": [first, second], "minimumSkinVertexGapMm": float(distance.min()),
                             "verticesWithinOneMm": int((distance < 1).sum())})
        angle_data = {finger: dict(zip(("mcpFlex", "mcpSpread", "pipFlex", "dipFlex"),
                                      np.rad2deg(params[6+4*i:10+4*i]).tolist())) for i, finger in enumerate(FINGERS)}
        angle_data["thumb"]["cmcAxialRotation"] = float(np.rad2deg(params[26]))
        thumb = patch[self.patch_slices["thumb"]].mean(axis=0)
        palm = points[self.palm_ids].mean(axis=0)
        metrics = {"skinVerticesAudited": len(points), "skinTriangles": len(rig.triangles),
                   "contactTargetModel": "pressed string top boardTop+fretHeight(1mm)+gauge; x=fretWire-4mm; studyGuitar dimensions",
                   "woodInteriorVertexCount": int((depth > .25).sum()),
                   "maximumWoodVertexPenetrationMm": float(depth.max()),
                   "woodVerticesOverOneMm": int((depth > 1).sum()), "padContacts": contacts,
                   "maximumContactErrorMm": max(c["errorMm"] for c in contacts),
                   "rmsContactErrorMm": float(np.sqrt(np.mean([c["errorMm"]**2 for c in contacts]))),
                   "openStrings": opens, "interFingerVertexProximity": gaps,
                   "anatomicalAnglesDegrees": angle_data, "thumbPadPositionMm": thumb.tolist(),
                   "thumbPadNormal": normals[self.patch_slices["thumb"]].mean(axis=0).tolist(),
                   "thumbBackSurfaceGapMm": float(solver.back_y(thumb[0], thumb[2])-thumb[1]),
                   "thumbBehindBoard": bool(thumb[1] < -5), "wristPositionMm": params[:3].tolist(),
                   "wristOutsideHighStringEdge": bool(params[2] < -22),
                   "palmMeanPositionMm": palm.tolist(), "palmOutsideHighStringEdge": bool(palm[2] < -22),
                   "triangleIntersectionAudit": "pending; vertex sampling does not establish triangle separation",
                   "selfCollisionAudit": "pending; vertex proximity is diagnostic only",
                   "anatomyReview": "pending; optimizer bounds are authoring constraints only",
                   "fourViewVisualReview": "pending"}
        if chord["barres"]:
            mcp = world[rig.by_name["finger2-1.L"], :3, 3]
            cap = patch[self.patch_slices["index"]].mean(axis=0)
            axis = (cap-mcp)/np.linalg.norm(cap-mcp)
            metrics["barre"] = {"inclusiveContactCount": sum(t["kind"] == "barre" for t in targets),
                                "distinctSurfaceTriangles": len({tuple(c["surfaceTriangleVertexIndices"]) for c in contacts if c["kind"] == "barre"}),
                                "indexAxisGuitar": axis.tolist(), "indexAxisAcrossStringsDot": float(abs(axis[2])),
                                "indexPipFlexDegrees": angle_data["index"]["pipFlex"],
                                "indexDipFlexDegrees": angle_data["index"]["dipFlex"]}
        return metrics


def write_reports(output, library):
    output.mkdir(parents=True, exist_ok=True)
    (output/"hand-pose-candidates.json").write_text(json.dumps(library, indent=2, ensure_ascii=False)+"\n")
    report = {"schemaVersion": 1, "assetSha256": library["assetSha256"], "rigSignature": library["rigSignature"],
              "createdAtUTC": library["createdAtUTC"], "candidateCount": len(library["poses"]),
              "verifiedCount": 0, "allRequireIndependentReview": True,
              "chords": {key: value["audit"]["metrics"] for key, value in library["poses"].items()}}
    (output/"authoring-metrics.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    lines = ["# Rigged hand candidates: authoring diagnostics", "",
             "Every row is a different candidate fitted through the actual MakeHuman skin weights and bind matrices. All candidates remain **needs-review**, with every review gate false. These are authoring artifacts, not validated practice examples.", "",
             "Contacts are measured against real deformed skin triangles. Ordinary fingers also report the distal flesh patch anchor error. Barre contacts independently select a barycentric point on the index palmar surface for every inclusive string, including strings fretted higher by another finger.", "",
             "Targets use the pressed string top (board top + 1 mm fret height + string gauge) at 4 mm behind the fret wire. This does not simulate compliant flesh. Wood measurements sample every skin vertex in a conservative neck solid. They do not rule out triangle crossings. Inter-finger gaps and open-string clearances are vertex diagnostics. Full triangle collision, self-collision, anatomy and four-view review remain pending.", "",
             "| Chord | Max skin contact error (mm) | RMS (mm) | Wood vertices >0.25 mm | Max wood depth (mm) | Min open-string clearance (mm) | Barre skin triangles |", "|---|---:|---:|---:|---:|---:|---:|"]
    for chord_id, pose in library["poses"].items():
        m = pose["audit"]["metrics"]
        clear = min((s["minimumVertexClearanceMm"] for s in m["openStrings"]), default=None)
        lines.append(f"| {chord_id} | {m['maximumContactErrorMm']:.3f} | {m['rmsContactErrorMm']:.3f} | {m['woodInteriorVertexCount']} | {m['maximumWoodVertexPenetrationMm']:.3f} | {clear if clear is None else f'{clear:.3f}'} | {m.get('barre', {}).get('distinctSurfaceTriangles', '—')} |")
    lines.extend(["", "The exact numeric angles, per-string target/actual coordinates, source triangle indices and barycentric coordinates, per-open-string clearances, optimizer termination and pose fingerprints are in `authoring-metrics.json` and `hand-pose-candidates.json`.", ""])
    lines.extend(["Rebuild the initial library with:", "", "```sh",
                  "OPENBLAS_NUM_THREADS=1 python scripts/practice/generate-pose-library.py", "```", "",
                  "Use `--resume path/to/hand-pose-candidates.json --chords A,Dmaj7,Fm7,Gm7,Csus4 --evaluations 64` for a bounded refinement pass. Resume preserves unselected chord candidates. The checked-in natural C seed keeps authoring reproducible without relying on temporary files. The final artifacts include related-voicing warm starts and a short refinement pass; `authoring-run.json` records that provenance. No command sets a review gate to true.", ""])
    (output/"README.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rig", type=Path, default=ROOT/"docs/practice-trainer/models/authoring/rig-data.json")
    parser.add_argument("--metadata", type=Path, default=ROOT/"src/features/practice/assets/makehuman-left-arm.metadata.json")
    parser.add_argument("--seed", type=Path, default=ROOT/"docs/practice-trainer/pose-candidates/C-natural-authoring-seed.json")
    parser.add_argument("--output", type=Path, default=Path("/tmp/fretline-trainer-candidates"))
    parser.add_argument("--report-output", type=Path, default=ROOT/"docs/practice-trainer/pose-candidates")
    parser.add_argument("--evaluations", type=int, default=34)
    parser.add_argument("--resume", type=Path, help="Refine existing candidates, preserving any unselected chords")
    parser.add_argument("--chords", help="Optional comma-separated chord IDs for a bounded authoring pass")
    args = parser.parse_args()
    rig = solver.Rig(args.rig, palmar_sign=-1)
    metadata = json.loads(args.metadata.read_text())
    if rig.data["sha256"] != metadata["assetSha256"]:
        raise ValueError("Rig extraction and exported GLB metadata must have the same SHA-256")
    chords = central_chords()
    if args.chords:
        requested = set(args.chords.split(","))
        chords = [c for c in chords if c["id"] in requested]
        if len(chords) != len(requested):
            raise ValueError("Unknown requested chord")
    if args.seed.exists():
        seed_data = json.loads(args.seed.read_text())
        if seed_data.get("assetSha256", metadata["assetSha256"]) != metadata["assetSha256"]:
            raise ValueError("Authoring seed belongs to a different exported asset")
        c_seed = seed_data["solverParameters"]
    else:
        c_seed = solver.initial_parameters()
    fitter = LibraryFitter(rig)
    library = {"schemaVersion": 1, "assetSha256": metadata["assetSha256"],
               "rigSignature": "|".join(sorted(rig.by_name)),
               "createdAtUTC": datetime.now(timezone.utc).isoformat(),
               "reviewPolicy": "Every candidate requires actual skin contact, full collision, anatomy and independent multi-view review. Numerical convergence never approves a pose.",
               "poses": {}}
    if args.resume:
        previous = json.loads(args.resume.read_text())
        if previous["assetSha256"] != library["assetSha256"] or previous["rigSignature"] != library["rigSignature"]:
            raise ValueError("Resume candidates must match this asset and rig")
        library["poses"] = previous["poses"]
    library["authoring"] = {"generator": "scripts/practice/generate-pose-library.py",
                            "evaluationsPerPrimaryStage": args.evaluations,
                            "skinMethod": "exported rig FK and original weighted linear blend skinning",
                            "boneRotationConvention": "absolute local quaternion [x,y,z,w]; original translations and scales retained",
                            "rootConvention": "millimetre translation and proper quaternion on 1000x GLB-metre wrapper"}
    for chord in chords:
        started = time.monotonic()
        targets = targets_for(chord)
        if args.resume and chord["id"] in library["poses"]:
            seed = np.array(library["poses"][chord["id"]]["solverParameters"])
            low, high = fitter.bounds(chord)
            seed = np.clip(seed, low+1e-7, high-1e-7)
        else:
            seed = fitter.seed(chord, targets, c_seed)
        params, stages = fitter.fit(chord, targets, seed, args.evaluations)
        world, quaternions, rotation = rig.fk(params)
        metrics = fitter.audit(params, chord, targets)
        root = {"positionMm": params[:3].tolist(), "quaternion": Rotation.from_matrix(rotation).as_quat().tolist()}
        bones = {bone["name"]: {"quaternion": quaternions[i].tolist()} for i, bone in enumerate(rig.bones)}
        fingerprint = hashlib.sha256(json.dumps({"root": root, "bones": bones}, sort_keys=True).encode()).hexdigest()
        metrics.update({"poseFingerprintSha256": fingerprint, "authoringSeconds": time.monotonic()-started,
                        "optimizerStages": stages})
        record = {"chordId": chord["id"], "status": "needs-review", "reviewed": False, "root": root,
                  "bones": bones, "targets": targets,
                  "audit": {"collisionPassed": False, "contactPassed": False, "anatomyPassed": False,
                            "multiViewReviewed": False, "metrics": metrics},
                  "reason": {"th": "ท่ามือต้นแบบจากผิวโมเดลจริง ยังมีข้อจำกัดด้านการสัมผัสและการชน รอการตรวจภาพหลายมุมและกายวิภาค ใช้ผังคอร์ดที่ตรวจแล้วสำหรับฝึก",
                             "en": "An actual-skin authoring candidate with unresolved contact and collision limits. Anatomy and independent multi-view review are pending. Use the reviewed diagram for practice."},
                  "assetSha256": library["assetSha256"], "rigSignature": library["rigSignature"],
                  "solverParameters": params.tolist(), "palmarNormalSource": rig.palmar.tolist()}
        library["poses"][chord["id"]] = record
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output/f"{chord['id']}-candidate.json").write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n")
        print(json.dumps({"chord": chord["id"], "seconds": round(metrics["authoringSeconds"], 2),
                          "maxContactErrorMm": round(metrics["maximumContactErrorMm"], 3),
                          "woodInteriorVertices": metrics["woodInteriorVertexCount"],
                          "maxWoodDepthMm": round(metrics["maximumWoodVertexPenetrationMm"], 3)}), flush=True)
        write_reports(args.output, library)
    if len({v["audit"]["metrics"]["poseFingerprintSha256"] for v in library["poses"].values()}) != len(library["poses"]):
        raise ValueError("The authoring pass produced duplicate transforms")
    write_reports(args.report_output, library)


if __name__ == "__main__":
    main()
