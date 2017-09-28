#!/bin/sh
echo "Add smart channel to target platform"
smart channel -y --add all type=rpm-md baseurl=http://172.30.109.231/broxton/CURRENT/rpm/all/ 
smart channel -y --add corei7_64 type=rpm-md baseurl=http://172.30.109.231/broxton/CURRENT/rpm/corei7_64/ 
smart channel -y --add corei7_64_intel_common type=rpm-md baseurl=http://172.30.109.231/broxton/CURRENT/rpm/corei7_64_intel_common/ 
smart channel -y --add intel_corei7_64 type=rpm-md baseurl=http://172.30.109.231/broxton/CURRENT/rpm/intel_corei7_64/
smart channel -y --add lib32_corei7_32 type=rpm-md baseurl=http://172.30.109.231/broxton/CURRENT/rpm/lib32_corei7_32/
