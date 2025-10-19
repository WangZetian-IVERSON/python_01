import { Game } from './game.js';
import { PlantRegistry, builtinPlants } from './registry.js';

const canvas = document.getElementById('game-canvas');
const ui = {
  palette: document.getElementById('plant-palette'),
  selectedPlant: document.getElementById('selected-plant'),
  score: document.getElementById('score'),
  gameState: document.getElementById('game-state'),
  customForm: document.getElementById('custom-plant-form'),
  sun: document.getElementById('sun'),
  restart: document.getElementById('restart-btn'),
  start: document.getElementById('start-btn'),
  nextLevel: document.getElementById('next-level-btn'),
  zombieUrl: document.getElementById('zombie-url'),
  zombieFile: document.getElementById('zombie-file'),
  gen: {
    form: document.getElementById('gen-form'),
    api: document.getElementById('gen-api'),
  backend: document.getElementById('gen-backend'),
    prompt: document.getElementById('gen-prompt'),
    width: document.getElementById('gen-width'),
    height: document.getElementById('gen-height'),
    steps: document.getElementById('gen-steps'),
    cfg: document.getElementById('gen-cfg'),
  model: document.getElementById('gen-model'),
  neg: document.getElementById('gen-neg'),
  seed: document.getElementById('gen-seed'),
    name: document.getElementById('gen-name'),
    cost: document.getElementById('gen-cost'),
    fireRate: document.getElementById('gen-fireRate'),
    damage: document.getElementById('gen-damage'),
    proj: document.getElementById('gen-proj'),
    cd: document.getElementById('gen-cd'),
    btnGen: document.getElementById('gen-generate'),
    btnAdd: document.getElementById('gen-add'),
    status: document.getElementById('gen-status'),
    preview: document.getElementById('gen-preview'),
  }
};

const registry = new PlantRegistry();
builtinPlants.forEach(p => registry.register(p));

let currentSelection = null;

function renderPalette() {
  ui.palette.innerHTML = '';
  registry.list().forEach(def => {
    const card = document.createElement('div');
    card.className = 'card';
    card.title = `${def.name} 费用:${def.cost} 伤害:${def.damage} 攻速:${def.fireRate}/s 冷却:${def.placeCooldown}s`;
    card.dataset.key = def.key;
    const img = document.createElement('img');
    if (def.imageUrl) {
      img.src = def.imageUrl;
    } else {
      // generate a simple placeholder
      const c = document.createElement('canvas');
      c.width = c.height = 32;
      const ctx = c.getContext('2d');
      ctx.fillStyle = def.color || '#48c774';
      ctx.beginPath();
      ctx.arc(16, 16, 14, 0, Math.PI * 2);
      ctx.fill();
      img.src = c.toDataURL();
    }
    const meta = document.createElement('div');
    meta.className = 'meta';
    const title = document.createElement('div');
    title.className = 'title';
    title.textContent = def.name;
    const sub = document.createElement('div');
    sub.className = 'sub';
    sub.textContent = `费:${def.cost} 冷:${def.placeCooldown}s`;
    meta.append(title, sub);
    card.append(img, meta);
    const cdOverlay = document.createElement('div');
    cdOverlay.className = 'cooldown';
    cdOverlay.style.display = 'none';
    card.append(cdOverlay);
    card.addEventListener('click', () => {
      currentSelection = def.key;
      [...ui.palette.children].forEach(el => el.classList.remove('selected'));
      card.classList.add('selected');
      ui.selectedPlant.textContent = def.name;
      game.setSelectedPlant(def.key);
    });
    ui.palette.appendChild(card);
  });
}

// Handle custom form
ui.customForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = new FormData(ui.customForm);
  let imageUrl = data.get('imageUrl')?.toString() || '';
  const file = data.get('imageFile');
  if (file && file instanceof File && file.size > 0) {
    imageUrl = await readFileAsDataUrl(file);
  }
  const def = {
    key: `custom_${Date.now()}`,
    name: data.get('name')?.toString().slice(0, 20) || '自定义植物',
    maxHealth: parseInt(data.get('maxHealth') || '100', 10),
    cost: parseInt(data.get('cost') || '0', 10),
    fireRate: parseFloat(data.get('fireRate') || '1'),
    damage: parseInt(data.get('damage') || '20', 10),
    projectileSpeed: parseFloat(data.get('projectileSpeed') || '200'),
    color: data.get('color')?.toString() || '#48c774',
    imageUrl,
  };
  registry.register(def);
  renderPalette();
  ui.customForm.reset();
});

const game = new Game(canvas, registry, {
  rows: 5,
  cols: 9,
  tileSize: 80,
});

renderPalette();
// Don't autostart; wait for user to click Start
ui.start.addEventListener('click', () => {
  // prefer local file over URL
  const f = ui.zombieFile?.files?.[0];
  if (f) {
    readFileAsDataUrl(f).then(url => game.setZombieSkin(url));
  } else {
    game.setZombieSkin(ui.zombieUrl.value.trim());
  }
  ui.gameState.textContent = '进行中';
  game.start();
});

