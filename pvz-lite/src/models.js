export class Grid {
  constructor(rows, cols, tileSize) {
    this.rows = rows; this.cols = cols; this.tileSize = tileSize;
    this.tiles = Array.from({ length: rows }, () => Array.from({ length: cols }, () => ({ plant: null })));
  }
  cellAt(x, y) {
    const c = Math.floor(x / this.tileSize);
    const r = Math.floor(y / this.tileSize);
    if (r < 0 || r >= this.rows || c < 0 || c >= this.cols) return null;
    return { r, c };
  }
  centerOf(r, c) {
    return { x: c * this.tileSize + this.tileSize / 2, y: r * this.tileSize + this.tileSize / 2 };
  }
}

export class Entity {
  constructor(x, y) {
    this.x = x; this.y = y; this.dead = false;
  }
}

export class Plant extends Entity {
  constructor(grid, r, c, def) {
    const { x, y } = grid.centerOf(r, c);
    super(x, y);
    this.r = r; this.c = c; this.grid = grid;
    this.def = def;
    this.health = def.maxHealth ?? 100;
    this.cooldown = 0; // time until next shot
    this.sunTimer = def.sunInterval || 0; // for sunflower
  }
  update(dt, game) {
    if (this.dead) return;
    if (this.cooldown > 0) this.cooldown -= dt;
    // shoot if there is any zombie in the same row and cooldown ready
    const hasTarget = game.zombies.some(z => !z.dead && z.r === this.r && z.x > this.x);
    if (hasTarget && this.cooldown <= 0) {
      const speed = this.def.projectileSpeed ?? 200;
      const dmg = this.def.damage ?? 20;
      game.spawnProjectile(this.x + 20, this.y, speed, dmg, this.r, this.def.color || '#48c774');
      const rate = Math.max(0.05, this.def.fireRate ?? 1);
      this.cooldown = 1 / rate;
    }
    // sun production
    if (this.def.sunRate && this.def.sunInterval) {
      this.sunTimer -= dt;
      if (this.sunTimer <= 0) {
        this.sunTimer = this.def.sunInterval;
        const { x, y } = this; // spawn a sun token around plant
        game.spawnSunToken(x + (Math.random()*20-10), y - 10, this.def.sunRate);
      }
    }
  }
  hit(dmg) {
    this.health -= dmg;
    if (this.health <= 0) this.dead = true;
  }
  render(ctx, tileSize) {
    const size = tileSize * 0.6;
    if (this.def.imageUrl) {
      // lazy image cache
      const img = getImage(this.def.imageUrl);
      if (img.complete) {
        ctx.drawImage(img, this.x - size/2, this.y - size/2, size, size);
      } else {
        ctx.fillStyle = this.def.color || '#48c774';
        circle(ctx, this.x, this.y, size * 0.35);
      }
    } else {
      ctx.fillStyle = this.def.color || '#48c774';
      circle(ctx, this.x, this.y, size * 0.35);
    }
    // health bar
    drawHealth(ctx, this.x, this.y - tileSize * 0.4, this.health, this.def.maxHealth ?? 100);
  }
}

import { getZombieSprites } from './sprites.js';

