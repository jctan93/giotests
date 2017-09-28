#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <linux/watchdog.h>


int main()
{
	int error = 0, timeleft = 30, pretimeout = 1;
	struct watchdog_info ident;
	int fd = open("/dev/watchdog", O_RDONLY|O_WRONLY);
	printf("FD value is %d\n", fd);
	error = ioctl(fd, WDIOC_SETTIMEOUT, &timeleft);
	if (!error) {
		printf("Settimeout is enabled\n");
	}
	else	
		printf("Settimeout is not enabled\n");
	error = ioctl(fd, WDIOC_KEEPALIVE, 0);
	if (!error) {
		printf("KEEPALIVE is enabled\n");
	}
	else	
		printf("KEEPALIVE is not enabled\n");
	error = ioctl(fd, WDIOC_GETTIMEOUT, &timeleft);
	if (!error) {
		printf("Gettimeout is enabled\n");
	}
	else	
		printf("Gettimeout is not enabled\n");
	error = ioctl(fd, WDIOC_SETPRETIMEOUT, &pretimeout);
	if (!error) {
		printf("Setpretimeout is enabled\n");
	}
	else	
		printf("Setpretimeout is not enabled\n");
	error = ioctl(fd, WDIOC_GETPRETIMEOUT, &pretimeout);
	if (!error) {
		printf("Setpretimeout is enabled\n");
	}
	else	
		printf("Setpretimeout is not enabled\n");
	error = ioctl(fd, WDIOC_GETSUPPORT, &ident);
	if (!error) {
		printf("Getsupport  is enabled\n");
	}
	else	
		printf("Getsupport is not enabled\n");
	error = ioctl(fd, WDIOC_GETTIMELEFT, &timeleft);
	if (!error) {
		printf("GEttimeleft is enabled\n");
	}
	else	
		printf("Gettimeleft is not enabled\n");
	return error;
}
