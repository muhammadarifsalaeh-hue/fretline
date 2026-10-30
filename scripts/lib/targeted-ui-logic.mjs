import { parse } from '@babel/parser';
import { createHash } from 'node:crypto';

// Permit display copy to change while comparing routes, JSX structure, form
// values, event handlers, authentication, RPC payloads and control flow exactly.
const COPY_IMPORTS = new Set(['@/i18n', './displayLabels', '@/features/admin/displayLabels', '@/components/detail/imageDisplayCopy', '@/styles/home-targeted-refinement.css']);
const COPY_ATTRIBUTES = new Set(['label', 'title', 'description', 'eyebrow', 'placeholder', 'aria-label', 'alt', 'lang']);
const COPY_CALLS = new Set(['t', 'copy', 'quizCopy']);
const DISPLAY_FORMATTERS = new Set(['publicationLabel', 'auditActionLabel', 'modelMatchDisplay', 'countryLabel']);
const DISPLAY_MESSAGES = new Set(['confirm', 'setError', 'setMessage']);
const OMIT = new Set(['start', 'end', 'loc', 'extra', 'leadingComments', 'trailingComments', 'innerComments', 'comments']);

const copyNode = () => ({ type: 'DisplayCopy' });
const callName = (node) => node?.type === 'CallExpression' && node.callee.type === 'Identifier' ? node.callee.name : null;

function normalize(node, display = false) {
  if (node == null || typeof node !== 'object') return node;
  if (Array.isArray(node)) return node.map((item) => normalize(item, display)).filter((item) => item !== null);
  if (node.type === 'JSXText') return null;
  if (node.type === 'ImportDeclaration' && COPY_IMPORTS.has(node.source.value)) return null;
  if (node.type === 'JSXAttribute' && COPY_ATTRIBUTES.has(node.name.name)) return { type: 'JSXAttribute', name: normalize(node.name), value: copyNode() };
  if (node.type === 'JSXExpressionContainer') {
    if (COPY_CALLS.has(callName(node.expression))) return null;
    return { type: node.type, expression: normalize(node.expression, true) };
  }
  if (node.type === 'StringLiteral' && display) return copyNode();
  if (node.type === 'ConditionalExpression') return {
    type: node.type, test: normalize(node.test),
    consequent: normalize(node.consequent, display), alternate: normalize(node.alternate, display),
  };
  if (node.type === 'LogicalExpression') return { type: node.type, operator: node.operator, left: normalize(node.left, display), right: normalize(node.right, display) };
  if (node.type === 'TemplateLiteral') return { type: node.type, expressions: node.expressions.map((expression) => normalize(expression, display)), quasis: normalize(node.quasis) };
  if (node.type === 'AssignmentExpression' && node.left?.type === 'MemberExpression' && node.left.object?.name === 'document' && node.left.property?.name === 'title') return { type: node.type, operator: node.operator, left: normalize(node.left), right: copyNode() };
  if (node.type === 'ObjectProperty' && (node.key.name === 'label' || node.key.value === 'label')) return { ...normalizeProperties(node), value: copyNode() };
  if (node.type === 'VariableDeclarator' && node.id?.name === 'counts' && node.init?.type === 'ArrayExpression') {
    return { type: node.type, id: normalize(node.id), init: { type: 'ArrayExpression', elements: node.init.elements.map((item) => ({ type: 'ArrayExpression', elements: [copyNode(), ...item.elements.slice(1).map((part) => normalize(part))] })) } };
  }
  if (node.type === 'VariableDeclarator' && node.id?.name === 'labels') return { type: node.type, id: normalize(node.id), init: normalizeLabelTable(node.init) };
  if (node.type === 'CallExpression') {
    const name = callName(node);
    if (display && COPY_CALLS.has(name)) return copyNode();
    if (display && DISPLAY_FORMATTERS.has(name)) return normalize(node.arguments[0], true);
    if (DISPLAY_MESSAGES.has(name)) return { ...normalizeProperties(node), arguments: node.arguments.map((argument) => normalize(argument, true)) };
  }
  return normalizeProperties(node);
}

function normalizeProperties(node) {
  return Object.fromEntries(Object.entries(node).filter(([key]) => !OMIT.has(key)).map(([key, value]) => [key, normalize(value)]));
}
function normalizeLabelTable(node) {
  if (node == null || typeof node !== 'object') return node;
  if (node.type === 'StringLiteral') return copyNode();
  if (Array.isArray(node)) return node.map(normalizeLabelTable);
  return Object.fromEntries(Object.entries(node).filter(([key]) => !OMIT.has(key)).map(([key, value]) => [key, normalizeLabelTable(value)]));
}

export const displaySafeAST = (source) => normalize(parse(source, { sourceType: 'module', plugins: ['jsx'] }).program);
export const uiLogicDigest = (source) => createHash('sha256').update(JSON.stringify(displaySafeAST(source))).digest('hex');
