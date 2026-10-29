#!/usr/bin/env node
/** Conservative, evidence-gated import for the 2026-10-29 user archive.
 * Default is dry-run. Neither an editorial description nor a Google search is
 * technical evidence. Existing nonempty records always win over this intake.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { ADDITIONAL_SPECIFICATIONS } from '../src/data/additionalSpecifications.js';

export const BATCH = 'catalog-prices-2026-10-29';
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const AUDIT = path.join(ROOT, 'docs/catalog-update-2026-10-29');
const SPEC_TYPES = new Map([
  ...['body', 'neck', 'fretboard', 'pickups', 'bridge', 'controls'].map((k) => [k, 'text']),
  ...['scale', 'scaleMm', 'frets', 'strings', 'weightKg'].map((k) => [k, 'number']),
  ...ADDITIONAL_SPECIFICATIONS.map(({ key, type }) => [key, type]),
]);
const hasValue = (v) => v != null && (typeof v !== 'string' || v.trim() !== '');
const positivePrice = (v) => typeof v === 'number' && Number.isInteger(v) && v > 0;
const clone = (v) => structuredClone(v);
const digest = (v) => createHash('sha256').update(v).digest('hex');
const json = (v) => `${JSON.stringify(v, null, 2)}\n`;
const validDate = (v) => typeof v === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(v)
  && Number.isFinite(Date.parse(v)) && new Date(v).toISOString().slice(0, 10) === v;
function sourceURL(value, { product = false } = {}) {
  try {
    const u = new URL(value);
    return u.protocol === 'https:' && !u.username && !u.password
      && !/(^|\.)google\.[a-z.]+$/.test(u.hostname)
      && (!product || !/^\/category(?:\/|$)/i.test(u.pathname));
  } catch { return false; }
}
function uniqueByID(rows, label) {
  if (!Array.isArray(rows)) throw new Error(`${label} must be an array`);
  const map = new Map();
  for (const row of rows) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(row?.id ?? '')) throw new Error(`${label}: invalid ID`);
    if (map.has(row.id)) throw new Error(`${label}: duplicate ID ${row.id}`);
    map.set(row.id, row);
  }
  return map;
}
export function validateIntake(incoming, baseline) {
  const current = uniqueByID(baseline, 'baseline');
  const rows = uniqueByID(incoming, 'intake');
  if (rows.size !== 200 || current.size !== 200) throw new Error('Expected exactly 200 existing and incoming models');
  if ([...rows.keys()].some((id) => !current.has(id))) throw new Error('Incoming IDs must exactly match the existing 200 IDs');
  const brands = new Map();
  for (const row of rows.values()) {
    const old = current.get(row.id);
    if (row.brand !== old.brand || row.model !== old.name) throw new Error(`Identity mismatch: ${row.id}`);
    brands.set(row.brand, (brands.get(row.brand) ?? 0) + 1);
  }
  if (brands.size !== 10 || [...brands.values()].some((n) => n !== 20)) throw new Error('Expected 10 brands with 20 models each');
  return { models: rows.size, brands: Object.fromEntries(brands) };
}

/** RFC4180-style reader, including UTF-8 BOM, escaped quotes and CRLF. */
export function parseCSV(text) {
  const rows = []; let row = []; let cell = ''; let quoted = false;
  const input = String(text).replace(/^\uFEFF/, '');
  for (let i = 0; i < input.length; i += 1) {
    const c = input[i];
    if (c === '"') {
      if (quoted && input[i + 1] === '"') { cell += '"'; i += 1; }
      else quoted = !quoted;
    } else if (c === ',' && !quoted) { row.push(cell); cell = ''; }
    else if ((c === '\n' || c === '\r') && !quoted) {
      if (c === '\r' && input[i + 1] === '\n') i += 1;
      row.push(cell); if (row.some((v) => v !== '')) rows.push(row); row = []; cell = '';
    } else cell += c;
  }
  if (quoted) throw new Error('Unclosed CSV quote');
  if (cell || row.length) { row.push(cell); rows.push(row); }
  if (!rows.length) throw new Error('CSV has no header');
  const headers = rows.shift();
  if (new Set(headers).size !== headers.length) throw new Error('Duplicate CSV header');
  return rows.map((values) => {
    if (values.length !== headers.length) throw new Error('CSV column count mismatch');
    return Object.fromEntries(headers.map((key, i) => [key, values[i]]));
  });
}

