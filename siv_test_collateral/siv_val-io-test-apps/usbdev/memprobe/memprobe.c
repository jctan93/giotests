
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define handle_error(msg) \
    do { perror(msg); exit(EXIT_FAILURE); } while (0)

int main(int argc, char *argv[])
{
	char *addr;
	int fd;
	struct stat sb;
	unsigned long offset = 0, pa_offset = 0, addr_offset = 0;
	unsigned int value;

	if (argc < 3 || argc > 5) {
		fprintf(stderr, "%s file offset [length]\n", argv[0]);
		exit(EXIT_FAILURE);
	}
	fd = open(argv[1], O_RDWR);
	if (fd == -1)
		handle_error("open");
	if (fstat(fd, &sb) == -1)           /* To obtain file size */
		handle_error("fstat");
	offset = strtoul(argv[3], NULL, 16);
	/* offset for mmap() must be page aligned */
	pa_offset = offset & ~(sysconf(_SC_PAGE_SIZE) - 1);
	addr_offset = offset - pa_offset;
	addr = mmap(NULL, getpagesize(), PROT_READ|PROT_WRITE,
				MAP_SHARED, fd, (off_t) pa_offset);
	if (addr == MAP_FAILED)
		handle_error("mmap");

	if(argv[2][0] == 'r') {
		printf("0x%08x\n", *((unsigned int*)(addr + addr_offset)));
	} else if(argv[2][0] == 'w') {
		value = strtoul(argv[4], NULL, 16);
		printf("Write Memory Address 0x%lx : 0x%08x\n", pa_offset + addr_offset, value);
		*((unsigned int*)(addr + addr_offset)) = value;
	} else {
		fprintf(stderr, "Unknown mode %c\n", argv[2][0]);
	}

	munmap(addr, getpagesize());
	return 0;
}
