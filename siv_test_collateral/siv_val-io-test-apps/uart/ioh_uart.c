/*This source is 
 *
 * NOT FOR EXTERNAL RELEASE
 *
 * Original source is found in archived directory.
 *Source was provided by OKI/ROHM for Co-Validation
 *and shall not be publicly released.
 */
#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#include "ioh_uart.h"
#include "crc8.c"

#define UART_SEND	0
#define UART_RECV	1

#define UART_DATA_AA	0
#define UART_DATA_XX	1
#define UART_DATA_RAND	2

#define FILL		1
#define DIRECT_SEND	0
#define GET		0
#define SET		1

#define RAND_DEV	"/dev/urandom"
#define END_SIGNAL	0x0F

#define RD_TIMEOUT	300 /* 30 seconds read timeout */

/*Global variables*/
int baud_global = 1200;
int uart_es(int mode, int value);

int main(int argc, char *argv[])
{
	int fd,ret_val = 0;
	int baud_rate_param = 1200;
	int data_bit_param = 8;
	int stop_bit_param = 1;
	int transfer_mode;
	int transfer_data_mode; 
	int transfer_size = 1;
	int single_flow = 0;
	int silent_mode = 0;
	user_UART_config_t user_config;
	int n;

	long BAUD = 1200; 		/* Holds the baud_rate value*/
	long DATABITS = 0;		/* Holds number of databits*/
	long STOPBITS = 0;		/* Number of stop bits */
	long PARITYON = 0;		/* Parity enabled or not */
	long PARITY = 0;		/* Parity bits */
	int flow_control = 0;
	struct termios newtio;  /*Place for old and new port settings for serial port*/

	if(argc < 3) {
		printf(	"\n"
			"Usage: %s device mode [[baud_rate] [data_bit] [parity] [stop_bit] [flow_control] [size]] [single_flow] [silent] [end_char]\n"
			" device       Specify the UART device (/dev/ttyx) x=PCH0,PCH1,PCH2,S0.\n"
			" mode         Specify the mode        (-tx,-rx, -txaa, -rxaa, -txr, -rxr) \n"
			"\n --------------------------------Optional Parameters--------------------------------\n"
			" baud_rate    Specify the baud_rate   (300,1200,2400,4800,9600,19200,38400,57600,\n"
			"                                       115200,230400,460800,921600,1000000,2000000,\n"
            		"                                       3000000, 4000000).\n"
			" data_bit     Specify the data bit    (5,6,7,8).\n"
			" parity       Specify the parity      (O,E,N,M,S).\n"
			"                                       O(Odd), E(Even), N(None), M(Mark), S(Space)\n" 
			" stop_bit     Specify the stop bit    (1,15,2).\n"
			"                                       1(1 Stop bit), 15(1.5 Stop bit), 2(2 Stop bit)\n"
			" flow_control Specify the flow control(S,H,N).\n"
			"                                       S(Software), H(Hardware), N(None)\n"
			" size         Specify the data size   (1,x), x = Iterations(1 to 1000000) \n"
			"                                       1(5KB Single Packet), x(1KB x Iterations).\n"
                        " single_flow  Specify if its single   o or O for Single Flow, n for normal dual flow\n"
                        "              flow \n"
                        " silent       Specify for silent mode s or S for Silent Mode, n for normal prints\n"
                        " end_char     Specify to turn on      c or C for end character, n for none\n"
                        "              end character transmit \n"
			" -------------------------------------------------------------------------------------\n"
			"     When the [[..] [..] [..] [..] [..]] parameters are not specified.\n"
			"     Default baud_rate = 9600, data_bit=8, parity=N, stop_bit=1, flow_control=N, size=1"
			"\n", argv[0]);
		return IOH_TEST_ERROR;
	}
	else if(argc <= 12) {
		/* Open the terminal port for UART */
		fd = open(argv[1], O_RDWR | O_NOCTTY | O_SYNC | O_NDELAY);
		n = fcntl(fd, F_GETFL, 0);
		fcntl(fd, F_SETFL, n & ~O_NDELAY);
		sleep(1);

		printf("\n----------------------------------------------------------------------------------\n");
		/* Check if device open correctly */
		if (fd < 0) {
		    	printf("ERROR: Unable to open the port %s \n", argv[1]);
            		close(fd);
			return IOH_TEST_ERROR;
		} 
		else {
			printf("UART Port %s opened. ", argv[1]);
		}
		
		/* Check for mode setting */
		if (!strcmp(argv[2], "-tx")) {
			transfer_mode = UART_SEND;
			transfer_data_mode = UART_DATA_XX;			
 			printf("Port set to transmit. Normal Data.");
		}
		else if (!strcmp(argv[2], "-rx")) {
			transfer_mode = UART_RECV;
			transfer_data_mode = UART_DATA_XX;
			printf("Port set to receive. Normal Data.");
		}
		else if (!strcmp(argv[2], "-txaa")) {
			transfer_mode = UART_SEND;
			transfer_data_mode = UART_DATA_AA;
			printf("Port set to transmit 0xAA data. For Clock Checking using Scope.");
		}
		else if (!strcmp(argv[2], "-rxaa")) {
			transfer_mode = UART_RECV;
			transfer_data_mode = UART_DATA_AA;
			printf("Port set to receive 0xAA data. For Clock Checking using Scope.");
		}
		else if (!strcmp(argv[2], "-txr")) {
			transfer_mode = UART_SEND;
			transfer_data_mode = UART_DATA_RAND;
			printf("Port set to transmit random data.");
		}
		else if (!strcmp(argv[2], "-rxr")) {
			transfer_mode = UART_RECV;
			transfer_data_mode = UART_DATA_RAND;
			printf("Port set to receive random data.");
		}
		else {
			printf("ERROR: Invalid Transfer Mode\n");
			close(fd);
			return IOH_TEST_ERROR;
		}
		
		/* Check and set baud rate */
		if (argc >= 4) {
			baud_rate_param = atoi(argv[3]);
			baud_global = baud_rate_param;            
		}

		switch (baud_rate_param) {

		case 50:
			user_config.baud_rate = BAUD_RATE_50;
			printf("Baud Rate: 50. ");
			break;
		case 300:
			user_config.baud_rate = BAUD_RATE_300;
			printf("Baud Rate: 300. ");
			break;
		case 600:
			user_config.baud_rate = BAUD_RATE_600;
			printf("Baud Rate: 600. ");
			break;
		case 1200:
			user_config.baud_rate = BAUD_RATE_1200;
			printf("Baud Rate: 1200. ");
			break;
		case 2400:
			user_config.baud_rate = BAUD_RATE_2400;
			printf("Baud Rate: 2400. ");
			break;
		case 4800: 
			user_config.baud_rate = BAUD_RATE_4800;
			printf("Baud Rate: 4800. ");
			break;
		case 9600: 
			user_config.baud_rate = BAUD_RATE_9600;
			printf("Baud Rate: 9600. ");
			break;
		case 19200:
			user_config.baud_rate = BAUD_RATE_19200;
			printf("Baud Rate: 19200. ");
			break;
		case 38400:
			user_config.baud_rate = BAUD_RATE_38400;
			printf("Baud Rate: 38400. ");
			break;
		case 57600:
			user_config.baud_rate = BAUD_RATE_57600;
			printf("Baud Rate: 57600. ");
			break;
		case 115200:
			user_config.baud_rate = BAUD_RATE_115200;
			printf("Baud Rate: 115200. ");
			break;
		case 230400:
			user_config.baud_rate = BAUD_RATE_230400;
			printf("Baud Rate: 230400. ");
			break;
		case 460800:		
			user_config.baud_rate = BAUD_RATE_460800;
			printf("Baud Rate is: 460800. ");
			break;
		case 921600:
			user_config.baud_rate = BAUD_RATE_921600;
			printf("Baud Rate: 921600. ");
			break;
		case 1000000:
			user_config.baud_rate = BAUD_RATE_1000000;
			printf("Baud Rate: 1000000. ");
			break;
		case 2000000:
			user_config.baud_rate = BAUD_RATE_2000000;
			printf("Baud Rate: 2000000. ");
			break;
		case 3000000:
			user_config.baud_rate = BAUD_RATE_3000000;
			printf("Baud Rate: 3000000. ");
			break;
		case 4000000:
			user_config.baud_rate = BAUD_RATE_4000000;
			printf("Baud Rate: 4000000. ");
			break;
		default:
            		printf("ERROR: Invalid Baud Rate %s \n", argv[3]);
			close(fd);
			break;
		}
		
		printf("\n");
		/* Check and set data bits */
		if (argc >= 5) {
			data_bit_param = atoi(argv[4]);
		}

		switch (data_bit_param) {
		case 5:
			user_config.Databits = DATABITS_SIZE_5;
			user_config.mask = 0x1F;
			printf("Data Bits: 5. ");
			break;
		case 6:
			user_config.Databits = DATABITS_SIZE_6;
			user_config.mask = 0x3F;
			printf("Data Bits: 6. ");
			break;
		case 7:
			user_config.Databits = DATABITS_SIZE_7;
			user_config.mask = 0x7F;
			printf("Data Bits: 7. ");
			break;
		case 8:
			user_config.Databits = DATABITS_SIZE_8;
			user_config.mask = 0xFF;
			printf("Data Bits: 8. ");
			break;
		default:
			printf("ERROR: Invalid Data Bit %s \n", argv[4]);
			close(fd);
			break;
		}
		
		/* Check and set parity */
		if (argc >= 6 && !strcmp(argv[5], "O")) {
			user_config.parity_stat = PARITY_ON;
			user_config.parity_bits = PARITY_ODD;
			printf("Parity: Odd. ");
		}
		else if (argc >= 6 && !strcmp(argv[5], "E")) {
			user_config.parity_stat = PARITY_ON;
			user_config.parity_bits = PARITY_EVEN;
			printf("Parity: Even. ");
		}
		else if (argc >= 6 && !strcmp(argv[5], "N")) {
			user_config.parity_stat = PARITY_OFF;
			user_config.parity_bits = PARITY_OFF;
			printf("Parity: None. ");
		}
		else if (argc >= 6 && !strcmp(argv[5], "M")) {
			user_config.parity_stat = PARITY_ON;
			user_config.parity_bits = PARITY_MARK;
			printf("Parity: Mark. ");
		}
		else if (argc >= 6 && !strcmp(argv[5], "S")) {
			user_config.parity_stat = PARITY_ON;
			user_config.parity_bits = PARITY_SPACE;
			printf("Parity: Space. ");
		}
		else if (argc < 6 ) {
			user_config.parity_stat = PARITY_OFF;
			user_config.parity_bits = PARITY_OFF;
			printf("Parity: None. ");
		}
		else {
			printf("ERROR: Invalid Parity Parameter %s \n", argv[5]);
			close(fd);
		}
			
		/* Check and set stop bits */
		if (argc >= 7) {
			stop_bit_param = atoi(argv[6]);
		}

		switch (stop_bit_param) {
		case 1:
			user_config.stopbits = STOPBITS_1;
			printf("Stop Bits: 1. ");
			break;
		case 15:
			user_config.stopbits = STOPBITS_1_5;
			printf("Stop Bits: 1.5. ");
			break;
		case 2:
			user_config.stopbits = STOPBITS_2;
			printf("Stop Bits: 2. ");
			break;
		default:
			printf("ERROR: Invalid Stop Bits %s \n", argv[6]);
			close(fd);
			break;
		}
		
		/* Check and set flow control */
		if (argc >= 8 && !strcmp(argv[7], "S")) {
			user_config.flow_control = SFTWRE_FLOW_CONTROL;
			printf("Flow Control: Software. ");
		}
		else if (argc >= 8 && !strcmp(argv[7], "H")) {	
			user_config.flow_control = HRDWRE_FLOW_CONTROL;
			printf("Flow Control: Hardware. ");
		}
		else if (argc >= 8 && !strcmp(argv[7], "N")) {
			user_config.flow_control = NO_FLOW_CONTROL;
			printf("Flow Control: None. ");
		}
		else if (argc < 8 ) {
			user_config.flow_control = NO_FLOW_CONTROL;
			printf("Flow Control: None. ");
		}
		else {
			printf("ERROR: Invalid Flow Control Parameter %s \n", argv[7]);
			close(fd);
		}

		/* Check and set transfer size */
		if (argc >= 9 && (atoi(argv[8]) != 1) )	{
			transfer_size = atoi(argv[8]);
			printf("Iteration: %d x 1KB.", transfer_size);
		}
		else {
			printf("Iteration: %d x 1KB. ", transfer_size);
		}

		printf("\n");
		if(argc >= 10 && (argv[9][0] == 'o' || argv[9][0] == 'O')) {
			printf("Single flow data transfer.\n");
			single_flow = 1;
		}
			
		if(argc >= 11 && (argv[10][0] == 's' || argv[10][0] == 'S')) {
			printf("Silent Mode\n");
			silent_mode = 1;
		}

		if(argc >= 12 && (argv[11][0] == 'c')) {
			printf("Function UART_send and UART_receive will have END signal notifier.\n");
			uart_es(SET, 1);
		}

		/* set uart settings based on the arguments given */
		BAUD = user_config.baud_rate;
		DATABITS = user_config.Databits;
		STOPBITS = user_config.stopbits;
		PARITYON = user_config.parity_stat;
		PARITY = user_config.parity_bits;
		flow_control = user_config.flow_control;
		/* Set new port settings for canonical input processing */
		newtio.c_cflag = (BAUD | DATABITS | STOPBITS | PARITYON | PARITY | CLOCAL | CREAD);
		if (flow_control ==  HRDWRE_FLOW_CONTROL) {
			newtio.c_cflag |= CRTSCTS;
		}
		if (flow_control == SFTWRE_FLOW_CONTROL) {
			newtio.c_iflag = INPCK | IXOFF;
		} else {
			newtio.c_iflag = INPCK;
		}
		/* To set the new port configuration values */
		newtio.c_oflag = 0;
		newtio.c_lflag = 0;
		newtio.c_cc[VMIN]=1;
		newtio.c_cc[VTIME]=0;
		tcflush(fd, TCIFLUSH);

		if (tcsetattr(fd,TCSANOW,&newtio) < 0) {
			printf("ERROR: Failed to set the port attributes for receving\n");
			return IOH_TEST_ERROR;
		} else {
			printf("SUCCESS: Port settings done according to user configuration for receiving\n");
		}

		printf("\n----------------------------------------------------------------------------------\n\n");	

		/* Actual Send Receive - Call Subroutines */
		if (transfer_mode == UART_SEND)	{
			if (transfer_size == 1) {
				user_config.data_size = SIZE_1KB;
				ret_val = Packet_transfer(fd,&user_config,transfer_data_mode, single_flow, silent_mode);
			}
			else if (transfer_size > 1 && transfer_size <=1000000 ) {
				user_config.data_size = SIZE_1KB;
				ret_val = Continous_transfer(fd,&user_config,transfer_size,transfer_data_mode, single_flow, silent_mode);
			}
			else {
				printf("ERROR: Invalid Iterations %s \n", argv[8]);
				close(fd);
				return IOH_TEST_ERROR;
			}
		}
		else if (transfer_mode == UART_RECV) {
			if (transfer_size == 1) {			
				user_config.data_size = SIZE_1KB;
				ret_val = Packet_receive(fd,&user_config,transfer_data_mode, single_flow, silent_mode);
			}
			else if (transfer_size > 1 && transfer_size <=1000000 ) {
				user_config.data_size = SIZE_1KB;
				ret_val = Continous_receive(fd,&user_config,transfer_size,transfer_data_mode, single_flow, silent_mode);
			}
			else {
				printf("ERROR: Invalid Iterations %s \n", argv[8]);
				close(fd);
				return IOH_TEST_ERROR;
			}
		}
		else {
			printf("ERROR: Invalid Transfer Mode %s \n", argv[2]);
			close(fd);
			return IOH_TEST_ERROR;
		}
		printf("IOH_UART END!!\n");
	}	
	else {
            printf(	"\n"
			"Usage: %s device mode [[baud_rate] [data_bit] [parity] [stop_bit] [flow_control] [size]] [single_flow] [silent] [end_char]\n"
			" device       Specify the UART device (/dev/ttyx) x=PCH0,PCH1,PCH2,S0.\n"
			" mode         Specify the mode        (-tx,-rx, -txaa, -rxaa, -txr, -rxr) \n"
			"\n --------------------------------Optional Parameters--------------------------------\n"
			" baud_rate    Specify the baud_rate   (300,1200,2400,4800,9600,19200,38400,57600,\n"
			"                                       115200,230400,460800,921600,1000000,2000000,\n"
            		"                                       3000000, 4000000).\n"
			" data_bit     Specify the data bit    (5,6,7,8).\n"
			" parity       Specify the parity      (O,E,N,M,S).\n"
			"                                       O(Odd), E(Even), N(None), M(Mark), S(Space)\n" 
			" stop_bit     Specify the stop bit    (1,15,2).\n"
			"                                       1(1 Stop bit), 15(1.5 Stop bit), 2(2 Stop bit)\n"
			" flow_control Specify the flow control(S,H,N).\n"
			"                                       S(Software), H(Hardware), N(None)\n"
			" size         Specify the data size   (1,x), x = Iterations(1 to 1000000) \n"
			"                                       1(5KB Single Packet), x(1KB x Iterations).\n"
                        " single_flow  Specify if its single   o or O for Single Flow, n for normal dual flow\n"
                        "              flow \n"
                        " silent       Specify for silent mode s or S for Silent Mode, n for normal prints\n"
                        " end_char     Specify to turn on      c or C for end character, n for none\n"
                        "              end character transmit \n"
			" -------------------------------------------------------------------------------------\n"
			"     When the [[..] [..] [..] [..] [..]] parameters are not specified.\n"
			"     Default baud_rate = 9600, data_bit=8, parity=N, stop_bit=1, flow_control=N, size=1"
			"\n", argv[0]);
		return IOH_TEST_ERROR;
	}
	    
	close(fd);
	printf("*******************************************\n");
	return ret_val;
}

