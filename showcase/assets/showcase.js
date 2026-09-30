const LAYERS = {
  housing: 'Chassis Housing', mounting: 'Mounting System', power: 'Power Whip Cord',
  breakers: 'Circuit Breakers', outlet_banks: '24-Outlet Banks', nmc3: 'NMC3 Controller',
  internal: 'Internal Busbars & PCB'
};

const STAGES = [
  { id: 1, title: 'Housing & chassis extrusion', short: 'Housing', summary: 'Inspect the 1,829 mm structural shell and end caps before adding retained modules.', mode: 'assembled', orbit: '-15deg 82deg 6.2m', target: '0m 0.915m 0m', layers: ['housing'] },
  { id: 2, title: 'Rear dual-pad toolless mounting', short: 'Mounting', summary: 'Follow the rear pad and peg system that anchors the PDU to the rack frame.', mode: 'assembled', orbit: '180deg 90deg 0.55m', target: '0m 1.750m -0.025m', layers: ['housing', 'mounting'] },
  { id: 3, title: 'Power whip & IEC 60309 plug', short: 'Power', summary: 'Trace the top entry, gland, whip cord and 230 V 32 A IEC 60309 plug.', mode: 'assembled', orbit: '-15deg 82deg 0.65m', target: '0m 2.1m 0m', layers: ['housing', 'mounting', 'power'] },
  { id: 4, title: 'Internal relays, busbars & PCB', short: 'Internals', summary: 'Open the electrical stack and expose relay boards, copper rails, NMC tray and PCB.', mode: 'exploded', orbit: '-10deg 85deg 0.5m', target: '0m 0.915m 0m', layers: ['housing', 'mounting', 'power', 'internal'] },
  { id: 5, title: 'Front controls, rockers & sockets', short: 'Controls', summary: 'Inspect the front fascia, breaker rockers, outlet banks and NMC3 controls.', mode: 'assembled', orbit: '0deg 88deg 0.45m', target: '0m 0.915m 0.024m', layers: ['housing', 'mounting', 'power', 'breakers', 'outlet_banks', 'nmc3', 'internal'] },
  { id: 6, title: 'Fully assembled unit', short: 'Complete', summary: 'Review the complete APDU9953 at its full 24-outlet, managed configuration.', mode: 'assembled', orbit: '-15deg 82deg 6.2m', target: '0m 0.915m 0m', layers: Object.keys(LAYERS) },
  { id: 7, title: '3D exploded view', short: 'Exploded', summary: 'See retained modules and service layers separated along their assembly axes.', mode: 'exploded', orbit: '-5deg 78deg 6.2m', target: '0m 0.915m 0m', layers: Object.keys(LAYERS) }
];

const COMPONENTS = {
  housing: { title: 'Housing & chassis extrusion', role: 'The structural 1,829 mm enclosure and front/rear retention surfaces.', spec: [['Envelope', '1829 × 56 × 46 mm'], ['Material cue', 'Powder-coated chassis'], ['Inspection', 'Extrusion, caps, inserts and fascia openings']], stage: 1, orbit: '-15deg 82deg 3.5m', target: '0m 0.915m 0m' },
  mounting: { title: 'Rear dual-pad toolless mounting', role: 'A rear service interface for rack engagement and tool-less positioning.', spec: [['Pad pattern', 'Dual rear pad system'], ['Vertical span', '1680 mm pitch'], ['Inspection', 'Pads, pegs, grounding stud and retainers']], stage: 2, orbit: '180deg 90deg 0.55m', target: '0m 1.75m -0.025m' },
  power: { title: 'Power whip & IEC 60309 plug', role: 'Top-entry power path from gland and whip cord to the 230 V 32 A plug.', spec: [['Input', '230 V · 32 A · 1-phase'], ['Connector', 'IEC 60309 2P+E blue'], ['Inspection', 'Terminal block, gland, cord and plug']], stage: 3, orbit: '-15deg 82deg 0.65m', target: '0m 2.1m 0m' },
  breakers: { title: 'Hydraulic-magnetic circuit breakers', role: 'Two 20 A protection modules with front rockers, guard and rear lugs.', spec: [['Count', '2 × 20 A'], ['Type', 'Hydraulic-magnetic'], ['Inspection', 'Fascia, guard, rocker, body and lugs']], stage: 5, orbit: '5deg 85deg 0.35m', target: '-0.007m 1.33m 0.024m' },
  outlet_banks: { title: '24-outlet switched banks', role: 'Three modular banks carrying 21 C13/C15 and 3 C19/C21 outlets.', spec: [['Count', '24 outlets'], ['Mix', '21 × C13/C15 · 3 × C19/C21'], ['Inspection', 'Facias, contacts, relays, busbars and numbering']], stage: 5, orbit: '-5deg 85deg 0.45m', target: '0m 1.16m 0.024m' },
  nmc3: { title: 'NMC3 network management controller', role: 'The managed controller cassette with display, service ports and internal PCB.', spec: [['Controller', 'NMC3'], ['Ports', 'RJ45, USB-A, Micro-B'], ['Inspection', 'Ports, display, buttons, tray and PCB']], stage: 5, orbit: '0deg 90deg 0.38m', target: '0m 0.915m 0.024m' },
  internal: { title: 'Internal busbars & PCB', role: 'The electrical distribution stack: copper rails, relay boards and controller electronics.', spec: [['Distribution', 'Continuous N / PE busbars'], ['Boards', 'Relay PCBs + NMC3 PCB'], ['Inspection', 'Contacts, busbars, relays, tray and electronics']], stage: 4, orbit: '-10deg 85deg 0.5m', target: '0m 0.915m 0m' }
};

