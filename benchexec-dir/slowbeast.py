# This file is part of BenchExec, a framework for reliable benchmarking:
# https://github.com/sosy-lab/benchexec
#
# SPDX-FileCopyrightText: 2007-2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import benchexec.tools.template
import benchexec.result as result
import benchexec.util as util


class Tool(benchexec.tools.template.BaseTool2):
    """
    SLOWBEAASSTTT!!!
    """

    REQUIRED_PATHS = [
        "/var/tmp/suyash/slowbeast/slowbeast"
    ]  # add the path to Slowbeast here

    def executable(self):
        return util.find_executable("sb")

    def name(self) -> str:
        return "slowbeast"

    # def cmdline(self, executable, options, tasks, propertyfile, rlimits):
    #     return [executable] + options + tasks

    def cmdline(self, executable, options, task, rlimits):
        data_model_param = get_data_model_from_task(
            task, {ILP32: "-pointer-bitwidth 32", LP64: "-pointer-bitwidth 64"}
        )
        if not data_model_param:
            data_model_param = "-pointer-bitwidth 32"
        return (
            [executable]
            + [task.single_input_file]
            + [data_model_param]
            + ["-exit-on-error"]
            + ["-threads-dpor"]
            + ["-check"]
            + ["no-data-race"]
        )

    def determine_result(self, returncode, returnsignal, output, isTimeout):
        if output is None:
            return f"{result.RESULT_ERROR}(no output)"

        noerrsline = False  # the last line
        noerrs = False
        nokilledpaths = False
        hitassert = False
        for line in output:
            line = line.strip()
            if line.startswith("Found errors:"):
                noerrsline = True
                if line == "Found errors: 0":
                    noerrs = True
            elif "assert False:bool" in line:
                hitassert = True
            elif line == "Killed paths: 0":
                nokilledpaths = True

        if not noerrsline:
            res = result.RESULT_FALSE_DATARACE
        elif noerrs and nokilledpaths:
            res = result.RESULT_TRUE_PROP
        elif not nokilledpaths:
            res = result.RESULT_ERROR
        else:
            res = result.RESULT_UNKNOWN

        if isTimeout:
            return res
        elif returnsignal != 0:
            return f"KILLED (signal {returnsignal}, {res})"
        elif returncode != 0:
            return f"{result.RESULT_ERROR}(returned {returncode}, {res})"
        else:
            return res