/** Accept only independently reviewed fields, never the raw comparison_specs. */
export function normalizeSpecEvidence(documents) {
  const output = [];
  const visit = (document, inherited = {}) => {
    if (Array.isArray(document)) { document.forEach((item) => visit(item, inherited)); return; }
    if (!document || typeof document !== 'object') return;
    const defaults = { ...inherited, ...(document.id ? { id: document.id } : {}),
      ...(document.checkedOn ? { checkedOn: document.checkedOn } : {}),
      ...(document.documentPath ? { documentPath: document.documentPath } : {}) };
    if (Array.isArray(document.acceptedSpecs)) {
      document.acceptedSpecs.forEach((item) => visit({ accepted: true, ...item }, defaults)); return;
    }
    if (document.fields && document.id) {
      Object.entries(document.fields).forEach(([key, item]) => visit({ ...item, canonicalKey: key,
        evidence: item.evidence ?? document.accessibleSource }, defaults)); return;
    }
    const key = document.canonicalKey ?? document.key ?? document.fieldPath?.replace(/^specs\./, '') ?? document.field?.replace(/^specs\./, '');
    if (key) output.push({ ...defaults, ...document, canonicalKey: key });
  };
  visit(documents);
  return output;
}
function reviewedSource(evidence) {
  return sourceURL(evidence.sourceURL) && validDate(evidence.checkedOn ?? evidence.verifiedOn ?? evidence.date)
    && typeof evidence.quote === 'string' && evidence.quote.trim().length > 0
    && (evidence.httpStatus ?? evidence.evidence?.httpStatus ?? evidence.evidence?.status) === 200;
}
function validSpecValue(key, value) {
  const type = SPEC_TYPES.get(key);
  if (type === 'number') return typeof value === 'number' && Number.isFinite(value)
    && (key === 'frets' ? Number.isInteger(value) && value >= 0 : value > 0)
    && (!['strings'].includes(key) || Number.isInteger(value));
  return type === 'text' && typeof value === 'string' && value.trim().length > 0
    && !/^(?:unknown|not verified|n\/a|ไม่ระบุ|ไม่มีข้อมูล|สอบถามราคา|[—-])$/i.test(value.trim());
}
function appendSource(record, field, evidence, kind) {
  record.source.fields ??= [];
  if (!record.source.fields.includes(field)) record.source.fields.push(field);
  record.source.additionalSources ??= [];
  const verifiedOn = evidence.checkedOn ?? evidence.verifiedOn ?? evidence.date;
  const sourceKind = evidence.sourceKind ?? kind;
  let entry = record.source.additionalSources.find((s) => s.batch === BATCH
    && s.url === evidence.sourceURL && s.verifiedOn === verifiedOn && s.kind === sourceKind);
  if (!entry) {
    entry = { batch: BATCH, url: evidence.sourceURL, verifiedOn, method: 'http', kind: sourceKind, fields: [], quotes: [] };
    if (evidence.modelScope ?? evidence.scope) entry.scope = evidence.modelScope ?? evidence.scope;
    if (evidence.documentPath) entry.evidenceFile = evidence.documentPath;
    if (evidence.evidence) entry.evidence = clone(evidence.evidence);
    record.source.additionalSources.push(entry);
  }
  if (!entry.fields.includes(field)) entry.fields.push(field);
  if (!entry.quotes.includes(evidence.quote)) entry.quotes.push(evidence.quote);
}

