import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { createHandReveal } from './handReveal.js';

// This module is reachable only through the lazy practice scene. Assets are
// fetched by the scene, so visiting the catalog never downloads the hand.
const MODEL_URL = new URL('../assets/makehuman-left-arm-sleeved.glb', import.meta.url).href;
const METADATA_URL = new URL('../assets/makehuman-left-arm.metadata.json', import.meta.url).href;
const POSES_URL = new URL('../assets/hand-poses.json', import.meta.url).href;
const reason = (th, en) => ({ th, en });
const REASONS = {
  loading: reason('กำลังโหลดโมเดลมือ ตำแหน่งทองและผังคอร์ดยังใช้งานได้', 'Loading the hand model. Gold markers and the chord diagram remain available.'),
  error: reason('โหลดโมเดลมือไม่สำเร็จ ตำแหน่งทองและผังคอร์ดยังใช้งานได้', 'The hand model could not load. Gold markers and the chord diagram remain available.'),
  missing: reason('ยังไม่มีท่ามือสำหรับคอร์ดนี้ ใช้ผังคอร์ดและหมายเลขนิ้ว', 'No hand pose is available for this chord. Use the diagram and finger numbers.'),
  mismatch: reason('ข้อมูลท่ามือไม่ตรงกับโมเดลที่โหลด จึงซ่อนมือไว้', 'The pose data does not match this hand model, so the hand is hidden.'),
  review: reason('ท่ามือนี้ยังรอตรวจทาน ไม่ใช้เป็นท่าสำหรับฝึก', 'This hand pose needs review and must not be used as a practice example.'),
  invalid: reason('ข้อมูลท่ามือไม่สมบูรณ์ จึงใช้ผังคอร์ดและหมายเลขนิ้ว', 'The hand pose data is incomplete. Use the chord diagram and finger numbers.'),
};

const finiteArray = (value, length) => Array.isArray(value) && value.length === length && value.every(Number.isFinite);
const validQuaternion = (value) => finiteArray(value, 4) && Math.abs(Math.hypot(...value) - 1) < .02;
const namesSignature = (names) => [...names].sort().join('|');
const poseReason = (value, fallback) => typeof value?.th === 'string' && typeof value?.en === 'string' ? value : fallback;

/** Evidence gates are deliberately separate from whether a candidate can render. */
export function assessHandPose({ library, metadata, assetSha256, boneNames, chordId }) {
  const record = library?.poses?.[chordId];
  if (!Array.isArray(boneNames) || !boneNames.length || boneNames.some((name) => typeof name !== 'string' || !name)
    || new Set(boneNames).size !== boneNames.length) {
    return { status: 'unavailable', candidate: false, reason: REASONS.mismatch };
  }
  const actualRig = namesSignature(boneNames);
  const metadataRig = metadata?.rigSignature || (Array.isArray(metadata?.expectedBoneNames) ? namesSignature(metadata.expectedBoneNames) : '');
  const matches = library?.schemaVersion === 1 && metadata?.schemaVersion === 1 && !!assetSha256
    && library.assetSha256 === assetSha256 && metadata?.assetSha256 === assetSha256
    && library.rigSignature === actualRig && metadataRig === actualRig
    && metadata.millimetresPerAssetUnit === 1000;
  if (!matches) return { status: 'unavailable', candidate: false, reason: REASONS.mismatch };
  if (!record || record.status === 'unavailable') return { status: 'unavailable', candidate: false, reason: poseReason(record?.reason, REASONS.missing) };
  if (record.status !== 'needs-review' && record.status !== 'verified') return { status: 'unavailable', candidate: false, reason: REASONS.invalid };
  const complete = validQuaternion(record.root?.quaternion) && finiteArray(record.root?.positionMm, 3)
    && boneNames.every((name) => validQuaternion(record.bones?.[name]?.quaternion));
  if (!complete) return { status: 'unavailable', candidate: false, reason: REASONS.invalid };
  // A readable source rig is separate from evidence that this particular chord
  // is safe to copy. Every physical and visual review gate must explicitly pass.
  const verified = record.status === 'verified' && record.reviewed === true
    && record.audit?.collisionPassed === true && record.audit?.contactPassed === true
    && record.audit?.anatomyPassed === true && record.audit?.multiViewReviewed === true;
  return {
    status: verified ? 'verified' : 'needs-review', candidate: true, record,
    reason: verified ? poseReason(record.reason, reason('ท่ามือผ่านการตรวจทานแล้ว', 'This hand pose has been reviewed.'))
      : record.status === 'needs-review' ? poseReason(record.reason, REASONS.review) : REASONS.review,
  };
}

