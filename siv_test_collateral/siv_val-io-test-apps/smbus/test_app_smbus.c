/*
 * SMBUS Test Application for User Space Access
 *
 * Author: Chew, Kean Ho <kean.ho.chew@intel.com>
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
#include <linux/i2c.h>
#include <linux/i2c-dev.h>

#define SUCCESS				0
#define ERROR				1
#define ADDRESS_SIZE_7BIT		0
#define ADDRESS_SIZE_10BIT		1
#define HEX				16
#define DEC				10
#define ADDRESS_MASK			0x3FF
#define SLEEP_TIME			10000
#define DATA_PARAM			8
#define APP_PARAM_COUNT			DATA_PARAM
#define USLEEP_TIME			10000
int main(int argc, char *argv[]){
	int ret, fd, command, i;
	unsigned long address;
	union i2c_smbus_data data;
	struct i2c_smbus_ioctl_data io_settings;

	/* Check Input */
	if(argc < (APP_PARAM_COUNT)){
		printf( "\n"
			"Usage: %s Device Type R/W PEC Add_bit Address Command (Data1 Data2 ...)\n"
			"Device		Specify SMBus device E.g (/dev/i2c-X) 			\n"
			"Type 		0 = Byte (8 bit)   		; 1 = Word (16 bit)	\n"
			"		2 = Proc Call (write only)	; 3 = Block Data	\n"
			"		4 = Blk Proc Call (write only) 	; 5 = Blk I2C		\n"
			"R/W		0 = Read	   		; 1 = Write		\n"
                        "PEC		0 = No PEC Feature 		; 1 = With PEC Feature	\n"
			"Add_bit		0 = 7-bit Address  		; 1 = 10-bit Address	\n"
			"Address		Specify the target address.			\n" 
			"			E.g: 50 means 0x50 				\n"
			"Command		Specify the SMBUS command.  			\n"
			"			In I2C Mode (write), this is the 1st Data.	\n"
			"			In I2C Mode (read), If SMBus is to test with	\n"
			"				I2C device, Command becomes your	\n"
			"				# of reads and as 1st data simultenously\n"
			"-----------------------------------------------------------------------\n"
			"Data		Specify Write data when R/W is Write		 	\n"
			"		Type = Byte: Only set Data1 for 8 bit data		\n"
			"			e.g: '55' for 0x55				\n"
			"		Type = Word: Only set Data1 for 16 bit data		\n"
			"			e.g: '1234' for 0x1234				\n"
			"		Type = Proc Call: Only set Data1 for 16-bit data	\n"
			"			e.g: '1234' for 0x1234				\n"
			"		Type = Block Write, I2C Block Write, Block Proc Call:	\n"
			"			Set 8 bit data in chain, up to 32 times max	\n"
			"									\n",
			argv[0]);
		
		return ERROR;
	}
	
	/* Open Device */
	fd = open(argv[1], O_RDWR);
	if (fd < 0) {
		printf("ERROR: Unable to open device: %s \n", argv[1]);
		return ERROR;
	}

	/* Set Addressing Bit */
	switch (strtol(argv[5], NULL, HEX)){
	case 0:
		if(ioctl(fd, I2C_TENBIT, ADDRESS_SIZE_7BIT)){
                	printf("ERROR: Unable to set 7-bit Addressing. \n");
                	return ERROR;
		}
		printf("NOTE: Set 7-Bit Addressing. \n");
		break;
	case 1:
		if(ioctl(fd, I2C_TENBIT, ADDRESS_SIZE_10BIT)){
                	printf("ERROR: Unable to set 10-bit Addressing. \n");
                	return ERROR;
        	}
		printf("NOTE: Set 10-Bit Addressing. \n");
		break;
	default:
		printf("ERROR: Invalid input for Address-Bit. \n");
		return ERROR;
	}

	/* Set Slave Address */
        if (ioctl(fd, I2C_SLAVE, (strtol(argv[6], NULL, HEX) & ADDRESS_MASK))) {
                printf("ERROR: IOCTL I2C_SLAVE failed\n");
                return ERROR;
        }
	printf("NOTE: Address: 0x%x \n", (strtol(argv[6], NULL, HEX) & ADDRESS_MASK));

	/* Set PEC Feature */
        switch (strtol(argv[5], NULL, HEX)){
        case 0:
        	if(ioctl(fd, I2C_PEC, 0)){ 
                	printf("ERROR: Unable to set PEC to OFF. \n");
                	return ERROR;
        	}
		printf("NOTE: PEC is now turn OFF \n");
                break;
        case 1:
		if(ioctl(fd, I2C_PEC, 1)){ 
                	printf("ERROR: Unable to set PEC to ON. \n");
                	return ERROR;
        	}
		printf("NOTE: PEC is now turn ON \n");
                break;
        default:
                printf("ERROR: Invalid input for PEC Features. \n");
		return ERROR;
        }
	
	/* Setting Data Size and Read/Write Data */
	switch(strtol(argv[2], NULL, DEC)){
	case 0:
		io_settings.size = I2C_SMBUS_BYTE_DATA;
		printf("NOTE: SMBUS set to BYTE Transfer \n");
		break;
	case 1:
		io_settings.size = I2C_SMBUS_WORD_DATA;
		printf("NOTE: SMBUS set to WORD Transfer \n");
		break;
	case 2:
		io_settings.size = I2C_SMBUS_PROC_CALL;
		printf("NOTE: SMBUS set to PROC_CALL Transfer \n");
		break;
	case 3:
		io_settings.size = I2C_SMBUS_BLOCK_DATA;
		printf("NOTE: SMBUS set to BLOCK_DATA Transfer \n");
		break;
	case 4:
		/* SMBus 2.0 */
		io_settings.size = I2C_SMBUS_BLOCK_PROC_CALL;
		printf("NOTE: SMBUS2.0 set to BLOCK_PROC_CALL Tranfer \n");
		break;
	case 5:
		/* SMBus 2.0 */
		io_settings.size = I2C_SMBUS_I2C_BLOCK_DATA;
		printf("NOTE: SMBUS2.0 set to I2C_BLOCK_DATA Transfer \n");
                break;
	default:
		printf("ERROR: Invalid Size Specifications \n");
		return ERROR;
	}

       /* Setting SMBus to Read/Write Mode */
        switch(strtol(argv[3], NULL, DEC)){
        case 0:
		switch(io_settings.size){
		case I2C_SMBUS_BYTE_DATA:
		case I2C_SMBUS_WORD_DATA:
		case I2C_SMBUS_I2C_BLOCK_DATA:
		case I2C_SMBUS_BLOCK_DATA:
                	io_settings.read_write = I2C_SMBUS_READ;
                	printf("NOTE: SMBUS set to Read \n");
			break;
		case I2C_SMBUS_PROC_CALL:
		case I2C_SMBUS_BLOCK_PROC_CALL:
			printf("ERRPR: Proc Calls / Block Proc Call needs to be in write mode \n");
			return ERROR;
		}
                break;
        case 1:
                if(argc < (DATA_PARAM + 1)){
                        printf("ERROR: No write data specified! \n");
                        return ERROR;
                }

                switch(io_settings.size){
                case I2C_SMBUS_BYTE_DATA:
                case I2C_SMBUS_WORD_DATA:
                case I2C_SMBUS_I2C_BLOCK_DATA:
                case I2C_SMBUS_BLOCK_DATA:
		case I2C_SMBUS_PROC_CALL:
		case I2C_SMBUS_BLOCK_PROC_CALL:
                        io_settings.read_write = I2C_SMBUS_WRITE;
                        printf("NOTE: SMBUS set to Write \n");
                        break;
                }
		break;
	default:
		printf("ERROR: Invalid input for R/W. \n");
		return ERROR;
	}
        
	/* Set Writing Data for Write Mode if any. Else, setup data memory for Read/Write */
	switch(io_settings.read_write){
	case I2C_SMBUS_WRITE:
		switch(io_settings.size){
		case I2C_SMBUS_BYTE_DATA:
                        data.byte = strtol(argv[DATA_PARAM], NULL, HEX);
                        break;
		case I2C_SMBUS_PROC_CALL:
		case I2C_SMBUS_WORD_DATA:
		default:
			data.word = strtol(argv[DATA_PARAM], NULL, HEX);
			break;
		case I2C_SMBUS_BLOCK_DATA:
		case I2C_SMBUS_BLOCK_PROC_CALL:
                        data.block[0] = (argc - APP_PARAM_COUNT); //First block is used as counter
                        for (i = 0; i < (argc - APP_PARAM_COUNT); i++){
                                if(i >= I2C_SMBUS_BLOCK_MAX)
                                        break;
                                data.block[i + 2] = strtol(argv[i + DATA_PARAM], NULL, HEX);
                        }
                        break;
		case I2C_SMBUS_I2C_BLOCK_DATA:
			data.block[0] = (argc - APP_PARAM_COUNT); //First block is used as counter
	                for (i = 0; i < (argc - APP_PARAM_COUNT); i++){
				if(i >= I2C_SMBUS_BLOCK_MAX)
					break;
				data.block[i + 1] = strtol(argv[i + DATA_PARAM], NULL, HEX);
			}
			break;
		}
		printf("NOTE: Setting Write data \n");
	case I2C_SMBUS_READ:
		switch(io_settings.size){
                case I2C_SMBUS_I2C_BLOCK_DATA:
                        data.block[0] = strtol(argv[7], NULL, HEX);
		case I2C_SMBUS_BYTE_DATA:
		case I2C_SMBUS_WORD_DATA:
		case I2C_SMBUS_PROC_CALL:
		case I2C_SMBUS_BLOCK_DATA:
		case I2C_SMBUS_BLOCK_PROC_CALL:
			break;
		}
		break;
	}
	io_settings.data = &data;

	/* Setting Command for SMBus */
	io_settings.command  = strtol(argv[7], NULL, HEX);
		
	/* Execute Read/Write */
	if(ioctl(fd, I2C_SMBUS, &io_settings)) {
		printf("ERROR: SMBUS read/write failed to execute. \n");
		return ERROR;
	}
	printf("NOTE: Executed SMBUS Read/Write. \n");

	usleep(USLEEP_TIME);

	switch(io_settings.read_write){
	case I2C_SMBUS_READ:
		printf("Data Read: ");
		switch(io_settings.size){
		case I2C_SMBUS_BYTE_DATA:
			printf("[Byte] 0x%x \n", data.byte);
			break;
		case I2C_SMBUS_WORD_DATA:
			printf("[Word] 0x%x \n", data.word);
			break;
		case I2C_SMBUS_PROC_CALL:
			printf("[Proc_Call] 0x%x \n", data.word);
			break;
		case I2C_SMBUS_BLOCK_DATA:
		case I2C_SMBUS_BLOCK_PROC_CALL:
		case I2C_SMBUS_I2C_BLOCK_DATA:
			printf("[Block] 	\n");
                        for (i = 0; i <= I2C_SMBUS_BLOCK_MAX; i++)
                                printf("	%d: 0x%x \n", i, data.block[i]);
		default:
                        break;
		}
		break;
	case I2C_SMBUS_WRITE:
		printf("Data Read After Write: ");
		switch(io_settings.size){
                case I2C_SMBUS_PROC_CALL:
                        printf("[Proc_Call] 0x%x \n", data.word);
                        break;
                case I2C_SMBUS_BLOCK_PROC_CALL:
                        printf("[Block]  \n");
                        for (i = 0; i <= I2C_SMBUS_BLOCK_MAX; i++)
                                printf("        %d: 0x%x \n", i, data.block[i]);
		case I2C_SMBUS_I2C_BLOCK_DATA:
		case I2C_SMBUS_BYTE_DATA:
		case I2C_SMBUS_WORD_DATA:
		case I2C_SMBUS_BLOCK_DATA:
                default:
                        break;
                }
		break;
		
	}

	return SUCCESS;	
}
