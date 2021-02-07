import pandas as pd
import sobol

from contextlib import contextmanager
from functools import partial
from itertools import product
from multiprocessing import Manager, Pool
from os import chdir as chdir_, environ, getcwd, system
from os.path import exists
from shutil import rmtree
from time import sleep
from tqdm.notebook import tqdm


CESM_ROOT = "/opt/ncar/cesm2"
SCRIPT_DIR = f"{CESM_ROOT}/cime/scripts"
IOP_DIR = f"{CESM_ROOT}/components/cam/cime_config/usermods_dirs"
CASE_ROOT = f"{environ['HOME']}/cases"


def qmc(iops, space, n):
    sample = sobol.sample(len(space), n)

    for column, bounds in zip(sample.T, space.values()):
        low, high = bounds
        column *= high - low
        column += low

    return [dict(zip(space.keys(), x)) for x in sample]


def plan_cases(iops, param_space, n_cases):
    cases = product(qmc(iops, param_space, n_cases), iops)

    df = pd.DataFrame([{"iop": iop, **params} for params, iop in cases])

    n_digits = len(str(df.index[-1]))
    df.insert(0, "name", [f"scm_ppe.{str(x).rjust(n_digits, '0')}"
                          for x in df.index])

    return df


@contextmanager
def chdir(dir):
    cwd = getcwd()

    try:
        chdir_(dir)
        yield
    finally:
        chdir_(cwd)


def run_case(conf, lock):
    name, iop = conf["name"], conf["iop"]
    del conf["name"], conf["iop"]

    user_nl_cam = dict(conf)
    user_nl_cam["use_topo_file"] = ".true."

    base_dir = f"{CASE_ROOT}/scm_ppe.{iop}"
    clone_dir = f"{CASE_ROOT}/{name}"

    cesm_exe = f"{base_dir}/bld/cesm.exe"

    if not exists(f"{clone_dir}/timing"):
        rmtree(clone_dir, ignore_errors=True)

        with lock:
            if not exists(cesm_exe):
                rmtree(base_dir, ignore_errors=True)

                assert system(f"{SCRIPT_DIR}/create_newcase"
                              f" --compset FSCAM "
                              f" --res T42_T42"
                              f" --user-mods-dir {IOP_DIR}/scam_{iop}"
                              f" --case {base_dir}") == 0, \
                       "create_newcase failed"

                with chdir(base_dir):
                    assert system("./case.setup") == 0, "./case.setup failed"
                    assert system("./case.build") == 0, "./case.build failed"

        while not exists(cesm_exe):
            sleep(1)

        assert system(f"{SCRIPT_DIR}/create_clone"
                      f" --clone {base_dir}"
                       " --keepexe"
                      f" --case {clone_dir}") == 0, "create_clone failed"

        with chdir(clone_dir):
            with open("user_nl_cam", "a") as f:
                for k, v in user_nl_cam.items():
                    print(f"{k} = {v}", file=f)

            assert system("./case.submit") == 0, "./case.submit failed"


def run_cases(df):
    lock = Manager().Lock()
    confs = [dict(x[1]) for x in df.iterrows()]

    # XXX: Don't do this if your system has a job scheduler.
    with Pool() as p:
        for _ in tqdm(p.imap_unordered(partial(run_case, lock=lock), confs),
                      total=len(confs), mininterval=0., miniters=1):
            pass
