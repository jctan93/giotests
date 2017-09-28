/*
 * Sample program for SPI on Intel(R) Platform Controller Hub EG20T.
 *
 * Copyright (C) 2011 OKI SEMICONDUCTOR Co., LTD.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; version 2 of the License.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307, USA.
 */
#include <string.h>
#include <stdio.h>
#include <wchar.h>
#include <fcntl.h>
#include <linux/ioctl.h>
#include <linux/spi/spidev.h>

#define PCH_SUCCESS		(0)
#define PCH_ERROR		(1)

#define EEPROM_DATA_SIZE	(8)
#define EEPROM_ADDR_SIZE	(2)
#define EEPROM_ADDR_MASK	(0x1FF)

#define WRITE_INSTRUCTION_8BIT	(0x2)
#define READ_INSTRUCTION_8BIT	(0x3)
#define WRITE_ENABLE_8BIT	(0x6)
#define WRITE_INSTRUCTION_16BIT	(0x200)
#define READ_INSTRUCTION_16BIT	(0x300)
#define WRITE_ENABLE_16BIT	(0x600)
#define WRITE_INSTRUCTION_32BIT	(0x20000)
#define READ_INSTRUCTION_32BIT	(0x30000)
#define WRITE_ENABLE_32BIT	(0x60000)


#define TRANSFER_SIZE_4BIT	(4)
#define TRANSFER_SIZE_8BIT	(8)
#define TRANSFER_SIZE_16BIT	(16)
#define TRANSFER_SIZE_32BIT	(32)

#define TRANSFER_SPEED_25KBPS	(25000)
#define TRANSFER_SPEED_75KBPS	(75000)
#define TRANSFER_SPEED_125KBPS	(125000)
#define TRANSFER_SPEED_250KBPS	(250000)
#define TRANSFER_SPEED_500KBPS	(500000)
#define TRANSFER_SPEED_750KBPS	(750000)
#define TRANSFER_SPEED_800KBPS	(800000)
#define TRANSFER_SPEED_1MBPS	(1000000)
#define TRANSFER_SPEED_2MBPS	(2000000)

#define LSB_FIRST		(1)
#define MSB_FIRST		(0)

#define USLEEP_TIME		(5000)
#define min(a, b)		((a) < (b) ? (a) : (b))

typedef struct user_config {
	int bpw;
	int speed;
	int lsb;
	int mode;
}user_config_t;


int pch_spi_read8bit(int dev_fd, int address, unsigned char *buff, unsigned char size)
{
	unsigned char buff_data[size + EEPROM_ADDR_SIZE];
	unsigned char rd_buff[size + EEPROM_ADDR_SIZE];
	int ret_val = 0, i;
	struct spi_ioc_transfer xfer[2];

	memset(buff_data, 0, sizeof buff_data);
	memset(rd_buff, 0, sizeof rd_buff);
	memset(xfer, 0, sizeof xfer);
	buff_data[0] = (READ_INSTRUCTION_8BIT | (unsigned char)((address & 0x100) >> 5));
	buff_data[1] = (unsigned char)(address & 0xFF);
	xfer[0].tx_buf = (unsigned long)buff_data;
	xfer[0].len = size + EEPROM_ADDR_SIZE;
	xfer[0].rx_buf = (unsigned long)rd_buff;
	ret_val = ioctl(dev_fd, SPI_IOC_MESSAGE(1), xfer);

	memcpy(buff ,(rd_buff + 2), size);
	return;
}

int pch_spi_write8bit(int dev_fd, int address, unsigned char *buff, unsigned char size)
{
	int ret_val, i;
	struct spi_ioc_transfer xfer;
	unsigned char rx_buff[2];
	unsigned char tx_buff[size + EEPROM_ADDR_SIZE];
	unsigned char wrt_signal;

	memset(&xfer, 0, sizeof xfer);
	memset(tx_buff, 0, sizeof tx_buff);
	memset(rx_buff, 0, sizeof rx_buff);
	xfer.tx_buf = (unsigned long)tx_buff;
	xfer.rx_buf = (unsigned long)rx_buff;
	xfer.len = 2;
	tx_buff[0] = 0x05;
	ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
	if (rx_buff[1] & 0x0C) {
		tx_buff[0] = 0x01;
		tx_buff[1] = rx_buff[1] & ~0x0C;
		ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
		printf("SUCCESS: Block Protection bits cleared\n");
	}

	wrt_signal = WRITE_ENABLE_8BIT;
	ret_val = write(dev_fd ,&wrt_signal, 1);
	if (ret_val <= 0) {
		printf("ERROR: 8bit Write enable failed\n");
		return PCH_ERROR;
	}

	memset(tx_buff,0, sizeof tx_buff);
	tx_buff[0] = (WRITE_INSTRUCTION_8BIT | (unsigned char)((address & 0x100) >> 5));
	tx_buff[1] = (unsigned char)(address & 0xFF);
	memcpy((tx_buff + 2) , buff, size);
	ret_val = write(dev_fd , tx_buff, size + 2);
	if (ret_val <= 0) {
		printf("ERROR: Writing data to EEPROM failed\n");
		return PCH_ERROR;
	}
	usleep(USLEEP_TIME);
	return PCH_SUCCESS;
}



