# PVZ-Lite Framework



https://github.com/user-attachments/assets/b34519c9-edfc-4c83-b268-ff449984ef6e



A minimal Plants vs. Zombies–style web game framework built with vanilla HTML/CSS/JS (ES Modules). It includes:
- Grid/lane system, basic plants, zombies, and projectiles
- Plant placement, auto shooting, zombie attacks, kill score, game-over detection
- Plant library and a “Custom Plant” form (tunable stats and image URL), prepared for future text-to-image (T2I) integration
- Basic economy (Sun) and placement cooldowns, plus a “Restart” button

## How to Run
No build step. Just open `index.html` in your browser.

On Windows, you can use VS Code Live Server or any local static server.

## Project Structure
- `index.html` – Page and UI
- `styles.css` – Styling
- `src/engine.js` – Game loop (fixed-timestep updates + per-frame render)
- `src/models.js` – Grid/Plant/Zombie/Projectile and core mechanics
- `src/game.js` – Orchestration (placement, spawns, scoring, game over)
- `src/main.js` – Bootstrap and UI wiring (plant palette and custom plants)
- `src/registry.js` – Plant registry and built-in plants

## Custom Plants and Text-to-Image (T2I)
- You can add plants via the “Custom Plant” form, configuring stats and an image URL.
- When T2I integration is in place, you can host the generated image locally or remotely and simply paste its URL here to display it.
- You can also extend `registry.js` and `Plant.render` to support Base64 data URLs, or cache textures in IndexedDB.

### Local T2I Recommendation (Windows)
- UI and API: AUTOMATIC1111 Stable Diffusion WebUI (provides a txt2img API)
- Model suggestions:
  - Lower VRAM (4–6 GB): SD 1.5 family (e.g., v1-5-pruned), use 256–384 for stability
  - Mid VRAM (8 GB+): SDXL + SDXL Turbo (for fast previews) with higher quality
  - You can also use LoRAs/checkpoints targeting icon/flat vector styles

### Startup and API
1) Download A1111 WebUI (no link included here). The first launch will download dependencies as instructed by the project.
2) Add `--api` to the launch arguments to enable the HTTP API.
3) Select the model in the WebUI and wait for it to load.
4) Make sure your browser can access `http://127.0.0.1:7860` (default port 7860).

If you need CORS:
- The simplest way is to open this project via the file protocol or serve it from the same origin. If you must access from a different origin/port, you can launch WebUI with `--cors-allow-origins *`.

### Using It in This Project
- In the sidebar “Text-to-Image” section, enter the API URL (default `http://127.0.0.1:7860`) and your prompt, then click “Generate”.
- When the image is ready, you’ll see a preview. Click “Add to Plant Library” to register it as a plant sprite, and set cost, fire rate, damage, projectile speed, and placement cooldown.

### Local Diffusers Backend (No A1111 Needed)
This project includes a simple backend (FastAPI + diffusers):
1) Install dependencies (preferably in a fresh environment):
   
	```bash
	pip install fastapi uvicorn diffusers transformers accelerate torch --upgrade
	```

2) Run the backend (port 7861):
   
	```bash
	uvicorn server.app:app --host 127.0.0.1 --port 7861 --reload
	```

3) In the frontend “Text-to-Image” panel, select “Local Diffusers Backend” and set the API URL to `http://127.0.0.1:7861`.
4) When served from the same origin, no extra CORS setup is required (the backend also serves the frontend static files).

### Fully Offline Workflow (No API)
If you prefer using `diffusers` locally without an HTTP API:
1) Install dependencies (ideally in a virtual environment)
   
	```bash
	pip install diffusers transformers accelerate torch --upgrade
	```

2) Run the helper script to generate an image:
   
	```bash
	python tools/generate_sdxl.py --prompt "cute green plant icon" --out plant.png --width 256 --height 256 --steps 20
	```

3) In the sidebar “Custom Plant” section:
	- Choose “Local Image” and upload `plant.png` (or paste an image URL).

4) The “Zombie Appearance” section also supports uploading a local image.

## Economy and Cooldowns
- Sun increases passively (default +5 every 5 seconds). Plant placement consumes Sun (each plant has its own cost).
- Plants have a placement cooldown (`placeCooldown`); while cooling down, that card cannot be placed again.
- The plant cards in the sidebar display cost and cooldown; they are grayed out when conditions are not met.

## Roadmap / Ideas
- Enrich economy (Sun), costs, cooldowns, and card slots