// Update palette states periodically (cooldowns, affordability)
function refreshPaletteStates() {
  const sun = game.getSun();
  for (const card of ui.palette.children) {
    const key = card.dataset.key;
    const def = registry.get(key);
    const cd = game.getCooldown(key);
    const can = game.canPlace(key);
    card.classList.toggle('disabled', !can);
    const overlay = card.querySelector('.cooldown');
    if (cd > 0 && overlay) {
      overlay.style.display = '';
      overlay.textContent = cd.toFixed(1) + 's';
    } else if (overlay) {
      overlay.style.display = 'none';
    }
  }
  ui.sun.textContent = String(sun);
}
setInterval(refreshPaletteStates, 100);

// Restart button
ui.restart.addEventListener('click', () => {
  // naive reset: reload page for now
  window.location.reload();
});

// Next level
ui.nextLevel?.addEventListener('click', () => {
  ui.nextLevel.disabled = true;
  const nEl = document.getElementById('level-num');
  const current = nEl ? parseInt(nEl.textContent || '1', 10) : 1;
  game.startLevel(current + 1);
});

// ============ Text-to-Image (AUTOMATIC1111) ============
let lastGenDataUrl = '';

async function generateImage() {
  const api = ui.gen.api.value.trim().replace(/\/$/, '');
  const prompt = ui.gen.prompt.value.trim() || 'A simple cute plant icon, flat, transparent background';
  const width = parseInt(ui.gen.width.value || '256', 10);
  const height = parseInt(ui.gen.height.value || '256', 10);
  const steps = parseInt(ui.gen.steps.value || '20', 10);
  const cfgScale = parseFloat(ui.gen.cfg.value || '7');
  const model = ui.gen.model.value.trim();
  const negative_prompt = ui.gen.neg.value.trim();
  const seed = ui.gen.seed.value ? parseInt(ui.gen.seed.value, 10) : undefined;
  ui.gen.status.textContent = '生成中...';
  ui.gen.form.classList.add('loading');
  ui.gen.btnAdd.disabled = true;
  ui.gen.preview.src = '';
  lastGenDataUrl = '';
  try {
    let dataUrl = '';
    if (ui.gen.backend.value === 'a1111') {
      const resp = await fetch(`${api}/sdapi/v1/txt2img`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, negative_prompt, steps, cfg_scale: cfgScale, width, height, sampler_name: 'DPM++ 2M Karras', seed })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      const b64 = data?.images?.[0];
      if (!b64) throw new Error('未获取到图片');
      dataUrl = `data:image/png;base64,${b64}`;
    } else {
      // local diffusers backend
      const resp = await fetch(`${api}/api/txt2img`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, steps, cfg: cfgScale, width, height, sampler_name: 'DPM++ 2M Karras', model: model || undefined, negative_prompt, seed })
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      const b64 = data?.image;
      if (!b64) throw new Error('未获取到图片');
      dataUrl = `data:image/png;base64,${b64}`;
    }
    ui.gen.preview.src = dataUrl;
    lastGenDataUrl = dataUrl;
    ui.gen.status.textContent = '生成完成，可加入植物库';
    ui.gen.btnAdd.disabled = false;
  } catch (err) {
    console.error(err);
    ui.gen.status.textContent = `生成失败：${err?.message || err}`;
  } finally {
    ui.gen.form.classList.remove('loading');
  }
}

ui.gen.btnGen.addEventListener('click', generateImage);

ui.gen.btnAdd.addEventListener('click', () => {
  if (!lastGenDataUrl) return;
  const def = {
    key: `t2i_${Date.now()}`,
    name: (ui.gen.name.value.trim() || '生成植物').slice(0, 20),
    maxHealth: 100,
    cost: parseInt(ui.gen.cost.value || '25', 10),
    fireRate: parseFloat(ui.gen.fireRate.value || '1'),
    damage: parseInt(ui.gen.damage.value || '20', 10),
    projectileSpeed: parseFloat(ui.gen.proj.value || '220'),
    placeCooldown: parseFloat(ui.gen.cd.value || '3'),
    color: '#48c774',
    imageUrl: lastGenDataUrl,
  };
  registry.register(def);
  renderPalette();
  ui.gen.status.textContent = '已加入植物库';
  ui.gen.btnAdd.disabled = true;
});

function readFileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// Backend switch: help user set sensible defaults
function updateApiPlaceholder() {
  if (ui.gen.backend.value === 'local') {
    // If we are served from the FastAPI server, prefer same-origin
    const origin = window.location.origin;
    ui.gen.api.value = origin;
  } else {
    ui.gen.api.value = 'http://127.0.0.1:7860';
  }
}
ui.gen.backend.addEventListener('change', updateApiPlaceholder);
// On load: if port matches 7861, default to local backend
window.addEventListener('DOMContentLoaded', () => {
  if (window.location.port === '7861') {
    ui.gen.backend.value = 'local';
    updateApiPlaceholder();
  }
});
