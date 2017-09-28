/*
 * Based on the
 * Raspberry Pi's gpio-irq-demo.c.
 *
 * Copyright (C) Mrkva.
 *
 * This program is for Intel Internal Use Only. 
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
 *
 * Original Source: http://www.raspberrypi.org/phpBB3/viewtopic.php?f=44&t=7509#p92074
 *
 */

#include <stdio.h>
#include <poll.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>

#define GPIO_FN_MAXLEN		32
#define POLL_TIMEOUT		1000
#define RDBUF_LEN			5
#define ERROR				1
#define SUCCESS				0
#define PRIORITY			0

int main(int argc,char *argv[]){
	char fn[GPIO_FN_MAXLEN];
	int device, ret;
	struct pollfd pdevice;
	char rdbuf[RDBUF_LEN];

	memset(rdbuf, 0x00, RDBUF_LEN);
	memset(fn, 0x00, GPIO_FN_MAXLEN);

	if(argc!=2) {
		printf(	"Usage: %s GPIO_Number \n"
				"Note: 	You must export your GPIO pin and set the interrupt edge\n"
				"		manually before using this app.\n",
			   argv[0]);
		goto FAIL_EXIT;
	}
	
	//GPIO device Check and Open
	snprintf(fn, GPIO_FN_MAXLEN-1, "/sys/class/gpio/gpio%s/value", argv[1]);
	device = open(fn, O_RDONLY);
	if(device < 0){
		printf("FAILED: Unable to access GPIO pin.\n");
		goto FAIL_EXIT;
	}
	
	//Initializing Interrupt Polling
	pdevice.fd = device;
	pdevice.events = POLLPRI;	
	ret=read(device, rdbuf, RDBUF_LEN-1);
	if(ret < 0) {
		printf("FAILED: Unable to access GPIO pin.\n");
		goto FAIL_EXIT;
	}


	/* Currently Linux Userspace uses Interrupts Polling Method
	 * to execute "Interrupts Service Routine". The Poll waits for
	 * interrupt activity to occurs, which then executes  ISR. 
	 * Otherwise, the main function will be triggered. 
	 */
	while(1) {
		memset(rdbuf, 0x00, RDBUF_LEN);
		lseek(device, 0, SEEK_SET);
		ret=poll(&pdevice, 1, POLL_TIMEOUT);

		printf("Main Loop is Executed.\n");
		printf("Performs Main Threads. \n");

		if(ret < 0) {
			printf("ERROR: Interrupts polling error. \n");
			close(device);
			goto FAIL_EXIT;
		}
		
		if(ret > PRIORITY) {		
			printf("Interrupts Service Routine Executed. \n");
			ret=read(device, rdbuf, RDBUF_LEN-1);
			if(ret<0) {
				printf("ERROR: Fails to read GPIO current Value.\n");
			goto FAIL_EXIT;
			}
			printf("ISR: GPIO read value is: %s\n", rdbuf);

		}
	}
	close(device);
	return SUCCESS;
	
FAIL_EXIT:
	close(device);
	return ERROR;
}
