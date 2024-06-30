
import os
import sys
import time

cur_dir = os.getcwd()
if not cur_dir in sys.path:
    sys.path.append(cur_dir)


if __name__ == "__main__":
    start = time.time()

    from organ_preprocess_utils import all_organ_process
    all_organ_process('print')

    end = time.time()

    print("It takes {} seconds to preprocess all the models.".format(end - start))
