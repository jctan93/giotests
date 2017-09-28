#include "linux/hpet.h"
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/time.h>

#define DEVICE "/dev/hpet"

static unsigned long tvdiff(struct timeval t1, struct timeval t2)
{
	return (t2.tv_sec - t1.tv_sec) * 1000000ul + t2.tv_usec - t1.tv_usec;
}

static void print_delay(struct timeval t1, struct timeval t2)
{
	unsigned long delay = tvdiff(t1, t2);
	printf("Delay: %lu.%06lu\n", delay / 1000000, delay % 1000000);
}

static int test_open(void)
{
	int i, fd[256];
	struct hpet_info info;

	for (i = 0; i < 256; i++) {
		fd[i] = open(DEVICE, O_RDONLY);
		if (fd[i] < 0) {
			if (errno != EBUSY) {
				printf("Unexpected: open %s attempt %d: %s\n",
						DEVICE, i+1, strerror(errno));
				return 1;
			}
			break;
		}
		if (ioctl(fd[i], HPET_INFO, &info) < 0) {
			printf("Unexpected: HPET_INFO: %s\n", strerror(errno));
			return 1;
		}
		printf("Opened timer: device %d, comparator %d\n",
				info.hi_hpet, info.hi_timer);
	}

	if (i == 0) {
		printf("Unexpected: no successful opens\n");
		return 1;
	}

	if (i == 256) {
		printf("Unexpected: open keeps succeeding\n");
		return 1;
	}

	if (close(fd[i - 1]) < 0) {
		printf("Unexpected: close %s: %s\n", DEVICE, strerror(errno));
		return 1;
	}

	fd[i - 1] = open(DEVICE, O_RDONLY);
	if (fd[i - 1] < 0) {
		printf("Unexpected: open %s after close: %s\n",
				DEVICE, strerror(errno));
		return 1;
	}

	printf("Passed\n");
	return 0;
}

static int test_timeout(void)
{
	int fd;
	struct timespec to;
	struct timeval t1, t2;
	unsigned long val;
	int ret;

	fd = open(DEVICE, O_RDONLY);
	if (fd < 0) {
		printf("Unexpected: open %s: %s\n", DEVICE, strerror(errno));
		return 1;
	}

	gettimeofday(&t1, NULL);

	to.tv_sec = 2;
	to.tv_nsec = 0;

	if (ioctl(fd, HPET_START, &to) < 0) {
		printf("Unexpected: HPET_START: %s\n", strerror(errno));
		return 1;
	}

	ret = read(fd, &val, sizeof(val));
	if (ret != sizeof(val)) {
		printf("Unexpected: read %s: ret=%d %s\n",
				DEVICE, ret, ret < 0 ? strerror(errno) : "");
		return 1;
	}

	gettimeofday(&t2, NULL);
	print_delay(t1, t2);
	return 0;
}

static int garbage_timeout(void)
{
	int fd;
	struct timespec to;

	fd = open(DEVICE, O_RDONLY);
	if (fd < 0) {
		printf("Unexpected: open %s: %s\n", DEVICE, strerror(errno));
		return 1;
	}

	to.tv_sec = 0x55555555;
	to.tv_nsec = 0xaaaaaaaa;

	if (ioctl(fd, HPET_START, &to) == 0 || errno != EINVAL) {
		printf("Unexpected: HPET_START: %s\n", strerror(errno));
		return 1;
	}

	printf("Passed\n");
	return 0;
}

static int test_start_stop(void)
{
	int fd;
	struct timespec to;
	struct timeval t1, t2;
	unsigned long val;
	int ret;

	fd = open(DEVICE, O_RDONLY);
	if (fd < 0) {
		printf("Unexpected: open %s: %s\n", DEVICE, strerror(errno));
		return 1;
	}

	to.tv_sec = 1;
	to.tv_nsec = 0;

	if (ioctl(fd, HPET_START, &to) < 0) {
		printf("Unexpected: HPET_START: %s\n", strerror(errno));
		return 1;
	}

	if (ioctl(fd, HPET_START, &to) == 0 || errno != EBUSY) {
		printf("Unexpected: double HPET_START: %s\n", strerror(errno));
		return 1;
	}

	if (ioctl(fd, HPET_STOP, 0) < 0) {
		printf("Unexpected: HPET_STOP: %s\n", strerror(errno));
		return 1;
	}

	gettimeofday(&t1, NULL);

	to.tv_sec = 2;
	to.tv_nsec = 0;

	if (ioctl(fd, HPET_START, &to) < 0) {
		printf("Unexpected: HPET_START: %s\n", strerror(errno));
		return 1;
	}

	ret = read(fd, &val, sizeof(val));
	if (ret != sizeof(val)) {
		printf("Unexpected: read %s: ret=%d %s\n",
				DEVICE, ret, ret < 0 ? strerror(errno) : "");
		return 1;
	}

	gettimeofday(&t2, NULL);
	print_delay(t1, t2);
	return 0;
}

static int test_query(void)
{
	int fd;
	struct timespec to, q;

	fd = open(DEVICE, O_RDONLY);
	if (fd < 0) {
		printf("Unexpected: open %s: %s\n", DEVICE, strerror(errno));
		return 1;
	}

	to.tv_sec = 2;
	to.tv_nsec = 0;

	if (ioctl(fd, HPET_START, &to) < 0) {
		printf("Unexpected: HPET_START: %s\n", strerror(errno));
		return 1;
	}

	usleep(500000);

	if (ioctl(fd, HPET_QUERY, &q) < 0) {
		printf("Unexpected: HPET_QUERY: %s\n", strerror(errno));
		return 1;
	}

	printf("Query result: %d.%06d\n", (int)q.tv_sec, (int)q.tv_nsec / 1000);
	return 0;
}

struct {
	const char *name;
	int (*func)(void);
} table[] = {
	{ "open", test_open },
	{ "timeout", test_timeout },
	{ "garbage_timeout", garbage_timeout },
	{ "start_stop", test_start_stop },
	{ "query", test_query },
	{ 0, 0 }
};

int main(int argc, char *argv[])
{
	int i;

	if (argc != 2)
		goto usage;

	for (i = 0; table[i].name; i++) {
		if (!strcmp(argv[1], table[i].name))
			return table[i].func();
	}

usage:
	printf("Usage: %s testname\n", argv[0]);
	return 1;
}