int uart_es(int mode, int value)
{
	static int uart_es_on = 0;
	if(mode == SET)
		uart_es_on = value;
	return uart_es_on;
}

ssize_t read_uart_data(int fd, void *buf, size_t count)
{
	fd_set set;
	struct timeval timeout;
	ssize_t ret = 0;

	FD_ZERO(&set);
	FD_SET(fd, &set);

	timeout.tv_sec = RD_TIMEOUT;
	timeout.tv_usec = 0;

	ret = select(fd + 1, &set, NULL, NULL, &timeout);
	if (ret > 0) { /* there's data incoming. just read it normally. */
		return read(fd, buf, count);
	}
	else if (ret == 0) {
		printf("Error! No available data for the past %d secs\n", RD_TIMEOUT);
		return -1; /* Error. Just pass it to call func() */
	}
	/* If ever we got here, there's probably an IO error! */
	return ret;
}

int UART_receive(int size,int dev_fd, char *buf_ptr)
{
        unsigned int rd_count  = 0;
        unsigned char read_size = 255;
        int ret = 0;
        char ch_stop = END_SIGNAL;

	printf("Destination/Receive Buffer address = %lx \n",(long unsigned int )&buf_ptr);
        
	printf("Start Receving data:\n");
        while (rd_count < size ) {
		if((size - rd_count) < read_size) {
			read_size = (size - rd_count);
		}
                ret = read_uart_data(dev_fd,&buf_ptr[rd_count],read_size);

                if (ret >= 0) {
                        rd_count += ret;
                }
		else {
                        printf("ERROR: Failed to read the data from the serial port\n");
                	return IOH_TEST_ERROR;
                }
        }

        printf("SUCCESS: %d bytes of Data read successfully\n",rd_count);

	if(uart_es(GET,0) == 1) {
		usleep(10000);
		if(write(dev_fd,&ch_stop,1) != 1) {
			printf("ERROR writing END signal!\n");
			return IOH_TEST_ERROR;
		}
		else
			printf("UART_recv: Data transfer read END signal sent\n");
	}

	return IOH_TEST_SUCCESS;
}

