# -------------- modprobe ISH driver ----------------------------
#!/bin/bash

## check

sleep 1s

lspci | grep 5aa2 > /home/log_pci
pci_1= `cat /home/log_pci`
cat /home/log_pci

exp_string="5aa2"
	if [[ $exp_string == *"$pci_1"* ]]
	then
		echo "This is a device 5aa2"
        echo "pass"
	fi

sleep 1s

exit

