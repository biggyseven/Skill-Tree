import assert from 'node:assert/strict';
import { test } from 'node:test';
import { DEVICE_GROUPS, EQUIPMENT_MODEL_COUNT } from './deviceCatalog.js';
import { CABLES, WIRELESS_LINK } from './cableCatalog.js';

const NODE_TYPES = new Set(['router','switch','pc','server','firewall','cloud']);
const ICON_TYPES = new Set(['router','switch','pc','server','firewall','cloud','hub','laptop','printer','phone','database','storage','load_balancer','wireless_controller','access_point','modem','vpn_gateway']);

test('catalogue équipements : quantité, catégories, modèles et icônes valides', () => {
  const models = DEVICE_GROUPS.flatMap(group => group.devices);
  assert.equal(EQUIPMENT_MODEL_COUNT, models.length);
  assert.ok(models.length >= 40);
  assert.equal(new Set(models.map(model => model.id)).size, models.length);
  for (const group of DEVICE_GROUPS) {
    assert.ok(group.title && group.caption && group.devices.length);
    for (const model of group.devices) {
      assert.ok(model.label && model.model && model.idPrefix, model.id);
      assert.ok(NODE_TYPES.has(model.type), model.id);
      assert.ok(Number.isInteger(model.portCount) && model.portCount >= 1 && model.portCount <= 48, model.id);
      assert.ok(ICON_TYPES.has(model.iconType || model.type), model.id);
    }
  }
  for (const id of ['router-isp-pe','switch-core-48','olt-gpon','ip-camera','iot-sensor','waf','router-4g5g']) assert.ok(models.some(model => model.id === id), id);
});

test('catalogue câbles : identifiants, descriptions et couleurs valides', () => {
  assert.ok(CABLES.length >= 18);
  const all = [...CABLES, WIRELESS_LINK];
  assert.equal(new Set(all.map(cable => cable.id)).size, all.length);
  for (const cable of all) {
    assert.ok(cable.name && cable.description && cable.detail, cable.id);
    assert.match(cable.color, /^#[0-9a-f]{6}$/i, cable.id);
    assert.equal(typeof cable.dash, 'string', cable.id);
  }
  for (const id of ['ethernet_cat6a','ethernet_cat8','cable_poe','fiber_gpon','fiber_armored','fiber_lc_patch','console_usb_c','serial_rs232','dac_qsfp']) assert.ok(CABLES.some(cable => cable.id === id), id);
});