/** Pure merge; inputs are never mutated. Only already-existing IDs are writable. */
export function mergeCatalogRecords({ incoming, baseline, reviewed, phase7, priceEvidence = [], specEvidence = [] }) {
  const candidates = uniqueByID(incoming, 'intake');
  const originals = uniqueByID(baseline, 'baseline');
  if (candidates.size !== originals.size || [...candidates.keys()].some((id) => !originals.has(id))) throw new Error('ID sets must match; adding/removing IDs is forbidden');
  const nextReviewed = clone(reviewed); const nextPhase7 = clone(phase7);
  const phaseMap = uniqueByID(nextPhase7, 'phase7');
  const target = (id) => Object.hasOwn(nextReviewed, id) ? nextReviewed[id] : phaseMap.get(id);
  const report = { batch: BATCH, baselineCommit: 'edc293f', changes: [], skipped: [], categoryConflicts: [], priceConflicts: [],
    policy: 'Only verified missing fields are filled; identities, existing nonempty values, primary manufacturer evidence, statuses, descriptions and images are preserved.' };
  for (const [id, row] of candidates) {
    if (!target(id)) throw new Error(`No existing writable datastore record for ${id}`);
    const before = originals.get(id);
    if (row.brand !== before.brand || row.model !== before.name) throw new Error(`Identity mismatch: ${id}`);
    const category = row.category === 'acoustic-electric' ? 'acoustic' : row.category;
    if (category !== before.category) report.categoryConflicts.push({ id, incoming: row.category, preserved: before.category });
    if (positivePrice(row.price_thb) && positivePrice(before.price) && row.price_thb !== before.price)
      report.priceConflicts.push({ id, incoming: row.price_thb, preserved: before.price, sourceURL: row.price_reference?.source_url,
        reason: 'Existing source-backed primary price is retained; a different retailer amount is not silently substituted.' });
  }
  const publicPrice = (id) => {
    const record = target(id);
    const sourced = positivePrice(record.price) && record.source?.fields?.includes('price')
      && record.priceSource?.currency === 'THB' && sourceURL(record.priceSource?.url)
      && validDate(record.priceSource?.verifiedOn);
    return sourced ? record.price : (positivePrice(originals.get(id).price) ? originals.get(id).price : null);
  };
  report.pricedModelsBefore = [...originals.keys()].filter((id) => publicPrice(id) != null).length;
  const priceRows = Array.isArray(priceEvidence) ? priceEvidence : priceEvidence.results ?? [];
  for (const evidence of priceRows) {
    const id = evidence.id; const row = candidates.get(id); const record = row && target(id);
    const amount = evidence.acceptedAmountTHB;
    const checkedOn = evidence.checkedOn ?? evidence.verifiedOn ?? evidence.date;
    const skip = (reason) => report.skipped.push({ id, field: 'price', reason });
    if (!row || !record) { skip('Evidence ID is not in the existing intake/catalog'); continue; }
    if (evidence.accepted !== true || evidence.currency !== 'THB' || !positivePrice(amount)
      || amount !== row.price_thb || amount !== row.price_reference?.amount_thb
      || row.price_reference?.currency !== 'THB' || !reviewedSource(evidence)
      || (evidence.model != null && evidence.model !== row.model)
      || !sourceURL(evidence.sourceURL, { product: true })
      || (evidence.productPriceObserved && (evidence.productPriceObserved.price !== amount || evidence.productPriceObserved.priceCurrency !== 'THB'))) {
      skip('Missing, invalid, non-THB, mismatched or unverified model-specific price evidence'); continue;
    }
    if (positivePrice(record.price) || publicPrice(id) != null) { skip('Existing primary price/source is preserved'); continue; }
    if (!record.source || !Array.isArray(record.source.fields)) { skip('No existing source-backed record to extend'); continue; }
    record.price = amount;
    const retailer = evidence.sourceLabel ?? new URL(evidence.sourceURL).hostname;
    record.priceSource = { currency: 'THB', url: evidence.sourceURL, verifiedOn: checkedOn,
      kind: 'retailer-listed', label: retailer, retailer,
      availability: 'unknown', note: 'ราคาขายที่ร้านแสดง อาจเปลี่ยนแปลงได้ ไม่ใช่ราคาขายปลีกแนะนำจากผู้ผลิต และไม่ยืนยันสต็อก',
      evidence: { httpStatus: evidence.httpStatus, quote: evidence.quote,
        ...(evidence.evidenceFile ? { file: `docs/catalog-update-2026-10-29/verification/${evidence.evidenceFile}` } : {}) } };
    record.source.priceNote = `${record.priceSource.label} — ราคาขายที่ร้านแสดง ตรวจ ${checkedOn}; ราคาอาจเปลี่ยนแปลงได้ ไม่ยืนยันสต็อก`;
    appendSource(record, 'price', evidence, 'retailer-listed');
    report.changes.push({ id, field: 'price', before: originals.get(id).price ?? null, after: amount, sourceURL: evidence.sourceURL, verifiedOn: checkedOn });
  }
  for (const evidence of normalizeSpecEvidence(specEvidence)) {
    const id = evidence.id; const key = evidence.canonicalKey; const record = candidates.has(id) && target(id);
    const skip = (reason) => report.skipped.push({ id, field: `specs.${key}`, reason });
    if (!record) { skip('Evidence ID is not in the existing intake/catalog'); continue; }
    if (evidence.accepted !== true || !SPEC_TYPES.has(key) || !validSpecValue(key, evidence.value) || !reviewedSource(evidence)) {
      skip('Missing, invalid, unsupported or unverified field evidence'); continue;
    }
    if (hasValue(record.specs?.[key]) || hasValue(originals.get(id).specs?.[key])) { skip('Existing nonempty specification is preserved'); continue; }
    if (!record.source || !Array.isArray(record.source.fields)) { skip('No existing source-backed record to extend'); continue; }
    record.specs ??= {}; record.specs[key] = clone(evidence.value);
    appendSource(record, `specs.${key}`, evidence, 'source-backed-specification');
    report.changes.push({ id, field: `specs.${key}`, before: null, after: evidence.value,
      sourceURL: evidence.sourceURL, verifiedOn: evidence.checkedOn ?? evidence.verifiedOn ?? evidence.date,
      sourceKind: evidence.sourceKind });
  }
  const changedIDs = [...originals.keys()].filter((id) => !isDeepStrictEqual(target(id), Object.hasOwn(reviewed, id) ? reviewed[id] : phase7.find((r) => r.id === id)));
  report.changedModelIDs = changedIDs;
  report.changedModels = changedIDs.length;
  report.newPrices = report.changes.filter((c) => c.field === 'price').length;
  report.newSpecificationFields = report.changes.filter((c) => c.field.startsWith('specs.')).length;
  report.pricedModelsAfter = [...originals.keys()].filter((id) => publicPrice(id) != null).length;
  report.preservedExistingPriceDespiteIncomingNull = [...originals].filter(([id, row]) => positivePrice(row.price) && !positivePrice(candidates.get(id).price_thb)).map(([id]) => id);
  return { reviewed: nextReviewed, phase7: nextPhase7, report };
}

