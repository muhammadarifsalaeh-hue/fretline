#!/usr/bin/env python3
"""Snapshot and reject actual runtime rig candidates without approving poses.

Runs serially, once per chord. This intentionally does not solve new poses,
modify runtime data, or infer anatomy approval from numerical convergence.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("candidate_generator", ROOT / "scripts/practice/generate-pose-library.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def actual_world(rig, record):
    """Read absolute local bone rotations, not cached optimizer parameters."""
    local = rig.rest_local.copy()
    for index, bone in enumerate(rig.bones):
        local[index, :3, :3] = Rotation.from_quat(record["bones"][bone["name"]]["quaternion"]).as_matrix() * np.asarray(bone["scale"])[None, :]
    world = np.zeros_like(local)
    done = set()

    def visit(index):
        if index in done:
            return
        parent = rig.parents[index]
        if parent >= 0:
            visit(parent)
            world[index] = world[parent] @ local[index]
        else:
            world[index] = local[index]
        done.add(index)

    for index in range(len(world)):
        visit(index)
    root = np.eye(4)
    root[:3, :3] = Rotation.from_quat(record["root"]["quaternion"]).as_matrix() * 1000
    root[:3, 3] = record["root"]["positionMm"]
    return root @ world


def geometry_diagnostics(rig, world, record, chord):
    geometry, opens = [], []
    skin = None
    for mesh in rig.data["meshes"]:
        vertices = rig.skin(world) if mesh is rig.mesh else rig.skin_mesh(world, mesh)
        triangles = vertices[np.asarray(mesh["indices"], dtype=int).reshape(-1, 3)]
        samples = np.concatenate((vertices, triangles.mean(axis=1), (triangles[:, 0] + triangles[:, 1]) / 2,
                                  (triangles[:, 1] + triangles[:, 2]) / 2, (triangles[:, 2] + triangles[:, 0]) / 2))
        depth = generator.solver.wood_depth(samples)
        geometry.append({"mesh": mesh["name"], "sampleCount": len(samples),
                         "interiorSamplesOverQuarterMm": int((depth > .25).sum()),
                         "maximumInteriorDepthMm": float(depth.max())})
        if mesh is rig.mesh:
            skin = vertices
            px = np.clip(samples[:, 0], 0, 330)
            for string in chord["openStrings"]:
                clearance = np.sqrt((samples[:, 1] - generator.solver.string_y(string, px)) ** 2 +
                                    (samples[:, 2] - generator.solver.string_z(string, px)) ** 2 +
                                    (samples[:, 0] - px) ** 2) - generator.solver.GAUGES[string - 1] / 2
                opens.append({"string": string, "minimumSampleClearanceMm": float(clearance.min()),
                              "samplesInsideTube": int((clearance < -1e-5).sum()),
                              "samplesWithinHalfMm": int((clearance < .5).sum())})
    contacts = []
    for entry in record.get("audit", {}).get("metrics", {}).get("padContacts", []):
        if not all(key in entry for key in ("surfaceTriangleVertexIndices", "surfaceBarycentric", "actualPositionMm")):
            continue
        indices = np.asarray(entry["surfaceTriangleVertexIndices"], dtype=int)
        barycentric = np.asarray(entry["surfaceBarycentric"])
        point = barycentric @ skin[indices]
        error = float(np.linalg.norm(point - entry["positionMm"]))
        contacts.append({"finger": entry["finger"], "string": entry["string"], "fret": entry["fret"],
                         "kind": entry["kind"], "contactErrorMm": error,
                         "reconstructionErrorMm": float(np.linalg.norm(point - entry["actualPositionMm"]))})
    return {"woodSampling": geometry, "openStringSampling": opens, "reconstructedContacts": contacts,
            "maximumContactErrorMm": max((entry["contactErrorMm"] for entry in contacts), default=None),
            "maximumContactReconstructionErrorMm": max((entry["reconstructionErrorMm"] for entry in contacts), default=None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--library", type=Path, default=ROOT / "src/features/practice/assets/hand-poses.json")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("runtime-review"))
    parser.add_argument("--chords", help="Comma-separated subset; default audits every snapshot chord")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    library_bytes = args.library.read_bytes()
    library = json.loads(library_bytes)
    chords = {chord["id"]: chord for chord in generator.central_chords()}
    rig = generator.solver.Rig(ROOT / "docs/practice-trainer/models/authoring/rig-data.json")
    requested = set(args.chords.split(",")) if args.chords else set(library["poses"])
    if requested - set(library["poses"]):
        raise ValueError("Unknown requested chord snapshot")
    actual_asset = hashlib.sha256((ROOT / "src/features/practice/assets/makehuman-left-arm-sleeved.glb").read_bytes()).hexdigest()
    if actual_asset != rig.data["sha256"]:
        raise ValueError("Rig extraction is stale relative to the actual model asset")
    if library["assetSha256"] != actual_asset:
        equivalence = json.loads((ROOT / "docs/practice-trainer/models/authoring/hand-rig-equivalence.json").read_text())
        if not (equivalence["beforeSha256"] == library["assetSha256"] and
                equivalence["afterSha256"] == actual_asset and equivalence["boneNodesIdentical"] and
                equivalence["skinDefinitionsIdentical"] and equivalence["inverseBindBytesIdentical"] and
                all(mesh["allAttributeBytesIdentical"] and mesh["allIndexBytesIdentical"] for mesh in equivalence["meshes"])):
            raise ValueError("Different assets require explicit byte-identical hand and rig evidence")
    rows = []
    environment = dict(os.environ, OPENBLAS_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    for key, record in library["poses"].items():
        if key not in requested:
            continue
        candidate = args.output / f"{key}-snapshot.json"
        candidate.write_text(json.dumps(record, separators=(",", ":")) + "\n")
        raw = args.output / f"{key}-skin-crossings.json"
        subprocess.run([sys.executable, str(ROOT / "scripts/practice/audit-hand-self-collisions.py"),
                        str(candidate), "--output", str(raw)], env=environment, check=True, stdout=subprocess.DEVNULL)
        crossings = json.loads(raw.read_text())
        with gzip.open(str(raw) + ".gz", "wb") as handle:
            handle.write(raw.read_bytes())
        raw.unlink()
        world = actual_world(rig, record)
        numerical = geometry_diagnostics(rig, world, record, chords[key])
        problems = []
        if crossings["crossingPairCount"]:
            problems.append(f"{crossings['crossingPairCount']} nonadjacent skin triangle crossing/overlap pairs")
        for mesh in numerical["woodSampling"]:
            if mesh["interiorSamplesOverQuarterMm"]:
                problems.append(f"{mesh['mesh']}: {mesh['interiorSamplesOverQuarterMm']} sampled points more than 0.25 mm inside conservative wood")
        for string in numerical["openStringSampling"]:
            if string["samplesInsideTube"]:
                problems.append(f"open string {string['string']}: {string['samplesInsideTube']} sampled skin points inside tube")
        problems.append("Full guitar-triangle, clothing/self, anatomical and four-view approval is separate and not established by this audit")
        row = {"chordId": key, "statusAtSnapshot": record["status"], "reviewedAtSnapshot": record["reviewed"],
               "actualTransformSha256": canonical_hash({"root": record["root"], "bones": record["bones"]}),
               "actualWorldMatricesSha256": canonical_hash(world.round(9).tolist()),
               "boneCount": len(record["bones"]), "skinCrossingPairs": crossings["crossingPairCount"],
               "coplanarOverlapPairs": crossings["coplanarOverlapPairCount"],
               "selfCrossingCategoryCounts": crossings["categoryCounts"], **numerical,
               "problems": problems, "snapshot": candidate.name, "rawCrossingsGzip": raw.name + ".gz",
               "allApprovalGatesRemainUnchanged": True}
        rows.append(row)
        (args.output / "progress.json").write_text(json.dumps({"complete": len(rows), "rows": rows}, indent=2) + "\n")
        print(json.dumps({"chord": key, "skinCrossings": row["skinCrossingPairs"], "woodSamplesOverQuarterMm": sum(m["interiorSamplesOverQuarterMm"] for m in row["woodSampling"])}), flush=True)
    report = {"schemaVersion": 1, "createdAtUTC": datetime.now(timezone.utc).isoformat(),
              "librarySnapshotSha256": hashlib.sha256(library_bytes).hexdigest(),
              "libraryDeclaredAssetSha256": library["assetSha256"], "auditedActualRigAssetSha256": rig.data["sha256"],
              "handAttributeEquivalenceEvidence": "../../models/authoring/hand-rig-equivalence.json",
              "scope": "Actual root and local bone quaternions reconstructed through exported GLB skin weights. Skin-only triangle crossings include coplanar interior overlaps. Wood/open-string rejection uses actual skin and garment vertices, triangle centroids and edge midpoints against conservative analytical solids. Sampling is not proof of absence of collisions. This report never certifies a pose.",
              "count": len(rows), "uniqueActualTransformCount": len({r["actualWorldMatricesSha256"] for r in rows}),
              "rowsWithSkinCrossings": sum(r["skinCrossingPairs"] > 0 for r in rows),
              "rows": rows}
    (args.output / "summary.json").write_text(json.dumps(report, indent=2) + "\n")
    lines = ["# Actual runtime hand candidate rejection audit", "", report["scope"], "",
             "The snapshots below are immutable inputs for this audit; later C refinements must be assessed against their own transform hash. No runtime status or approval gate was changed.", "",
             "| Chord | Skin crossing pairs | Wood samples >0.25 mm | Smallest open-string sampled clearance (mm) | Status at snapshot |",
             "|---|---:|---:|---:|---|"]
    for row in rows:
        clearance = min((s["minimumSampleClearanceMm"] for s in row["openStringSampling"]), default=None)
        lines.append(f"| {row['chordId']} | {row['skinCrossingPairs']} | {sum(m['interiorSamplesOverQuarterMm'] for m in row['woodSampling'])} | {'—' if clearance is None else f'{clearance:.3f}'} | {row['statusAtSnapshot']} |")
    lines.extend(["", f"{len(rows)} actual poses audited; {report['uniqueActualTransformCount']} distinct transform fingerprints; {report['rowsWithSkinCrossings']} have skin crossing/overlap rejections.", "",
                  "Raw triangle indices, bone categories and crossing locations are retained in the gzip reports. See `summary.json` for complete contact reconstruction, per-mesh and per-open-string measurements, source hashes and limitations.", ""])
    (args.output / "README.md").write_text("\n".join(lines))
    (args.output / "progress.json").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