const viewerState = new WeakMap();
function stateFor(viewer) { if (!viewerState.has(viewer)) viewerState.set(viewer, { pending: null, source: null, original: new Map() }); return viewerState.get(viewer); }
// The model-viewer library (about 900 KB) and the models are fetched when the visitor first asks for 3D, not on page load.
// Hovering or focusing a load button warms the library up so the click feels instant.
const MODEL_VIEWER_URL = new URL('./vendor/model-viewer-3.5.0.min.js', import.meta.url).href;
const DRACO_URL = new URL('./vendor/draco-1.5.6/', import.meta.url).href; // model-viewer would otherwise fetch it from gstatic
let libraryPromise;
function loadLibrary() {
  return libraryPromise ??= import(MODEL_VIEWER_URL)
    .then(() => customElements.whenDefined('model-viewer'))
    .then(() => { customElements.get('model-viewer').dracoDecoderLocation = DRACO_URL; }) // before the first model loads
    .catch(error => { libraryPromise = null; throw error; });
}

// reveal="manual" holds a model back until dismissPoster(). model-viewer forgets that request when it processes a new `src`
// (asynchronously), so after every src swap call this with force = true. It waits for `updateComplete` for that reason.
async function dismiss(viewer, force = false) {
  const state = stateFor(viewer);
  if (state.revealed && !force) return;
  state.revealed = true;
  const buttons = viewer.querySelectorAll('[data-load-3d]');
  buttons.forEach(button => { button.disabled = true; button.textContent = 'Loading 3D model…'; });
  try {
    await loadLibrary();
    await viewer.updateComplete;
    viewer.dismissPoster();
  } catch {
    state.revealed = false;
    buttons.forEach(button => { button.disabled = false; button.textContent = 'Could not load the 3D viewer. Try again'; });
  }
}

// Mirrors the visual .active state of toggle buttons for assistive technology.
function markPressed(root) { root.querySelectorAll('[data-stage], [data-mode]').forEach(button => button.setAttribute('aria-pressed', String(button.classList.contains('active')))); }
function stageFor(id) { return STAGES.find(stage => stage.id === Number(id)) || STAGES[0]; }
function setCamera(viewer, stage) { viewer.minCameraOrbit = 'auto auto 0.04m'; viewer.cameraOrbit = stage.orbit; viewer.cameraTarget = stage.target; viewer.autoRotate = false; }

function applyVisibility(viewer, visibleLayers) {
  if (!viewer.model?.materials) return;
  const visible = new Set(visibleLayers);
  const state = stateFor(viewer);
  viewer.model.materials.forEach(material => {
    const name = (material.name || '').toLowerCase();
    const layer = Object.keys(LAYERS).find(key => name.startsWith(`${key}__`));
    if (!layer) return;
    if (!state.original.has(material)) {
      const factor = material.pbrMetallicRoughness.baseColorFactor || [1, 1, 1, 1];
      state.original.set(material, { color: [...factor], mode: material.getAlphaMode?.() || 'OPAQUE' });
    }
    const original = state.original.get(material);
    const factor = [...original.color];
    factor[3] = visible.has(layer) ? original.color[3] : 0;
    material.pbrMetallicRoughness.setBaseColorFactor(factor);
    material.setAlphaMode(visible.has(layer) ? original.mode : 'BLEND');
  });
}

