import { fileURLToPath } from 'node:url';

/** A built module URL enables explicit retry after WebKit caches a failed import. */
export function practiceSceneModule() {
  const virtualId = 'virtual:fretline-practice-scene';
  const resolvedId = `\0${virtualId}`;
  let build = false;
  return {
    name: 'fretline-practice-scene-url',
    configResolved(config) { build = config.command === 'build'; },
    resolveId(id) { return id === virtualId ? resolvedId : null; },
    load(id) {
      if (id !== resolvedId) return null;
      if (!build) return 'export default "/src/features/practice/scene/createNeckScene.js";';
      const reference = this.emitFile({
        type: 'chunk',
        id: fileURLToPath(new URL('../../src/features/practice/scene/createNeckScene.js', import.meta.url)),
        name: 'practice-three',
        preserveSignature: 'strict',
      });
      return `export default import.meta.ROLLUP_FILE_URL_${reference};`;
    },
  };
}
