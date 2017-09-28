# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

## check

sleep 1s

cd /dev
cat iio



lspci | grep 5aa2 > /iiotest/log_pci
pci_1= `cat /iiotest/log_pci`

exp_string="5aa2"
	if [[ $exp_string == *"$pci_1"* ]]
	then
		echo "This is a device 5aa2"
        echo "pass"
	fi

sleep 1s

exit

