# Small helper script to run demo using the project's demo script
# Usage: python run_demo_from_saved.py path/to/image.jpg

import sys
import os

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python run_demo_from_saved.py path/to/image.jpg')
        sys.exit(1)
    img = sys.argv[1]
    os.system(f'python tool\\demo.py --config=config/ade20k/ade20k_pspnet50.yaml --image={img} TEST.scales 1.0')
