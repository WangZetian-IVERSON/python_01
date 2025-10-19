export class PlantRegistry {
  constructor() { this.map = new Map(); }
  register(def) {
    if (!def || !def.key) throw new Error('Plant def requires key');
    const norm = normalizeDef(def);
    this.map.set(norm.key, norm);
    return norm;
  }
  get(key) { return this.map.get(key); }
  list() { return [...this.map.values()]; }
}

function normalizeDef(d) {
  return {
    key: d.key,
    name: d.name || '植物',
    maxHealth: clamp(d.maxHealth ?? 100, 10, 1000),
    cost: clamp(d.cost ?? 0, 0, 9999),
    fireRate: clamp(d.fireRate ?? 1, 0, 20), // shots per second
    damage: clamp(d.damage ?? 20, 1, 1000),
    projectileSpeed: clamp(d.projectileSpeed ?? 200, 10, 2000),
    color: d.color || '#48c774',
    imageUrl: d.imageUrl || '',
    placeCooldown: clamp(d.placeCooldown ?? 3, 0, 60), // seconds between placements of same card
    sunRate: d.sunRate ? clamp(d.sunRate, 0, 1000) : 0, // sun per trigger; if >0, plant produces sun periodically
    sunInterval: d.sunInterval ? clamp(d.sunInterval, 0.1, 120) : 0, // seconds between sun production
  };
}
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

export const builtinPlants = [
  {
    key: 'pea', name: '豌豆', maxHealth: 100, cost: 25,
    fireRate: 0.8, damage: 18, projectileSpeed: 220, color: '#22c55e', placeCooldown: 2
  },
  {
    key: 'rapid', name: '速射', maxHealth: 80, cost: 50,
    fireRate: 2.0, damage: 10, projectileSpeed: 260, color: '#34d399', placeCooldown: 3
  },
  {
    key: 'heavy', name: '重击', maxHealth: 140, cost: 75,
    fireRate: 0.4, damage: 40, projectileSpeed: 200, color: '#10b981', placeCooldown: 4
  },
  {
    key: 'sunflower', name: '向日葵', maxHealth: 90, cost: 50,
    fireRate: 0, damage: 0, projectileSpeed: 0, color: '#f59e0b', placeCooldown: 5,
    sunRate: 25, sunInterval: 7
  },
];
