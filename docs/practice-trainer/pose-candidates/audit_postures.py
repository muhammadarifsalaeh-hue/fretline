#!/usr/bin/env python3
"""Bounded non-contacting-chain cleanup and rejection diagnostics for all poses.

Preserves the root and every pressed finger chain. No audit gate is approved.
Raw independent skin-triangle crossing reports are retained in /tmp by default.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("pose_library_generator", ROOT/"scripts/practice/generate-pose-library.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def dense_geometry(rig, params, chord):
    world, _, _ = rig.fk(params)
    summaries, arrays, open_clearances = [], {}, {}
    for mesh in rig.data["meshes"]:
        skin = rig.skin(world) if mesh is rig.mesh else rig.skin_mesh(world, mesh)
        triangles = skin[np.array(mesh["indices"], dtype=int).reshape(-1, 3)]
        samples = np.concatenate((skin, triangles.mean(axis=1),
                                  (triangles[:, 0]+triangles[:, 1])/2,
                                  (triangles[:, 1]+triangles[:, 2])/2,
                                  (triangles[:, 2]+triangles[:, 0])/2))
        depth = generator.solver.wood_depth(samples)
        arrays[mesh["name"]] = depth
        summaries.append({"mesh": mesh["name"], "sampleCount": len(depth),
                          "interiorSamplesOverTenNanometres": int((depth > 1e-5).sum()),
                          "interiorSamplesOverQuarterMm": int((depth > .25).sum()),
                          "maximumInteriorDepthMm": float(depth.max())})
        if mesh is rig.mesh:
            px = np.clip(samples[:, 0], 0, 330)
            for string in chord["openStrings"]:
                clearance = np.sqrt((samples[:, 1]-generator.solver.string_y(string, px))**2 +
                                    (samples[:, 2]-generator.solver.string_z(string, px))**2 +
                                    (samples[:, 0]-px)**2)-generator.solver.GAUGES[string-1]/2
                open_clearances[string] = clearance
    summary = {"allMeshWoodSamples": summaries,
               "openStringSurfaceSamples": [{"string": key, "minimumSampleClearanceMm": float(value.min()),
                                              "samplesInsideString": int((value < -1e-5).sum()),
                                              "samplesWithinHalfMm": int((value < .5).sum())}
                                             for key, value in open_clearances.items()],
               "scope": "Actual LBS vertices, triangle centroids and edge midpoints; conservative analytic neck and open-string tubes. Sampling is a rejection diagnostic, not an exact mesh intersection proof."}
    return summary, arrays, open_clearances


def acceptable_geometry(before, after):
    reasons, new_wood, new_strings = [], 0, 0
    for name, depth in after[1].items():
        old = before[1][name]
        new_wood += int(((depth > 1e-5) & (old <= 1e-5)).sum())
        if depth.max() > old.max()+1e-5:
            reasons.append(f"deeper wood incursion on {name}")
    if new_wood:
        reasons.append("new wood sample incursions")
    for string, clearance in after[2].items():
        old = before[2][string]
        new_strings += int(((clearance < -1e-5) & (old >= -1e-5)).sum())
        if clearance.min() < min(float(old.min()), .5)-1e-5:
            reasons.append(f"reduced open-string {string} safety margin")
    if new_strings:
        reasons.append("new open-string sample incursions")
    return not reasons, {"acceptedAgainstGuitarSamples": not reasons, "newWoodSampleIncursions": new_wood,
                         "newOpenStringSampleIncursions": new_strings, "reasons": reasons}


def record_from_params(rig, original, params):
    record = copy.deepcopy(original)
    _, quaternions, rotation = rig.fk(params)
    record["root"] = {"positionMm": params[:3].tolist(),
                      "quaternion": generator.Rotation.from_matrix(rotation).as_quat().tolist()}
    record["bones"] = {bone["name"]: {"quaternion": quaternions[i].tolist()} for i, bone in enumerate(rig.bones)}
    record["solverParameters"] = params.tolist()
    return record


def bounded_thumb_fit(rig, original_params, safe_thumb, chord):
    """One small five-variable solve, keeping every contact chain and root fixed."""
    params = original_params.copy()
    # Use all vertices influenced by the thumb, including blended borders.
    thumb_joints = [i for i, name in enumerate(rig.mesh["skinJointNames"]) if name.startswith("finger1-")]
    influenced = np.any(np.isin(rig.joints, thumb_joints) & (rig.weights > 1e-5), axis=1)
    ids = np.flatnonzero(influenced)
    low = np.deg2rad([-10, -65, -15, -10, -35])
    high = np.deg2rad([55, 65, 45, 50, 35])
    initial = np.clip(safe_thumb, low+1e-7, high-1e-7)
    def residual(thumb):
        params[22:27] = thumb
        world, _, _ = rig.fk(params)
        points = rig.skin(world, ids)
        cap = rig.skin(world, rig.patch_ids["thumb"]).mean(axis=0)
        target_y = generator.solver.back_y(cap[0], np.clip(cap[2], -19, 19))-2
        out = list((thumb-safe_thumb)*np.array([.3, .3, .6, .6, .4]))
        out.extend(generator.solver.wood_depth(points)*18)
        out.extend([max(0., cap[1]-target_y)*1.5, max(0., abs(cap[2])-22)*.25])
        for string in chord["openStrings"]:
            px = np.clip(points[:, 0], 0, 330)
            distance = np.sqrt((points[:, 1]-generator.solver.string_y(string, px))**2 +
                               (points[:, 2]-generator.solver.string_z(string, px))**2 + (points[:, 0]-px)**2)
            out.extend(np.maximum(0, generator.solver.GAUGES[string-1]/2+.7-distance)*5)
        return out
    result = least_squares(residual, initial, bounds=(low, high), max_nfev=24,
                           ftol=1e-5, xtol=1e-5, gtol=1e-5, x_scale="jac")
    params[22:27] = result.x
    return params, {"evaluations": result.nfev, "cost": float(result.cost), "termination": result.message,
                    "scope": "Thumb-only five-variable bounded fit; all contact chains and wrist fixed"}


def run_self_audit(candidate_path, output_path):
    environment = dict(os.environ, OPENBLAS_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, str(ROOT/"scripts/practice/audit-hand-self-collisions.py"),
                             str(candidate_path), "--output", str(output_path)],
                            env=environment, capture_output=True, text=True, check=True)
    return json.loads(output_path.read_text())


def summarize_self(report):
    by_finger = {finger: 0 for finger in generator.FINGERS}
    other_fingers = 0
    for pair in report["pairs"]:
        labels = [name for triangle in pair["dominantBones"] for name in triangle]
        for finger, number in generator.solver.NUMBERS.items():
            if any(name.startswith(f"finger{number}-") for name in labels):
                by_finger[finger] += 1
        if any(name.startswith(("finger2-", "finger3-", "finger4-")) for name in labels):
            other_fingers += 1
    return {"crossingPairCount": report["crossingPairCount"], "broadphasePairs": report["broadphasePairs"],
            "crossingPairsInvolvingFinger": by_finger, "categoryCounts": report["categoryCounts"],
            "crossingPairsInvolvingIndexMiddleRing": other_fingers,
            "scope": report["scope"], "fingerCountsOverlap": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT/"docs/practice-trainer/pose-candidates/hand-pose-candidates.json")
    parser.add_argument("--safe-seed", type=Path, default=Path("/tmp/fretline-trainer-pose/C-thumb-bent0.json"))
    parser.add_argument("--raw", type=Path, default=Path("/tmp/fretline-trainer-candidates/posture-audit"))
    parser.add_argument("--jobs", type=int, default=3)
    args = parser.parse_args()
    args.raw.mkdir(parents=True, exist_ok=True)
    library = json.loads(args.library.read_text())
    rig = generator.solver.Rig(ROOT/"docs/practice-trainer/models/authoring/rig-data.json")
    if library["assetSha256"] != rig.data["sha256"]:
        raise ValueError("Candidate and rig hashes differ; retain the source extraction before auditing")
    safe = json.loads(args.safe_seed.read_text())
    safe_params = np.array(safe["solverParameters"])
    safe_thumb, safe_unused = safe_params[22:27], safe_params[18:22]
    chords = {chord["id"]: chord for chord in generator.central_chords()}
    fitter = generator.LibraryFitter(rig)
    (args.raw/"pre-safe-posture-library.json").write_text(json.dumps(library, indent=2)+"\n")
    variants, diagnostics, jobs = {}, {}, []
    for key, original in library["poses"].items():
        chord = chords[key]
        params = np.array(original["solverParameters"])
        baseline = dense_geometry(rig, params, chord)
        unused = params.copy()
        pressed = {t["finger"] for t in original["targets"]}
        for i, finger in enumerate(generator.FINGERS[:4]):
            if finger not in pressed:
                unused[6+4*i:10+4*i] = safe_unused
        unused_geometry = dense_geometry(rig, unused, chord)
        unused_ok, unused_decision = acceptable_geometry(baseline, unused_geometry)
        if not unused_ok:
            unused = params.copy()
            unused_geometry = baseline
        thumb = params.copy(); thumb[22:27] = safe_thumb
        thumb_geometry = dense_geometry(rig, thumb, chord)
        thumb_ok, thumb_decision = acceptable_geometry(baseline, thumb_geometry)
        fit_stats = None
        if not thumb_ok:
            fitted, fit_stats = bounded_thumb_fit(rig, params, safe_thumb, chord)
            fitted_geometry = dense_geometry(rig, fitted, chord)
            fitted_ok, fitted_decision = acceptable_geometry(baseline, fitted_geometry)
            thumb_decision["boundedFit"] = {**fit_stats, **fitted_decision}
            if fitted_ok:
                thumb, thumb_geometry, thumb_ok = fitted, fitted_geometry, True
        combined = unused.copy()
        if thumb_ok:
            combined[22:27] = thumb[22:27]
        combined_geometry = dense_geometry(rig, combined, chord)
        combined_ok, combined_decision = acceptable_geometry(baseline, combined_geometry)
        if not combined_ok:
            combined = unused.copy(); combined_geometry = unused_geometry
        variants[key] = {"baseline": (params, baseline), "unused-only": (unused, unused_geometry),
                         "combined-safe": (combined, combined_geometry)}
        diagnostics[key] = {"unusedPosture": unused_decision, "thumbPosture": thumb_decision,
                            "combinedPosture": combined_decision, "variants": {}}
        for name, (variant, geometry) in variants[key].items():
            path = args.raw/f"{key}-{name}.json"
            report_path = args.raw/f"{key}-{name}-self.json"
            # Raw unused-only files supplied by the parallel independent audit
            # may differ when guitar geometry rejected the proposed posture.
            record = record_from_params(rig, original, variant)
            unchanged = np.array_equal(variant, params)
            if name == "unused-only" and not unused_ok:
                path = args.raw/f"{key}-baseline.json"
                report_path = args.raw/f"{key}-baseline-self.json"
            if name == "combined-safe" or not path.exists():
                path.write_text(json.dumps(record, indent=2)+"\n")
            diagnostics[key]["variants"][name] = {"geometry": geometry[0], "recordPath": str(path),
                                                   "selfReportPath": str(report_path)}
            if name == "combined-safe" and unchanged:
                diagnostics[key]["variants"][name]["selfReportPath"] = str(args.raw/f"{key}-baseline-self.json")
            elif name == "combined-safe" and np.array_equal(variant, unused):
                diagnostics[key]["variants"][name]["selfReportPath"] = diagnostics[key]["variants"]["unused-only"]["selfReportPath"]
            elif name == "combined-safe":
                jobs.append((path, report_path))
        print(json.dumps({"chord": key, "safeUnused": unused_ok, "safeThumb": thumb_ok,
                          "thumbFit": fit_stats is not None}), flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(run_self_audit, path, output): path.name for path, output in jobs}
        for future in as_completed(futures):
            result = future.result()
            print(json.dumps({"audit": futures[future], "crossings": result["crossingPairCount"]}), flush=True)
    # The independent parallel audit supplies all baselines and raw unused
    # candidates. Wait for missing reports only by running the same helper.
    for key, entries in diagnostics.items():
        original = library["poses"][key]
        for name, variant in entries["variants"].items():
            report_path = Path(variant["selfReportPath"])
            if not report_path.exists():
                run_self_audit(Path(variant["recordPath"]), report_path)
            variant["self"] = summarize_self(json.loads(report_path.read_text()))
        chosen = min(entries["variants"], key=lambda name: (entries["variants"][name]["self"]["crossingPairCount"],
                                                           {"combined-safe": 0, "unused-only": 1, "baseline": 2}[name]))
        params, geometry = variants[key][chosen]
        record = record_from_params(rig, original, params)
        # Pressed source bones and root must remain bit-for-bit equivalent.
        assert np.array_equal(params[:6], np.array(original["solverParameters"])[:6])
        for finger in {t["finger"] for t in original["targets"]}:
            i = generator.FINGERS.index(finger)
            assert np.array_equal(params[6+4*i:10+4*i], np.array(original["solverParameters"])[6+4*i:10+4*i])
        metrics = fitter.audit(params, chords[key], original["targets"])
        old_metrics = original["audit"]["metrics"]
        for metric in ("optimizerStages", "authoringSeconds"):
            metrics[metric] = old_metrics[metric]
        metrics["poseFingerprintSha256"] = hashlib.sha256(json.dumps({"root": record["root"], "bones": record["bones"]}, sort_keys=True).encode()).hexdigest()
        metrics["denseGeometryAudit"] = geometry[0]
        metrics["skinSelfTriangleAudit"] = entries["variants"][chosen]["self"]
        metrics["selfCollisionAudit"] = "crossings found" if metrics["skinSelfTriangleAudit"]["crossingPairCount"] else "zero noncoplanar skin crossings; coplanar and sleeve audit pending"
        entries["selectedVariant"] = chosen
        entries["selectedCrossings"] = metrics["skinSelfTriangleAudit"]["crossingPairCount"]
        entries["selectedGeometry"] = geometry[0]
        record["audit"] = {"collisionPassed": False, "contactPassed": False, "anatomyPassed": False,
                           "multiViewReviewed": False, "metrics": metrics}
        record["reviewed"], record["status"] = False, "needs-review"
        record["postureRefinement"] = {"selectedVariant": chosen,
                                       "preservedPressedFingerChains": sorted({t["finger"] for t in original["targets"]}),
                                       "rootPreserved": True, "safeSeed": str(args.safe_seed)}
        library["poses"][key] = record
        (args.raw.parent/f"{key}-candidate.json").write_text(json.dumps(record, indent=2, ensure_ascii=False)+"\n")
    report = {"schemaVersion": 1, "assetSha256": library["assetSha256"], "chordCount": len(diagnostics),
              "allReviewGatesFalse": True, "method": "Pressed bones and root fixed; safe thumb and relaxed unused chains selected only without new sampled guitar collision, then lowest independent skin-triangle crossing count.",
              "limitations": "Skin segment/triangle audit omits coplanar cases and sleeve. Dense neck/string samples are rejection diagnostics. Actual deformed-string mesh intersections and independent anatomy/multi-view review remain pending.",
              "chords": diagnostics}
    destination = args.library.parent
    (destination/"physical-posture-audit.json").write_text(json.dumps(report, indent=2)+"\n")
    write_physical_markdown(destination, report)
    generator.write_reports(destination, library)
    generator.write_reports(args.raw.parent, library)
    print(json.dumps({"completed": len(diagnostics), "zeroSkinCrossings": sum(x["selectedCrossings"] == 0 for x in diagnostics.values())}), flush=True)


def write_physical_markdown(destination, report):
    lines = ["# Physical posture rejection audit", "",
             "Every candidate remains **needs-review**. This pass changes only the thumb or unused finger chains. All pressed chains, barre contacts and wrist transforms are retained. A replacement is rejected if it creates newly interior neck samples, deeper wood penetration, newly intersecting open-string samples or a lower open-string safety margin. Among accepted variants, the one with fewer independent skin-triangle crossings is retained.", "",
             "Skin triangle counts use the independent bidirectional segment/triangle helper, excluding pairs that share an original vertex index. Coplanar contacts and sleeve self intersections remain outside that test. Wood samples include every actual skin/sleeve vertex, triangle centroid and edge midpoint. Actual string-mesh intersection and independent anatomy/multi-view review remain pending. Zero sampled incursions would not certify a practice pose.", "",
             "Thumb, little and other-finger involvement counts can overlap: one crossing can involve two fingers.", "",
             "| Chord | Original crossings | Selected crossings | Thumb | Little | Index/middle/ring | Wood samples >0.25mm | Max wood depth mm | Selected |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for key, chord in report["chords"].items():
        variant = chord["variants"][chord["selectedVariant"]]
        self_audit = variant["self"]
        fingers = self_audit["crossingPairsInvolvingFinger"]
        wood = variant["geometry"]["allMeshWoodSamples"]
        lines.append(f"| {key} | {chord['variants']['baseline']['self']['crossingPairCount']} | {self_audit['crossingPairCount']} | {fingers['thumb']} | {fingers['little']} | {self_audit.get('crossingPairsInvolvingIndexMiddleRing', 'see JSON')} | {sum(x['interiorSamplesOverQuarterMm'] for x in wood)} | {max(x['maximumInteriorDepthMm'] for x in wood):.3f} | {chord['selectedVariant']} |")
    (destination/"physical-posture-audit.md").write_text("\n".join(lines)+"\n")


if __name__ == "__main__":
    main()
