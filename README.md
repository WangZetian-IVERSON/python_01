# Semantic Segmentation — Training & Demo Artifacts

This repository branch contains only the training artifacts and a concise README describing how this semantic segmentation model was trained and how to reproduce the demo outputs.

## Overview
- Project: semseg (HS Zhao)
- Model: PSPNet (ResNet50 backbone) trained on ADE20K subset (demonstration run)
- Purpose: Save configuration, scripts, example outputs (colorized label and overlay), and reproducible instructions.

## What's included in this branch
- `training_artifacts/`
  - `configs/` — YAML configs used for training/evaluation
  - `scripts/` — helper scripts (demo runner, conversion helpers)
  - `results/` — example outputs: colorized segmentation and overlay images

## Environment
- OS: Windows or Linux (commands below assume Windows PowerShell)
- Python: 3.9+ (use a virtualenv or conda env)
- PyTorch: GPU-enabled build recommended (CUDA 11.x or 12.x depending on your GPU)
- Key packages: numpy, Pillow, opencv-python, torchvision, PyYAML

Example (conda):
```powershell
conda create -n semseg python=3.9 -y
conda activate semseg
conda install pytorch torchvision torchaudio cudatoolkit=11.8 -c pytorch -y
pip install -r requirements.txt  # if provided
```

## Checkpoints
- The demo in `training_artifacts/results` was generated using a checkpoint placed in the original repository's `exp/` path. If you wish to reproduce training or inference, place the checkpoint at the path expected by the config or update the config accordingly.

## Reproduce demo (single image)
From the project root (where `tool/demo.py` exists):

```powershell
# ensure PYTHONPATH points to the project root
$env:PYTHONPATH = (Get-Location).Path
python tool\demo.py --config=config\ade20k\ade20k_pspnet50.yaml --image=figure\demo\ADE_val_00001515.jpg TEST.scales 1.0
```

This will write results to `figure/demo` and (in our webapp) to `webapp/static/results/`.

## Notes & Reproducibility
- Some pretrained weights are required (ImageNet backbone, model checkpoint). If not available, training will take significantly longer.
- The original `hszhao/semseg` repository has additional scripts and dataset links — consult it for full training recipes.

## Contact
If anything is unclear or you want me to add training logs, hyperparameters, or saved checkpoints to this branch, tell me and I will include them.
