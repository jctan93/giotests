#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdbool.h>

static struct termios oldterminfo;


void closeserial(int fd)
{
    tcsetattr(fd, TCSANOW, &oldterminfo);
    if (close(fd) < 0)
        perror("closeserial()");
}


int openserial(char *devicename)
{
    int fd;
    bool status;
    struct termios attr;
    if ((fd = open(devicename, O_RDWR)) == -1) {
        perror("openserial(): open()");
            return 0;
            }
    if (tcgetattr(fd, &oldterminfo) == -1) {
        perror("openserial(): tcgetattr()");
            return 0;
            }
    /* this is for test purpose*/
    //printf("", &oldterminfo);
    /* End of test purpose */
    attr = oldterminfo;
    attr.c_cflag |= CRTSCTS | CLOCAL;
    attr.c_oflag = 0;
    if (tcflush(fd, TCIOFLUSH) == -1) {
        perror("openserial(): tcflush()");
            return 0;
            }
    if (tcsetattr(fd, TCSANOW, &attr) == -1) {
        perror("initserial(): tcsetattr()");
            return 0;
            }
    return fd;
}


int setRTS(int fd, int level)
{
    int status;
    if (ioctl(fd, TIOCMGET, &status) == -1) {
        perror("setRTS(): TIOCMGET");
            return 0;
            }
    if (level)
        status |= TIOCM_RTS;
    else
        status &= ~TIOCM_RTS;
    if (ioctl(fd, TIOCMSET, &status) == -1) {
        perror("setRTS(): TIOCMSET");
            return 0;
            }
    return 1;
}


int main()
{
	    int fd;
	    char *serialdev = "/dev/ttyS1";
		char testData[50]="This is Test message for ttyS1  \n";
		char recvBuf[50];
		int i;
        fd = openserial(serialdev);
        //printf("Status : %d \n", fd);
        /* if (!fd) {
            printf("Error while initializing %s.\n", serialdev);
            return 1;
        } */
        if (fd != 3){
            printf("Your TxD and RxD pin are not connected.\n");
            printf("UART Manual Control Test Fail\nUART-F022-M Fail.\n");
            return 1;
        }
        setRTS(fd, 0);
        write(fd,&testData,30);
        
        usleep(5000); 
        setRTS(fd, 1);

        read(fd,&recvBuf,30);
        printf("\nTest Data : %s\n", &testData);
        printf("Received Data : %s\n\n", &recvBuf);
        if(!strncmp(&recvBuf,&testData,30)){
            printf("UART-F022-M PASS\n");
        }
        else { 
            printf("UART-F022-M FAIL\n");
            printf("Recv Data = ");
            for(i=0;i<30;i++)
                printf("%c",recvBuf[i]);
            printf("\n");
        }
        closeserial(fd);
            return 0;
}