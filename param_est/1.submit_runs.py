#!/usr/bin/env python3

# $ module load python/3.7.9
# $ ncar_pylib

from shutil import rmtree
from subprocess import call
from os.path import exists, join

from common import SCRATCH_DIR, read_run_specs


PROJECT = "UMIN0005"
CESM_ROOT = "/glade/u/home/nlydeen/cesm-2.2.0"
SCRIPT_DIR = f"{CESM_ROOT}/cime/scripts"
BASE_CASE_DIR = join(SCRATCH_DIR, "param_est.base")


def submit_run(args):
    member, run_spec = args

    case_dir = join(SCRATCH_DIR,
                    f"param_est.{run_specs.iter:03d}.{member:03d}")

    assert call([f"{SCRIPT_DIR}/create_clone", "--clone", BASE_CASE_DIR,
                 "--keepexe", "--cime-output-root", case_dir, "--case",
                 case_dir]) == 0

    assert call(["./xmlchange", f"STOP_OPTION={run_spec.setup.stop_option},"
                 f"STOP_N={run_spec.setup.stop_n}"], cwd=case_dir) == 0

    with open(f"{case_dir}/user_nl_cam", "a") as f:
        for k, v in run_spec.theta.items():
            print(f"{k} = {v}", file=f)

    assert call("./case.submit", cwd=case_dir) == 0


if __name__ == "__main__":
    if not exists(join(BASE_CASE_DIR, "bld/cesm.exe")):
        rmtree(BASE_CASE_DIR, ignore_errors=True)

        assert call([f"{SCRIPT_DIR}/create_newcase", "--compset", "B1850",
                     "--res", "f19_g17", "--case", BASE_CASE_DIR,
                     "--project", PROJECT, "--run-unsupported"]) == 0

        assert call("./case.setup", cwd=BASE_CASE_DIR) == 0
        assert call(["./case.build", "--skip-provenance-check"],
                     cwd=BASE_CASE_DIR) == 0

    run_specs = read_run_specs()

    for run_spec in run_specs.iterrows():
        submit_run(run_spec)
