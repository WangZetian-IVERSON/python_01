import { Engine } from './engine.js';
import { Grid, Plant, Zombie, Projectile, SunToken } from './models.js';

export class Game {
  constructor(canvas, registry, { rows = 5, cols = 9, tileSize = 80 } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.registry = registry;
    this.grid = new Grid(rows, cols, tileSize);
    this.engine = new Engine(canvas);
    this.plants = [];
    this.zombies = [];
    this.projectiles = [];
    this.sunTokens = [];
    this.running = false;
    this.score = 0;
    // sun economy
    this.sun = 50; // current sun
    this.totalSun = 0; // total gained
    this.sunSpent = 0; // total spent
    this.sunRate = 5; // sun per 5s passive gain
    this.sunTimer = 0;
    this.selectedPlantKey = null;
    this.spawnTimer = 0; // zombie spawn timer
    this.cooldowns = new Map(); // key -> remaining seconds

    // Level system
    this.levelNum = 0;
    this.levelDurationSec = 120; // 2 minutes target per level
    this.levelElapsed = 0;
    this.levelActive = false;
    this.allowedTypes = ['normal'];
    this.spawnBase = 2.5; // base spawn interval (seconds)

  this.engine.onUpdate = (dt) => this.update(dt);
  this.engine.onRender = (ctx) => this.render(ctx);

    canvas.addEventListener('click', (e) => this.onCanvasClick(e));
  }

  start() {
    this.running = true;
    if (!this.levelActive && this.levelNum === 0) {
      this.startLevel(1);
    } else {
      this.engine.start();
    }
  }
  startLevel(n) {
    this.levelNum = n;
    this.levelElapsed = 0;
    this.levelActive = true;
    this.spawnTimer = 0;
    // Allowed zombie types per level
    const seq = [ ['normal'], ['normal','fast'], ['normal','fast','cone'], ['normal','fast','cone','tank'] ];
    this.allowedTypes = seq[Math.min(n-1, seq.length-1)];
    // Spawn pacing tightens by level
    this.spawnBase = Math.max(0.8, 2.5 - (n-1) * 0.3);
    // UI updates
    const numEl = document.getElementById('level-num'); if (numEl) numEl.textContent = String(n);
    const durEl = document.getElementById('level-duration'); if (durEl) durEl.textContent = formatTime(this.levelDurationSec);
    const timeEl = document.getElementById('level-time'); if (timeEl) timeEl.textContent = formatTime(0);
    const btn = document.getElementById('next-level-btn'); if (btn) btn.disabled = true;
    const st = document.getElementById('game-state'); if (st) st.textContent = '进行中';
    this.renderLevelTypes();
    this.updateSunUI();
    this.engine.start();
  }
  renderLevelTypes() {
    const map = { normal: '普通', fast: '快速', cone: '路锥', tank: '坦克' };
    const ul = document.getElementById('level-types');
    if (!ul) return;
    ul.innerHTML = '';
    (this.allowedTypes || []).forEach(k => { const li = document.createElement('li'); li.textContent = map[k] || k; ul.appendChild(li); });
  }
  stop() { this.running = false; this.engine.stop(); }
  setSelectedPlant(key) { this.selectedPlantKey = key; }
  setZombieSkin(url) { this.zombieSkin = (url && url.length > 0) ? url : ''; }
  getSun() { return this.sun; }
  getCooldown(key) { return this.cooldowns.get(key) || 0; }
  canPlace(key) {
    const def = this.registry.get(key);
    if (!def) return false;
    const cd = this.getCooldown(key);
    return this.sun >= def.cost && cd <= 0;
  }
  spendSun(amount) { this.sun = Math.max(0, this.sun - amount); this.sunSpent = (this.sunSpent || 0) + amount; this.updateSunUI(); }
  addSun(amount) { this.sun += amount; this.totalSun = (this.totalSun || 0) + amount; this.updateSunUI(); }
  updateSunUI() {
    const sunEl = document.getElementById('sun'); if (sunEl) sunEl.textContent = String(this.sun);
    const ts = document.getElementById('total-sun'); if (ts) ts.textContent = String(this.totalSun || 0);
    const sp = document.getElementById('sun-spent'); if (sp) sp.textContent = String(this.sunSpent || 0);
  }

  onCanvasClick(e) {
    if (!this.running) return;
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left; const y = e.clientY - rect.top;
    // try collect sun first
    for (const s of this.sunTokens) {
      if (s.contains && s.contains(x, y)) {
        this.addSun(s.value);
        s.dead = true;
        return;
      }
    }
    const cell = this.grid.cellAt(x, y);
    if (!cell) return;
    const { r, c } = cell;
    if (!this.grid.tiles[r][c].plant && this.selectedPlantKey) {
      const key = this.selectedPlantKey;
      const def = this.registry.get(key);
      if (!def) return;
      if (!this.canPlace(key)) return; // not enough sun or cooling
      const plant = new Plant(this.grid, r, c, def);
      this.grid.tiles[r][c].plant = plant; this.plants.push(plant);
      this.spendSun(def.cost);
      this.cooldowns.set(key, def.placeCooldown || 0);
      this.updateSunUI();
    }
  }

