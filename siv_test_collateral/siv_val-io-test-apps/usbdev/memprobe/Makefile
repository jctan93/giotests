# Variables #
CC = gcc
CFLAGS = -Wall -g
LDFLAGS = 
RDIR = ../release/tools/
SCRIPTS = ulpi_write.sh ulpi_read.sh

# Files #
EXEC = memprobe
SOURCES = $(wildcard *.c)
OBJS = $(SOURCES:.c=.o)

# Target
$(EXEC): $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) -o $(EXEC)

# Object Files #
%.o: %.c
	$(CC) -c $(CFLAGS) $< -o $@

# Clean #
clean:
	rm -rf $(EXEC) $(OBJS)