export function verifyArchiveRepresentations(directory, incoming) {
  const byID = uniqueByID(incoming, 'intake');
  const brandFiles = fs.readdirSync(directory).filter((n) => n.endsWith('_20_models_with_prices.json'));
  const csvFiles = fs.readdirSync(directory).filter((n) => n.endsWith('_20_prices.csv'));
  if (brandFiles.length !== 10 || csvFiles.length !== 10) throw new Error('Expected ten per-brand JSON files and ten price CSV files');
  const jsonIDs = []; const csvIDs = [];
  for (const name of brandFiles) {
    const rows = JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8'));
    if (rows.length !== 20) throw new Error(`${name}: expected 20 models`);
    rows.forEach((row) => { if (!isDeepStrictEqual(row, byID.get(row.id))) throw new Error(`${name}: aggregate mismatch for ${row.id}`); jsonIDs.push(row.id); });
  }
  for (const name of csvFiles) {
    const rows = parseCSV(fs.readFileSync(path.join(directory, name), 'utf8'));
    if (rows.length !== 20) throw new Error(`${name}: expected 20 models`);
    rows.forEach((row) => {
      const original = byID.get(row.id); const amount = row.price_thb?.trim() ? Number(row.price_thb) : null;
      if (!original || row.brand !== original.brand || row.model !== original.model || row.category !== original.category
        || amount !== original.price_thb || (row.price_source_url || null) !== original.price_reference?.source_url
        || row.price_status !== original.price_reference?.type) throw new Error(`${name}: aggregate price/identity mismatch for ${row.id}`);
      csvIDs.push(row.id);
    });
  }
  for (const ids of [jsonIDs, csvIDs]) if (ids.length !== 200 || new Set(ids).size !== 200 || ids.some((id) => !byID.has(id))) throw new Error('Per-brand files do not cover exactly the 200 original IDs');
  return { perBrandJSONFiles: brandFiles.length, priceCSVFiles: csvFiles.length, aggregateMatches: true };
}

