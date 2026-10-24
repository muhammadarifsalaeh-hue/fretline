# Temporary optimized hand candidate

Original model: 3D Rigged Hand Model © 2026 Emma L. D. Lieker.
Source: https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c
License: CC BY-NC 4.0, https://creativecommons.org/licenses/by-nc/4.0/
Noncommercial use and attribution remain required. This scratch candidate has not been adopted into Fretline.

Changes: maximum texture dimension1024 with Lanczos resize and lossless PNG encoding; strictly constant nail textures folded into their equivalent PBR factors, including sRGB-to-linear base color conversion; buffer views repacked. Mesh positions, normals, UVs, indices, joint indices, weights, skin, nodes and animation data are unchanged. No mirroring, pose, joint, or hand-shape edits were performed.

Important inherited material defect: the source stores a grayscale skin height image in the glTF normalTexture slot. It remains in that slot for an explicit runtime adapter to transfer normalMap to bumpMap and clear normalMap. This GLB alone does NOT claim a corrected tangent-space normal map or a finished realistic material. The material extras carry the same warning.

This is not a verified C-major pose or anatomical collision pass. See the .optimization.json file for byte hashes, changes and memory estimate.