function updateStageUI(root, stage) {
  root.querySelectorAll('[data-stage]').forEach(button => button.classList.toggle('active', Number(button.dataset.stage) === stage.id));
  markPressed(root);
  root.querySelectorAll('[data-stage-number]').forEach(node => { node.textContent = `Stage ${String(stage.id).padStart(2, '0')}`; });
  root.querySelectorAll('[data-stage-title]').forEach(node => { node.textContent = stage.title; });
  root.querySelectorAll('[data-stage-summary]').forEach(node => { node.textContent = stage.summary; });
}

function updateLayerUI(root, layers) {
  const visible = new Set(layers);
  root.querySelectorAll('[data-layer]').forEach(input => { input.checked = visible.has(input.dataset.layer); });
}

function setModelMode(viewer, mode) {
  const prefix = document.body.dataset.component ? '../' : '';
  const source = `${prefix}${mode === 'exploded' ? 'gspe_pdu_apdu9953_exploded.glb' : 'gspe_pdu_apdu9953.glb'}`;
  const state = stateFor(viewer);
  const changed = viewer.getAttribute('src') !== source;
  if (changed) { state.pending = { ...(state.pending || {}), mode }; viewer.setAttribute('src', source); }
  dismiss(viewer, changed); // after the swap, so only the model we want is fetched
  const root = rootFor(viewer);
  root.querySelectorAll('[data-mode]').forEach(button => button.classList.toggle('active', button.dataset.mode === mode));
  markPressed(root);
}

function rootFor(viewer) { return viewer.closest('[data-showcase-root]') || document; }
function setStage(viewer, stageId) {
  const root = rootFor(viewer); const stage = stageFor(stageId); const state = stateFor(viewer);
  root.classList.remove('customized');
  state.pending = stage;
  updateStageUI(root, stage);
  setModelMode(viewer, stage.mode);
  if (viewer.getAttribute('src') === (stage.mode === 'exploded' ? 'gspe_pdu_apdu9953_exploded.glb' : 'gspe_pdu_apdu9953.glb') && viewer.model) {
    setCamera(viewer, stage); applyVisibility(viewer, stage.layers); updateLayerUI(root, stage.layers);
  }
}

// The card is absolutely positioned inside its hotspot, so it follows the marker with no coordinate maths.
// model-viewer moves hotspots with a transform, which is why the old `position: fixed` card landed far off screen.
// This only keeps the card inside the viewer: flip below the marker near the top edge, slide sideways near the sides.
function placeCard(viewer, hotspot) {
  const card = hotspot.querySelector('.hotspot-card'); if (!card) return;
  const view = viewer.getBoundingClientRect(); const pad = 8;
  card.style.maxWidth = `${view.width - 2 * pad}px`;
  card.style.setProperty('--shift', '0px'); card.classList.remove('below');
  let box = card.getBoundingClientRect();
  if (box.top < view.top + pad) { card.classList.add('below'); box = card.getBoundingClientRect(); }
  const shift = box.left < view.left + pad ? view.left + pad - box.left : box.right > view.right - pad ? view.right - pad - box.right : 0;
  card.style.setProperty('--shift', `${shift}px`);
}

function focusHotspot(viewer, hotspot) {
  const root = rootFor(viewer); const wasActive = hotspot.classList.contains('active');
  root.querySelectorAll('.hotspot').forEach(item => item.classList.remove('active'));
  if (wasActive) return; // second click closes the tip
  hotspot.classList.add('active'); viewer.cameraOrbit = hotspot.dataset.orbit || viewer.cameraOrbit; viewer.cameraTarget = hotspot.dataset.target || viewer.cameraTarget;
  placeCard(viewer, hotspot);
}

