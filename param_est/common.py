import pandas as pd

from os import environ, listdir, makedirs
from os.path import dirname
from re import search


REF_CASE = "b.e21.B1850.f19_g17.CMIP6-piControl-2deg.001"
REF_VALUES = [0.28, 200.0e-6]

ACCOUNT = "UMIN0005"
USER = environ["USER"]

TMP_DIR = f"/glade/scratch/{USER}"
HIST_DIR = f"{TMP_DIR}/archive"
LAPL_DIR = f"/glade/work/{USER}/laplacians"

RUN_SPECS_DIR = f"{dirname(__file__)}/run_specs"


for x in [HIST_DIR, LAPL_DIR]:
    makedirs(x, exist_ok=True)


def get_run_specs_info():
    i, basename = max((int(match.group(1)), x) for x in listdir(RUN_SPECS_DIR)
                      for match in [search(r"(^\d+).csv$", x)] if match)

    return i, f"{RUN_SPECS_DIR}/{basename}"


def read_run_specs(i=None):
    if i is None:
        i, run_specs_file = get_run_specs_info()
    else:
        run_specs_file = f"{RUN_SPECS_DIR}/{i:03d}.csv"

    run_specs = pd.read_csv(run_specs_file, header=[0, 1])
    run_specs.i = i

    return run_specs


def write_run_specs(run_specs):
    i, _ = get_run_specs_info()

    run_specs.to_csv(f"{RUN_SPECS_DIR}/{(i + 1):03d}.csv", index=False)
