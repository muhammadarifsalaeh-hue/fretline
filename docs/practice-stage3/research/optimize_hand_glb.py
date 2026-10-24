"""Technical GLB texture optimization, never pose/mesh generation.

Single embedded-buffer GLB; standard PNG/JPEG material textures only. Geometry,
skin, nodes and animation data are kept byte-for-byte. Meshopt-compressed views
and texture-source extensions are rejected instead of silently mishandled.
"""
import argparse
import copy
import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_glb(path):
    raw = Path(path).read_bytes()
    magic, version, total = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and total == len(raw), 'Invalid GLB header'
    chunks = []
    offset = 12
    while offset < total:
        length, kind = struct.unpack_from('<II', raw, offset)
        assert length % 4 == 0 and offset + 8 + length <= total
        chunks.append((kind, raw[offset + 8:offset + 8 + length]))
        offset += 8 + length
    assert [kind for kind, _ in chunks] == [0x4e4f534a, 0x004e4942], 'Only JSON+BIN supported'
    gltf = json.loads(chunks[0][1])
    assert len(gltf['buffers']) == 1 and 'uri' not in gltf['buffers'][0]
    assert all(view.get('buffer', 0) == 0 for view in gltf['bufferViews'])
    assert not any('EXT_meshopt_compression' in view.get('extensions', {}) for view in gltf['bufferViews'])
    assert not any(texture.get('extensions') for texture in gltf.get('textures', [])), 'Texture extensions need a separate optimizer'
    return gltf, chunks[1][1], raw


def view_bytes(gltf, binary, index):
    view = gltf['bufferViews'][index]
    start = view.get('byteOffset', 0)
    return binary[start:start + view['byteLength']]


def texture_infos(material):
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == 'extras':
                    continue
                if key.endswith('Texture') and isinstance(child, dict) and isinstance(child.get('index'), int):
                    yield child
                else:
                    yield from walk(child)
        elif isinstance(value, list):
            for child in value:
                yield from walk(child)
    yield from walk(material)


def srgb_to_linear(value):
    value /= 255
    return value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4


def remap_buffer_views(value, mapping):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'bufferView' and isinstance(child, int):
                value[key] = mapping[child]
            elif key != 'extras':
                remap_buffer_views(child, mapping)
    elif isinstance(value, list):
        for child in value:
            remap_buffer_views(child, mapping)


def accessor_bytes(gltf, binary, index):
    accessor = gltf['accessors'][index]
    assert 'sparse' not in accessor, 'Sparse mesh accessor validation needs separate handling'
    sizes = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
    widths = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4, 'MAT2': 4, 'MAT3': 9, 'MAT4': 16}
    width = sizes[accessor['componentType']] * widths[accessor['type']]
    view = gltf['bufferViews'][accessor['bufferView']]
    start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', width)
    return b''.join(binary[start + row * stride:start + row * stride + width] for row in range(accessor['count']))


def mesh_hashes(gltf, binary):
    result = {}
    for mi, mesh in enumerate(gltf['meshes']):
        for pi, primitive in enumerate(mesh['primitives']):
            for semantic, accessor in primitive['attributes'].items():
                result[f'{mi}/{pi}/{semantic}'] = sha(accessor_bytes(gltf, binary, accessor))
            if 'indices' in primitive:
                result[f'{mi}/{pi}/indices'] = sha(accessor_bytes(gltf, binary, primitive['indices']))
    return result


