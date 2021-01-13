#!/bin/sh
workdir=$(cd $(dirname $0); pwd)

#1.  ffmpeg
sudo apt install ffmpeg -y
sudo apt install graphviz -y
#2. create env
conda env create -f env.yaml
#3. build package of DAIN
cd ${workdir}/modules/thirdparty/VideoPhotoRepair/DAIN/my_package
cp build.sh build_tmp.sh
sed -i "s/pytorch1.0.0/VCtest/g" build_tmp.sh
output=`./build_tmp.sh`
rm build_tmp.sh
cd ../PWCNet/correlation_package_pytorch1_0
cp build.sh build_tmp.sh
sed -i "s/pytorch1.0.0/VCtest/g" build_tmp.sh
output=`./build_tmp.sh`
rm build_tmp.sh

