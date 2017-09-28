#include <sys/ioctl.h>
#include <termios.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <signal.h>
#include <errno.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>

void signal_handler(int status);

int main(void)
{
        int fd;
        switch (fork()) {
                case 0:
                        break;
                case -1:
                //Error
                printf("Error demonizing (fork)! %d - %s\n", errno, strerror);
                exit(0);
                break;
                default:
                _exit(0);
        }

        if (setsid() == -1)
        {
                printf("Error demonizing (setsid)! %d - %s\n", errno, strerror);
                exit(0);
        }

        fd = open ("/dev/ttyS1", O_RDWR, 0 );

        struct sigaction saio; /* definition of signal action */
        saio.sa_handler = signal_handler;

        saio.sa_flags = 0;
        saio.sa_restorer = NULL;
        sigaction(SIGINT,&saio,NULL);
        struct termios options;
        memset (&options, 0x00, sizeof (options));
        options.c_cflag |= (CREAD);
        options.c_cflag |= CLOCAL;
        options.c_cflag |= CS8; // Select 8 l2_data bits
        options.c_iflag |= (BRKINT);
		
        options.c_cc[VTIME] = 1;
        if (tcsetattr (fd, TCSAFLUSH, &options) == -1)
        {
                printf("port setup failure\n");
                return -1;
        }
        ioctl(fd, TIOCSCTTY, (char *)NULL);

        printf("\nWaiting for SIGINT...\n");
        printf("Press any key to exit\n");

        getchar();

}

void signal_handler(int status)
{
        printf("received SIGINT %d signal.\n", status);
        printf("Press any key to exit\n");
        exit(0);
}

