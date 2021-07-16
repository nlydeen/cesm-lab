#!/usr/bin/env python

from shutil import copy, rmtree
from subprocess import call
from os.path import dirname, exists, realpath

from common import ACCOUNT, HIST_DIR, REF_CASE, TMP_DIR, USER, read_run_specs


CREATE_CLONE = realpath(f"{dirname(realpath(__file__))}/../cesm_2.1.1/cime"
                        "/scripts/create_clone")

BASE_CASE_DIR = f"{TMP_DIR}/{REF_CASE}.clone"


def submit_run(i, run_spec_row):
    member, run_spec = run_spec_row

    case = f"param_est.{i:03d}.{member:03d}"
    case_dir = f"{TMP_DIR}/{case}"

    if exists(f"{HIST_DIR}/{case}"):
        return

    assert call([CREATE_CLONE, "--case", case_dir, "--clone", BASE_CASE_DIR,
                 "--keepexe"]) == 0

    xmlchange = {
        "RUN_TYPE": "branch",

        "RUN_REFCASE": REF_CASE,
        "RUN_REFDIR": f"/glade/work/{USER}/restarts/{REF_CASE}"
                      f"/{run_spec.meta.start_date}-00000",

        "RUN_REFDATE": run_spec.meta.start_date,
        "RUN_STARTDATE": run_spec.meta.start_date,

        "STOP_N": run_spec.meta.stop_n,
        "STOP_OPTION": run_spec.meta.stop_option,

        "JOB_WALLCLOCK_TIME": run_spec.meta.real_time
    }

    for k, v in xmlchange.items():
        assert call(["./xmlchange", f"{k}={v}"], cwd=case_dir) == 0

    copy("user_nl_cam.def", f"{case_dir}/user_nl_cam")

    with open(f"{case_dir}/user_nl_cam", "a") as f:
        for k, v in run_spec.theta.items():
            print(f"{k} = {v}", file=f)

    assert call("./case.submit", cwd=case_dir) == 0


if __name__ == "__main__":
    if not exists(f"{BASE_CASE_DIR}/bld/cesm.exe"):
        rmtree(BASE_CASE_DIR, ignore_errors=True)

        assert call([CREATE_CLONE, "--case", BASE_CASE_DIR, "--clone",
                     f"/glade/work/cmip6/cases/DECK_2deg/{REF_CASE}",
                     "--cime-output-root", TMP_DIR, "--project", ACCOUNT]) == 0

        assert call("./case.setup", cwd=BASE_CASE_DIR) == 0
        assert call(["qcmd", "-A", ACCOUNT, "--", "./case.build"],
                    cwd=BASE_CASE_DIR) == 0

    run_specs = read_run_specs()

    for run_spec in run_specs.iterrows():
        submit_run(run_specs.i, run_spec)
