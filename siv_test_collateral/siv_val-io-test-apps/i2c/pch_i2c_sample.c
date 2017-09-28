/*
 * Sample program for I2C on Intel(R) Platform Controller Hub EG20T.
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
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <linux/ioctl.h>
//#include <linux/i2c.h>
#include <linux/i2c-dev.h>

#define PCH_SUCCESS		(0)
#define PCH_ERROR		(1)
#define EEPROM_ADDRESS		(0x50)
#define ADDRESS_SIZE_7BIT	(0)
#define ADDRESS_SIZE_10BIT	(1)
#define EEPROM_ADDR_SIZE	(2)
#define EEPROM_DATA_SIZE	(255)
#define EEPROM_ADDR_MASK	(0x7FFF) /* The maxmum memory size is 32K bytes */
#define USLEEP_TIME		(10000)
#define min(a, b)		((a) < (b) ? (a) : (b))

typedef struct Init_dat {
	long addr;		/* To sepcify the slave address */
	long addr_size;	/* Specify wether 7-bit or 10-bit */
}Init_dat_t;

int pch_i2c_write(int dev_fd, int address, unsigned char *buff, unsigned char size)
{
	int ret;
	//unsigned char tx_buff[size + EEPROM_ADDR_SIZE];
	unsigned char tx_buff[size];

	memset(tx_buff, 0, sizeof tx_buff);
	//tx_buff[0]= (address >> 8) & 0xFF;
	//tx_buff[1]= address & 0xFF;
	//memcpy((tx_buff + 2) , buff, size);
	//ret = write(dev_fd, tx_buff, size + EEPROM_ADDR_SIZE);
	memcpy(tx_buff , buff, size);
	ret = write(dev_fd, tx_buff, size);
	
	if (!ret) {
		printf("ERROR: Failed to write the data to the EEPROM[1]\n");
		return PCH_ERROR;
	} else {
		printf("Data sucessfully written to the EEPROM[1].\n");
		printf("Check Validity of Data at the Receiving End.\n");	
		usleep(USLEEP_TIME);
        	return PCH_SUCCESS;
	}
}

int pch_i2c_read(int dev_fd, int address, unsigned char *buff, unsigned char size)
{
	int ret;
	unsigned char add_buff[2];
	unsigned char rx_buff[size + EEPROM_ADDR_SIZE];

	memset(rx_buff, 0, sizeof rx_buff);
	//add_buff[0]= (address >> 8) & 0xFF;
	//add_buff[1]= address & 0xFF;
	//ret = write(dev_fd, add_buff, EEPROM_ADDR_SIZE);
	//if (ret <= 0) {
	//	printf("ERROR: Failed to specify address location"
	//		" to EEPROM from which data to be read[1]\n");
	//	printf("Check Slave Address Settings on Receiving End matches address: 0x%04X \n",address);
	//	return PCH_ERROR;
	//}
	//usleep(USLEEP_TIME);

	ret = read(dev_fd, rx_buff, size);
	if (ret <= 0) {
		printf("ERROR: Failed to read data from eeprom[1]\n");
		return PCH_ERROR;
	}
	memcpy(buff, rx_buff, size);
	return PCH_SUCCESS;
}

int i2c_data_send_setting(int I2C_fd, Init_dat_t *info)
{
	int ret = 0;

	/* To set the slave address size*/
	ret = ioctl(I2C_fd, I2C_TENBIT, info->addr_size);
	if (ret) {
		printf("ERROR: IOCTL I2C_TENBIT failed to set address size \n");
		return PCH_ERROR;
	}
	/* To set the slave address*/
	ret = ioctl(I2C_fd, I2C_SLAVE, info->addr);
	if (ret) {
		printf("ERROR: IOCTL I2C_SLAVE failed\n");
		return PCH_ERROR;
	}

	return PCH_SUCCESS;
}

int main(int argc, char *argv[])
{
	int ret, write_ret, read_ret;
	int fd;
	int address, data_size, i;
	unsigned char tx_buf[EEPROM_DATA_SIZE], rx_buf[EEPROM_DATA_SIZE];
	Init_dat_t  user_conf;

	if(argc < 3) {
		printf(	"\n"
			"Usage: %s device address [data [data [data [...]]]]\n"
			" device     Specify the I2C device (/dev/i2c-X).\n"
			" address    Specify the address of the I2C EEPROM (address=0000-%03X).\n"
			" data       Specify the write data to the I2C EEPROM (data=00-FF).\n"
			"            When the data is not specified, it reads 255 bytes from I2C EEPROM.\n"
			"            It is possible to spcify the data up to 255 bytes or less.\n"
			"\n", argv[0], EEPROM_ADDR_MASK);
		return PCH_ERROR;
	}
	/* Open device */
	fd = open(argv[1], O_RDWR);
	if (fd < 0) {
                printf("ERROR :Unable to open the %s device\n", argv[1]);
		return PCH_ERROR;
	}

	/* Get specified address and data */
	address = strtol(argv[2], NULL, 16);
	address = (unsigned int)address & EEPROM_ADDR_MASK;
	data_size = min((argc - 3), EEPROM_DATA_SIZE);
	for (i = 0; i < data_size; i++)
		tx_buf[i] = strtol(argv[i + 3], NULL, 16);
	printf("--- Accepted parameter ---\n");
	printf("  address : 0x%04X\n", address);
	
	user_conf.addr = address;
	
	if (address > 119){
		printf ("Debug: Using 10 bit addressing mode\n");
		user_conf.addr_size = ADDRESS_SIZE_10BIT;
	} else {
		printf ("Debug: Using 7 bit addressing mode\n");
		user_conf.addr_size = ADDRESS_SIZE_7BIT;
	}

	ret = i2c_data_send_setting(fd,&user_conf);
	if (ret)
		return PCH_ERROR;

	/* Read Data Only */
	if (argc < 4) {
		printf("--- Read data from I2C EEPROM ---\n");
		read_ret=pch_i2c_read(fd, address, rx_buf, EEPROM_DATA_SIZE);
		for(i=0; i < EEPROM_DATA_SIZE; i++)
			printf("  address=%03x data=%02x \n",(address + i), rx_buf[i]);
			
			if (!read_ret) {
			printf("SUCCESS: Data sucessfully read from the EEPROM[1].\n");
			} else {
			printf("ERROR: Data not read from the EEPROM[1].\n");
			}		
	
	/* Write then Read Data */
	} else {
		printf("  size    : %d\n", data_size);
		for (i = 0; i < data_size; i++)
			printf("  data    : 0x%02x\n", tx_buf[i]);
		printf("--- Write data to I2C EEPROM ---\n");
		write_ret=pch_i2c_write(fd, address, tx_buf, data_size);
		
		/*if (!write_ret) {
			printf("--- Read data from I2C EEPROM ---\n");
			read_ret=pch_i2c_read(fd, address, rx_buf, EEPROM_DATA_SIZE);
			for(i=0; i < EEPROM_DATA_SIZE; i++)
			printf("  address=%03x data=%02x \n",(address + i), rx_buf[i]);
			
			if (!read_ret) {
			printf("SUCCESS: Data sucessfully read from the EEPROM[1].\n");
			} else {
			printf("ERROR: Data not read from the EEPROM[1].\n");
			}
		}*/
	}

	

        close(fd);
        return PCH_SUCCESS;
}