/** Dispose shared GLTF resources once, including GPU skinning textures. */
export function disposeHandObject(root) {
  const geometries = new Set(), materials = new Set(), textures = new Set(), skeletons = new Set(), images = new Set();
  root.traverse((object) => {
    if (object.geometry) geometries.add(object.geometry);
    if (object.skeleton) skeletons.add(object.skeleton);
    (object.material ? (Array.isArray(object.material) ? object.material : [object.material]) : []).forEach((material) => materials.add(material));
  });
  materials.forEach((material) => {
    Object.values(material).forEach((value) => { if (value?.isTexture) textures.add(value); });
    material.dispose();
  });
  textures.forEach((texture) => { if (texture.source?.data) images.add(texture.source.data); texture.dispose(); });
  images.forEach((source) => source.close?.());
  skeletons.forEach((skeleton) => skeleton.dispose());
  geometries.forEach((geometry) => geometry.dispose());
  root.removeFromParent(); root.clear();
}

function poseSignature(bones, wrapper) {
  // Hash the actual applied local bone quaternions and root transform, including
  // candidates while hidden. A chord ID or precomputed JSON hash is insufficient.
  let hash = 2166136261;
  const values = [...wrapper.position.toArray(), ...wrapper.quaternion.toArray()];
  [...bones].sort(([a], [b]) => a.localeCompare(b)).forEach(([, bone]) => values.push(...bone.quaternion.toArray()));
  for (const word of new Uint32Array(new Float32Array(values).buffer)) hash = Math.imul(hash ^ word, 16777619) >>> 0;
  return hash.toString(16).padStart(8, '0');
}

