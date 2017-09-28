/*
 * Sample program for CAN on Intel(R) Platform Controller Hub EG20T.
 *
 * Copyright (C) 2011 OKI SEMICONDUCTOR Co., LTD.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307, USA.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include "pch_can_sample.h"

/* Constants used */
#define PCH_SUCCESS		(0)
#define PCH_ERROR		(1)

#define STANDARD_FRAME 		(0)
#define EXTENDED_FRAME 		(1)

#define PCH_CAN_BAUD_10		"10000"
#define PCH_CAN_BAUD_20		"20000"
#define PCH_CAN_BAUD_50		"50000"
#define PCH_CAN_BAUD_125	"125000"
#define PCH_CAN_BAUD_250	"250000"
#define PCH_CAN_BAUD_500	"500000"
#define PCH_CAN_BAUD_800	"800000"
#define PCH_CAN_BAUD_1000	"1000000"

#define PCH_CAN_MSG_DATA_LEN	(8)		/* CAN Msg data length */

#define PCH_CAN_LOOP	0
#define PCH_CAN_SEND	1

struct pch_can_msg {
	unsigned short ide;			/* Standard/extended msg    */
	unsigned int id;			/* 11 or 29 bit msg id      */
	unsigned short dlc;			/* Size of data             */
	unsigned char data[PCH_CAN_MSG_DATA_LEN];	/* Message pay load */
	unsigned short rtr;			/* RTR message              */
};


void pch_can_print_frame_data(struct pch_can_msg *frame)
{
        int data;

        if ( frame->ide == 1)
                printf("  Frame is Extended frame\n");
        if ( frame->ide == 0)
                printf("  Frame is Standard frame\n");

        printf("  ID  : %x\n",frame->id);
        printf("  DLC : %d\n",frame->dlc);
        printf("  Data: ");
        for (data = 0; data < frame->dlc; data++ )
                printf("%x  ",frame->data[data]);
        printf("\n");

        if (frame->rtr == 1)
		printf("  Frame type: Remote frame\n");
}

ssize_t pch_can_write(int fd, const struct pch_can_msg *pch_can_dat)
{
	int writebyte;
	struct can_frame can_frame_dat;

	can_frame_dat.can_id = pch_can_dat->id;
	if(pch_can_dat->ide)
		can_frame_dat.can_id |= 0x80000000;		

	if(pch_can_dat->rtr)
		can_frame_dat.can_id |= 0x40000000;		

	can_frame_dat.can_dlc = pch_can_dat->dlc;
	memcpy(can_frame_dat.data, pch_can_dat->data, PCH_CAN_MSG_DATA_LEN);

	writebyte = write(fd, &can_frame_dat, sizeof(can_frame_dat));

	return writebyte;
}

ssize_t pch_can_read(int fd, struct pch_can_msg *pch_can_dat)
{
	struct can_frame can_frame_dat;
	int readbyte;

	readbyte = read(fd, &can_frame_dat, sizeof(can_frame_dat));
	if(can_frame_dat.can_id & 0x80000000){
		pch_can_dat->ide = 1;
		pch_can_dat->id  = can_frame_dat.can_id & 0x1fffffff;
	} else {
		pch_can_dat->ide = 0;
		pch_can_dat->id  = can_frame_dat.can_id & 0x0000ffff;
	}

	pch_can_dat->dlc = can_frame_dat.can_dlc;

	if(can_frame_dat.can_id & 0x40000000)
		pch_can_dat->rtr = 1;
	else
		pch_can_dat->rtr = 0;		

	memcpy(pch_can_dat->data, can_frame_dat.data, PCH_CAN_MSG_DATA_LEN);

	return readbyte;
}

