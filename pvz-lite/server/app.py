import base64
from io import BytesIO
import os
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="PVZ-Lite Local Backend")


# -------- Diffusers pipeline (lazy init) --------
pipe = None
device = None

def get_pipeline(model_id: str = "black-forest-labs/FLUX.1-dev"):
    global pipe, device
    if pipe is None:
        import torch
        from diffusers import DiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        # Offline mode: block downloads, only use local cache
        offline = os.getenv("PVZ_T2I_OFFLINE", "").lower() in ("1", "true", "yes") or \
                  os.getenv("HF_HUB_OFFLINE", "").lower() in ("1", "true", "yes")
        pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            use_safetensors=True,
            variant="fp16" if dtype == torch.float16 else None,
            local_files_only=offline,
            cache_dir="F:/HF"
        )
        pipe.to(device)
        # Optionally enable attention slicing for low VRAM
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass
    return pipe


class Txt2ImgReq(BaseModel):
    prompt: str
    width: Optional[int] = 256
    height: Optional[int] = 256
    steps: Optional[int] = 20
    cfg: Optional[float] = 7.0
    model: Optional[str] = None
    sampler_name: Optional[str] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None


@app.post("/api/txt2img")
def txt2img(req: Txt2ImgReq):
    model_id = req.model or "stabilityai/stable-diffusion-xl-base-1.0"
    pl = get_pipeline(model_id)
    # Optional: approximate sampler mapping for diffusers
    sampler = (req.sampler_name or "").lower()
    try:
        if "dpm" in sampler and "karras" in sampler:
            from diffusers import DPMSolverMultistepScheduler
            pl.scheduler = DPMSolverMultistepScheduler.from_config(pl.scheduler.config, use_karras_sigmas=True)
    except Exception:
        pass

    # Seeded generator if provided
    gen = None
    if req.seed is not None:
        import torch
        # Use the same device as pipeline
        gen = torch.Generator(device=device).manual_seed(int(req.seed))

    image = pl(
        prompt=req.prompt,
        negative_prompt=(req.negative_prompt or None),
        width=int(req.width or 256),
        height=int(req.height or 256),
        num_inference_steps=int(req.steps or 20),
        guidance_scale=float(req.cfg or 7.0),
        generator=gen,
    ).images[0]

    buf = BytesIO()
    image.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return {"image": b64}


# Serve static frontend under /pvz-lite AFTER routes to avoid shadowing /api
app.mount("/pvz-lite", StaticFiles(directory="..", html=True), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/pvz-lite/index.html")

# To run: uvicorn app:app --host 127.0.0.1 --port 7861 --reload