export function createHandPoseEngine({ scene, canvas, chord, nutX, unit, invalidate, onPoseStatus = () => {} }) {
  const guitarSpace = new THREE.Group();
  guitarSpace.name = 'Hand_Guitar_Millimetres';
  guitarSpace.position.x = nutX; guitarSpace.scale.setScalar(1 / unit);
  const wrapper = new THREE.Group();
  wrapper.name = 'Hand_Pose_Root'; wrapper.scale.setScalar(1000); wrapper.visible = false;
  guitarSpace.add(wrapper); scene.add(guitarSpace);
  let currentChord = chord, reviewMode = false, disposed = false, revision = 0;
  let assetStatus = 'loading', assetSha256 = '', metadata, library, asset, controller;
  let bones = new Map(), rest = new Map();
  const reveal = createHandReveal(wrapper, { invalidate, onProgress({ phase, progress }) {
    canvas.dataset.handRevealState = phase; canvas.dataset.handRevealProgress = String(progress);
  } });

  const resetRest = () => {
    bones.forEach((bone, name) => {
      const original = rest.get(name);
      bone.position.copy(original.position); bone.quaternion.copy(original.quaternion); bone.scale.copy(original.scale);
    });
    wrapper.position.set(0, 0, 0); wrapper.quaternion.identity();
  };
  const publish = () => {
    if (disposed) return;
    let assessment = { status: 'unavailable', candidate: false, reason: assetStatus === 'loading' ? REASONS.loading : REASONS.error };
    if (assetStatus === 'ready') assessment = assessHandPose({ library, metadata, assetSha256, boneNames: [...bones.keys()], chordId: currentChord.id });
    const previouslyVisible = wrapper.visible;
    const previousSignature = canvas.dataset.handPoseSignature;
    wrapper.visible = false;
    if (asset) {
      resetRest();
      if (assessment.candidate) {
        wrapper.position.fromArray(assessment.record.root.positionMm);
        wrapper.quaternion.fromArray(assessment.record.root.quaternion).normalize();
        bones.forEach((bone, name) => bone.quaternion.fromArray(assessment.record.bones[name].quaternion).normalize());
        wrapper.visible = assessment.status === 'verified' || reviewMode;
      }
      wrapper.updateMatrixWorld(true);
      asset.traverse((object) => { if (object.isSkinnedMesh) object.skeleton.update(); });
    }
    const signature = asset ? poseSignature(bones, wrapper) : '';
    if (!wrapper.visible) reveal.cancel();
    else if (!previouslyVisible || signature !== previousSignature) reveal.start();
    canvas.dataset.handStatus = assessment.status;
    canvas.dataset.handAssetStatus = assetStatus;
    canvas.dataset.handVisible = String(wrapper.visible);
    canvas.dataset.handModelReady = String(assetStatus === 'ready');
    canvas.dataset.handChordId = currentChord.id;
    canvas.dataset.handReviewMode = String(reviewMode);
    canvas.dataset.handPoseSignature = signature;
    canvas.dataset.handModelSha256 = assetSha256;
    onPoseStatus({ chordId: currentChord.id, status: assessment.status, assetStatus, reason: assessment.reason, reviewMode });
    invalidate();
  };
  const clearAsset = () => {
    wrapper.visible = false; reveal.reset();
    if (asset) disposeHandObject(asset);
    asset = null; bones.clear(); rest.clear(); assetSha256 = '';
  };
  const fetchResource = async (url, signal, type) => {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error('HAND_ASSET_UNAVAILABLE');
    return type === 'json' ? response.json() : response.arrayBuffer();
  };
  async function load() {
    const thisRevision = ++revision;
    controller?.abort(); controller = new AbortController();
    const { signal } = controller;
    clearAsset(); reviewMode = false; assetStatus = 'loading'; publish();
    let parsed;
    try {
      const [buffer, nextMetadata, nextLibrary] = await Promise.all([
        fetchResource(MODEL_URL, signal), fetchResource(METADATA_URL, signal, 'json'), fetchResource(POSES_URL, signal, 'json'),
      ]);
      if (disposed || signal.aborted || thisRevision !== revision) return;
      // The hash covers exactly the bytes the loader parses, including weights,
      // bind matrices, sleeve and embedded textures.
      const digest = await crypto.subtle.digest('SHA-256', buffer);
      const nextHash = [...new Uint8Array(digest)].map((value) => value.toString(16).padStart(2, '0')).join('');
      if (disposed || signal.aborted || thisRevision !== revision) return;
      parsed = await new GLTFLoader().parseAsync(buffer, new URL('.', MODEL_URL).href);
      if (disposed || signal.aborted || thisRevision !== revision) { disposeHandObject(parsed.scene); return; }
      const nextBones = new Map();
      parsed.scene.traverse((object) => {
        if (object.isBone) {
          // GLTFLoader sanitizes dots in Object3D.name. Keep original glTF joint
          // names to agree with the offline solver, without editing the rig.
          const originalName = object.userData.name || object.name;
          if (nextBones.has(originalName)) throw new Error('HAND_DUPLICATE_BONE');
          nextBones.set(originalName, object);
        }
        if (object.isSkinnedMesh) object.frustumCulled = false;
      });
      if (!nextBones.size) throw new Error('HAND_RIG_MISSING');
      asset = parsed.scene; bones = nextBones;
      bones.forEach((bone, name) => rest.set(name, { position: bone.position.clone(), quaternion: bone.quaternion.clone(), scale: bone.scale.clone() }));
      metadata = nextMetadata; library = nextLibrary; assetSha256 = nextHash;
      wrapper.add(asset); assetStatus = 'ready'; publish();
    } catch (error) {
      if (parsed?.scene && parsed.scene !== asset) disposeHandObject(parsed.scene);
      if (disposed || signal.aborted || thisRevision !== revision) return;
      controller.abort(); clearAsset(); assetStatus = 'error'; publish();
    }
  }
  load();
  return {
    setChord(nextChord) {
      if (disposed) return;
      if (nextChord.id !== currentChord.id) reviewMode = false;
      currentChord = nextChord; publish();
    },
    setHandReviewMode(value) { if (!disposed) { reviewMode = value === true; publish(); } },
    retryHand() { if (!disposed) load(); },
    dispose() {
      if (disposed) return;
      disposed = true; revision++; controller?.abort(); clearAsset(); reveal.dispose(); guitarSpace.removeFromParent(); guitarSpace.clear();
    },
  };
}