unsigned int pch_can_stnd_frame_send(unsigned int can_fd, unsigned char value, int frame_type)
{
    int ret;
    unsigned int data;
    struct pch_can_msg read_over_signal;
	unsigned int re_xmit_cnt=0;
	struct pch_can_msg msg_frame;

	memset(&msg_frame ,0 ,sizeof(struct pch_can_msg) );
	
	if (frame_type){
		msg_frame.ide = EXTENDED_FRAME;
		msg_frame.id = 0x7FF; /* Not sure if this is correct*/
		}
	else
		{
		msg_frame.ide = STANDARD_FRAME;
		msg_frame.id = 0x7FF;
		}
		
	msg_frame.dlc = PCH_CAN_MSG_DATA_LEN;
	
	for ( data = 0;data < msg_frame.dlc; data++ ) {
		msg_frame.data[data] = value + data;
	}
	
	msg_frame.rtr = 0;

AGAIN:
	ret = pch_can_write(can_fd, &msg_frame);
	if (ret <= 0) {
		usleep(500);
		re_xmit_cnt++;
		goto AGAIN;
	} else {
		printf("=============== Send Frame data ===============\n");
		pch_can_print_frame_data(&msg_frame);
		printf(	"==============================================\n");
	}
	ret = PCH_SUCCESS;

        if (ret) {
                return PCH_ERROR;
        }
	printf("Wait over signal");
	ret = pch_can_read(can_fd, &read_over_signal);
        if (ret <= 0) {
                printf("ERROR: Failed to receive read over signal\n");
                return PCH_ERROR;
        }
        printf("  --->  received\n\n");
        return PCH_SUCCESS;
}

unsigned int pch_can_stnd_frame_recv(unsigned int can_fd)
{
        int ret;
        struct pch_can_msg read_over_signal = {0,1,0,{0},0};

        for (;;) {
                struct pch_can_msg rmessage;
                memset(&rmessage, 0, sizeof(struct pch_can_msg));
                ret = pch_can_read(can_fd, &rmessage);
                if (ret <= 0) {
                        printf("ERROR: Unable to read the message\n");
                        ret = PCH_ERROR;
                        break;
                } else {
                        printf("SUCCESS: %d bytes of data has been recieved(0x%x)\n",
				ret, rmessage.id);

			printf("=============== Read Frame data ===============\n");
			pch_can_print_frame_data(&rmessage);
			printf(	"==============================================\n");
		        ret = pch_can_write(can_fd, &read_over_signal);
                }
                /****Adjusting the DLC value ****/
                ret = PCH_SUCCESS;
        }
        if (ret)
                return PCH_ERROR;
        return PCH_SUCCESS;
}