function initViewer(viewer) {
  const root = rootFor(viewer); const state = stateFor(viewer);
  viewer.querySelectorAll('[data-load-3d]').forEach(button => {
    button.addEventListener('click', () => dismiss(viewer));
    ['pointerenter', 'focus', 'touchstart'].forEach(type => button.addEventListener(type, () => loadLibrary().catch(() => {}), { once: true, passive: true }));
  });
  viewer.addEventListener('click', () => dismiss(viewer), { once: true });
  markPressed(root);
  viewer.addEventListener('load', () => {
    const pending = state.pending || stageFor(viewer.dataset.initialStage || 6);
    // Layers toggled before the model existed win over the stage defaults.
    const custom = root.classList.contains('customized') ? [...root.querySelectorAll('[data-layer]:checked')].map(item => item.dataset.layer) : null;
    setCamera(viewer, pending); applyVisibility(viewer, custom || pending.layers); updateStageUI(root, pending); if (!custom) updateLayerUI(root, pending.layers); state.pending = pending;
  });
  root.querySelectorAll('[data-stage]').forEach(button => button.addEventListener('click', () => setStage(viewer, button.dataset.stage)));
  root.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => setModelMode(viewer, button.dataset.mode)));
  root.querySelectorAll('[data-layer]').forEach(input => input.addEventListener('change', () => { const layers = [...root.querySelectorAll('[data-layer]:checked')].map(item => item.dataset.layer); root.classList.add('customized'); dismiss(viewer); applyVisibility(viewer, layers); }));
  root.querySelectorAll('.hotspot').forEach(hotspot => hotspot.addEventListener('click', event => { event.stopPropagation(); focusHotspot(viewer, hotspot); }));
  viewer.addEventListener('camera-change', () => root.querySelectorAll('.hotspot.active').forEach(hotspot => placeCard(viewer, hotspot)));
  root.querySelectorAll('[data-camera-reset]').forEach(button => button.addEventListener('click', () => { const stage = state.pending || stageFor(6); setCamera(viewer, stage); }));
}

document.querySelectorAll('model-viewer[data-showcase-viewer]').forEach(initViewer);
document.addEventListener('keydown', event => { if (event.key === 'Escape') document.querySelectorAll('.hotspot.active').forEach(hotspot => hotspot.classList.remove('active')); });
// ARIA tabs: click or arrow keys select, and only the selected tab is in the tab order.
document.querySelectorAll('[role="tablist"]').forEach(list => {
  const tabs = [...list.querySelectorAll('[role="tab"]')];
  const select = (tab, focus) => {
    tabs.forEach(item => {
      const on = item === tab;
      item.classList.toggle('active', on); item.setAttribute('aria-selected', String(on)); item.tabIndex = on ? 0 : -1;
      document.getElementById(item.getAttribute('aria-controls')).hidden = !on;
    });
    if (focus) tab.focus();
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', event => {
      const target = { ArrowRight: tabs[(index + 1) % tabs.length], ArrowLeft: tabs[(index + tabs.length - 1) % tabs.length], Home: tabs[0], End: tabs[tabs.length - 1] }[event.key];
      if (target) { event.preventDefault(); select(target, true); }
    });
  });
});

const componentKey = document.body.dataset.component;
if (componentKey && COMPONENTS[componentKey]) {
  const component = COMPONENTS[componentKey];
  document.querySelectorAll('[data-component-title]').forEach(node => node.textContent = component.title);
  document.querySelectorAll('[data-component-role]').forEach(node => node.textContent = component.role);
  document.querySelectorAll('[data-component-spec]').forEach(node => node.innerHTML = component.spec.map(([label, value]) => `<dt>${label}</dt><dd>${value}</dd>`).join(''));
  document.querySelectorAll('[data-component-viewer]').forEach(viewer => {
    // Attributes, not properties: the model-viewer library may not be loaded yet, so plain properties would not stick.
    viewer.setAttribute('src', `../${component.stage === 4 || component.stage === 7 ? 'gspe_pdu_apdu9953_exploded.glb' : 'gspe_pdu_apdu9953.glb'}`);
    viewer.dataset.initialStage = component.stage;
    viewer.setAttribute('camera-orbit', component.orbit);
    viewer.setAttribute('camera-target', component.target);
    viewer.addEventListener('load', () => { stateFor(viewer).pending = { ...stageFor(component.stage), ...component, layers: [componentKey] }; setCamera(viewer, component); applyVisibility(viewer, [componentKey]); });
    const root = rootFor(viewer);
    root.querySelectorAll('[data-mode]').forEach(button => button.classList.toggle('active', button.dataset.mode === (component.stage === 4 || component.stage === 7 ? 'exploded' : 'assembled')));
    markPressed(root);
  });
  const previous = document.querySelector('[data-component-previous]');
  const next = document.querySelector('[data-component-next]');
  const keys = Object.keys(COMPONENTS); const index = keys.indexOf(componentKey);
  if (previous) { const key = keys[(index + keys.length - 1) % keys.length]; previous.href = `${key === 'outlet_banks' ? 'outlet-banks' : key === 'internal' ? 'internal-busbars-pcb' : key}.html`; }
  if (next) { const key = keys[(index + 1) % keys.length]; next.href = `${key === 'outlet_banks' ? 'outlet-banks' : key === 'internal' ? 'internal-busbars-pcb' : key}.html`; }
}
