import pandas as pd

from glob import glob
from os import environ, listdir, makedirs
from os.path import dirname, join
from re import search


__all__ = ["REF_NAME", "REF_FILES", "SCRATCH_DIR", "ARCHIVE_DIR", "LAPL_DIR",
           "REF_LAPL_FILE", "read_run_specs", "write_run_specs"]


REF_NAME = "b.e21.B1850.f19_g17.CMIP6-piControl-2deg.001"
REF_FILES = sorted(glob(join(
    "/glade/campaign/collections/cmip/CMIP6/timeseries-cmip6", REF_NAME,
    "atm/proc/tseries/month_1", f"{REF_NAME}.cam.h0.SST.*.nc")))

USER = environ["USER"]

SCRATCH_DIR = join("/glade/scratch", USER)
ARCHIVE_DIR = join(SCRATCH_DIR, "archive")
RUN_SPECS_DIR = join(dirname(__file__), "run_specs")

LAPL_DIR = join("/glade/work", USER, "laplacians")
REF_LAPL_FILE = join(LAPL_DIR, f"{REF_NAME}.npy")

for x in [ARCHIVE_DIR, LAPL_DIR, RUN_SPECS_DIR]:
    makedirs(x, exist_ok=True)


def _get_run_specs_info():
    return max([(int(match.group(1)), x) for x in listdir(RUN_SPECS_DIR)
                for match in [search(r"(^\d+).csv$", x)] if match])


def read_run_specs():
    i, run_specs_file = _get_run_specs_info()

    run_specs_file = join(RUN_SPECS_DIR, run_specs_file)

    run_specs = pd.read_csv(run_specs_file, header=[0, 1])
    run_specs.iter = i

    return run_specs


def write_run_specs(run_specs):
    i = _get_run_specs_info()[0] + 1

    run_specs.to_csv(join(RUN_SPECS_DIR, f"{i:03d}.csv"), index=False)