int pch_spi_read32bit(int dev_fd, int address, unsigned int *buff, unsigned char size)
{
	unsigned int buff_data[size + EEPROM_ADDR_SIZE];
	unsigned int rd_buff[size + EEPROM_ADDR_SIZE];
	int ret_val = 0, i;
	struct spi_ioc_transfer xfer[2];

	memset(buff_data, 0, sizeof buff_data);
	memset(rd_buff, 0, sizeof rd_buff);
	memset(xfer, 0, sizeof xfer);
	buff_data[0] = (READ_INSTRUCTION_32BIT | (unsigned short)((address & 0x100) >> 5));
	buff_data[1] = (unsigned short)(address & 0xFF);
	xfer[0].tx_buf = (unsigned long)buff_data;
	xfer[0].len = (size + EEPROM_ADDR_SIZE) * 4;
	xfer[0].rx_buf = (unsigned long)rd_buff;
	ret_val = ioctl(dev_fd, SPI_IOC_MESSAGE(1), xfer);

	memcpy(buff ,(rd_buff + 2), size * 4);
	return;
}

int pch_spi_read16bit(int dev_fd, int address, unsigned short *buff, unsigned char size)
{
	unsigned short buff_data[size + EEPROM_ADDR_SIZE];
	unsigned short rd_buff[size + EEPROM_ADDR_SIZE];
	int ret_val = 0, i;
	struct spi_ioc_transfer xfer[2];

	memset(buff_data, 0, sizeof buff_data);
	memset(rd_buff, 0, sizeof rd_buff);
	memset(xfer, 0, sizeof xfer);
	buff_data[0] = (READ_INSTRUCTION_16BIT | (unsigned short)((address & 0x100) >> 5));
	buff_data[1] = (unsigned short)(address & 0xFF);
	xfer[0].tx_buf = (unsigned long)buff_data;
	xfer[0].len = (size + EEPROM_ADDR_SIZE) * 2;
	xfer[0].rx_buf = (unsigned long)rd_buff;
	ret_val = ioctl(dev_fd, SPI_IOC_MESSAGE(1), xfer);

	memcpy(buff ,(rd_buff + 2), size * 2);
	return;
}

int pch_spi_write32bit(int dev_fd, int address, unsigned int *buff, unsigned char size)
{
	int ret_val, i;
	struct spi_ioc_transfer xfer;
	unsigned int rx_buff[2];
	unsigned int tx_buff[size + EEPROM_ADDR_SIZE];
	unsigned int wrt_signal;

    printf("bytes: %x \n", size*4);

	memset(&xfer, 0, sizeof xfer);
	memset(tx_buff, 0, sizeof tx_buff);
	memset(rx_buff, 0, sizeof rx_buff);
	xfer.tx_buf = (unsigned long)tx_buff;
	xfer.rx_buf = (unsigned long)rx_buff;
	xfer.len = 4;
	tx_buff[0] = 0x05;
	ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
	if (rx_buff[1] & 0x0C) {
		tx_buff[0] = 0x01;
		tx_buff[1] = rx_buff[1] & ~0x0C;
		ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
		printf("SUCCESS: Block Protection bits cleared\n");
	}

	wrt_signal = WRITE_ENABLE_32BIT;
	ret_val = write(dev_fd ,&wrt_signal, 4);
	if (ret_val <= 0) {
		printf("ERROR: 32bit Write enable failed\n");
		return PCH_ERROR;
	}

	memset(tx_buff,0, sizeof tx_buff);
	tx_buff[0] = (WRITE_INSTRUCTION_32BIT | (unsigned short)((address & 0x100) >> 5));
	tx_buff[1] = (unsigned short)(address & 0xFF);
	memcpy((tx_buff + 2) , buff, size * 4 );
	ret_val = write(dev_fd , tx_buff, (size + 2) *4 );


        printf("written bytes: %d \n", ret_val);


	if (ret_val <= 0) {
		printf("ERROR: Writing data to EEPROM failed\n");
		return PCH_ERROR;
	}
	usleep(USLEEP_TIME);
	return PCH_SUCCESS;
}

