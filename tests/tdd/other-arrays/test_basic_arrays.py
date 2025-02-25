import pytest
import os
import glob

from tests.utils.utils import *

IN_DIR = os.path.abspath("/app/tests/tdd/other-arrays/input-files") + os.sep
OUT_DIR = os.path.abspath("/app/tests/tdd/other-arrays/output-files") + os.sep

def get_input_files():
    """Returns file ids for indexing tests"""
    pattern = os.path.join(IN_DIR, "*.yml")
    return glob.glob(pattern)

def file_id(filename):
    return os.path.basename(str(filename).split('.')[0])

@pytest.mark.parametrize("input_file", get_input_files(), ids=file_id)
def test_all_files(input_file):
    target_file, expected_verdict, out_dir_target = get_verdict(input_file, OUT_DIR)

    output = run_sb(target_file, out_dir_target, IN_DIR)

    write_output_log(out_dir_target, output)
    
    evaluate_result(expected_verdict, output)