int generate_random_data(char *buf, unsigned int size, unsigned int mask)
{
	int fd, i, ret = 0;
	if( (fd = open(RAND_DEV, O_RDONLY)) == -1)
	{
		printf("Error opening device %s.\n", RAND_DEV);
		return -1;
	}

	for(i = 0; i < size ; ++i) {
		if(read(fd, buf + i, 1) != 1) {
			printf("ERROR. Unable to read properly from the %s.\n", RAND_DEV);
			ret = -1;
			goto end;
		}
		*(buf + i) &= mask;
	}
	
end:	close(fd);
	return ret;
}

void generate_crc8(int size, char *buf_ptr,unsigned int mask)
{
	unsigned char crc = 0x0;
	unsigned char temp;

	crc = crc8(crc, (unsigned char *) (buf_ptr+1), size-1);
	/* the crc8 function requires unsigned char
	 * but for our data we need char. So we just
	 * force the crc8 to char type. */
	crc = ((char) (crc & 0xff)) & mask;
	*(buf_ptr) = crc;
}

/* returns 1 if crc are equal
 * else returns 0 */
int check_crc8(int size, char *buf_ptr)
{
	unsigned char calc_crc = 0x0;
	unsigned char read_crc = 0x0;

	read_crc = *((unsigned char *) buf_ptr) & 0xff;
	calc_crc = crc8(calc_crc, (unsigned char *) (buf_ptr+1), size-1);

	return (read_crc == calc_crc);
}

