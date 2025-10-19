export class Engine {
  constructor(canvas, { tickRate = 60 } = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.tickRate = tickRate;
    this.acc = 0;
    this.last = 0;
    this.running = false;
    this.onUpdate = () => {};
    this.onRender = () => {};
  }

  start() {
    this.running = true;
    this.last = performance.now();
    const step = 1 / this.tickRate;
    const loop = (t) => {
      if (!this.running) return;
      const dt = Math.min(0.05, (t - this.last) / 1000);
      this.last = t;
      this.acc += dt;
      while (this.acc >= step) {
        this.onUpdate(step);
        this.acc -= step;
      }
      this.onRender(this.ctx);
      requestAnimationFrame(loop);
    };
    requestAnimationFrame(loop);
  }

  stop() { this.running = false; }
}
