# Testing Symbiotic using FormelaCloud
This guide is similar to the [how to test manual](../symbiotic_how_to_test.md) for Benchexec with slight changes in the execution. The way benchmarks are executed using VerifierCloud is very similar to executing Benchexec, the main difference is how the benchmarks are actually executed.
## 1. Setting up the environment ([Original guide](../symbiotic_how_to_test.md#1-setup-environment))
### arran and ben(s)
The script for executing the benchmarks on FormelaCloud can currently only be run from **arran** and **ben01**-**ben14**
```bash
ssh <xlogin>@arran.fi.muni.cz # or ben01 - ben14.fi.muni.cz
cd /var/tmp #because this directory is not synchronized unlike the $HOME folder
mkdir vcloud-test # use own name
cd vcloud-test
```

### sv-benchmarks

```bash
git clone --depth 1 https://gitlab.com/sosy-lab/benchmarking/sv-benchmarks.git
cd sv-benchmarks
git fetch --tags
git checkout <tag> #e.g. git checkout svcomp22 or checkout a branch
```

### symbiotic

```bash
git clone https://github.com/staticafi/symbiotic.git
git checkout <branch> #e.g. git checkout 9-rc
# build symbiotic
```

## 2. Define tasks ([Original guide](../symbiotic_how_to_test.md#2-describe-what))
**Benchmark definitions**: https://gitlab.com/sosy-lab/sv-comp/bench-defs/-/tree/main/benchmark-defs

```bash
vim sv-benchmarks/symbiotic.xml
```

### symbiotic.xml
```xml
<?xml version="1.0"?>
<!DOCTYPE benchmark PUBLIC "+//IDN sosy-lab.org//DTD BenchExec benchmark 1.9//EN" "https://www.sosy-lab.org/benchexec/benchmark-2.3.dtd">
<benchmark tool="symbiotic" timelimit="15 min" memlimit="15 GB" cpuCores="8">

<require cpuModel="Intel Core i7"/>

  <resultfiles>**/*.graphml</resultfiles>

  <option name="--witness">witness.graphml</option>
  <option name="--sv-comp"/>

<rundefinition name="SV-COMP22_valid-memcleanup">
  <tasks name="MemSafety-MemCleanup">
    <includesfile>../sv-benchmarks/c/MemSafety-MemCleanup.set</includesfile>
    <propertyfile>../sv-benchmarks/c/properties/valid-memcleanup.prp</propertyfile>
  </tasks>
</rundefinition>
</benchmark>
```

#### Important fields:
##### `<benchmark/>`
- tool
- timelimit
- memlimit
- cpuCores

##### `<require/>`
- cpuModel - if the specified cpuModel doesn't match with the actual model of the workers, the benchmarks won't be executed on the workers (can be later overwritten using the `--vcloudCPUModel` option or omited completely)

#### Tasks

`*.xml` describing various tasks must include `rundefinition` and `tasks` fields.

```xml
<rundefinition name="SV-COMP22_no-data-race">
  <tasks name="NoDataRace-Main">
    <includesfile>../sv-benchmarks/c/NoDataRace-Main.set</includesfile>
    <propertyfile>../sv-benchmarks/c/properties/no-data-race.prp</propertyfile>
  </tasks>
</rundefinition>
```


## 3. How to run
Download the script (you need to clone the `benchexec` repository):
```bash
git clone https://github.com/sosy-lab/benchexec.git
```
- The script is not only the `vcloud-benchmark.py` file but also the modules in the `vcloud` subdirectory of `benchexec/contrib/` and other `benchexec` modules

