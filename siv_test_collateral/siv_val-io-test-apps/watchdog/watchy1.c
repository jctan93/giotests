#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <linux/watchdog.h>


int main()
{
	int error = 0, timeleft = 30;
	int fd = open("/dev/watchdog", O_RDONLY|O_WRONLY);
	printf("FD value is %d\n", fd);
	error = ioctl(fd, WDIOC_SETTIMEOUT, &timeleft);
	if (!error) {
		printf("Timeleft is %d\n", timeleft);
	}
	else	
		return error;
}
