#!/usr/bin/env python

import numpy as np

from os import listdir
from rpy2.robjects import globalenv, numpy2ri, r
from xarray import open_dataset

from common import LAPL_DIR, REF_CASE, read_run_specs, write_run_specs


def read_laplacians(case):
    if not case.endswith(".nc"):
        case += ".nc"

    return open_dataset(f"{LAPL_DIR}/{case}").SST.data


def update(fs_ref, fs_ens, thetas):
    fs_ref = fs_ref.T
    fs_ens = fs_ens.swapaxes(0, 1)

    r["source"]("enkf_delsole.R")
    numpy2ri.activate()
    thetas = np.array(
        globalenv["parameter.est.enkf"](fs_ref, fs_ens, thetas)[2]).T
    numpy2ri.deactivate()

    return thetas


if __name__ == "__main__":
    run_specs = read_run_specs()

    fs_ref = read_laplacians(REF_CASE)
    fs_ens = np.dstack([
        read_laplacians(x) for x in sorted(listdir(LAPL_DIR))
        if x.startswith(f"param_est.{run_specs.i:03d}.")])

    run_specs.theta = update(fs_ref, fs_ens, run_specs.theta.values)

    write_run_specs(run_specs)