Run the script with the benchmarks:
```bash
./benchexec/contrib/vcloud-benchmark.py ./sv-benchmarks/slowbeast.xml --tool-directory ./slowbeast -o /var/tmp/vcloud-test/results/test --name <name>%test --read-only-dir / --full-access-dir ./ --hidden-dir /home
```
```bash
./benchexec/contrib/vcloud-benchmark.py ./sv-benchmarks/slowbeast.xml --tool-directory ./slowbeast -o /var/tmp/suyash/vcloud-test/results/test --name NoDataRace-Main%test --read-only-dir / --full-access-dir ./ --hidden-dir /home
```
```bash
./benchexec/contrib/vcloud-benchmark.py ./sv-benchmarks/slowbeastOld.xml --tool-directory ./slowbeast -o /var/tmp/suyash/vcloud-test/results/test --name NoDataRace-Main%test --read-only-dir / --full-access-dir ./ --hidden-dir /home
```
- replace `<name>` with your specified name for the test results
- Use relative paths for the `--tool-directory` option. The tool does **not** need to be on every worker machine, it is distributed to all workers. However, the `--tool-directory` option is fully sent to the worker and if an absolute path is specified, the worker will look for the tool on that path.
- The container options that will be given to runexec on the workers are already specified on the workers. However, the script still needs container options like `--hidden-dir /home` to be able to run.
- If this is the first time you are running the script and you do not have the Config file configured (`~/.verifiercloud/client/Config`) use the option `--vcloudMaster HOST` and replace `HOST` with the hostname of the VCloud master (arran.fi.muni.cz). After running the script for the first time, the Config file will be generated **but only with default values**, not taking any values from the command option arguments.
- You can use `--vcloudCPUModel` to specify the cpu model of the workers on which the benchmark should run. The string specified in this option is checked against the actual cpu model found on the workers (it's checked as a substring of the actual cpu model). This option also overwrites the option specified in the benchmark definition xml file.
- You can specify the priority of the run using `--vcloudPriority`. Possible priorities (in ascending order) are: `IDLE`, `LOW`, `HIGH`, `URGENT`. The default priority is set to `LOW`. Use higher priorities with consideration to other users. The priority of the run can be changed after the run collection has already been submitted in the [interactive client](./vcloud-client.md).

### Notes
The script has a `--help` option, explaining all the options.

#### Additional files/tools
It is important to understand that the specified tool is being sent to the master and then distributed to the workers that execute it. The tool is sent to an unspecified directory (the directory is known but nothing can assumed about it) on the worker. If your tool needs some additional files or tools to execute, it would be incorrect to assume if they are on the worker or where they are.

The additional files or tools need to be sent along with the main tool. This can be achieved by overriding the `REQUIRED_PATHS` variable in the python script that defines the tool module if the required files or tools are always a part of the main tool. Otherwise, additional files or tools can be specified when running the script using the option `--vcloudAdditionalFile`.

#### `vcloud-benchmark.py` runs on the foreground
The `vcloud-benchmark.py` script runs on the foreground in the terminal and interrupting it would interrupt the run collection (the completed run results will be collected). You can run the script as a background task (adding `&` at the end) and in case you want to log out of the machine without interrupting the script, also use `nohup` (`nohup [command] &`). You can also use a terminal multiplexer like `tmux` or simply just `screen` to be able to detach from the terminal and reattach later.

#### Running the script from a worker
The workers will be marked as occupied if a user is logged in on the worker machine. This unfortunately means that running the script from the worker will make the worker unable to execute tasks.

In case you want to avoid occupying the worker, consider executing the benchmark from a non-worker machine that has access to the master (in this case from `arran.fi.muni.cz`).

### Troubleshooting
If the script fails with a java outOfMemoryError, add the `--vcloudClientHeap` option with a reasonable amount of MB (200 MB should be enough for Symbiotic, more than 500 MB should not be needed):
```bash
./benchexec/contrib/vcloud-benchmark.py ./sv-benchmarks/symbiotic.xml --tool-directory ./symbiotic/install/bin -o /var/tmp/vcloud-test/results/test --name NAME%test -N 1 --read-only-dir / --full-access-dir ./ --hidden-dir /home --vcloudClientHeap 200
```

## 4. Results ([Original guide](../symbiotic_how_to_test.md#4-where-to-look))
The results will be sent to output folder you specified with the `-o` option. There is no need to download them from anywhere!

Look inside `*.logfiles.zip` (compact representation)
## 5. [Upload results](../symbiotic_how_to_test.md#5-upload-results-mamato)