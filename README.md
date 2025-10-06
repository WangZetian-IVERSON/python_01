# Semantic Segmentation — Training & Demo Artifacts (Concise)

This branch holds only the training artifacts produced during a local demo/training run using the `hszhao/semseg` codebase. It intentionally contains only small artifacts (configs, example outputs, and helper scripts) — large datasets and ImageNet pre-trained backbones are NOT included here for size and licensing reasons.

What is included
- `training_artifacts/`
  - `configs/` — YAML configs used for training/testing (small text files)
  - `scripts/` — helper scripts for running the demo
  - `results/` — example outputs (colorized labels and overlay images)
- `README.md` — this document describing how to reproduce the demo and where to get required large files

What is NOT included (and why)
- ADE20K dataset: large dataset (several GBs). Not included due to size and licensing. See download instructions below.
- ImageNet pretrained backbones (ResNet weights): large binary files and third-party distribution rules. Not included here.
- Full training logs and checkpoints (unless small): checkpoints are large and may be added separately upon request.

Required external downloads (how to obtain)
- ADE20K (dataset used for evaluation/training):
  - Official ADE20K page and download instructions: http://groups.csail.mit.edu/vision/datasets/ADE20K/
  - Mirror (BaiduNetDisk / Google Drive links) — please use the official page first. If you have trouble, I can add a direct link you control.

- ImageNet pretrained weights (ResNet50 backbone):
  - Official PyTorch weights: https://download.pytorch.org/models/resnet50-0676ba61.pth
  - You can also use torchvision's model downloader (recommended):
    - In Python: `torchvision.models.resnet50(pretrained=True)` or the `torch.hub` loader.

Quick setup (Windows PowerShell example)
```powershell
# create env (conda)
conda create -n semseg python=3.9 -y
conda activate semseg
conda install pytorch torchvision torchaudio cudatoolkit=11.8 -c pytorch -y
pip install -r requirements.txt  # if using the project requirements

# download ADE20K manually and place at 'dataset/ADEChallengeData2016' as expected by semseg
# download ResNet50 pretrained and place under initmodel/ if your config expects it
```

Reproduce demo (single image)
```powershell
cd semseg  # project root
$env:PYTHONPATH = (Get-Location).Path
python tool\demo.py --config=config\ade20k\ade20k_pspnet50.yaml --image=figure\demo\ADE_val_00001515.jpg TEST.scales 1.0
```

Notes and help
- If you want, I can add a script to download the ImageNet backbone automatically and place it in `initmodel/`.
- If you provide a preferred ADE20K mirror link, I can add it to the README.

If this looks good, I will push this README to the `local-artifacts` branch to replace the current README there.