int UART_send(int size,int dev_fd,unsigned int mask,int type, 
		int fill, char *buf_ptr)
{
	unsigned int loop = 0;
	int ret = 0;
	char ch_stop = 0x0;
	
	printf("Source/Send Buffer address = %lx \n",( long unsigned int)&buf_ptr);

	if(fill) {
		if(type == UART_DATA_RAND) {
			if(generate_random_data(buf_ptr, size, mask) != 0) {
				return IOH_TEST_ERROR;
			}
		}
		else {
			for (loop =0;loop<size;loop++) {
				if (type == UART_DATA_AA) {
					buf_ptr[loop] = 0xAA; 
				}
				else {
					buf_ptr[loop] = (loop % mask) ;
				}
			}
		}

		/* append crc8 at the last byte */
		generate_crc8(size, buf_ptr,mask);
		/* write to uart */
		ret = write(dev_fd,buf_ptr,size);
	}
	else {
		/* append crc8 at the last byte */
		generate_crc8(size, buf_ptr,mask);
		/* write to uart */
		ret = write(dev_fd,buf_ptr,size);
	}

	if (ret <= 0) {
		printf("ERROR: Failed to write the data\n");
		return IOH_TEST_ERROR;
	}

	printf("SUCCESS: %d bytes of data written successfully\n", ret);

	if(uart_es(GET,0) == 1) {
		printf("UART_send: Waiting for END signal\n");
	        if(read(dev_fd,&ch_stop,1) != 1) {
			printf("ERROR reading END signal!\n");
			return IOH_TEST_ERROR;
		}

		if(ch_stop == END_SIGNAL)
		        printf("UART_send: Data transfer read END signal received\n");
		else {
			printf("UART_send: END Signal not received!!!\n");
			printf("UART_send: Received 0x%x instead.\n", ch_stop);
			return IOH_TEST_ERROR;
		}
	}

	usleep(1);
	return IOH_TEST_SUCCESS;
}

