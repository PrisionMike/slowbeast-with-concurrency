import yaml
import subprocess


def __init__(self):
    pass
def evaluate_result(expected_verdict, output):
    for line in output.stdout:
        line = line.strip()
        if line == 'Data Race Found: True':
            assert expected_verdict == "false"
            break
        elif line == 'Data Race Found: False':
            assert expected_verdict == "true"
            break


def get_verdict(input_file, out_dir):
    with open(input_file) as f:
        yml_verdict = yaml.safe_load(f)
    target_file = yml_verdict.get("input_files")
    data_race_results = yml_verdict.get("properties", [])
    for drr in data_race_results:
        prop_file = drr.get("property_file")
        assert prop_file == '../properties/no-data-race.prp'
        expected_verdict = drr.get("expected_verdict")
    out_dir_target = out_dir + target_file

    return target_file, expected_verdict, out_dir_target


def run_sb(target_file, out_dir_target, base_dir):
    output = subprocess.run(
            ["sb-main", base_dir + target_file, "-out-dir", out_dir_target],
            capture_output=True,
            text=True
        )
    
    return output


def write_output_log(target_file, out_dir_target, output):
    with open(out_dir_target + target_file + ".log", 'w') as g:
        g.write("****** STDOUT *******\n")
        g.write(output.stdout)
        g.write("********************\n")
        if output.stderr != '':
            g.write("****** STDERR *******\n")
            g.write(output.stderr)
            g.write("*********************")
            assert False