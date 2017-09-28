/*UART user space program to read the HSUART pins status(Active/Inactive).
 *
 *  CTS pin - Clear to send
 *  DSR pin - Data set ready
 *  DCD pin - Data carieer detect
 *  RI  pin - Ring Indicator
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <termios.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

static struct termios old_terminfo;

/*
 func: hsuart_close(fd)
 fd  : Returned file descriptor from open.
 Desc:  This function shall close the fd.
*/
void hsuart_close(int fd)
{
	tcsetattr(fd, TCSANOW, &old_terminfo);
	if (close(fd) < 0)
		perror("hsuart_close()");
}

/*
 func: hsuart_close(fd)
 fd  : file descriptor returned from open.
 Desc: This function shall read the status(Active/Inactive) of HSUART pins. 
*/
int hsuart_getstatus(int fd)
{
	int pin_status;

	/* Read terminal status line */
	ioctl(fd, TIOCMGET, &pin_status);

	return pin_status;
}

/*
 func: hsuart_open()
 Desc: This function shall open the hsuart serial port.
*/
int hsuart_open(char *hsuart_device)
{
	int fd;
	struct termios hsuart_attr;

	if ((fd = open(hsuart_device, O_RDWR|O_NONBLOCK)) == -1) {
		perror("hsuart_open(): open()");
		return 0;
	}

	if (tcgetattr(fd, &old_terminfo) == -1) {
		perror("hsuart_open(): tcgetattr()");
		return 0;
	}

	hsuart_attr = old_terminfo;
	hsuart_attr.c_cflag |= CRTSCTS | CLOCAL;
	hsuart_attr.c_oflag = 0;

	if (tcflush(fd, TCIOFLUSH) == -1) {
		perror("hsuart_open(): tcflush()");
		return 0;
	}

	if (tcsetattr(fd, TCSANOW, &hsuart_attr) == -1) {
		perror("initserial(): tcsetattr()");
		return 0;
	}

	return fd;
}

/*
 func: hsuart_setRTS(fd)
 fd  : Returned file descriptor from open.
 Desc: This function shall set/reset the RTS pin.
*/
int hsuart_setRTS(int fd, int RTS_flag)
{
	int RTS_status;

	if (ioctl(fd, TIOCMGET, &RTS_status) == -1) {
		perror("hsuart_setRTS(): TIOCMGET");
		return 0;
	}

	if (RTS_flag)
		RTS_status |= TIOCM_RTS;
	else
		RTS_status &= ~TIOCM_RTS;

	if (ioctl(fd, TIOCMSET, &RTS_status) == -1) {
		perror("hsuart_setRTS(): TIOCMSET");
		return 0;
	}

	return 1;
}

int main(int argc,char *argv[])
{
	int fd;
	int count = 0, count1=0;
	int pin_status = 0;
	//char *hsuart_dev = "/dev/ttyS1";
	char *hsuart_dev;
	bool CTS=0, RI=0, DCD=0, DSR=0;

	if((argc < 2) || (argc > 2)) {
	printf(	"\n"
		"Usage: [device name] i.e /dev/ttyS0 or /dev/ttyS1 or /dev/ttyS2 or /dev/ttyS3 \n");
		
		return -1;
	}
		
	hsuart_dev = argv[1];
	
	
	fd = hsuart_open(hsuart_dev);
	if (!fd) {
		fprintf(stderr, "Error while initializing %s.\n", hsuart_dev);
		printf("Test Fail");
		return -1;
	}

//	while(1)
//	{
		pin_status =hsuart_getstatus(fd);

		/* Check status of RI pin */
		RI = (pin_status & TIOCM_RNG) ? 1 : 0;
		if (RI)
			puts("Ring(RI) pin status is Active\n");
		else
			puts("Ring(RI) pin status is Inactive\n");

		/* Check status of DCD pin */
		DCD = (pin_status & TIOCM_CAR);
		if (DCD)
			puts("dcd pin status is Active\n");
		else
			puts("dcd pin status is Inactive\n");

		/*Check status of DSR pin*/
		DSR = (pin_status & TIOCM_DSR);
		if (DSR)
			puts("dsr pin status is Active\n");
		else
			puts("dsr pin status is Inactive\n");

		/*Check status of CTS pin*/
		CTS = ((pin_status & TIOCM_CTS) ? 1 : 0);
		if (CTS) {
			puts("cts pin status is Active\n");
/*
			if (count < 2)
			{
				write (fd, "This is a test code ", 20);
				count1 += 20;
			}

			if (count == 2)
			{
				write(fd,"\n",1);
				count1++;
				count = 0;
			}	

			count++;
			if (count1 > 307648)
				break;
			hsuart_setRTS(fd,0);
			hsuart_setRTS(fd,1);
		*/
		}
		else
			puts("cts pin status is Inactive\n");
//	}

	printf("Test PASS for %s \n",hsuart_dev);
	hsuart_close(fd);
	return 0;
}

