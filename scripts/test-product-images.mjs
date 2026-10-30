import { test } from 'node:test';
import assert from 'node:assert/strict';
import { imagePlan, validateImageFile } from '../src/features/admin/images.js';

test('1200 square keeps every source pixel and has no padding or upscale', () => {
  const p = imagePlan(1200, 1200);
  assert.deepEqual([p.width,p.height,p.drawWidth,p.drawHeight,p.x,p.y], [1200,1200,1200,1200,0,0]);
  assert.equal(p.padded, false); assert.equal(p.downscaled, false);
});
test('large square is reduced to the delivery standard', () => {
  const p = imagePlan(2400,2400);
  assert.deepEqual([p.width,p.height,p.drawWidth,p.drawHeight], [1200,1200,1200,1200]);
  assert.equal(p.downscaled,true);
});
test('portrait and landscape require the explicit padding choice', () => {
  assert.throws(() => imagePlan(1200,2400), /1:1/);
  assert.throws(() => imagePlan(2400,1200), /1:1/);
});
test('padding keeps the complete neck and body centered in either orientation', () => {
  const tall=imagePlan(1200,2400,'pad'), wide=imagePlan(2400,1200,'pad');
  assert.deepEqual([tall.width,tall.height,tall.drawWidth,tall.drawHeight,tall.x,tall.y], [1200,1200,600,1200,300,0]);
  assert.deepEqual([wide.width,wide.height,wide.drawWidth,wide.drawHeight,wide.x,wide.y], [1200,1200,1200,600,0,300]);
});
test('small originals are never enlarged to simulate resolution', () => {
  const square=imagePlan(600,600), tall=imagePlan(600,800,'pad');
  assert.deepEqual([square.width,square.height,square.drawWidth,square.drawHeight], [600,600,600,600]);
  assert.deepEqual([tall.width,tall.height,tall.drawWidth,tall.drawHeight,tall.x], [800,800,600,800,100]);
});
test('all four instrument silhouette proportions fit, without stretching or clipping', () => {
  for(const [w,h] of [[300,800],[231,548],[400,846],[313,1056],[1254,1254],[1024,1280],[1600,900]]) {
    const p=imagePlan(w,h,'pad');
    assert.equal(p.width,p.height); assert.ok(p.width<=1200);
    assert.ok(p.drawWidth<=w && p.drawHeight<=h);
    assert.ok(p.x>=0 && p.y>=0 && p.x+p.drawWidth<=p.width && p.y+p.drawHeight<=p.height);
    assert.ok(Math.abs(p.drawWidth/w-p.drawHeight/h)<=1/Math.min(w,h));
  }
});
test('invalid dimensions and unknown layout modes cannot reach a canvas', () => {
  for(const n of [0,-1,NaN,Infinity,12.5]) assert.throws(()=>imagePlan(n,1200));
  assert.throws(()=>imagePlan(1200,1200,'crop'));
});
test('JPG, PNG and WebP are accepted; unsupported or oversized files are rejected', () => {
  for(const type of ['image/jpeg','image/png','image/webp']) assert.doesNotThrow(()=>validateImageFile({type,size:1024}));
  for(const type of ['image/heic','image/svg+xml','application/octet-stream']) assert.throws(()=>validateImageFile({type,size:1024}),/รองรับ/);
  for(const size of [0,26*1024*1024]) assert.throws(()=>validateImageFile({type:'image/png',size}));
});
