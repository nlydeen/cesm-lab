import pandas as pd
import sobol

from itertools import product
from multiprocessing import Pool
from os import environ
from os.path import exists
from shutil import rmtree
from subprocess import call
from tqdm.notebook import tqdm


CESM_ROOT = "/opt/ncar/cesm2"

SCRIPT_DIR = f"{CESM_ROOT}/cime/scripts"
MODS_DIR = f"{CESM_ROOT}/components/cam/cime_config/usermods_dirs"

CASE_ROOT = f"/tmp/cases"
ARCHIVE_ROOT = f"{environ['HOME']}/archive"

IOP_CASE_DIR = f"{CASE_ROOT}/scm_ppe.base"


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


def run_case(config):
    name, iop = config["name"], config["iop"]
    del config["name"], config["iop"]
    user_nl_cam = dict(config)

    clone_dir = f"{CASE_ROOT}/{name}"

    if not exists(f"{ARCHIVE_ROOT}/{name}"):
        rmtree(clone_dir, ignore_errors=True)

        assert call([f"{SCRIPT_DIR}/create_clone",
                     "--clone", IOP_CASE_DIR,
                     "--user-mods-dir", f"{MODS_DIR}/scam_{iop}",
                     "--keepexe",
                     "--cime-output-root", clone_dir,
                     "--case", clone_dir]) == 0

        with open(f"{clone_dir}/user_nl_cam", "a") as f:
            for k, v in user_nl_cam.items():
                print(f"{k} = {v}", file=f)

        assert call("./case.submit", cwd=clone_dir) == 0

        rmtree(clone_dir, ignore_errors=True)


def run_cases(df):
    configs = [dict(x[1]) for x in df.iterrows()]

    if not exists(f"{IOP_CASE_DIR}/bld/cesm.exe"):
        rmtree(IOP_CASE_DIR, ignore_errors=True)

        assert call([f"{SCRIPT_DIR}/create_newcase",
                     "--compset", "FSCAM",
                     "--res", "T42_T42",
                     "--user-mods-dir", f"{MODS_DIR}/scam_mandatory",
                     "--case", IOP_CASE_DIR]) == 0

        assert call("./case.setup", cwd=IOP_CASE_DIR) == 0
        assert call("./case.build", cwd=IOP_CASE_DIR) == 0

    with Pool() as p:
        for _ in tqdm(p.imap_unordered(run_case, configs), total=len(configs),
                      mininterval=0., miniters=1):
            pass
