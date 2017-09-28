
/*Return testcase values*/
#define IOH_TEST_SUCCESS    	(0)
#define IOH_TEST_ERROR      	(1)

/*Baud rate constants*/
#define BAUD_RATE_50		(B50)
#define BAUD_RATE_300		(B300)
#define BAUD_RATE_600		(B600)
#define BAUD_RATE_1200		(B1200)
#define BAUD_RATE_2400		(B2400)
#define BAUD_RATE_4800		(B4800)
#define BAUD_RATE_9600		(B9600)
#define BAUD_RATE_19200		(B19200)
#define BAUD_RATE_38400		(B38400)
#define BAUD_RATE_57600		(B57600)
#define BAUD_RATE_115200	(B115200)
#define BAUD_RATE_230400	(B230400)
#define BAUD_RATE_460800	(B460800)
#define BAUD_RATE_921600	(B921600)
#define BAUD_RATE_1000000	(B1000000)
#define BAUD_RATE_2000000	(B2000000)
#define BAUD_RATE_3000000	(B3000000)
#define BAUD_RATE_4000000	(B4000000)

/*Data size to be send*/
#define SIZE_5KB                (5 * 1024)
#define SIZE_2KB                (2 * 1024)
#define SIZE_256BYTES           (256)
#define SIZE_512BYTES           (512)
#define SIZE_1KB                (1000)
#define SIZE_64B                (64)

/*Databits size*/
#define DATABITS_SIZE_8		(CS8)
#define DATABITS_SIZE_5		(CS5)
#define DATABITS_SIZE_6		(CS6)
#define DATABITS_SIZE_7		(CS7)

/*stop bits */
#define STOPBITS_1		(0)
#define STOPBITS_2		(CSTOPB)
#define STOPBITS_1_5		(CSTOPB)

/*parity*/
#define PARITY_OFF		(0)
#define PARITY_ON		(PARENB)
#define PARITY_EVEN		(0)
#define PARITY_ODD		(PARODD)
#define PARITY_SPACE		(CMSPAR)
#define PARITY_MARK		(CMSPAR | PARODD)
#define STICKY_PARITY		(1)
#define STICKY_OFF		(0)

/*flow control*/
#define HRDWRE_FLOW_CONTROL	(1)
#define SFTWRE_FLOW_CONTROL	(2)
#define NO_FLOW_CONTROL		(0)

#define UART_FIFO_SIZE	    	(1000)

/*Structure used to pass user port configuration values*/
typedef struct user_UART_config {
        long baud_rate;
        long Databits;
        long stopbits;
        long parity_stat;
        long parity_bits;
        char sticky_parity;
        int data_size;
        unsigned int  mask;
        char flow_control;
} user_UART_config_t;

/*Function prototypes*/
int UART_receive(int size,int dev_fd, char *buf_ptr);
int UART_send(int size,int dev_fd,unsigned int mask,int type, int fill, char *buf_ptr);
int Packet_receive(int UART_fd,user_UART_config_t *uart_config,int type, int single_flow, int silent_mode);
int Packet_transfer(int UART_fd,user_UART_config_t *uart_config,int type, int single_flow, int silent_mode);
int Continous_receive(int UART_fd,user_UART_config_t *uart_config,int iter,int type, int single_flow, int silent_mode);
int Continous_transfer(int UART_fd,user_UART_config_t *uart_config,int iter, int type, int single_flow, int silent_mode);