export function runCLI(argv = process.argv.slice(2)) {
  const apply = argv.includes('--apply');
  if (apply && argv.includes('--dry-run')) throw new Error('Choose --apply or --dry-run');
  const extra = argv.filter((v, i) => !['--apply', '--dry-run', '--report'].includes(v) && argv[i - 1] !== '--report');
  if (extra.length) throw new Error(`Unknown arguments: ${extra.join(' ')}`);
  const reportIndex = argv.indexOf('--report');
  if (reportIndex >= 0 && !argv[reportIndex + 1]) throw new Error('--report needs a path');
  const reportFile = reportIndex >= 0 ? path.resolve(ROOT, argv[reportIndex + 1]) : path.join(AUDIT, 'merge-report.json');
  const read = (name) => JSON.parse(fs.readFileSync(name, 'utf8'));
  const incoming = read(path.join(AUDIT, 'intake/ALL_200_WITH_PRICES.json'));
  const baseline = read(path.join(AUDIT, 'baseline-effective.json'));
  const reviewedFile = path.join(ROOT, 'src/data/catalog/reviewedGuitars.json');
  const phaseFile = path.join(ROOT, 'src/data/catalog/phase7Guitars.json');
  const reviewedText = fs.readFileSync(reviewedFile, 'utf8'); const phaseText = fs.readFileSync(phaseFile, 'utf8');
  const intakeCheck = validateIntake(incoming, baseline);
  const representations = verifyArchiveRepresentations(path.join(AUDIT, 'intake'), incoming);
  const evidence = (file) => ({ ...read(path.join(AUDIT, file)), documentPath: `docs/catalog-update-2026-10-29/${file}` });
  const result = mergeCatalogRecords({ incoming, baseline, reviewed: JSON.parse(reviewedText), phase7: JSON.parse(phaseText),
    priceEvidence: evidence('verification/fender-sources.json'),
    specEvidence: [evidence('verification/yamaha-sources.json'), evidence('verification/fender-specs.json')] });
  const files = [[reviewedFile, reviewedText, json(result.reviewed)], [phaseFile, phaseText, json(result.phase7)]];
  const changed = files.filter(([, before, after]) => before !== after);
  if (apply) {
    const branch = execFileSync('git', ['branch', '--show-current'], { cwd: ROOT, encoding: 'utf8' }).trim();
    if (branch !== 'feature/catalog-prices-2026-10-29') throw new Error('Apply is allowed only on the isolated catalog feature branch');
    for (const [file, before] of files) if (fs.readFileSync(file, 'utf8') !== before) throw new Error('Datastore changed during import; rerun dry-run');
    for (const [file, , after] of changed) {
      const temporary = `${file}.catalog-import-${process.pid}.tmp`;
      try { fs.writeFileSync(temporary, after); fs.renameSync(temporary, file); }
      finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
    }
  }
  const report = { ...result.report, mode: apply ? 'apply' : 'dry-run', intakeCheck, archiveRepresentations: representations,
    dataFiles: files.map(([file, before, after]) => ({ path: path.relative(ROOT, file), beforeSHA256: digest(before),
      plannedSHA256: digest(after), changed: before !== after, written: apply && before !== after })) };
  fs.mkdirSync(path.dirname(reportFile), { recursive: true }); fs.writeFileSync(reportFile, json(report));
  console.log(json({ mode: report.mode, changedModels: report.changedModels, newPrices: report.newPrices,
    newSpecificationFields: report.newSpecificationFields, pricedModelsBefore: report.pricedModelsBefore,
    pricedModelsAfter: report.pricedModelsAfter, dataFilesChanged: changed.length, report: path.relative(ROOT, reportFile) }));
  return report;
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try { runCLI(); } catch (error) { console.error(`Import aborted: ${error.message}`); process.exitCode = 1; }
}
