/*
 * Based on the
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

#define SUCCESS			(0)
#define ERROR			(1)

#define EEPROM_DATA_SIZE	(200)
#define TX_8_BIT		(8)
#define TX_16_BIT		(16)

#define LSB			(1)
#define MSB			(0)

#define USLEEP_TIME		(5000)
#define min(a, b)		((a) < (b) ? (a) : (b))

typedef struct user_config {
	int bpw;
	int speed;
	int lsb;
	int mode;
}user_config_t;



int main(int argc,char *argv[])
{

	/*  Declaring Variables  */
	/*=======================*/
	unsigned char tx_buf[EEPROM_DATA_SIZE], rx_buf[EEPROM_DATA_SIZE];
    unsigned short tx_buf16[EEPROM_DATA_SIZE], rx_buf16[EEPROM_DATA_SIZE];
	int ret;
	int Device;
	int data_size, i;
	user_config_t spi_config;
	int size_param, speed_param, mode_param;
	struct spi_ioc_transfer SPI_Xfer[2];
	
	/*  Argument Checking    */
	/*=======================*/		
	if(argc < 7) 
	{
		printf(	""
			"Usage: %s device size speed msb mode [data [data [data [...]]]]\n"
			" device     Specify the SPI device (/dev/spidevX.X).\n"
			" size       Specify the transfer size (size = 8,16).\n"
			" speed      Specify the transfer speed. It will be written directly.\n"
			"            (E.g: 25000,75000,125000,250000,500000,750000,\n"
			"                  800000,1000000,10000000,etc.)\n"
			" msb        Specify msb or lsb first (msb = msb,lsb).\n"
			" mode       Specify the transfer mode (mode = 0,1,2,3).\n"
			"            mode 0: clock base-0, capture-rising edge, propogate-falling edge .\n"
			"            mode 1: clock base-0, capture-falling edge, propogate-rising edge .\n"
			"            mode 2: clock base-1, capture-falling edge, propogate-rising edge .\n"
			"            mode 3: clock base-1, capture-rising edge, propogate-falling edge .\n"
			" data       Specify the write data to the SPI EEPROM\n"
			"            For reading, specify [00 00 00 ...]\n"
			"                where number of 00 indicates number of bytes to be read.\n"			
			"            Best work with minimum of 2 bytes. Max 200 Bytes. \n"
			"       Defaults: size=8, speed=25000, msb=msb, mode=0.\n"
			"\n", argv[0]);

		return ERROR;
	}
	
	printf("[DEBUG]: Begin SPI Test App.\n");

	
	/*  Open SPI Device      */
	/*=======================*/	
	Device = open(argv[1], O_RDWR);
	if(Device < 0){
		printf("ERROR :Unable to open the %s device.\n", argv[1]);
		printf("-------------------------------------------------------------------------------\n\n\n");
		return ERROR;
		
	}
	else {
		printf("[DEBUG]:SPI device %s opened. \n", argv[1]);
	}

	
	
	/*Get and Set Transfers Size*/
	/*==========================*/
	size_param = atoi(argv[2]);	
	if(size_param == 8){
		spi_config.bpw = TX_8_BIT;
		printf("[DEBUG]:SPI Transfer Size Set: 8-bit.\n");
	}
	else if (size_param == 16){
		spi_config.bpw = TX_16_BIT;
		printf("[DEBUG]:SPI Transfer Size Set: 16-bit.\n");
	}
	else{
		printf("ERROR :Invalid Data Size %s .\n", argv[2]);
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}

	

	/*Get and Set Transfers Speed*/
	/*===========================*/	
	speed_param = atoi(argv[3]);
	spi_config.speed = speed_param;
	printf("[DEBUG]:SPI Transfer Speed Set to: %s Hz.\n", argv[3]);
	
	
	
	/* Get and Set First MSB/LSB */
	/*===========================*/	
	if(!strcmp(argv[4], "msb")){
		spi_config.lsb = MSB;
		printf("[DEBUG]:SPI Transfer Endianness Set: MSB First.\n");
	}
	else if (!strcmp(argv[4], "lsb")){
		spi_config.lsb = LSB;
		printf("[DEBUG]:SPI Transfer Endianness Set: LSB First.\n");
	}
	else{
		printf("ERROR :Invalid 1st MSB/LSB Argument: %s .\n", argv[4]);
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;	
	}
	
	
	/* Get and Set SPI Transfer Mode */
	/*===============================*/	
	mode_param = atoi(argv[5]);
	switch (mode_param) {
	case 0:
		spi_config.mode = SPI_MODE_0;
		printf("[DEBUG]:SPI Mode: 0.\n");
		break;
	case 1:
		spi_config.mode = SPI_MODE_1;
		printf("[DEBUG]:SPI Mode: 1.\n");
		break;
	case 2:
		spi_config.mode = SPI_MODE_2;
		printf("[DEBUG]:SPI Mode: 2.\n");
		break;
	case 3:
		spi_config.mode = SPI_MODE_3;
		printf("[DEBUG]:SPI Mode: 3.\n");
		break;
	default:
		printf("ERROR :Invalid SPI Mode: %s .\n", argv[5]);
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
		break;
	}

	
	/* Setting SPI Device with All Settings*/
	/*=====================================*/	
	ret = 0;
	/* Set SPI device word length */
	ret = ioctl(Device, SPI_IOC_WR_BITS_PER_WORD, &(spi_config.bpw));
	if (ret < 0) {
		printf("ERROR:IOCTL SPI_IOC_WR_BITS_PER_WORD failed\n");
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}
	
	ret = 0;
	/* Set SPI device default max speed */
	ret = ioctl(Device, SPI_IOC_WR_MAX_SPEED_HZ, &(spi_config.speed));
	if (ret < 0) {
		printf("ERROR IOCTL SPI_IOC_WR_MAX_SPEED_HZ failed\n");
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}
	
	ret = 0;
	/* Set SPI bit justification */
	ret = ioctl(Device, SPI_IOC_WR_LSB_FIRST, &(spi_config.lsb));
	if (ret < 0) {
		printf("ERROR: IOCTL SPI_IOC_WR_LSB_FIRST failed\n");
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}
	
	ret = 0;
	/* Set SPI mode */
	ret = ioctl(Device, SPI_IOC_WR_MODE, &(spi_config.mode));
	if (ret < 0) {
		printf("ERROR: IOCTL SPI_IOC_WR_MODE failed\n");
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}
	
	printf("[DEBUG]:SPI Device has been configured according to provided settings.\n");	
	
	
	
	/* Processing Data For Transmission */
	/*=====================================*/
	data_size = min((argc - 6), EEPROM_DATA_SIZE);
	printf("[DEBUG]: Data Size : %d .\n", data_size);	
    	if (size_param == 8) {
        	for (i = 0; i < data_size; i++)
            		tx_buf[i] = strtol(argv[i + 6], NULL, 16);
	}
    	else if (size_param == 16){	
        	for (i = 0; i < data_size; i++)
			tx_buf16[i] = strtol(argv[i + 6], NULL, 16);
	}
	
	
	/* Transmit/Receive Data */
	/*=====================================*/
	printf("[DEBUG]: SPI Transmission Begin. \n");	
	//Flush Memory
	memset(&SPI_Xfer, 0, sizeof SPI_Xfer);
	memset(rx_buf, 0, sizeof rx_buf);
	
	//Write to SPI
    	if (size_param == 8) {
		SPI_Xfer[0].tx_buf = (unsigned long)tx_buf;
		SPI_Xfer[0].len = data_size;
		SPI_Xfer[0].rx_buf = (unsigned long)rx_buf;
	}
	else if (size_param == 16){	
		SPI_Xfer[0].tx_buf = (unsigned long)tx_buf16;
		SPI_Xfer[0].len = data_size;
		SPI_Xfer[0].rx_buf = (unsigned long)rx_buf16;
	}
	


	printf("Source/Destination Buffer Address = %lx \n",(long unsigned int)&SPI_Xfer);
		//Check SPI Status
	ret = ioctl(Device, SPI_IOC_MESSAGE(2), SPI_Xfer);
	if (ret < 0) {
		printf("ERROR: SPI_IOC_MESSAGE: %d . \n", ret);
		printf("-------------------------------------------------------------------------------\n\n\n");
		close(Device);
		return ERROR;
	}

	/*  		 Printing Output	   	   */
	/*=================================================*/
	printf("-------------------------------------------------------------------------------\n");
	printf("Data Transmit (Data Size: %2d, Status: %2d): ", data_size, ret);

	if(size_param ==8){
		for(i=0; i < data_size; i++)
			printf(" %02x", tx_buf[i]);
	}
	else if (size_param==16){
		for(i=0; i < data_size; i++)
			printf(" %04x", tx_buf16[i]);	
	}

	printf("\n");
	printf("Data Received (Data Size: %2d, Status: %2d): ", data_size, ret);

	if(size_param == 8){
		for(i=0; i < data_size; i++)
			printf(" %02x", rx_buf[i]);
	}
	else if (size_param == 16){
		for(i=0; i < data_size; i++)
			printf(" %04x", rx_buf16[i]);	
	}

	printf("\n");
	printf("-------------------------------------------------------------------------------\n\n\n");

	
	
	/*  End of SPI Test App Prototype */
	/*=====================================*/	
	close(Device);
	return SUCCESS;	
}
