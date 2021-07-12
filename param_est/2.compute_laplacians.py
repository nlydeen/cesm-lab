#!/usr/bin/env python
# $ module load python/3.7.9
# $ ncar_pylib

import numpy as np

from glob import glob
from os import listdir
from os.path import exists, join
from xarray import open_dataarray, open_mfdataset

from common import REF_FILES, ARCHIVE_DIR, LAPL_DIR, REF_LAPL_FILE


lapl_eofi = open_dataarray("lapl.glo.eofi.nc")


def compute_laplacians(files):
    sst = open_mfdataset(files).SST.interp_like(lapl_eofi)

    return np.einsum("ikl,jkl->ij", lapl_eofi, sst)


if __name__ == "__main__":
    if not exists(REF_LAPL_FILE):
        np.save(REF_LAPL_FILE, compute_laplacians(REF_FILES))

    for case_name in filter(lambda x: x.startswith("param_est."),
                            listdir(ARCHIVE_DIR)):
        lapl_file = join(LAPL_DIR, f"{case_name}.npy")

        if not exists(lapl_file):
            files = sorted(glob(join(ARCHIVE_DIR, case_name, "atm/hist/*.nc")))
            np.save(lapl_file, compute_laplacians(files))
