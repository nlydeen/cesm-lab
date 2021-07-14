#!/usr/bin/env python3

# $ conda env create
# $ conda run -n param_est ./3.enkf.py

import numpy as np

from os import listdir
from os.path import join
from rpy2.robjects import globalenv, numpy2ri, r as r_

from common import LAPL_DIR, REF_LAPL_FILE, read_run_specs, write_run_specs


def update(fs_ref, fs_ens, thetas, r=0.5):
    fs_ref = fs_ref.T
    fs_ens = fs_ens.swapaxes(0, 1)

    r_["source"]("enkf_delsole.R")
    numpy2ri.activate()
    thetas = np.array(globalenv["parameter.est.enkf"](fs_ref, fs_ens, thetas)[2]).T
    numpy2ri.deactivate()

    return thetas


if __name__ == "__main__":
    run_specs = read_run_specs()

    fs_ref = np.load(REF_LAPL_FILE)
    fs_ens = np.dstack([np.load(join(LAPL_DIR, x))
                        for x in sorted(listdir(LAPL_DIR))
                        if x.startswith(f"param_est.{run_specs.iter:03d}.")])

    thetas = run_specs.theta.values
    thetas = update(fs_ref, fs_ens, thetas)

    run_specs.theta = thetas
    write_run_specs(run_specs)