int Packet_receive(int UART_fd,user_UART_config_t *uart_config,
		int type, int single_flow, int silent_mode)
{
	char *buff = NULL, *ptr = NULL;
	int count = 0,size = 0,rem_size = 0,loop = 0;
	int ret_val = IOH_TEST_SUCCESS;

	/* To determine amount of data to be written */
	rem_size = uart_config->data_size;
	count = (uart_config->data_size / UART_FIFO_SIZE);
	if (count == 0)
		size = uart_config->data_size;
	else
		size = UART_FIFO_SIZE;

	/* Memory to store whole received data */
	buff = (char *)malloc(uart_config->data_size + 1);
	if (buff == NULL) {
		printf("ERROR: Failed to allocate buffer for storing Data to be received\n");
		return IOH_TEST_ERROR;
	}
	memset(buff, 0, (uart_config->data_size+1));
	printf("Buffer address: %p\n", buff);

	/* Receving data from the port */
	ptr = buff;
	loop = 0;
	do {
		if(UART_receive(size,UART_fd,ptr) == IOH_TEST_ERROR) {
			ret_val = IOH_TEST_ERROR;
			goto pkt_rcv_free_mem;
		}

		ptr += size;
		rem_size -= size;

		if (rem_size >= UART_FIFO_SIZE)
			size = UART_FIFO_SIZE;
		else
			size = rem_size;

	} while ((++loop) < count);

	if (count == 0)
		size = uart_config->data_size;
	else
		size = UART_FIFO_SIZE;

	/* in bidirectional traffic, forward the data back to sender 
	   for unidirectional, check crc to see if data is OK */
	if(single_flow) {
		if (check_crc8(size, buff) == 0) {
			printf("ERROR! Data received corrupted!\n");
			goto pkt_rcv_free_mem;
		}
	} else {
		rem_size = uart_config->data_size;
		/* Sending data to the UART port */
		loop = 0;
		ptr = buff;
		do {
			if(UART_send(size,UART_fd,uart_config->mask,type,DIRECT_SEND,ptr) == IOH_TEST_ERROR) {
				ret_val = IOH_TEST_ERROR;
				goto pkt_rcv_free_mem;
			}

			ptr += size;
			rem_size -= size;

			if (rem_size >= UART_FIFO_SIZE)
				size = UART_FIFO_SIZE;
			else
				size = rem_size;

        	} while ((++loop) < count);
	}

	if(!silent_mode) {
		printf("Received data\n");
		printf("****************\n");
		for (loop = 0;loop <uart_config->data_size;loop++) {
			printf("%x ",buff[loop]);
		}
		printf("\n");
	}

pkt_rcv_free_mem:
	/* free allocated memory */
        if (buff) {
        	free(buff);
        	buff=NULL;
        }
	return ret_val;
}