def run(source, target, maximum):
    original, binary, source_raw = read_glb(source)
    gltf = copy.deepcopy(original)
    textures = gltf.get('textures', [])
    images = gltf.get('images', [])
    decoded = {}
    for index, image in enumerate(images):
        assert 'bufferView' in image and image.get('mimeType') in {'image/png', 'image/jpeg'}
        decoded[index] = Image.open(io.BytesIO(view_bytes(gltf, binary, image['bufferView']))).copy()

    def constant(index):
        image = decoded[textures[index]['source']].convert('RGBA')
        extrema = image.getextrema()
        return tuple(lo for lo, hi in extrema) if all(lo == hi for lo, hi in extrema) else None

    changes = []
    for material in gltf.get('materials', []):
        pbr = material.get('pbrMetallicRoughness', {})
        if 'baseColorTexture' in pbr:
            pixel = constant(pbr['baseColorTexture']['index'])
            if pixel is not None:
                factor = pbr.get('baseColorFactor', [1, 1, 1, 1])
                pbr['baseColorFactor'] = [factor[c] * srgb_to_linear(pixel[c]) for c in range(3)] + [factor[3] * pixel[3] / 255]
                del pbr['baseColorTexture']
                changes.append({'material': material.get('name'), 'folded': 'baseColorTexture', 'sRGBA8': pixel, 'linearRGBAFactor': pbr['baseColorFactor']})
        if 'metallicRoughnessTexture' in pbr:
            pixel = constant(pbr['metallicRoughnessTexture']['index'])
            if pixel is not None:
                pbr['roughnessFactor'] = pbr.get('roughnessFactor', 1) * pixel[1] / 255
                pbr['metallicFactor'] = pbr.get('metallicFactor', 1) * pixel[2] / 255
                del pbr['metallicRoughnessTexture']
                changes.append({'material': material.get('name'), 'folded': 'metallicRoughnessTexture', 'linearRGBA8': pixel, 'roughnessFactor': pbr['roughnessFactor'], 'metallicFactor': pbr['metallicFactor']})
        if 'normalTexture' in material:
            index = material['normalTexture']['index']
            pixel = constant(index)
            if pixel is not None and pixel[:3] == (128, 128, 255):
                del material['normalTexture']
                changes.append({'material': material.get('name'), 'folded': 'neutralNormalTexture', 'note': 'Removed standard flat normal map; no normals recomputed.'})
            else:
                image = decoded[textures[index]['source']].convert('RGB')
                if image.getchannel('R').tobytes() == image.getchannel('G').tobytes() == image.getchannel('B').tobytes():
                    material.setdefault('extras', {})['fretlineHeightTextureAudit'] = {
                        'status': 'source-grayscale-height-in-normal-slot',
                        'runtimeActionRequired': 'Transfer loaded normalMap to bumpMap and clear normalMap, with a separately reviewed bumpScale. This file does not claim a valid tangent-space normal map.',
                    }
                    changes.append({'material': material.get('name'), 'warning': 'Grayscale height texture retained in original normalTexture slot pending explicit runtime correction.'})

    used_textures = sorted({info['index'] for mat in gltf.get('materials', []) for info in texture_infos(mat)})
    texture_mapping = {old: new for new, old in enumerate(used_textures)}
    for material in gltf.get('materials', []):
        for info in texture_infos(material):
            info['index'] = texture_mapping[info['index']]
    used_images = sorted({textures[index]['source'] for index in used_textures})
    image_mapping = {old: new for new, old in enumerate(used_images)}
    gltf['textures'] = [copy.deepcopy(textures[index]) for index in used_textures]
    for texture in gltf['textures']:
        texture['source'] = image_mapping[texture['source']]
    gltf['images'] = [copy.deepcopy(images[index]) for index in used_images]

    replacements = {}
    image_changes = []
    for old_index in used_images:
        image = decoded[old_index].copy()
        before = image.size
        if max(before) > maximum:
            image.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        options = {'format': 'PNG', 'compress_level': 9, 'optimize': True}
        # glTF's material slot defines color/data interpretation. Embedded custom
        # ICC/EXIF/XMP profiles are unsupported by the glTF image rules; stripping
        # metadata does not alter the resized pixel samples.
        image.info.clear()
        image.save(output, **options)
        encoded = output.getvalue()
        view_index = images[old_index]['bufferView']
        replacements[view_index] = encoded
        new_image = gltf['images'][image_mapping[old_index]]
        new_image['mimeType'] = 'image/png'
        image_changes.append({'name': images[old_index].get('name'), 'oldSize': before, 'newSize': image.size,
                              'sourceImageSHA256': sha(view_bytes(original, binary, view_index)),
                              'optimizedImageSHA256': sha(encoded), 'bytes': len(encoded),
                              'change': 'Lanczos maximum dimension resize, lossless PNG encoding and removal of unsupported color/profile/editor metadata; not a creative image alteration.'})

    removed_images = set(range(len(images))) - set(used_images)
    removed_views = {images[index]['bufferView'] for index in removed_images}
    all_image_views = {image['bufferView'] for image in images}
    # A view shared with an accessor must never be discarded as an image.
    accessor_views = {accessor['bufferView'] for accessor in gltf.get('accessors', []) if 'bufferView' in accessor}
    assert not removed_views & accessor_views
    keep_views = [i for i in range(len(gltf['bufferViews'])) if i not in removed_views]
    view_mapping = {old: new for new, old in enumerate(keep_views)}
    rebuilt = bytearray()
    new_views = []
    for old_index in keep_views:
        data = replacements.get(old_index, view_bytes(original, binary, old_index))
        rebuilt.extend(b'\0' * (-len(rebuilt) % 4))
        view = copy.deepcopy(gltf['bufferViews'][old_index])
        view['byteOffset'] = len(rebuilt)
        view['byteLength'] = len(data)
        view['buffer'] = 0
        rebuilt.extend(data)
        new_views.append(view)
    gltf['bufferViews'] = new_views
    remap_buffer_views(gltf, view_mapping)
    rebuilt.extend(b'\0' * (-len(rebuilt) % 4))
    gltf['buffers'][0]['byteLength'] = len(rebuilt)
    gltf.setdefault('asset', {}).setdefault('extras', {})['fretlineScratchOptimization'] = {
        'status': 'temporary candidate, no pose or anatomical certification',
        'originalSHA256': sha(source_raw),
        'changes': 'Texture-only technical optimization; skin height-map correction remains an explicit runtime requirement.',
    }
    payload = json.dumps(gltf, separators=(',', ':'), ensure_ascii=False).encode('utf8')
    payload += b' ' * (-len(payload) % 4)
    total = 12 + 8 + len(payload) + 8 + len(rebuilt)
    output = struct.pack('<4sII', b'glTF', 2, total) + struct.pack('<II', len(payload), 0x4e4f534a) + payload + struct.pack('<II', len(rebuilt), 0x004e4942) + rebuilt
    Path(target).write_bytes(output)

    final, final_binary, final_raw = read_glb(target)
    mesh_before = mesh_hashes(original, binary)
    mesh_after = mesh_hashes(final, final_binary)
    assert mesh_before == mesh_after
    for key in ['nodes', 'skins', 'meshes', 'animations', 'scenes']:
        assert original.get(key) == final.get(key), key
    for old_index in keep_views:
        if old_index not in all_image_views:
            assert view_bytes(original, binary, old_index) == view_bytes(final, final_binary, view_mapping[old_index]), old_index
    for accessor in final['accessors']:
        if 'bufferView' in accessor:
            view = final['bufferViews'][accessor['bufferView']]
            assert view['byteOffset'] + view['byteLength'] <= len(final_binary)
    source_pixels = sum(pic.width * pic.height for pic in decoded.values())
    output_pixels = sum(item['newSize'][0] * item['newSize'][1] for item in image_changes)
    report = {
        'source': str(source), 'target': str(target), 'sourceBytes': len(source_raw), 'optimizedBytes': len(final_raw),
        'sourceSHA256': sha(source_raw), 'optimizedSHA256': sha(final_raw),
        'sourceImages': len(images), 'optimizedImages': len(final['images']), 'imageChanges': image_changes,
        'materialChanges': changes, 'meshAccessorHashesBefore': mesh_before, 'meshAccessorHashesAfter': mesh_after,
        'allMeshAccessorsByteIdentical': True, 'allNonImageViewsByteIdentical': True,
        'skinNodeMeshAnimationStructureUnchanged': True,
        'sourceTextureRGBA8MipMiBEstimate': source_pixels * 4 * 4 / 3 / 1048576,
        'optimizedTextureRGBA8MipMiBEstimate': output_pixels * 4 * 4 / 3 / 1048576,
        'gpuEstimateLimit': 'RGBA8 plus full mip chain estimate only; actual driver allocations vary.',
        'runtimeMaterialCorrectionStillRequired': True,
        'noMirrorNoPoseNoBoneNoShapeEdits': True,
    }
    report_path = Path(target).with_suffix('.optimization.json')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--max-texture', type=int, default=1024)
    args = parser.parse_args()
    assert args.input.resolve() != args.output.resolve(), 'Never overwrite the source model'
    assert args.max_texture > 0
    report = run(args.input, args.output, args.max_texture)
    print(json.dumps({key: report[key] for key in ['sourceBytes', 'optimizedBytes', 'sourceImages', 'optimizedImages', 'allMeshAccessorsByteIdentical', 'sourceTextureRGBA8MipMiBEstimate', 'optimizedTextureRGBA8MipMiBEstimate']}, indent=2))