export class Zombie extends Entity {
  constructor(r, x, y, opts = {}) {
    super(x, y);
    this.r = r;
    this.speed = opts.speed ?? 20; // px/s
    this.damage = opts.damage ?? 10; // DPS when eating
    this.health = opts.health ?? 100;
    this.maxHealth = this.health;
    this.eating = false;
    this.skin = opts.skin || '';
    this.color = opts.color || '';
    this.hat = opts.hat || '';
    this.typeKey = opts.typeKey || 'normal';
    this.animTime = 0;
  }
  update(dt, game) {
    if (this.dead) return;
    this.animTime += dt;
    // check plant in front on same row
    const tileSize = game.grid.tileSize;
    const c = Math.floor(this.x / tileSize);
    const plant = game.grid.tiles[this.r]?.[c]?.plant;
    if (plant && !plant.dead && Math.abs(plant.y - this.y) < tileSize * 0.4 && plant.x < this.x) {
      // eat
      this.eating = true;
      plant.hit(this.damage * dt);
      if (plant.dead) game.grid.tiles[plant.r][plant.c].plant = null;
    } else {
      this.eating = false;
      this.x -= this.speed * dt;
      if (this.x < 0) {
        game.gameOver();
      }
    }
  }
  hit(dmg) {
    this.health -= dmg;
    if (this.health <= 0) this.dead = true;
  }
  render(ctx, tileSize) {
    // Prefer user-provided skin image; otherwise use generated sprites
    const sprites = getZombieSprites(tileSize);
    const cycle = this.eating ? sprites[this.typeKey]?.eat : sprites[this.typeKey]?.walk;
    const size = sprites[this.typeKey]?.size || { w: tileSize * 0.6, h: tileSize * 0.7 };
    const w = size.w, h = size.h;
    if (this.skin) {
      const img = getImage(this.skin);
      if (img.complete) {
        ctx.drawImage(img, this.x - w/2, this.y - h/2, w, h);
      } else {
        ctx.fillStyle = this.eating ? '#b45309' : (this.color || '#94a3b8');
        ctx.fillRect(this.x - w/2, this.y - h/2, w, h);
      }
    } else {
      const frames = cycle && cycle.length ? cycle : null;
      if (frames) {
        const idx = Math.floor((this.animTime * 8) % frames.length);
        const frame = frames[idx];
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(frame, this.x - w/2, this.y - h/2, w, h);
      } else {
        ctx.fillStyle = this.eating ? '#b45309' : (this.color || '#94a3b8');
        ctx.fillRect(this.x - w/2, this.y - h/2, w, h);
      }
    }
    // cone hat
    if (this.hat === 'cone') {
      ctx.fillStyle = '#f97316';
      ctx.beginPath();
      ctx.moveTo(this.x, this.y - h/2 - 8);
      ctx.lineTo(this.x - 14, this.y - h/2 + 8);
      ctx.lineTo(this.x + 14, this.y - h/2 + 8);
      ctx.closePath(); ctx.fill();
      ctx.strokeStyle = '#ea580c'; ctx.stroke();
    }
    drawHealth(ctx, this.x, this.y - h/2 - 6, this.health, this.maxHealth || 100);
  }
}

export class Projectile extends Entity {
  constructor(x, y, speed, damage, r, color) {
    super(x, y);
    this.speed = speed; this.damage = damage; this.r = r; this.color = color || '#34d399';
  }
  update(dt, game) {
    this.x += this.speed * dt;
    if (this.x > game.grid.cols * game.grid.tileSize + 40) {
      this.dead = true; return;
    }
    // collision with first zombie in row intersecting circle-rect
    for (const z of game.zombies) {
      if (z.dead || z.r !== this.r) continue;
      const w = game.grid.tileSize * 0.6, h = game.grid.tileSize * 0.7;
      if (intersectCircleRect(this.x, this.y, 6, z.x - w/2, z.y - h/2, w, h)) {
        z.hit(this.damage);
        this.dead = true;
        break;
      }
    }
  }
  render(ctx) {
    ctx.fillStyle = this.color;
    circle(ctx, this.x, this.y, 6);
  }
}

export class SunToken extends Entity {
  constructor(x, y, value = 25) {
    super(x, y);
    this.value = value;
    this.vy = 10; // slight float down
    this.age = 0; this.life = 8; // seconds
  }
  update(dt) {
    this.age += dt;
    this.y += this.vy * dt;
    if (this.age >= this.life) this.dead = true;
  }
  contains(px, py) {
    const r = 14; const dx = px - this.x; const dy = py - this.y; return dx*dx + dy*dy <= r*r;
  }
  render(ctx) {
    // simple sun coin
    ctx.save();
    ctx.translate(this.x, this.y);
    const r = 12;
    ctx.fillStyle = '#fbbf24';
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI*2); ctx.fill();
    ctx.strokeStyle = '#fde68a'; ctx.lineWidth = 2; ctx.stroke();
    ctx.fillStyle = '#0b1324'; ctx.font = '10px sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText('+'+this.value, 0, 0);
    ctx.restore();
  }
}

// helpers
function circle(ctx, x, y, r) {
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
}
function drawHealth(ctx, x, y, hp, max) {
  const w = 36, h = 4;
  ctx.fillStyle = 'rgba(0,0,0,0.5)';
  ctx.fillRect(x - w/2, y - h/2, w, h);
  const p = Math.max(0, Math.min(1, hp / max));
  ctx.fillStyle = p > 0.5 ? '#22c55e' : p > 0.25 ? '#f59e0b' : '#ef4444';
  ctx.fillRect(x - w/2, y - h/2, w * p, h);
}
function intersectCircleRect(cx, cy, cr, rx, ry, rw, rh) {
  const closestX = Math.max(rx, Math.min(cx, rx + rw));
  const closestY = Math.max(ry, Math.min(cy, ry + rh));
  const dx = cx - closestX; const dy = cy - closestY; return (dx*dx + dy*dy) <= cr*cr;
}

const imageCache = new Map();
function getImage(url) {
  if (!imageCache.has(url)) {
    const img = new Image(); img.crossOrigin = 'anonymous'; img.src = url; imageCache.set(url, img);
  }
  return imageCache.get(url);
}
