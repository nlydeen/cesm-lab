#!/usr/bin/env python

import numpy as np

from glob import glob
from os import listdir
from os.path import exists
from sys import stderr
from tqdm import tqdm
from xarray import DataArray, Dataset, open_dataarray, open_mfdataset

from common import ACCOUNT, HIST_DIR, LAPL_DIR, REF_CASE


def compute_laplacians(case=REF_CASE, field_names=["LWCF", "SST"],
                       eofi=open_dataarray("lapl.eofi.nc")):
    lapl_file = f"{LAPL_DIR}/{case}.nc"

    if exists(lapl_file):
        return

    lapls = {}

    if case != REF_CASE:
        hist_files = glob(f"{HIST_DIR}/{case}/atm/hist/*.cam.h0.*.nc")

        hist_files = sorted(hist_files)
        hist = open_mfdataset(hist_files).interp_like(eofi)

    for field_name in field_names:
        if case == REF_CASE:
            hist_files = glob("/glade/campaign/collections/cmip/CMIP6"
                              f"/timeseries-cmip6/{REF_CASE}/atm/proc/tseries"
                              f"/month_1/{REF_CASE}.cam.h0.{field_name}.*.nc")
            hist = open_mfdataset(hist_files).interp_like(eofi)

        field = hist[field_name]

        lapls[field_name] = DataArray(np.einsum("ikl,jkl->ij", eofi, field),
                                      dims=["lapl", "time"])
        lapls[field_name].attrs.update(field.attrs)

    Dataset(lapls, coords={"lapl": np.arange(len(eofi)) + 1,
                           "time": hist.time}).to_netcdf(lapl_file)


if __name__ == "__main__":
    if (not exists(f"{LAPL_DIR}/{REF_CASE}.nc")
          and not exists("/glade/campaign")):
        print(f"ERROR: You must use Casper (`execcasper -A {ACCOUNT}`) to"
              " compute Laplacians for the reference case.")
        exit(1)
    else:
        compute_laplacians()

    cases = sorted(x for x in listdir(HIST_DIR) if x.startswith("param_est."))

    for case in tqdm(cases, bar_format="|{bar}|{percentage:3.0f}%|",
                     ascii="-#", mininterval=0, leave=False):
        print(f"{HIST_DIR}/{case}")
        print("\033[2A", end="", file=stderr)

        compute_laplacians(case)
