from diffusers import DiffusionPipeline
import torch
import argparse

# Simple local SDXL generator that saves a single image to disk
# Example:
#   python tools/generate_sdxl.py --prompt "cute green plant icon" --out out.png --width 256 --height 256 --steps 20


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='stabilityai/stable-diffusion-xl-base-1.0')
    parser.add_argument('--prompt', required=True)
    parser.add_argument('--out', default='out.png')
    parser.add_argument('--width', type=int, default=256)
    parser.add_argument('--height', type=int, default=256)
    parser.add_argument('--steps', type=int, default=20)
    parser.add_argument('--cfg', type=float, default=7.0)
    args = parser.parse_args()

    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    pipe = DiffusionPipeline.from_pretrained(
        args.model, torch_dtype=dtype, use_safetensors=True, variant='fp16' if dtype==torch.float16 else None
    )
    if torch.cuda.is_available():
        pipe.to('cuda')

    img = pipe(prompt=args.prompt, width=args.width, height=args.height, num_inference_steps=args.steps, guidance_scale=args.cfg).images[0]
    img.save(args.out)
    print(f"Saved to {args.out}")


if __name__ == '__main__':
    main()