int pch_spi_write16bit(int dev_fd, int address, unsigned short *buff, unsigned char size)
{
	int ret_val, i;
	struct spi_ioc_transfer xfer;
	unsigned short rx_buff[2];
	unsigned short tx_buff[size + EEPROM_ADDR_SIZE];
	unsigned short wrt_signal;

        printf("bytes: %x \n", size*2);

	memset(&xfer, 0, sizeof xfer);
	memset(tx_buff, 0, sizeof tx_buff);
	memset(rx_buff, 0, sizeof rx_buff);
	xfer.tx_buf = (unsigned long)tx_buff;
	xfer.rx_buf = (unsigned long)rx_buff;
	xfer.len = 4;
	tx_buff[0] = 0x05;
	ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
	if (rx_buff[1] & 0x0C) {
		tx_buff[0] = 0x01;
		tx_buff[1] = rx_buff[1] & ~0x0C;
		ret_val = ioctl(dev_fd,SPI_IOC_MESSAGE(1), &xfer);
		printf("SUCCESS: Block Protection bits cleared\n");
	}

	wrt_signal = WRITE_ENABLE_16BIT;
	ret_val = write(dev_fd ,&wrt_signal, 2);
	if (ret_val <= 0) {
		printf("ERROR: 16bit Write enable failed\n");
		return PCH_ERROR;
	}

	memset(tx_buff,0, sizeof tx_buff);
	tx_buff[0] = (WRITE_INSTRUCTION_16BIT | (unsigned short)((address & 0x100) >> 5));
	tx_buff[1] = (unsigned short)(address & 0xFF);
	memcpy((tx_buff + 2) , buff, size * 2 );
	ret_val = write(dev_fd , tx_buff, (size + 2) *2 );


        printf("written bytes: %d \n", ret_val);


	if (ret_val <= 0) {
		printf("ERROR: Writing data to EEPROM failed\n");
		return PCH_ERROR;
	}
	usleep(USLEEP_TIME);
	return PCH_SUCCESS;
}




int pch_spi_Transfer_setting(int SPI_fd, user_config_t *init_dat)
{
	unsigned int ret = 0;

	/* Set SPI device word length */
	ret = ioctl(SPI_fd, SPI_IOC_WR_BITS_PER_WORD, &(init_dat->bpw));
	if (ret < 0) {
		printf("ERROR:IOCTL SPI_IOC_WR_BITS_PER_WORD failed\n");
		return PCH_ERROR;
	}
	/* Set SPI device default max speed */
	ret = ioctl(SPI_fd, SPI_IOC_WR_MAX_SPEED_HZ, &(init_dat->speed));
	if (ret < 0) {
		printf("ERROR IOCTL SPI_IOC_WR_MAX_SPEED_HZ failed\n");
		return PCH_ERROR;
	}
	/* Set SPI bit justification */
	ret = ioctl(SPI_fd, SPI_IOC_WR_LSB_FIRST, &(init_dat->lsb));
	if (ret < 0) {
		printf("ERROR: IOCTL SPI_IOC_WR_LSB_FIRST failed\n");
		return PCH_ERROR;
	}
	/* Set SPI mode */
	ret = ioctl(SPI_fd, SPI_IOC_WR_MODE, &(init_dat->mode));
	if (ret < 0) {
		printf("ERROR: IOCTL SPI_IOC_WR_MODE failed\n");
		return PCH_ERROR;
	}
	return PCH_SUCCESS;
}

