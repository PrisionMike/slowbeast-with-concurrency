import pytest
import os
import glob

from tests.utils.utils import *

IN_DIR = os.path.abspath("/app/tests/tdd/array-errors/input-files") + os.sep
OUT_DIR = os.path.abspath("/app/tests/tdd/array-errors/output-files") + os.sep

def get_input_files():
    """Returns file ids for indexing tests"""
    pattern = os.path.join(IN_DIR, "*.yml")
    return glob.glob(pattern)

def file_id(filename):
    return os.path.basename(str(filename).split('.')[0])

@pytest.mark.parametrize("input_file", get_input_files(), ids=file_id)
def test_all_units(input_file):
    target_file, expected_verdict, out_dir_target = get_verdict(input_file, OUT_DIR)

    output = run_sb(target_file, out_dir_target, IN_DIR)

    write_output_log(out_dir_target, output)
    
    evaluate_result(expected_verdict, output)

def _evaluate_result(expected_verdict, output):
    for line in output.stdout.splitlines():
        line = line.strip()
        print(line)
        if line == 'Data Race Found: True':
            print("SS: 1", line)
            assert expected_verdict is False
            break
        elif line == 'Data Race Found: False':
            print("SS: 2", line)
            assert expected_verdict is True
            break