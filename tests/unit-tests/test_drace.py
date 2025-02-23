import subprocess
import yaml

BASE_DIR = '/app/tests/unit-tests/input-files/'
OUT_DIR = "/app/tests/unit-tests/output-files/"

def test_drace():
    input_file = 'drace.yml'
    with open(BASE_DIR + input_file) as f:
        yml_verdict = yaml.safe_load(f)
        target_file = yml_verdict.get("input_files")
        data_race_results = yml_verdict.get("properties", [])
        for drr in data_race_results:
            prop_file = drr.get("property_file")
            assert prop_file == '../properties/no-data-race.prp'
            expected_verdict = drr.get("expected_verdict")
        out_dir_target = OUT_DIR + target_file
        output = subprocess.run(
            ["sb-main", BASE_DIR + target_file, "-out-dir", out_dir_target],
            capture_output=True,
            text=True
        ) 
        with open(out_dir_target + target_file + ".log", 'w') as g:
            g.write("****** STDOUT *******")
            g.write(output.stdout)
            g.write("********************")
            if output.stderr != '':
                g.write("****** STDERR *******")
                g.write(output.stderr)
                g.write("*********************")
                assert False

        for line in output.stdout:
            line = line.strip()
            if line == 'Data Race Found: True':
                assert expected_verdict == "false"
                break
            elif line == 'Data Race Found: False':
                assert expected_verdict == "true"
                break