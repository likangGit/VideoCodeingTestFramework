#!/bin/sh
workdir=$(cd $(dirname $0); pwd)

#1. create env
conda env create -f env.yaml
#2. build package of DAIN
cd ${workdir}/module/3rdparty/VideoPhotoRepair/DAIN/my_package
cp build.sh build_tmp.sh
sed -i "s/pytorch1.0.0/VideoCodingTest/g" build_tmp.sh
output=`./build_tmp.sh`
rm build_tmp.sh
cd ../PWCNet/correlation_package_pytorch1_0
cp build.sh build_tmp.sh
sed -i "s/pytorch1.0.0/VideoCodingTest/g" build_tmp.sh
output=`./build_tmp.sh`
rm build_tmp.sh

