import test from 'node:test';
import assert from 'node:assert/strict';
import * as pc from '../web/node_modules/playcanvas/build/playcanvas.mjs';
import {SceneBridge} from '../web/src/scene.mjs';

test('loaded GLB animation subassets bind their track names and survive idle, walking and talking updates', async () => {
  const app = {systems: new pc.EventHandler(), assets: new pc.EventHandler(), _entityIndex: {}};
  app.assets.get = () => null;
  app.systems.anim = new pc.AnimComponentSystem(app);
  app.root = new pc.Entity('Scene', app);
  const model = new pc.Entity('Bip01', app);
  model.setLocalScale(.01, .01, .01);
  const clips = ['Idle', 'Walking', 'Talking'].map((name, index) => ({
    // This is the real PlayCanvas GLB subasset naming convention. The authored
    // state name lives on the AnimTrack, not the generated asset name.
    name: `rocketbox.low.glb/animation/${index}`,
    resource: new pc.AnimTrack(name, 1, [], [], [])
  }));
  app.assets.loadFromUrl = (_url, type, callback) => {
    assert.equal(type, 'container');
    callback(null, {resource: {instantiateRenderEntity: () => model, animations: clips}});
  };
  const scene = {app, trace: [], assetLoads: []};
  const wrapper = await SceneBridge.prototype.loadModel.call(scene, './fixture.glb', 'world://npc/0', [8, 0, 13], 1, 180);
  const anim = wrapper.animation;
  assert.equal(anim, model.anim);
  assert.deepEqual(anim.baseLayer.states, ['START', 'Idle', 'Walking', 'Talking']);
  assert.deepEqual(scene.trace.find(event => event.event === 'animation.bound').bindings,
    {Idle: 'Idle', Walking: 'Walking', Talking: 'Talking'});
  assert.equal(anim.playing, true);
  assert.equal(wrapper.motion, 'Idle');
  assert.ok(Math.abs(model.getLocalScale().x - .01) < 1e-7);
  assert.doesNotThrow(() => {
    for (let frame = 0; frame < 20; frame++) anim.update(1 / 60);
    assert.equal(anim.baseLayer.activeState, 'Idle');
    for (const state of ['Walking', 'Talking', 'Idle']) {
      anim.baseLayer.transition(state, .2);
      for (let frame = 0; frame < 20; frame++) anim.update(1 / 60);
      assert.equal(anim.baseLayer.activeState, state);
    }
  });
});