int Continous_receive(int UART_fd,user_UART_config_t *uart_config,
		int iter,int type, int single_flow, int silent_mode)
{
        int indx = 0;	/*o open uart terminal port*/
	int ret_val = IOH_TEST_SUCCESS;
        char *buff = NULL, *ptr = NULL;
	int count = 0,size = 0,rem_size = 0,loop=0, dw_cntr=0;

        /* Memeory to store whole received data */
        buff = (char *)malloc(uart_config->data_size + 1);
        if (buff == NULL) {
                printf("ERROR: Failed to allocate buffer for storing Data to be received\n");
		return IOH_TEST_ERROR;
        }

        for (loop = 0;loop < iter;loop ++) {
		if(baud_global >= 1000000)
			usleep(10000);

        	memset(buff,0,(uart_config->data_size+1));

                printf("Iteration count:%d\n",loop + 1);
                count = (uart_config->data_size / UART_FIFO_SIZE);
		if (count == 0)
			size = uart_config->data_size;
		else
			size = UART_FIFO_SIZE;

		/* Receving data from the port */
                ptr = buff;
		dw_cntr = 0;
		rem_size = uart_config->data_size;
                do {
                        if(UART_receive(size,UART_fd,ptr) == IOH_TEST_ERROR) {
                                ret_val = IOH_TEST_ERROR;
				goto cont_rcv_free_mem;
                        }

                        ptr += size;
			rem_size -= size;

                        if (rem_size >= UART_FIFO_SIZE)
                                size = UART_FIFO_SIZE;
                        else
                                size = rem_size;

        	} while ((++dw_cntr) < count);

		if (count == 0)
			size = uart_config->data_size;
		else
			size = UART_FIFO_SIZE;

		/* in bidirectional traffic, forward the data back to sender 
	   	   for unidirectional, check crc to see if data is OK */
		if (single_flow) {
			if (check_crc8(size, buff) == 0) {
				printf("ERROR! Data received corrupted!\n");
				goto cont_rcv_free_mem;
			}

		} else {
                	ptr = buff;
			dw_cntr = 0;
			rem_size = uart_config->data_size;
	                do {
				if(UART_send(size,UART_fd,uart_config->mask,type,DIRECT_SEND,ptr) == IOH_TEST_ERROR) {
	                                ret_val = IOH_TEST_ERROR;
					goto cont_rcv_free_mem;
	                        }

	                        ptr += size;
				rem_size -= size;

	                        if (rem_size >= UART_FIFO_SIZE)
	                                size = UART_FIFO_SIZE;
	                        else
	                                size = rem_size;

        		} while ((++dw_cntr) < count);
		}

		if(!silent_mode) {
	                printf("Received data\n");
	                printf("***************\n");
        	        for (indx = 0;indx <uart_config->data_size;indx++) {
	                        printf("%x ",buff[indx]);
	                }
	                printf("\n");
		}
        }

cont_rcv_free_mem:
        if (buff) {
                free(buff);
                buff=NULL;
        }
	return ret_val;
}

