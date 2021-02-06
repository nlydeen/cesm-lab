{ pkgs ? import (fetchTarball
  "https://github.com/nixos/nixpkgs/archive/nixpkgs-unstable.tar.gz") { } }:

# XXX: My NixOS configuration manages the `escomp/cesm-lab-2.2` image.
with pkgs;
let
  python = python3.withPackages (pyPkgs:
    with pyPkgs; [
      bokeh
      cartopy
      dask
      flake8
      joblib
      matplotlib
      netcdf4
      numpy
      pandas
      requests
      scikitlearn
      scipy
      tqdm
      xarray
    ]);
in mkShell { buildInputs = [ duperemove ncview netcdf python ]; }
