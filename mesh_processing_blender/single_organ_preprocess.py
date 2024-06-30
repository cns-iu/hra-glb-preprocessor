"""
Date: 06/28/2024
Author: Lu
"""

import sys 
import os

cur_dir = os.getcwd()
if not cur_dir in sys.path:
    sys.path.append(cur_dir)

if __name__ == "__main__":
    from organ_preprocess_utils import single_organ_process
    single_organ_process('print')