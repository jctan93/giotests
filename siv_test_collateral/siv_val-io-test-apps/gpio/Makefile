
KERNEL_SOURCE ?=
KDIR:=$(KERNEL_SOURCE)

//KDIR:=/home/nirav/bxt/bxt-io-kernel/nirav_test/iotg_broxton-nightly_build_41y_release



PWD:=$(shell pwd)

obj-m += GPIO_Interrupts_Kernel_Based.o GPIO_Concurrent_Access.o
 

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