int main(int argc,char *argv[])
{
	int ret_val;
	int fd;
	int address, data_size, i;
	unsigned char tx_buf[EEPROM_DATA_SIZE], rx_buf[EEPROM_DATA_SIZE];
    	unsigned short tx_buf16[EEPROM_DATA_SIZE], rx_buf16[EEPROM_DATA_SIZE];
	unsigned int tx_buf32[EEPROM_DATA_SIZE], rx_buf32[EEPROM_DATA_SIZE];
	user_config_t init_dat;
	int size_param, speed_param, mode_param;

	if(argc < 7) {
		printf(	"\n"
			"Usage: %s device size speed msb mode address [data [data [data [...]]]]\n"
			" device     Specify the SPI device (/dev/spidevX.X).\n"
			" size       Specify the transfer size (size = 8,16).\n"
			" speed      Specify the transfer speed.\n"
			"            (speed=25000,75000,125000,250000,500000,750000,800000,1000000,2000000).\n"
			" msb        Specify msb or lsb first (msb = msb,lsb).\n"
			" mode       Specify the transfer mode (mode = 0,1,2,3).\n"
			"            mode 0: clock base-0, capture-rising edge, propogate-falling edge .\n"
			"            mode 1: clock base-0, capture-falling edge, propogate-rising edge .\n"
			"            mode 2: clock base-1, capture-falling edge, propogate-rising edge .\n"
			"            mode 3: clock base-1, capture-rising edge, propogate-falling edge .\n"
			" address    Specify the address of the SPI EEPROM (address=000-%03X).\n"
			" data       Specify the write data to the SPI EEPROM (data=00-FF).\n"
			"            When the data is not specified, it reads 8 bytes from SPI EEPROM.\n"
			"            It is possible to spcify the data up to 8 bytes or less.\n"
			"       Defaults: size=8, speed=25000, msb=msb, mode=0.\n"
			"\n", argv[0], EEPROM_ADDR_MASK);
		return PCH_ERROR;
	}
	
	printf("\n--------------------------------------------------------------------------------------\n");
	
	/* Open spi device */
	fd = open(argv[1], O_RDWR);
	if (fd < 0) 
	{
		printf("ERROR :Unable to open the %s device\n", argv[1]);
		printf("\n--------------------------------------------------------------------------------------\n");
		return PCH_ERROR;
		}
	else
		{
		printf("SPI device %s opened. ", argv[1]);}
	
	/* Get and set transfer size */
	size_param = atoi(argv[2]);
        if (size_param == 4)
                {
                init_dat.bpw = TRANSFER_SIZE_4BIT;
                printf("SPI Data Size: 4 .");
                }

	else if (size_param == 8) 
		{
		init_dat.bpw = TRANSFER_SIZE_8BIT;
		printf("SPI Data Size: 8 .");
		}
	else if (size_param == 16) 
		{
		init_dat.bpw = TRANSFER_SIZE_16BIT;
		printf("SPI Data Size: 16 .");
		}
       else if (size_param == 32)
                {
                init_dat.bpw = TRANSFER_SIZE_32BIT;
                printf("SPI Data Size: 32 .");
   	} 
	else 
		{
		printf("ERROR :Invalid Data Size %s . ", argv[2]);
		printf("\n--------------------------------------------------------------------------------------\n");
		close(fd);
		return PCH_ERROR;
		}

	/* Get and set transfer speed */
	speed_param = atoi(argv[3]);
	switch (speed_param) {
	case 25000:
		init_dat.speed = TRANSFER_SPEED_25KBPS;
		printf("Transfer Speed: 25KBPS .");
		break;
	case 75000:
		init_dat.speed = TRANSFER_SPEED_75KBPS;
		printf("Transfer Speed: 75KBPS .");
		break;
	case 125000:
		init_dat.speed = TRANSFER_SPEED_125KBPS;
		printf("Transfer Speed: 125KBPS .");
		break;
	case 250000:
		init_dat.speed = TRANSFER_SPEED_250KBPS;
		printf("Transfer Speed: 250KBPS .");
		break;
	case 500000:
		init_dat.speed = TRANSFER_SPEED_500KBPS;
		printf("Transfer Speed: 500KBPS .");
		break;
	case 750000:
		init_dat.speed = TRANSFER_SPEED_750KBPS;
		printf("Transfer Speed: 750KBPS .");
		break;
	case 800000:
		init_dat.speed = TRANSFER_SPEED_800KBPS;
		printf("Transfer Speed: 800KBPS .");
		break;
	case 1000000:
		init_dat.speed = TRANSFER_SPEED_1MBPS;
		printf("Transfer Speed: 1MBPS .");
		break;
	case 2000000:
		init_dat.speed = TRANSFER_SPEED_2MBPS;
		printf("Transfer Speed: 2MBPS .");
		break;
	default:	
		printf("ERROR :Invalid Speed %s . ", argv[3]);
		printf("\n--------------------------------------------------------------------------------------\n");
		close(fd);
		return PCH_ERROR;
		break;
	}
	
	printf("\n");
	
	/* Get and set msb or lsb first */
	if (!strcmp(argv[4], "msb")) 
		{
		init_dat.lsb = MSB_FIRST;
		printf("Bit Justification: MSB First .");
		}
	else if (!strcmp(argv[4], "lsb")) 
		{
		init_dat.lsb = LSB_FIRST;
		printf("Bit Justification: LSB First .");
		}
	else 
		{
		printf("ERROR :Invalid Bit Justification %s . ", argv[4]);
		printf("\n--------------------------------------------------------------------------------------\n");
		close(fd);
		return PCH_ERROR;
		}
	
	/* Get and set spi transfer mode */
	mode_param = atoi(argv[5]);
	switch (mode_param) {
	case 0:
		init_dat.mode = SPI_MODE_0;
		printf("SPI Mode: 0 .");
		break;
	case 1:
		init_dat.mode = SPI_MODE_1;
		printf("SPI Mode: 1 .");
		break;
	case 2:
		init_dat.mode = SPI_MODE_2;
		printf("SPI Mode: 2 .");
		break;
	case 3:
		init_dat.mode = SPI_MODE_3;
		printf("SPI Mode: 3 .");
		break;
	default:
		printf("ERROR :Invalid SPI Mode %s . ", argv[5]);
		printf("\n--------------------------------------------------------------------------------------\n");
		close(fd);
		return PCH_ERROR;
		break;
	}
				
	/* Get specified address */
	address = strtol(argv[6], NULL, 16);
	address = (unsigned int)address & EEPROM_ADDR_MASK;
	printf("SPI Address : 0x%03X . ", address);
	printf("\n--------------------------------------------------------------------------------------\n");
	/* Check if SPI Device can be initiated with settings */
	ret_val = pch_spi_Transfer_setting(fd,&init_dat);
	
		
	/* Get specified data */
	data_size = min((argc - 7), EEPROM_DATA_SIZE);
	
    if (size_param == 4) 
    {
        for (i = 0; i < data_size; i++)
            tx_buf[i] = strtol(argv[i + 7], NULL, 16);
	}
    else if (size_param == 8) 
    {
        for (i = 0; i < data_size; i++)
            tx_buf[i] = strtol(argv[i + 7], NULL, 16);
	}
    else if (size_param == 16)
    {
        for (i = 0; i < data_size; i++)
 	    tx_buf16[i] = strtol(argv[i + 7], NULL, 16);
	}

    else if (size_param == 32)
    {
        for (i = 0; i < data_size; i++)
            tx_buf32[i] = strtol(argv[i + 7], NULL, 16);
        }

	
 	
	if (argc < 8) {
            printf("--- Read data from SPI EEPROM ---\n");
	if (size_param == 4) 
		{
			    pch_spi_read8bit(fd, address, rx_buf, EEPROM_DATA_SIZE);
			    for(i=0; i < EEPROM_DATA_SIZE; i++)
				    printf("  address=%03x data=%02x \n",(address + i), rx_buf[i]);
			}
        else if (size_param == 8) 
        {
		    pch_spi_read8bit(fd, address, rx_buf, EEPROM_DATA_SIZE);
		    for(i=0; i < EEPROM_DATA_SIZE; i++)
			    printf("  address=%03x data=%02x \n",(address + i), rx_buf[i]);
		}
        else if (size_param == 16)
        {
		    pch_spi_read16bit(fd, address, rx_buf16, EEPROM_DATA_SIZE);
		    for(i=0; i < EEPROM_DATA_SIZE; i++)
			    printf("  address=%03x data=%04x \n",(address + i), rx_buf16[i]);
		}
       else if (size_param == 32)
        {
                    pch_spi_read32bit(fd, address, rx_buf32, EEPROM_DATA_SIZE);
                    for(i=0; i < EEPROM_DATA_SIZE; i++)
                            printf("  address=%03x data=%04x \n",(address + i), rx_buf32[i]);
         }

	} else {
		printf("  size    : %d\n", data_size);


        if (size_param == 4) 
        {
		    for (i = 0; i < data_size; i++)
			    printf("  data    : 0x%02x\n", tx_buf[i]);
		    printf("--- Write data to SPI EEPROM ---\n");
		    pch_spi_write8bit(fd, address, tx_buf, data_size);
        }

        else if (size_param == 8) 
        {
		    for (i = 0; i < data_size; i++)
			    printf("  data    : 0x%02x\n", tx_buf[i]);
		    printf("--- Write data to SPI EEPROM ---\n");
		    pch_spi_write8bit(fd, address, tx_buf, data_size);
        }
        else if (size_param == 16)
        {
		    for (i = 0; i < data_size; i++)
			    printf("  data    : 0x%04x\n", tx_buf16[i]);
		    printf("--- Write data to SPI EEPROM ---\n");
		    pch_spi_write16bit(fd, address, tx_buf16, data_size);
        }
		else if (size_param == 32)
		 {
			 for (i = 0; i < data_size; i++)
				 printf("  data    : 0x%08x\n", tx_buf32[i]);
			 printf("--- Write data to SPI EEPROM ---\n");
			 pch_spi_write32bit(fd, address, tx_buf32, data_size);
		 }

	}

	close(fd);
	return PCH_SUCCESS;
}

