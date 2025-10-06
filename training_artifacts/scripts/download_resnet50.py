#!/usr/bin/env python3
"""
Safe downloader for ResNet50 pretrained weights into initmodel/
Usage: python download_resnet50.py --out-dir initmodel
"""
import argparse
import os
import sys
import hashlib
from urllib.request import urlopen, urlretrieve

RESNET50_URL = "https://download.pytorch.org/models/resnet50-0676ba61.pth"
RESNET50_SHA256 = "0676ba618c5472b6f3b7be1e0b5a2d3d"  # placeholder; we'll not strictly verify in this script


def sha256sum(path, block_size=65536):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            h.update(block)
    return h.hexdigest()


def download(url, out_path):
    print(f"Downloading {url} -> {out_path}")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    urlretrieve(url, out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="initmodel", help="Directory to save pretrained weights")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file if present")
    args = parser.parse_args()

    out_dir = args.out_dir
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.basename(RESNET50_URL)
    out_path = os.path.join(out_dir, filename)

    if os.path.exists(out_path) and not args.force:
        print(f"File already exists at {out_path}. Skipping download. Use --force to overwrite.")
        sys.exit(0)

    try:
        download(RESNET50_URL, out_path)
    except Exception as e:
        print("Download failed:", e)
        sys.exit(2)

    print("Download finished.")
    # optional checksum
    try:
        s = sha256sum(out_path)
        print("Downloaded file SHA256:", s)
    except Exception:
        pass


if __name__ == '__main__':
    main()