  spawnProjectile(x, y, speed, damage, r, color) {
    this.projectiles.push(new Projectile(x, y, speed, damage, r, color));
  }

  spawnZombie() {
    const r = Math.floor(Math.random() * this.grid.rows);
    const { y } = this.grid.centerOf(r, 0);
    const x = this.grid.cols * this.grid.tileSize + 40;
    // pick a type from allowed pool
    const defs = {
      normal: { key: 'normal', speed: 20, health: 110, color: '#94a3b8' },
      fast:   { key: 'fast',   speed: 35, health: 80,  color: '#60a5fa' },
      tank:   { key: 'tank',   speed: 14, health: 200, color: '#64748b' },
      cone:   { key: 'cone',   speed: 18, health: 140, color: '#94a3b8', hat: 'cone' },
    };
    const pool = (this.allowedTypes || []).map(k => defs[k]).filter(Boolean);
    const t = pool.length ? pool[Math.floor(Math.random() * pool.length)] : defs.normal;
    this.zombies.push(new Zombie(r, x, y, { typeKey: t.key, speed: t.speed, health: t.health, skin: this.zombieSkin, color: t.color, hat: t.hat }));
  }

  gameOver() {
    this.running = false;
    const el = document.getElementById('game-state');
    if (el) el.textContent = '失败';
    // stop updates but leave render to show final state
    this.engine.onUpdate = () => {};
  }

  update(dt) {
    // level timer and completion
    if (this.levelActive) {
      this.levelElapsed += dt;
      const tEl = document.getElementById('level-time'); if (tEl) tEl.textContent = formatTime(Math.floor(this.levelElapsed));
      if (this.levelElapsed >= this.levelDurationSec) {
        this.levelActive = false;
        const st = document.getElementById('game-state'); if (st) st.textContent = '通关';
        const btn = document.getElementById('next-level-btn'); if (btn) btn.disabled = false;
      }
    }
    // passive sun income
    this.sunTimer += dt;
    if (this.sunTimer >= 5) {
      this.sunTimer -= 5;
      this.addSun(this.sunRate); // +5 sun per 5s by default
    }

    // tick placement cooldowns
    for (const [key, t] of this.cooldowns) {
      const nt = Math.max(0, t - dt);
      if (nt === 0) this.cooldowns.delete(key); else this.cooldowns.set(key, nt);
    }

    // spawn zombies over time (only if active level)
    if (this.levelActive) {
      this.spawnTimer -= dt;
      if (this.spawnTimer <= 0) {
        const difficulty = Math.min(1.0, this.levelElapsed / this.levelDurationSec);
        const pace = Math.max(0.6, this.spawnBase - difficulty * 0.4);
        this.spawnTimer = pace;
        this.spawnZombie();
      }
    }

    // update entities
    for (const p of this.plants) p.update(dt, this);
    for (const z of this.zombies) z.update(dt, this);
    for (const pr of this.projectiles) pr.update(dt, this);

    // cleanup
    const zBefore = this.zombies.length;
    this.zombies = this.zombies.filter(z => !z.dead);
    const zKilled = zBefore - this.zombies.length;
    if (zKilled > 0) {
      this.score += zKilled * 10;
      // spawn sun tokens on kill
      for (let i = 0; i < zKilled; i++) {
        const r = Math.floor(Math.random() * this.grid.rows);
        const { x, y } = this.grid.centerOf(r, 2 + Math.floor(Math.random()*3));
        this.spawnSunToken(x, y - 10, 25);
      }
      const sc = document.getElementById('score');
      if (sc) sc.textContent = String(this.score);
    }
    this.projectiles = this.projectiles.filter(p => !p.dead);
    this.plants = this.plants.filter(p => !p.dead);
    // update sun tokens
    for (const s of this.sunTokens) s.update(dt);
    this.sunTokens = this.sunTokens.filter(s => !s.dead);
  }

  render(ctx) {
    const { rows, cols, tileSize } = this.grid;
    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    // background
    ctx.fillStyle = '#0b1324';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // grid
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = c * tileSize; const y = r * tileSize;
        ctx.fillStyle = (r + c) % 2 === 0 ? '#0f1b34' : '#0c162a';
        roundRect(ctx, x + 2, y + 2, tileSize - 4, tileSize - 4, 8);
        ctx.fill();
      }
    }

    // lanes markers
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    for (let r = 1; r < rows; r++) {
      const y = r * tileSize;
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cols * tileSize, y); ctx.stroke();
    }

    // entities
    for (const p of this.plants) p.render(ctx, tileSize);
    for (const z of this.zombies) z.render(ctx, tileSize);
    for (const pr of this.projectiles) pr.render(ctx);
    for (const s of this.sunTokens) s.render(ctx);
  }

  spawnSunToken(x, y, value) { this.sunTokens.push(new SunToken(x, y, value)); }
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function formatTime(sec) {
  const s = Math.max(0, Math.floor(sec));
  const m = Math.floor(s / 60); const r = s % 60;
  return `${String(m).padStart(2,'0')}:${String(r).padStart(2,'0')}`;
}