int Packet_transfer(int UART_fd,user_UART_config_t *uart_config,
		int type, int single_flow, int silent_mode)
{
	int count = 0,size = 0,rem_size  =0,loop =0;
	int ret_val = IOH_TEST_SUCCESS;
        char *ptr = NULL, *sd_buff = NULL, *rd_buff = NULL;

        /* To determine amount of data to be written */
	rem_size = uart_config->data_size;
        count = (uart_config->data_size / UART_FIFO_SIZE);
        if (count == 0) {
                size = uart_config->data_size;
        } else {
                size = UART_FIFO_SIZE;
        }

        /* Memory to store whole data send */
        sd_buff = (char *)malloc(uart_config->data_size + 1);
        if (sd_buff == NULL) {
                printf("ERROR: Failed to allocate buffer for storing data to be send\n");
                return IOH_TEST_ERROR;
        }
        memset(sd_buff,0,(uart_config->data_size+1));
	printf ("Buffer address: %p\n", sd_buff);

        /* Memory to store whole received data */
        rd_buff = (char *)malloc(uart_config->data_size + 1);
        if (rd_buff == NULL) {
                printf("ERROR: Failed to allocate buffer for storing Data to be received\n");
                ret_val = IOH_TEST_ERROR;
		goto pkt_tx_free_sd_mem;
        }
        memset(rd_buff, 0, (uart_config->data_size+1));

        /* Sending data to the UART port */
        ptr = sd_buff;
	loop = 0;
        do {
		printf("Sending %d bytes\n", size);
                if(UART_send(size,UART_fd,uart_config->mask,type,FILL,ptr) == IOH_TEST_ERROR) {
                        ret_val = IOH_TEST_ERROR;
			goto pkt_tx_free_rd_mem;
                }

                ptr += size;
		rem_size -= size;

                if (rem_size >= UART_FIFO_SIZE)
                        size = UART_FIFO_SIZE;
                else
                        size = rem_size;

        } while ((++loop) < count);

	printf("Packet transfer: transfer loop done!\n");

	if(!single_flow) {
	        /* To determine amount of data to be received */
		rem_size = uart_config->data_size;
	        if (count == 0) {
	                size = uart_config->data_size;
	        } else {
	                size = UART_FIFO_SIZE;
	        }

	        /* Receving data from the port */
        	ptr = rd_buff;
		loop = 0;
	        do {
	                if(UART_receive(size,UART_fd,ptr) == IOH_TEST_ERROR) {
	                        ret_val = IOH_TEST_ERROR;
				goto pkt_tx_free_rd_mem;
	                }

	                ptr += size;
			rem_size -= size;

	                if (rem_size >= UART_FIFO_SIZE) {
	                        size = UART_FIFO_SIZE;
	                } else {
	                        size = rem_size;
	                }

        	} while ((++loop) < count);


	        /* Comparing the data send and received */
	        ret_val = memcmp(sd_buff,rd_buff,uart_config->data_size);

	        if (ret_val != 0) {
	                printf("ERROR: Send and received data differs\n");
	                ret_val = IOH_TEST_ERROR;
			goto pkt_tx_free_rd_mem;
	        }
	        else printf("SUCCESS: Data sent and received are same\n");

		if(!silent_mode) {
		        printf("Received data\n");
		        printf("***************\n");
		        for (loop = 0;loop <uart_config->data_size;loop++) {
		                printf("%x ",rd_buff[loop]);
		        }
		        printf("\n");
		}
	}

	if(!silent_mode) {
	        printf("Send data:\n");
	        printf("*************\n");
	        for (loop = 0;loop < uart_config->data_size;loop++) {
	                printf("%x ",sd_buff[loop]);
	        }
        	printf("\n");
	}

pkt_tx_free_rd_mem:
        if (rd_buff) {
                free(rd_buff);
                rd_buff=NULL;
        }
pkt_tx_free_sd_mem:
        if (sd_buff) {
                free(sd_buff);
                sd_buff=NULL;
        }
        return ret_val;
}

