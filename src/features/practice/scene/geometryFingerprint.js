// Geometry is static while the camera moves. Cache buffer work by the actual
// BufferAttribute references/versions; matrix changes still affect every result.
// Weak keys let replaced/disposed string geometry be collected with its buffers.
export function createGeometryFingerprint(root) {
  const cache = new WeakMap();
  let bufferScans = 0;
  const mix = (hash, word) => Math.imul(hash ^ word, 16777619) >>> 0;
  const signature = () => {
    let hash = 2166136261;
    root.traverse((object) => {
      const geometry = object.geometry, position = geometry?.attributes.position;
      if (!position) return;
      const index = geometry.index;
      let saved = cache.get(geometry);
      if (!saved || saved.position !== position || saved.positions !== position.array || saved.version !== position.version
        || saved.index !== index || saved.indices !== index?.array || saved.indexVersion !== index?.version) {
        let value = mix(2166136261, position.array.length);
        const positions = position.array instanceof Float32Array ? position.array : new Float32Array(position.array);
        const words = new Uint32Array(positions.buffer, positions.byteOffset, positions.length);
        for (const word of words) value = mix(value, word);
        value = mix(value, index?.array.length ?? 0);
        if (index) for (const word of index.array) value = mix(value, word);
        saved = { position, positions: position.array, version: position.version,
          index, indices: index?.array, indexVersion: index?.version, value };
        cache.set(geometry, saved); bufferScans++;
      }
      hash = mix(hash, saved.value);
      for (const word of new Uint32Array(new Float32Array(object.matrixWorld.elements).buffer)) hash = mix(hash, word);
    });
    return hash.toString(16).padStart(8, '0');
  };
  signature.bufferScans = () => bufferScans;
  return signature;
}
