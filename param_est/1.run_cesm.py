#!/usr/bin/env python3

# $ module load python/3.7.9
# $ ncar_pylib

from shutil import copy, rmtree
from subprocess import call
from os.path import dirname, exists, join, realpath

from common import ARCHIVE_DIR, REF_NAME, SCRATCH_DIR, read_run_specs

CMIP6_CASE_DIR = f"/glade/work/cmip6/cases/DECK_2deg/{REF_NAME}"
PROJECT = "UMIN0005"
CESM_ROOT = f"{dirname(realpath(__file__))}/../cesm_2.1.1"
SCRIPT_DIR = f"{CESM_ROOT}/cime/scripts"
BASE_CASE_DIR = join(SCRATCH_DIR, "param_est.base")
#BASE_CASE_DIR = join(SCRATCH_DIR, REF_NAME)  # XXX
RESTART_DIR = f"/glade/work/nlydeen/restarts/{REF_NAME}"


def submit_run(args):
    member, run_spec = args

    # XXX
    if exists(join(ARCHIVE_DIR, f"param_est.{run_specs.iter:03d}.{member:03d}")):
        return

    case_dir = join(SCRATCH_DIR,
                    f"param_est.{run_specs.iter:03d}.{member:03d}")

    assert call([f"{SCRIPT_DIR}/create_clone", "--clone", BASE_CASE_DIR,
                 "--keepexe", "--case", case_dir]) == 0

    xmlchange = {
        "JOB_WALLCLOCK_TIME": run_spec.meta.max_wallclock_time,
        "RUN_REFCASE": REF_NAME,
        "RUN_REFDATE": run_spec.meta.start_date,
        "RUN_REFDIR": f"{RESTART_DIR}/{run_spec.meta.start_date}-00000",
        "RUN_STARTDATE": run_spec.meta.start_date,
        "RUN_TYPE": "branch",
        "STOP_N": run_spec.meta.stop_n,
        "STOP_OPTION": run_spec.meta.stop_option
    }

    for k, v in xmlchange.items():
        assert call(["./xmlchange", f"{k}={v}"], cwd=case_dir) == 0

    copy("user_nl_cam.def", f"{case_dir}/user_nl_cam")

    with open(f"{case_dir}/user_nl_cam", "a") as f:
        for k, v in run_spec.theta.items():
            print(f"{k} = {v}", file=f)

    assert call("./case.submit", cwd=case_dir) == 0


if __name__ == "__main__":
    if not exists(join(BASE_CASE_DIR, "bld/cesm.exe")):
        rmtree(BASE_CASE_DIR, ignore_errors=True)

        assert call([f"{SCRIPT_DIR}/create_clone", "--clone", CMIP6_CASE_DIR,
                     "--cime-output-root", SCRATCH_DIR, "--project", PROJECT,
                     "--case", BASE_CASE_DIR]) == 0

        assert call("./case.setup", cwd=BASE_CASE_DIR) == 0
        assert call(["qcmd", "-A", PROJECT, "--", "./case.build"],
                    cwd=BASE_CASE_DIR) == 0

    run_specs = read_run_specs()

    for run_spec in run_specs.iterrows():
        submit_run(run_spec)
