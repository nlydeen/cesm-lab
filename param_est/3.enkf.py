#!/usr/bin/env python
# $ module load python/3.7.9
# $ ncar_pylib

import numpy as np

from numpy.random import multivariate_normal as mv_normal
from os import listdir
from os.path import join
from rpy2.robjects import globalenv, numpy2ri, r as r_

from common import LAPL_DIR, REF_LAPL_FILE, read_run_specs, write_run_specs


# If true (false), use DelSole's (Iglesias') approach.
delsole = True


# TODO: Don't use `rpy2`, since it's not available on Cheyenne.
def update(fs_ref, fs_ens, thetas, r=0.5):
    if delsole:
        r_["source"]("enkf_delsole.R")

        numpy2ri.activate()

        thetas = globalenv["parameter.est.enkf"](
            fs_ref.T, fs_ens.swapaxes(0, 1), thetas)[2].T

        numpy2ri.deactivate()
    else:
        f_mean_ref = fs_ref.mean(axis=1)
        f_mean_ens = fs_ens.mean(axis=1)

        n_params = thetas.shape[1]
        n_lapls = f_mean_ref.shape[0]
        n_vars = n_params + n_lapls

        H = np.eye(n_lapls, n_vars, n_params)
        H_perp = np.eye(n_params, n_vars)
        I = np.eye(n_vars)

        R = r**2 * np.diag(fs_ref.var(axis=1))

        Z = np.concatenate([thetas, f_mean_ens.T], axis=1).T

        z_bar = Z.mean(axis=1)

        C = np.mean([np.outer(z, z) for z in Z.T], axis=0)
        C -= np.outer(z_bar, z_bar)

        K = C @ H.T @ np.linalg.inv(H @ C @ H.T + R)

        O = (f_mean_ref.reshape(-1, 1)
             + mv_normal(np.zeros(n_lapls), R, Z.shape[1]).T)

        Z = (I - K @ H) @ Z + K @ O

        thetas = Z.T @ H_perp.T

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