int Continous_transfer(int UART_fd,user_UART_config_t *uart_config,
		int iter, int type, int single_flow, int silent_mode)
{
	int dw_cntr = 0;
	int loop = 0,indx = 0;
	int ret_val = 0,count = 0,size = 0,rem_size  = 0;	/*to open uart terminal port*/
	char *ptr = NULL ,*rd_buff = NULL, *sd_buff = NULL;

	/* Memory to store whole data send */
	sd_buff = (char *)malloc(uart_config->data_size + 1);
	if (sd_buff == NULL) {
		printf("ERROR: Failed to allocate buffer for storing data to be send\n");
		return IOH_TEST_ERROR;
	}
	memset(sd_buff,0,(uart_config->data_size+1));

	/* Memeory to store whole received data */
	rd_buff = (char *)malloc(uart_config->data_size + 1);
	if (rd_buff == NULL) {
		printf("ERROR: Failed to allocate buffer for storing Data to be received\n");
		ret_val = IOH_TEST_ERROR;
		goto cont_tx_free_sd_mem;
	}
	memset(rd_buff, 0, (uart_config->data_size+1));

	for (loop = 0;loop < iter;loop ++) 
	{
		if(baud_global >= 1000000)
			usleep(10000);

		memset(sd_buff,0,(uart_config->data_size+1));
		memset(rd_buff,0,(uart_config->data_size+1));
		printf("Iteration count: %d\n",loop + 1);

		rem_size = uart_config->data_size;
		count = (uart_config->data_size / UART_FIFO_SIZE);
		if (count == 0) {
			size = uart_config->data_size;
		} else {
			size = UART_FIFO_SIZE;
		}

		ptr = sd_buff;
		dw_cntr = 0;
		do {
			if(UART_send(size,UART_fd,uart_config->mask,type,FILL,ptr) == IOH_TEST_ERROR) {
				ret_val = IOH_TEST_ERROR;
				goto cont_tx_free_rd_mem;
			}

			ptr += size;
			rem_size -= size;

			if (rem_size >= UART_FIFO_SIZE) {
				size = UART_FIFO_SIZE;
			} else {
				size = rem_size;
			}

		} while ((++dw_cntr) < count);

		if(!single_flow) {
			rem_size = uart_config->data_size;
			if (!count) {
				size = uart_config->data_size;
			} else {
				size = UART_FIFO_SIZE;
			}

			dw_cntr = 0;
			ptr = rd_buff;
			do {
				if(UART_receive(size,UART_fd,ptr) == IOH_TEST_ERROR) {
					ret_val = IOH_TEST_ERROR;
					goto cont_tx_free_rd_mem;
				}

				ptr += size;
				rem_size -= size;

				if (rem_size >= UART_FIFO_SIZE) {
					size = UART_FIFO_SIZE;
				} else {
					size = rem_size;
				}

			} while ((++dw_cntr) < count);

			/* Comparing the data send and received */
			ret_val = memcmp(sd_buff,rd_buff,uart_config->data_size);

			if (ret_val != 0) {
				printf("ERROR: Send and received data differs\n");
				printf("Received data\n");
				printf("***************\n");
				for (indx = 0;indx <uart_config->data_size;indx++) {
					printf("%x ",rd_buff[indx]);
				}
				printf("\n");
				printf("Send data:\n");
				printf("*************\n");
				for (indx = 0;indx < uart_config->data_size;indx++) {
					printf("%x ",sd_buff[indx]);
				}
				printf("\n");
				ret_val = IOH_TEST_ERROR;
				goto cont_tx_free_rd_mem;
			}

			printf("SUCCESS: Data sent and received are same\n");

			if(!silent_mode) {
				printf("Received data\n");
				printf("***************\n");
				for (indx = 0;indx <uart_config->data_size;indx++) {
					printf("%x ",rd_buff[indx]);
				}
				printf("\n");
			}
		}

		if(!silent_mode) {
			printf("Send data:\n");
			printf("*************\n");
			for (indx = 0;indx < uart_config->data_size;indx++) {
				printf("%x ",sd_buff[indx]);
			}
			printf("\n");
		}
	}

cont_tx_free_rd_mem:
	if (rd_buff) {
		free(rd_buff);
		rd_buff=NULL;
	}
cont_tx_free_sd_mem:
	if (sd_buff) {
		free(sd_buff);
		sd_buff=NULL;
	}
	return ret_val;
}
