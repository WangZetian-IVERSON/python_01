// Programmatic zombie sprites as pixel-art style frames
// We draw at a small base resolution (pixel grid), then scale up with nearest-neighbor

function makeCanvas(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h; return c;
}

function clamp(v, a, b) { return Math.max(a, Math.min(b, v)); }

function drawPixelZombie(ctx, bw, bh, opts, phase, action) {
  // Helper to draw a pixel block
  const px = (x, y, w = 1, h = 1, color) => {
    if (color) ctx.fillStyle = color;
    ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h));
  };

  ctx.imageSmoothingEnabled = false;

  // Palette
  const bodyCol = opts.color || '#7b8da3'; // muted blue-gray
  const headCol = '#cbd5e1';
  const eyeCol = action === 'eat' ? '#f59e0b' : '#0b1324';
  const mouthCol = '#111827';
  const outline = '#0a0f1a';

  // Layout (base grid units)
  const bodyW = Math.floor(bw * 0.42);
  const bodyH = Math.floor(bh * 0.48);
  const cx = Math.floor(bw / 2), cy = Math.floor(bh / 2) + Math.floor(bh * 0.08);
  const headW = Math.floor(bodyW * 0.85), headH = Math.floor(bodyH * 0.35);

  const step = Math.round(Math.sin(phase) * Math.max(1, Math.floor(bh * 0.05)));
  const arm = Math.round(Math.sin(phase * (action === 'eat' ? 2 : 1)) * Math.max(1, Math.floor(bh * 0.04)));

  // Legs (two simple columns swinging)
  px(cx - Math.floor(bodyW * 0.18), cy + Math.floor(bodyH * 0.5), 2, Math.floor(bh * 0.22) + step, bodyCol);
  px(cx + Math.floor(bodyW * 0.18), cy + Math.floor(bodyH * 0.5), 2, Math.floor(bh * 0.22) - step, bodyCol);

  // Body block + outline
  const bx = cx - Math.floor(bodyW / 2), by = cy - Math.floor(bodyH / 2);
  px(bx, by, bodyW, bodyH, bodyCol);
  // outline
  ctx.strokeStyle = outline; ctx.lineWidth = 1;
  ctx.strokeRect(bx + 0.5, by + 0.5, bodyW, bodyH);

  // Head block
  const hx = cx - Math.floor(headW / 2), hy = by - headH - Math.floor(bh * 0.04);
  px(hx, hy, headW, headH, headCol);
  ctx.strokeStyle = outline; ctx.lineWidth = 1; ctx.strokeRect(hx + 0.5, hy + 0.5, headW, headH);

  // Eyes (two pixels)
  px(hx + Math.floor(headW * 0.2), hy + Math.floor(headH * 0.35), 2, 2, eyeCol);
  px(hx + Math.floor(headW * 0.65), hy + Math.floor(headH * 0.35), 2, 2, eyeCol);

  // Mouth (small line)
  px(cx - 3, hy + headH - 3, 6, 1, mouthCol);

  // Arms (simple sticks)
  px(bx - 4 - arm, cy - Math.floor(bodyH * 0.15), 4, 2, bodyCol);
  px(bx + bodyW + arm, cy - Math.floor(bodyH * 0.05), 4, 2, bodyCol);

  // Cone hat (pixel triangle-ish)
  if (opts.hat === 'cone') {
    const topX = cx, topY = hy - 4;
    px(topX - 1, topY, 2, 1, '#f97316');
    px(topX - 2, topY + 1, 4, 1, '#f97316');
    px(topX - 3, topY + 2, 6, 1, '#f97316');
    px(topX - 4, topY + 3, 8, 1, '#f97316');
    // base line
    px(topX - 5, topY + 4, 10, 1, '#ea580c');
  }
}

function genFrames(tileSize, opts, action, count, seedPhase = 0) {
  const frames = [];
  // Target displayed size
  const w = Math.floor(tileSize * 0.8);
  const h = Math.floor(tileSize * 0.9);
  // Base pixel-art resolution (smaller, then upscale)
  const scale = clamp(Math.floor(tileSize / 16), 2, 6);
  const bw = Math.max(24, Math.floor(w / scale));
  const bh = Math.max(28, Math.floor(h / scale));
  for (let i = 0; i < count; i++) {
    const c = makeCanvas(bw, bh); const ctx = c.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const phase = seedPhase + (Math.PI * 2) * (i / count);
    drawPixelZombie(ctx, bw, bh, opts, phase, action);
    frames.push(c);
  }
  return frames;
}

export function createZombieSprites(tileSize = 80) {
  const types = {
    normal: { color: '#94a3b8' },
    fast: { color: '#60a5fa' },
    tank: { color: '#64748b' },
    cone: { color: '#94a3b8', hat: 'cone' },
  };
  const sprites = {};
  for (const [key, conf] of Object.entries(types)) {
    sprites[key] = {
      walk: genFrames(tileSize, conf, 'walk', 6, 0),
      eat: genFrames(tileSize, conf, 'eat', 4, Math.PI/4),
      size: { w: Math.floor(tileSize * 0.8), h: Math.floor(tileSize * 0.9) }
    };
  }
  return sprites;
}

// Singleton cache to avoid regenerating
let _ZOMBIE_SPRITES = null;
export function getZombieSprites(tileSize = 80) {
  if (!_ZOMBIE_SPRITES) _ZOMBIE_SPRITES = createZombieSprites(tileSize);
  return _ZOMBIE_SPRITES;
}
