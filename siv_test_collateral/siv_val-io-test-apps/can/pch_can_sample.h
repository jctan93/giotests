enum sock_type {
	SOCK_STREAM	= 1,
	SOCK_DGRAM	= 2,
	SOCK_RAW	= 3,
	SOCK_RDM	= 4,
	SOCK_SEQPACKET	= 5,
	SOCK_DCCP	= 6,
	SOCK_PACKET	= 10,
};
typedef unsigned short   sa_family_t;
typedef unsigned int canid_t;
#define AF_CAN          29      /* Controller Area Network      */
#define PF_CAN          AF_CAN
#define IFNAMSIZ        16
#define CAN_RAW         1 /* RAW sockets */
#define SIOCGIFINDEX    0x8933          /* name -> if_index mapping     */
#define SIOGIFINDEX     SIOCGIFINDEX    /* misprint compatibility :-)   */
#define CAN_SFF_MASK 0x000007FFU /* standard frame format (SFF) */

#define SOL_CAN_BASE 100
#define SOL_CAN_RAW (SOL_CAN_BASE + CAN_RAW)
#define STANDARD_FRAME                       (0)
#define CAN_SFF_MASK 0x000007FFU
enum {
        CAN_RAW_FILTER = 1,     /* set 0 .. n can_filter(s)          */
        CAN_RAW_ERR_FILTER,     /* set filter for error frames       */
        CAN_RAW_LOOPBACK,       /* local loopback (default:on)       */
        CAN_RAW_RECV_OWN_MSGS   /* receive my own msgs (default:off) */
};

struct can_filter {
        canid_t can_id;
        canid_t can_mask;
};

struct sockaddr_can {
        sa_family_t can_family;
        int         can_ifindex;
        union {
                /* transport protocol class address information (e.g. ISOTP) */
                struct { canid_t rx_id, tx_id; } tp;

                /* reserved for future CAN protocols address information */
        } can_addr;
};

struct sockaddr {
        sa_family_t     sa_family;      /* address family, AF_xxx       */
        char            sa_data[14];    /* 14 bytes of protocol address */
};

struct ifmap {
        unsigned long mem_start;
        unsigned long mem_end;
        unsigned short base_addr; 
        unsigned char irq;
        unsigned char dma;
        unsigned char port;
        /* 3 bytes spare */
};
typedef struct {
        unsigned short encoding;
        unsigned short parity;
} raw_hdlc_proto;

typedef struct {
    unsigned int interval;
    unsigned int timeout;
} cisco_proto;

typedef struct {
        unsigned int t391;
        unsigned int t392;
        unsigned int n391;
        unsigned int n392;
        unsigned int n393;
        unsigned short lmi;
        unsigned short dce; /* 1 for DCE (network side) operation */
} fr_proto;

typedef struct {
        unsigned int dlci;
} fr_proto_pvc;          /* for creating/deleting FR PVCs */

typedef struct {
        unsigned int dlci;
        char master[IFNAMSIZ];  /* Name of master FRAD device */
}fr_proto_pvc_info;             /* for returning PVC information only */

typedef struct { 
        unsigned int clock_rate; /* bits per second */
        unsigned int clock_type; /* internal, external, TX-internal etc. */
        unsigned short loopback;
        unsigned int slot_map;
} te1_settings;                  /* T1, E1 */

typedef struct { 
        unsigned int clock_rate; /* bits per second */
        unsigned int clock_type; /* internal, external, TX-internal etc. */
        unsigned short loopback;
} sync_serial_settings;          /* V.35, V.24, X.21 */

# define __user                //__attribute__((noderef, address_space(1)))


struct if_settings {
        unsigned int type;      /* Type of physical device or protocol */
        unsigned int size;      /* Size of the data allocated by the caller */
        union {
                /* {atm/eth/dsl}_settings anyone ? */
                raw_hdlc_proto          __user *raw_hdlc;
                cisco_proto             __user *cisco;
                fr_proto                __user *fr;
                fr_proto_pvc            __user *fr_pvc;
                fr_proto_pvc_info       __user *fr_pvc_info;

                /* interface settings */
                sync_serial_settings    __user *sync;
                te1_settings            __user *te1;
        } ifs_ifsu;
};

struct ifreq {
#define IFHWADDRLEN     6
        union
        {
                char    ifrn_name[IFNAMSIZ];            /* if name, e.g. "en0" */
        } ifr_ifrn;
        
        union {
                struct  sockaddr ifru_addr;
                struct  sockaddr ifru_dstaddr;
                struct  sockaddr ifru_broadaddr;
                struct  sockaddr ifru_netmask;
                struct  sockaddr ifru_hwaddr;
                short   ifru_flags;
                int     ifru_ivalue;
                int     ifru_mtu;
                struct  ifmap ifru_map;
                char    ifru_slave[IFNAMSIZ];   /* Just fits the size */
                char    ifru_newname[IFNAMSIZ];
                void __user *   ifru_data;
                struct  if_settings ifru_settings;
        } ifr_ifru;
};

struct can_frame {
        canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
        unsigned char    can_dlc; /* data length code: 0 .. 8 */
        unsigned char    data[8] __attribute__((aligned(8)));
};