int main(int argc, char *argv[])
{
	int fd;
	int ret_val;
	int s,rtn;
	struct sockaddr_can addr; 
	struct ifreq ifr; 
	int mode;
	unsigned char value;
	int frame_type = -1;
	int baud_rate_param = -1;
	
	printf("\n----------------------------------------------------------------------------------\n");
	
	/* Check for loop/receive setting */
	if ((argc == 5) && !strcmp(argv[4], "-loop")) 
		{
		mode = PCH_CAN_LOOP;
		baud_rate_param = atoi(argv[2]); /* get baud rate parameter */
		printf("Port set to loop. ");
		} 
	
	else if ((argc == 6) && !strcmp(argv[4], "-send")) 
		{
		mode = PCH_CAN_SEND;
		value = strtol(argv[5], NULL, 16); /* get data parameter */
		baud_rate_param = atoi(argv[2]); /* get baud rate parameter */
		printf("Port set to transmit. ");
		} 
		
	else {
		printf( "\n"
			"Usage: %s device speed frame [-send [value] | -loop]\n"
			" device         Specify the CAN device. eg: can0.\n"
			" speed          Specify the CAN Baud Rate.\n"
			"                (10000,20000,50000,125000,250000,500000,800000,1000000)\n"
			" frame          Specify the CAN Data Frame.\n"
			"                -std (Standard Frame) -ext (Extended Frame)\n"
			" -send [value]  Transmit data, and receive. \n"
			"                Specify the initial value of the transmit data (value=00-FF).\n"
			" -loop          Operate as loop back program. \n"
			"\n", argv[0]);
			
		printf("\n----------------------------------------------------------------------------------\n");
		return PCH_ERROR;
		}
		
	/* Check for loop/receive setting */
	switch (baud_rate_param) {
	case 10000:
		printf("Baud Rate: 10000. ");
		break;
	case 20000:
		printf("Baud Rate: 20000. ");
		break;
	case 50000:
		printf("Baud Rate: 50000. ");
		break;		
	case 125000:
		printf("Baud Rate: 125000. ");
		break;
	case 250000:
		printf("Baud Rate: 250000. ");
		break;		
	case 500000:
		printf("Baud Rate: 500000. ");
		break;	
	case 800000:
		printf("Baud Rate: 800000. ");
		break;		
	case 1000000:
		printf("Baud Rate: 1000000. ");
		break;
	default:
		printf("ERROR: Invalid Baud Rate %s \n", argv[1]);
		close(fd);
		return PCH_ERROR;
		break;	
	}	
	
	system("ifconfig can0 down");
	printf("\nCommand: ifconfig can0 down");
		
	char str[256], buf[256];
	sprintf(buf, "ip link set %s type can bitrate %s", argv[1], argv[2]);
	system(buf);
	printf("\nCommand: ip link set %s type can bitrate %s", argv[1], argv[2]);
	
	system("ifconfig can0 up");
	printf("\nCommand: ifconfig can0 up");
	
	
	printf("\n----------------------------------------------------------------------------------\n");
	
	s = socket(PF_CAN, SOCK_RAW, CAN_RAW);

	strcpy(ifr.ifr_ifrn.ifrn_name, argv[1] ); 
	rtn = ioctl(s, SIOCGIFINDEX, &ifr); 

	addr.can_family = AF_CAN; 
	addr.can_ifindex = ifr.ifr_ifru.ifru_ivalue; 
	rtn = bind(s, (struct sockaddr *)&addr, sizeof(addr)); 

	fd = s;
	if (fd < 0) {
		printf("ERROR :Unable to open the CAN device\n");
        return PCH_ERROR;
	}
	
	/* Check for mode setting */
	if (mode==PCH_CAN_SEND)
		{
		printf(	"===============================================\n");
		
		if (!strcmp(argv[3], "-std")){
			printf( "Transmission of a Standard frame at %s bps \n", argv[2]);
			frame_type = 0;
			pch_can_stnd_frame_send(fd, value, frame_type);
			}
		
		else if (!strcmp(argv[3], "-ext")){
			printf( "Transmission of a Extended frame at %s bps \n", argv[2]);
			frame_type = 1;
			pch_can_stnd_frame_send(fd, value, frame_type);
			}
		
		else{
			printf( "Invalid Transmission Frame Parameter \n");
			close(fd);
			}		
		printf( "===============================================\n");
		
		}
	
	else if (mode==PCH_CAN_LOOP)
		{
		printf(	"===============================================\n");
		
		if (!strcmp(argv[3], "-std")){
			printf( "Reception of a Standard frame at %s bps \n", argv[2]);
			pch_can_stnd_frame_recv(fd);
			}
		
		else if (!strcmp(argv[3], "-ext")){
			printf( "Reception of a Extended frame at %s bps \n", argv[2]);
			pch_can_stnd_frame_recv(fd);
			}
		
		else{
			printf( "Invalid Transmission Frame Parameter \n");
			close(fd);
			}
		printf( "===============================================\n");
		
		}

	   
	close(fd);
    return ret_val;
}

/*

static int __pch_can_set_bitrate(char *speed)
{
	char *ip_bitrate_10000[9] = {"","link","set","can0","type", "can", "bitrate", speed, NULL};
	int pid = fork();
	int status;
	int i;

	if ( pid == -1 ){
		return -1;
	} else {
		if (pid == 0) {
			execv("ip", ip_bitrate_10000);
			return 0;
		} else {
			waitpid(pid, &status, 0);
		}
	}
	printf("  ip");
	for (i = 0; i < 8; i++)
		printf("%s ", ip_bitrate_10000[i]);
	printf("\n");

	return 0;
}
int pch_can_set_bitrate(char *speed){
	int rtn;
	printf("\nbitrate setting(->%s)\n", speed);

	rtn = pch_can_ifconfig("down");
	
	if(rtn)
		{
		printf("ifconfig down error\n");
		}
		
	__pch_can_set_bitrate(speed);
	rtn = pch_can_ifconfig("up");
	
	if(rtn)
		printf("ifconfig  up error\n");

	return 0;
}

int pch_can_ifconfig(char *ope)
{
	char *env[4] = {"", "can0", ope, NULL};
	int pid = fork();
	int status;
	int i;

	if (pid == -1) {
		return -1;
	} else {
		if (pid == 0) {
			execv("ifconfig", env);
			return 0;
		} else {
			waitpid(pid, &status, 0);
		}
	}
	printf("  ifconfig");
	for (i = 0; i < 3; i++)
		printf("%s ", env[i]);
	printf("\n");
	return 0;
	
	}
*/



