
IPPROOT=/opt/intel/ipp

if [ -f ./testsample_st ]; then
  rm ./testsample_st
fi

if [ -f ./testsample_dyn ]; then
  rm ./testsample_dyn
fi


echo "Static libraries test:"

gcc -o testsample_st -I $IPPROOT/include ./testsample.cpp  $IPPROOT/lib/intel64_lin/libipps.a $IPPROOT/lib/intel64_lin/libippvm.a $IPPROOT/lib/intel64_lin/libippcore.a -lm

if [ ! -f ./testsample_st ]; then
   echo "TEST FAILED"
else
   ./testsample_st
   rm ./testsample_st
fi

echo "Dynamic libraries test:"

gcc -o testsample_dyn -I $IPPROOT/include ./testsample.cpp  $IPPROOT/lib/intel64_lin/libipps.so $IPPROOT/lib/intel64_lin/libippvm.so $IPPROOT/lib/intel64_lin/libippcore.so -lm

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$IPPROOT/lib/intel64_lin/

if [ ! -f ./testsample_dyn ]; then
   echo "TEST FAILED"
else
   ./testsample_dyn
   rm ./testsample_dyn
fi


