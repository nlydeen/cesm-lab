#!/bin/sh -e

case="b.e21.B1850.f19_g17.CMIP6-piControl-2deg.001"
tar_dir="/glade/campaign/collections/cmip/CMIP6/restarts/$case"
untar_dir="/glade/work/nlydeen/restarts/$case"

mkdir $untar_dir
cd $untar_dir

for file in $tar_dir/*.tar; do
    tar xvf $file
done

rm -rf $untar_dir/glade
