#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

 
#include <termios.h>
#include <unistd.h>

int main(void)
{
        int fd;

        fd = open("/dev/ttyS1", O_RDWR);
        tcsendbreak(fd, 0);

        tcsendbreak(fd, 0);
        tcsendbreak(fd, 0);
        tcsendbreak(fd, 0);
        tcsendbreak(fd, 0);
	
	close(fd);
	return 0;
}
