#include <sys/io.h>
#include<stdio.h>
unsigned char coms_read(int offset);
#define MAX_BYTES 256
unsigned char cmos_read(int offset)
{
     unsigned char value;

     ioperm(0x70, 0x2, 1);
     ioperm(0x80, 0x1, 1);

//printf("1");
     outb(offset, 0x70);
     outb(0, 0x80);  /* Small delay */
     value = inb(0x71);

     ioperm(0x80, 0x1, 0);
     ioperm(0x70, 0x2, 0);
//printf("2");
     return value;
}

unsigned char readData[MAX_BYTES];
unsigned char tempData[MAX_BYTES];
main()
{
	unsigned char result;
	int i;
	for(i=0;i<MAX_BYTES;i++)
	{
		result = cmos_read(i);
		readData[i] = result;
		printf("Byte %d = %02x\n",i,readData[i]);
	}
	//It should not be zero
	if(memcmp(&readData,&tempData,MAX_BYTES))
		printf("\nTest PASS \n");
	else
		printf("\nTest FAIL\n");
		

}
