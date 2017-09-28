CC = gcc  
BUILD ?=
SPI1  =  pch_spi_sample
SPI2  =  spi_EEPROM
SPISRC1  =  spi/pch_spi_sample.c           
SPISRC2  =  spi/spi_EEPROM.c            
SPIOBJ1  =  $(SPISRC1:.c=.o)
SPIOBJ2  =  $(SPISRC2:.c=.o)

I2C1  =  pch_i2c_sample
I2CSRC1  =  i2c/pch_i2c_sample.c           
I2COBJ1  =  $(I2CSRC1:.c=.o)

CAN1  =  pch_can_sample
CANSRC1  =  can/pch_can_sample.c           
CANOBJ1  =  $(CANSRC1:.c=.o)

UART1  =  ioh_uart
UARTSRC1  =  uart/ioh_uart.c
UARTSRC1_2  =  uart/crc8.c           
UARTOBJ1  =  $(UARTSRC1:.c=.o)


UART2  =  sigint
UARTSRC2  =  uart/sigint.c
UARTOBJ2  =  $(UARTSRC2:.c=.o)

UART3  =  uart_flowcntl
UARTSRC3  =  uart/uart_flowcntl.c
UARTOBJ3  =  $(UARTSRC3:.c=.o)

UART4  =  uart_line_break
UARTSRC4  =  uart/uart_line_break.c
UARTOBJ4  =  $(UARTSRC4:.c=.o)

RTC1 = rtc_cmos_test
RTCSRC1 = rtc/rtc_cmos_test.c
RTCOBJ1 = $(RTCSRC1:.c=.o)

RTC2 = rtctest
RTCSRC2 = rtc/rtctest.c
RTCOBJ2 = $(RTCSRC2:.c=.o)


HPET1 = hpet-example
HPETSRC1 = hpet/hpet-example.c
HPETOBJ1 = $(HPETSRC1:.c=.o)

HPET2 = hpet-test
HPETSRC2 = hpet/hpet-test.c
HPETOBJ2 = $(HPETSRC2:.c=.o)

WATCHY1 = watchy1
WATCHYSRC1 = watchdog/watchy1.c
WATCHYOBJ1 = $(WATCHYSRC1:.c=.o)

WATCHY3 = watchy3
WATCHYSRC3 = watchdog/watchy3.c
WATCHYOBJ3 = $(WATCHYSRC3:.c=.o)

.PHONY: all, install, clean

all:clean $(SPI1) $(SPI2) $(HPET1) $(I2C1) $(RTC1) $(RTC2) $(CAN1) $(UART1) $(UART2) $(UART3) $(UART4) $(WATCHY1) $(WATCHY3) #$(HPET2) 


#all: $(SPI1) 

$(SPI1) :
	echo 'Building $(BUILD) binaries' 
	$(CC) -o $(SPI1) $(SPISRC1) $(BUILD)  ;mv $(SPI1) spi/
#$(SPI1) : $(SPIOBJ1)
#	$(CC) $(SPIOBJ1) -o $(SPI1) ; mv $(SPI1) $(BINDIR) 

$(SPI2) :
	$(CC) -o $(SPI2) $(SPISRC2) $(BUILD); mv $(SPI2) spi/

$(I2C1) :
	$(CC) -o $(I2C1) $(I2CSRC1) $(BUILD); mv $(I2C1) i2c/

$(CAN1) :
	$(CC) -o $(CAN1) $(CANSRC1) $(BUILD); mv $(CAN1) can/

$(UART1) :
	$(CC) -o $(UART1) $(UARTSRC1) $(BUILD) ; mv $(UART1) uart/

$(UART2) :
	$(CC) -o $(UART2) $(UARTSRC2) -I. $(BUILD) ; mv $(UART2) uart/

$(UART3) :
	$(CC) -o $(UART3) $(UARTSRC3) -I. $(BUILD) ; mv $(UART3) uart/

$(UART4) :
	$(CC) -o $(UART4) $(UARTSRC4) -I. $(BUILD) ; mv $(UART4) uart/

$(HPET2) :
	$(CC) -o $(HPET2) $(HPETSRC2) $(BUILD) ; mv $(HPET2) hpet/

$(RTC1) :
	$(CC) -o $(RTC1) $(RTCSRC1) $(BUILD) ; mv $(RTC1) rtc/

$(RTC2) :
	$(CC) -o $(RTC2) $(RTCSRC2) $(BUILD) ; mv $(RTC2) rtc/

$(HPET1) :
	$(CC) -o $(HPET1) $(HPETSRC1) $(BUILD) ; mv $(HPET1) hpet/

$(WATCHY1) :
	$(CC) -o $(WATCHY1) $(WATCHYSRC1) $(BUILD) ; mv $(WATCHY1) watchdog/

$(WATCHY3) :
	$(CC) -o $(WATCHY3) $(WATCHYSRC3) $(BUILD) ; mv $(WATCHY3) watchdog/

