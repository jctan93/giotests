#!/bin/bash

###############################################################################################
#
#   remove lpc_ich modules  , insert lpc_ich modules and check if the pci device is detected
#
###############################################################################################

modprobe lpc_ich
rmmod lpc_ich
   if [ $? == 0 ]
       then
               echo "Success remove lpc_ich module"
       else
               echo "Fail to remove lpc_ich module"
               exit 1
   fi

modprobe lpc_ich

   if [ $? == 0 ]
       then
              echo "Success to load lpc_ich module"
       else
              echo "Fail to load lpc_ich module"
              exit 1

   fi

lspci | grep -i 5ae8
   if [ $? == 0 ]

        then
              echo "lpc device detected"
              echo "==================="
              exit 0
        else
              echo "lpc device not detected"
              echo "======================="
              exit 1
   fi
