#!/usr/bin/env python

import numpy as np

from glob import glob
from os import listdir
from os.path import exists
from xarray import DataArray, Dataset, open_dataarray, open_mfdataset

from common import ACCOUNT, HIST_DIR, LAPL_DIR, REF_CASE


def compute_laplacians(hist_files, case, fields=["SST"],
                       eofi=open_dataarray("lapl.eofi.nc")):
    lapl_file = f"{LAPL_DIR}/{case}.nc"

    if exists(lapl_file):
        return

    hist_files = sorted(hist_files)
    hist = open_mfdataset(hist_files).interp_like(eofi)

    lapls = {}

    for field in fields:
        lapls[field] = DataArray(np.einsum("ikl,jkl->ij", eofi, hist[field]),
                                 dims=["lapl", "time"])

    Dataset(lapls, coords={"lapl": np.arange(len(eofi)) + 1,
                           "time": hist.time},
            attrs={"source_files": hist_files}).to_netcdf(lapl_file)


if __name__ == "__main__":
    if (not exists(f"{LAPL_DIR}/{REF_CASE}.nc")
          and not exists("/glade/campaign")):
        print(f"ERROR: You must use Casper (`execcasper -A {ACCOUNT}`) to"
              " compute Laplacians for the reference case.")
        exit(1)
    else:
        hist_files = glob("/glade/campaign/collections/cmip/CMIP6"
                          f"/timeseries-cmip6/{REF_CASE}/atm/proc/tseries"
                          f"/month_1/{REF_CASE}.cam.h0.SST.*.nc")
        compute_laplacians(hist_files, REF_CASE)

    for case in sorted(listdir(HIST_DIR)):
        if case.startswith("param_est."):
            hist_files = glob(f"{HIST_DIR}/{case}/atm/hist/*.cam.h0.*.nc")
            compute_laplacians(hist_files, case)
