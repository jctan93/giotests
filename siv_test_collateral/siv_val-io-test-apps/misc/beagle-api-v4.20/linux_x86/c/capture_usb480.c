/*=========================================================================
| (c) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_usb480.c
|--------------------------------------------------------------------------
| Simple Capture Example for Beagle USB 480
|--------------------------------------------------------------------------
| Redistribution and use of this file in source and binary forms, with
| or without modification, are permitted.
|
| THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
| "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
| LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
| FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
| COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
| INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
| BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
| LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
| CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
| LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
| ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
| POSSIBILITY OF SUCH DAMAGE.
 ========================================================================*/

/*=========================================================================
| INCLUDES
 ========================================================================*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "beagle.h"


/*=========================================================================
| MACROS
 ========================================================================*/
/* This will only work for sample rates that
   are multiples of 1MHz.  If any other rates
   are desired, this code needs to be changed.*/
#define TIMESTAMP_TO_NS(stamp, samplerate_khz) \
    (u64)(stamp * (u64)1000 / (u64)(samplerate_khz/1000))

/* USB collapsed packet idle threshold (in milliseconds)
   along with Beagle USB 480's sampling rate (in kHz) */
#define IDLE_THRESHOLD 2000
#define IDLE_SAMPLES (IDLE_THRESHOLD * samplerate_khz)

/* The printf format strings are differenct for 64-bit integers
   between Windows and Linux */
#if defined(WIN32) || defined(_WIN32)
#  define U64_FORMAT_STR "I64u"
#else
#  include <inttypes.h>
#  define U64_FORMAT_STR PRIu64
#endif

/* These macros are used to simplify the collapsing state machine */
#define COLLAPSE(group) \
    collapse(group, &collapse_info, &pkt_q)

#define SAVE_PACKET() \
    save_packet(&pkt_q)

#define OUTPUT_SAVED() \
    output_saved(&packetnum, &signal_errors, &collapse_info, &pkt_q)


/*=========================================================================
| STATIC GLOBALS
 ========================================================================*/
static Beagle beagle;
static u32    samplerate_khz;

// Packet groups to be collapsed
#define SOF              0
#define IN_ACK           1
#define IN_NAK           2
#define PING_NAK         3
#define SPLIT_IN_ACK     4
#define SPLIT_IN_NYET    5
#define SPLIT_IN_NAK     6
#define SPLIT_OUT_NYET   7
#define SPLIT_SETUP_NYET 8
#define KEEP_ALIVE       9

#define NUM_COLLAPSE  10

#define FALSE 0
#define TRUE  1

typedef struct {
    u08  data[1024];
    u64  time_sop;
    u64  time_sop_ns;
    u64  time_duration;
    u32  time_dataoffset;
    u32  status;
    u32  events;
    int  length;
} PacketInfo;

#define QUEUE_SIZE 3

// Used to store the packets that are saved during the collapsing
// process.  The tail of the queue is always used to store the
// current packet.
typedef struct {
    PacketInfo pkt[QUEUE_SIZE];
    int        head;
    int        tail;
} PacketQueue;

typedef struct {
    // Timestamp when collapsing begins
    u64 time_sop;
    // The number of packets collapsed for each packet group
    int count[NUM_COLLAPSE];
} CollapseInfo;

// Disable COMBINE_SPLITS by commenting the line below.  Disabling
// will show individual split counts for each group (such as
// SPLIT/IN/ACK, SPLIT/IN/NYET, ...).  Enabling will show all the
// collapsed split counts combined.
#define COMBINE_SPLITS


/*=========================================================================
| UTILITY FUNCTIONS
 ========================================================================*/
static void print_general_status (u32 status)
{
    printf(" ");

    // General status codes
    if (status == BG_READ_OK)                   printf("OK ");
    if (status & BG_READ_TIMEOUT)               printf("TIMEOUT ");
    if (status & BG_READ_ERR_UNEXPECTED)        printf("UNEXPECTED ");
    if (status & BG_READ_ERR_MIDDLE_OF_PACKET)  printf("MIDDLE ");
    if (status & BG_READ_ERR_SHORT_BUFFER)      printf("SHORT BUFFER ");
    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE)
        printf("PARTIAL_BYTE(bit %d) ", status & 0xff);
}


/*=========================================================================
| USB DUMP FUNCTIONS
 ========================================================================*/
static void print_usb_status (u32 status)
{
    // USB status codes
    if (status & BG_READ_USB_ERR_BAD_SIGNALS)  printf("BAD_SIGNAL; ");
    if (status & BG_READ_USB_ERR_BAD_SYNC)     printf("BAD_SYNC; ");
    if (status & BG_READ_USB_ERR_BIT_STUFF)    printf("BAD_STUFF; ");
    if (status & BG_READ_USB_ERR_FALSE_EOP)    printf("BAD_EOP; ");
    if (status & BG_READ_USB_ERR_LONG_EOP)     printf("LONG_EOP; ");
    if (status & BG_READ_USB_ERR_BAD_PID)      printf("BAD_PID; ");
    if (status & BG_READ_USB_ERR_BAD_CRC)      printf("BAD_CRC; ");
    if (status & BG_READ_USB_TRUNCATION_MODE)  printf("TRUNCATION_MODE; ");
    if (status & BG_READ_USB_END_OF_CAPTURE)   printf("END_OF_CAPTURE; ");
}

static void print_usb_events (u32 events)
{
    // USB event codes
    if (events & BG_EVENT_USB_HOST_DISCONNECT)   printf("HOST_DISCON; ");
    if (events & BG_EVENT_USB_TARGET_DISCONNECT) printf("TGT_DISCON; ");
    if (events & BG_EVENT_USB_RESET)             printf("RESET; ");
    if (events & BG_EVENT_USB_HOST_CONNECT)      printf("HOST_CONNECT; ");
    if (events & BG_EVENT_USB_TARGET_CONNECT)    printf("TGT_CONNECT/UNRST; ");
    if (events & BG_EVENT_USB_DIGITAL_INPUT)     printf("INPUT_TRIGGER %X; ",
        events & BG_EVENT_USB_DIGITAL_INPUT_MASK);
    if (events & BG_EVENT_USB_CHIRP_J)           printf("CHIRP_J; ");
    if (events & BG_EVENT_USB_CHIRP_K)           printf("CHIRP_K; ");
    if (events & BG_EVENT_USB_KEEP_ALIVE)        printf("KEEP_ALIVE; ");
    if (events & BG_EVENT_USB_SUSPEND)           printf("SUSPEND; ");
    if (events & BG_EVENT_USB_RESUME)            printf("RESUME; ");
    if (events & BG_EVENT_USB_LOW_SPEED)         printf("LOW_SPEED; ");
    if (events & BG_EVENT_USB_FULL_SPEED)        printf("FULL_SPEED; ");
    if (events & BG_EVENT_USB_HIGH_SPEED)        printf("HIGH_SPEED; ");
    if (events & BG_EVENT_USB_SPEED_UNKNOWN)     printf("UNKNOWN_SPEED; ");
    if (events & BG_EVENT_USB_LOW_OVER_FULL_SPEED)
        printf("LOW_OVER_FULL_SPEED; ");
}

static void usb_print_summary (int   i,
                               u64   collapse_sop,
                               char *summary)
{
    printf("%d,%" U64_FORMAT_STR ",USB,( ),%s\n",
           i, TIMESTAMP_TO_NS(collapse_sop, samplerate_khz), summary);
}

// Renders packet data for printing
static const char *usb_print_data_packet (u08  *packet,
                                          int   length)
{
    static char packetstring[1 + 7 + 1 + 3*1024 + 1 + 1];
    u08         pid;
    char       *pidstr = "";
    int         n, offset;

    if (length == 0) {
        packetstring[0] = 0;
        return packetstring;
    }

    // Get the packet identifier
    pid = packet[0];

    // Print the packet identifier
    switch (pid) {
      case BG_USB_PID_OUT:      pidstr = "OUT";      break;
      case BG_USB_PID_IN:       pidstr = "IN";       break;
      case BG_USB_PID_SOF:      pidstr = "SOF";      break;
      case BG_USB_PID_SETUP:    pidstr = "SETUP";    break;

      case BG_USB_PID_DATA0:    pidstr = "DATA0";    break;
      case BG_USB_PID_DATA1:    pidstr = "DATA1";    break;
      case BG_USB_PID_DATA2:    pidstr = "DATA2";    break;
      case BG_USB_PID_MDATA:    pidstr = "MDATA";    break;

      case BG_USB_PID_ACK:      pidstr = "ACK";      break;
      case BG_USB_PID_NAK:      pidstr = "NAK";      break;
      case BG_USB_PID_STALL:    pidstr = "STALL";    break;
      case BG_USB_PID_NYET:     pidstr = "NYET";     break;

      case BG_USB_PID_PRE:      pidstr = "PRE";      break;
      case BG_USB_PID_SPLIT:    pidstr = "SPLIT";    break;
      case BG_USB_PID_PING:     pidstr = "PING";     break;
      case BG_USB_PID_EXT:      pidstr = "EXT";      break;

      default:
        pidstr = "INVALID";
        break;
    }

    sprintf(packetstring, ",%s,", pidstr);

    offset = strlen(packetstring);
    // Print the packet data
    for (n = 0; n < length; ++n) {
        sprintf(packetstring + offset, "%02x ", packet[n]);
    offset += 3;
    }

    return packetstring;
}

// Print common packet header information
static void usb_print_packet (int          packet_number,
                              PacketInfo * packet,
                              const char * error_status)
{
    const char *packet_data;

    if (error_status == 0) {
        error_status = "";
        packet_data = usb_print_data_packet(packet->data, packet->length);
    } else {
        packet_data = "";
    }

    printf("%d,%" U64_FORMAT_STR ",USB,(%s",
                 packet_number, packet->time_sop_ns, error_status);
    print_general_status(packet->status);
    print_usb_status(packet->status);
    print_usb_events(packet->events);

    printf(")%s\n", packet_data);
    fflush(stdout);
}

// Dump saved summary information
static int usb_print_summary_packet (int          * packet_number,
                                     CollapseInfo * collapse_info,
                                     int          * signal_errors)
{
#ifdef COMBINE_SPLITS
    int split_count = 0;
#endif
    int offset = 0;

    char summary[128];
    if (collapse_info->count[KEEP_ALIVE]     ||
        collapse_info->count[SOF]            ||
        collapse_info->count[PING_NAK]       ||
        collapse_info->count[SPLIT_IN_ACK]   ||
        collapse_info->count[SPLIT_IN_NYET]  ||
        collapse_info->count[SPLIT_IN_NAK]   ||
        collapse_info->count[SPLIT_OUT_NYET] ||
        collapse_info->count[SPLIT_SETUP_NYET])
    {
        char *p = summary;
        sprintf(p, "COLLAPSED ");
        p += strlen(p);

        if (collapse_info->count[KEEP_ALIVE] > 0) {
            sprintf(p, "[%d KEEP-ALIVE] ", collapse_info->count[KEEP_ALIVE]);
            p += strlen(p);
        }

        if (collapse_info->count[SOF] > 0) {
            sprintf(p, "[%d SOF] ", collapse_info->count[SOF]);
            p += strlen(p);
        }

        if (collapse_info->count[IN_ACK] > 0) {
            sprintf(p, "[%d IN/ACK] ", collapse_info->count[IN_ACK]);
            p += strlen(p);
        }

        if (collapse_info->count[IN_NAK] > 0) {
            sprintf(p, "[%d IN/NAK] ", collapse_info->count[IN_NAK]);
            p += strlen(p);
        }

        if (collapse_info->count[PING_NAK] > 0) {
            sprintf(p, "[%d PING/NAK] ", collapse_info->count[PING_NAK]);
            p += strlen(p);
        }

#ifdef COMBINE_SPLITS
        split_count =
            collapse_info->count[SPLIT_IN_ACK]   +
            collapse_info->count[SPLIT_IN_NYET]  +
            collapse_info->count[SPLIT_IN_NAK]   +
            collapse_info->count[SPLIT_OUT_NYET] +
            collapse_info->count[SPLIT_SETUP_NYET];

        if (split_count > 0) {
            sprintf(p, "[%d SPLITS] ", split_count);
            p += strlen(p);
        }
#else
        if (collapse_info->count[SPLIT_IN_ACK] > 0) {
            sprintf(p, "[%d SPLIT/IN/ACK] ",
                    collapse_info->count[SPLIT_IN_ACK]);
            p += strlen(p);
        }

        if (collapse_info->count[SPLIT_IN_NYET] > 0) {
            sprintf(p, "[%d SPLIT/IN/NYET] ",
                    collapse_info->count[SPLIT_IN_NYET]);
            p += strlen(p);
        }

        if (collapse_info->count[SPLIT_IN_NAK] > 0) {
            sprintf(p, "[%d SPLIT/IN/NAK] ",
                    collapse_info->count[SPLIT_IN_NAK]);
            p += strlen(p);
        }

        if (collapse_info->count[SPLIT_OUT_NYET] > 0) {
            sprintf(p, "[%d SPLIT/OUT/NYET] ",
                    collapse_info->count[SPLIT_OUT_NYET]);
            p += strlen(p);
        }

        if (collapse_info->count[SPLIT_SETUP_NYET] > 0) {
            sprintf(p, "[%d SPLIT/SETUP/NYET] ",
                    collapse_info->count[SPLIT_SETUP_NYET]);
            p += strlen(p);
        }
#endif
        usb_print_summary(*packet_number+offset, collapse_info->time_sop,
                          summary);
        ++offset;
    }

    // Output any signal errors
    if (*signal_errors > 0) {
        sprintf(summary, "<%d SIGNAL ERRORS>", *signal_errors);

        usb_print_summary(*packet_number+offset, collapse_info->time_sop,
                          summary);
        *signal_errors = 0;
        ++offset;
    }

    memset(collapse_info, 0, sizeof(CollapseInfo));
    *packet_number += offset;
    return offset;
}

// Outputs any packets saved during the collapsing process
static void output_saved (int          * packetnum,
                          int          * signal_errors,
                          CollapseInfo * collapse_info,
                          PacketQueue  * pkt_q)
{
    usb_print_summary_packet(packetnum, collapse_info, signal_errors);

    while (pkt_q->head != pkt_q->tail) {
        usb_print_packet(*packetnum, &pkt_q->pkt[pkt_q->head], 0);
        *packetnum += 1;
        pkt_q->head = (pkt_q->head + 1) % QUEUE_SIZE;
    }
}

// Saves the current packet
static void save_packet (PacketQueue * pkt_q)
{
    pkt_q->tail = (pkt_q->tail + 1) % QUEUE_SIZE;
}

// Collapses a group of packets.  This involves incrementing the group
// counter and clearing the queue. If this is the first group to be
// collapsed, the collapse time needs to be set, which marks when this
// collapsing began.
static void collapse (int            group,
                      CollapseInfo * collapse_info,
                      PacketQueue  * pkt_q)
{
    collapse_info->count[group]++;
    if (collapse_info->time_sop == 0) {
        if (pkt_q->head != pkt_q->tail)
            collapse_info->time_sop = pkt_q->pkt[pkt_q->head].time_sop;
        else
            collapse_info->time_sop = pkt_q->pkt[pkt_q->tail].time_sop;
    }
    pkt_q->head = pkt_q->tail;
}

// The main USB dump routine
static void usb_dump (int num_packets)
{
    // Packets will be saved during the collapse process
    PacketQueue pkt_q;

    // Points to the current packet
    PacketInfo * cur_pkt;

    // Collapsing counts and time collapsing started
    CollapseInfo collapse_info;

    // Collapsing of packets is handled through a state machine.
    // Sometimes the machine will need to be re-run to properly
    // handle the sequence of packets.
    enum CollapseStates {
        IDLE = 0,
        IN, PING, SPLIT, SPLIT_IN, SPLIT_OUT, SPLIT_SETUP
    } state = IDLE;

    u08 re_run = FALSE;

    u08  pid           = 0;
    int  signal_errors = 0;
    int  packetnum     = 0;

    // Initialize structures
    memset(&pkt_q, 0, sizeof(PacketQueue));
    memset(&collapse_info, 0, sizeof(CollapseInfo));

    samplerate_khz = bg_samplerate(beagle, 0);

    // Configure Beagle 480 for realtime capture
    bg_usb480_capture_configure(beagle,
                        BG_USB480_CAPTURE_REALTIME,
                        BG_USB2_AUTO_SPEED_DETECT);

    // Filter packets intended for the Beagle analyzer. This is only
    // relevant when one host controller is being used.
    bg_usb480_hw_filter_config(beagle,
                               BG_USB2_HW_FILTER_SELF);

    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK) {
        printf("error: could not enable USB capture; exiting...\n");
        exit(1);
    }

    // Output the header...
    printf("index,time(ns),USB,status,pid,data0 ... dataN(*)\n");
    fflush(stdout);

    // ...then start decoding packets
    while (packetnum < num_packets || !num_packets) {
        cur_pkt = &pkt_q.pkt[pkt_q.tail];

        cur_pkt->length = bg_usb480_read(beagle,
                                         &cur_pkt->status,
                                         &cur_pkt->events,
                                         &cur_pkt->time_sop,
                                         &cur_pkt->time_duration,
                                         &cur_pkt->time_dataoffset,
                                         1024,
                                         cur_pkt->data);

        cur_pkt->time_sop_ns =
            TIMESTAMP_TO_NS(cur_pkt->time_sop, samplerate_khz);

        // Exit if observed end of capture
        if (cur_pkt->status & BG_READ_USB_END_OF_CAPTURE) {
            usb_print_summary_packet(&packetnum, &collapse_info,
                                     &signal_errors);
            break;
        }

        // Check for invalid packet or Beagle error
        if (cur_pkt->length < 0) {
            char error_status[32];
            sprintf(error_status, "error=%d", cur_pkt->length);
            usb_print_packet(packetnum, cur_pkt, error_status);
            break;
        }

        // Check for USB error
        if (cur_pkt->status == BG_READ_USB_ERR_BAD_SIGNALS)
            ++signal_errors;

        // Set the PID for collapsing state machine below.  Treat
        // KEEP_ALIVEs as packets.
        if (cur_pkt->length > 0)
            pid = cur_pkt->data[0];
        else if ((cur_pkt->events & BG_EVENT_USB_KEEP_ALIVE) &&
                 !(cur_pkt->status & BG_READ_USB_ERR_BAD_PID))
        {
            pid = KEEP_ALIVE;
        }
        else
            pid = 0;

        // Collapse these packets approprietly:
        // KEEP_ALIVE* SOF* (IN (ACK|NAK))* (PING NAK)*
        // (SPLIT (OUT|SETUP) NYET)* (SPLIT IN (ACK|NYET|NACK))*

        // If the time elapsed since collapsing began is greater than
        // the threshold, output the counts and zero out the counters.
        if ((int)(cur_pkt->time_sop - collapse_info.time_sop) >= IDLE_SAMPLES)
            usb_print_summary_packet(&packetnum, &collapse_info,
                                     &signal_errors);

        while(1) {
            re_run = FALSE;
            switch (state) {
                // The initial state of the state machine.  Collapse SOFs
                // and KEEP_ALIVEs. Save IN, PING, or SPLIT packets and
                // move to the next state for the next packet.  Otherwise,
                // print the collapsed packet counts and the current packet.
              case IDLE:
                switch (pid) {
                  case KEEP_ALIVE:
                    COLLAPSE(KEEP_ALIVE);
                    break;
                  case BG_USB_PID_SOF:
                    COLLAPSE(SOF);
                    break;
                  case BG_USB_PID_IN:
                    SAVE_PACKET();
                    state = IN;
                    break;
                  case BG_USB_PID_PING:
                    SAVE_PACKET();
                    state = PING;
                    break;
                  case BG_USB_PID_SPLIT:
                    SAVE_PACKET();
                    state = SPLIT;
                    break;
                  default:
                    usb_print_summary_packet(&packetnum, &collapse_info,
                                             &signal_errors);

                    if (cur_pkt->length > 0 || cur_pkt->events ||
                        (cur_pkt->status != 0 &&
                         cur_pkt->status != BG_READ_TIMEOUT))
                    {
                        usb_print_packet(packetnum, cur_pkt, 0);
                        packetnum++;
                    }
                }
                break;

                // Collapsing IN+ACK or IN+NAK.  Otherwise, output any
                // saved packets and rerun the collapsing state machine
                // on the current packet.
              case IN:
                state = IDLE;
                switch (pid) {
                  case BG_USB_PID_ACK:
                    COLLAPSE(IN_ACK);
                    break;
                  case BG_USB_PID_NAK:
                    COLLAPSE(IN_NAK);
                    break;
                  default:
                    re_run = TRUE;
                }
                break;

                // Collapsing PING+NAK
              case PING:
                state = IDLE;
                switch (pid) {
                  case BG_USB_PID_NAK:
                    COLLAPSE(PING_NAK);
                    break;
                  default:
                    re_run = TRUE;
                }
                break;

                // Expecting an IN, OUT, or SETUP
              case SPLIT:
                switch (pid) {
                  case BG_USB_PID_IN:
                    SAVE_PACKET();
                    state = SPLIT_IN;
                    break;
                  case BG_USB_PID_OUT:
                    SAVE_PACKET();
                    state = SPLIT_OUT;
                    break;
                  case BG_USB_PID_SETUP:
                    SAVE_PACKET();
                    state = SPLIT_SETUP;
                    break;
                  default:
                    state = IDLE;
                    re_run = TRUE;
                }
                break;

                // Collapsing SPLIT+IN+NYET, SPLIT+IN+NAK, SPLIT+IN+ACK
              case SPLIT_IN:
                state = IDLE;
                switch (pid) {
                  case BG_USB_PID_NYET:
                    COLLAPSE(SPLIT_IN_NYET);
                    break;
                  case BG_USB_PID_NAK:
                    COLLAPSE(SPLIT_IN_NAK);
                    break;
                  case BG_USB_PID_ACK:
                    COLLAPSE(SPLIT_IN_ACK);
                    break;
                  default:
                    re_run = TRUE;
                }
                break;

                // Collapsing SPLIT+OUT+NYET
              case SPLIT_OUT:
                state = IDLE;
                switch (pid) {
                  case BG_USB_PID_NYET:
                    COLLAPSE(SPLIT_OUT_NYET);
                    break;
                  default:
                    re_run = TRUE;
                }
                break;

                // Collapsing SPLIT+SETUP+NYET
              case SPLIT_SETUP:
                state = IDLE;
                switch (pid) {
                  case BG_USB_PID_NYET:
                    COLLAPSE(SPLIT_SETUP_NYET);
                    break;
                  default:
                    re_run = TRUE;
                }
                break;
            }

            if (re_run == FALSE)
                break;

            // The state machine is about to be re-run.  This
            // means that a complete packet sequence wasn't collapsed
            // and there are packets in the queue that need to be
            // output before we can process the current packet.
            OUTPUT_SAVED();
        }
    }

    // Stop the capture
    bg_disable(beagle);
}


/*=========================================================================
| DIGITAL INPIT/OUTPUT CONFIG
 ========================================================================*/
static void setup_digital_lines ()
{
    // Digital input mask
    u08 input_enable_mask =
        BG_USB2_DIGITAL_IN_ENABLE_PIN1 |
        BG_USB2_DIGITAL_IN_ENABLE_PIN2 |
        BG_USB2_DIGITAL_IN_ENABLE_PIN3 |
        BG_USB2_DIGITAL_IN_ENABLE_PIN4;

    BeagleUsb2PacketMatch packet_match;
    BeagleUsb2DataMatch   data_match;

    // Enable digital input pins
    bg_usb480_digital_in_config(beagle, input_enable_mask);
    printf("Configuring digital input with %x\n", input_enable_mask);

    // Configure digital out pins
    packet_match.pid_match_type = BG_USB2_MATCH_TYPE_EQUAL;
    packet_match.pid_match_val  = BG_USB_PID_PING;
    packet_match.dev_match_type = BG_USB2_MATCH_TYPE_DISABLED;
    packet_match.dev_match_val  = 0;
    packet_match.ep_match_type  = BG_USB2_MATCH_TYPE_DISABLED;
    packet_match.ep_match_val   = 0;

    data_match.data_match_type   = BG_USB2_MATCH_TYPE_DISABLED;
    data_match.data_match_pid    = 0;
    data_match.data_length       = 0;
    data_match.data              = NULL;
    data_match.data_valid_length = 0;
    data_match.data_valid        = NULL;

    // Enable digital output pin 4
    bg_usb480_digital_out_config(beagle,
                                 BG_USB2_DIGITAL_OUT_ENABLE_PIN4,
                                 BG_USB2_DIGITAL_OUT_PIN4_ACTIVE_HIGH);

    // Configure digital output pin 4 match pattern
    bg_usb480_digital_out_match(beagle,
                                BG_USB2_DIGITAL_OUT_MATCH_PIN4,
                                &packet_match, &data_match);

    printf("Configuring digital output pin 4.\n");
}


/*=========================================================================
| USAGE INFORMATION
 ========================================================================*/
static void print_usage (void)
{
    printf(
"Usage: capture_usb480 num_events\n"
"Example utility for capturing USB data from a Beagle 480 protocol analyzer.\n"
"Certain packet groups (such as IN/NAK, SPLIT/IN/ACK, etc.) are collapsed\n"
"in software.  See the source code for more details about packet collapsing.\n"
"\n"
"  The parameter num_events is set to the number of events to process\n"
"  before exiting.  If num_events is set to zero, the capture will continue\n"
"  indefinitely.\n"
"\n"
"For product documentation and specifications, see www.totalphase.com.\n");
    fflush(stdout);
};


/*=========================================================================
| MAIN PROGRAM ENTRY POINT
 ========================================================================*/
int main (int argc, char *argv[])
{
    int port       = 0;   // open port 0 by default
    int samplerate = 0;   // in kHz (query)
    int timeout    = 500; // in milliseconds
    int latency    = 200; // in milliseconds
    int num        = 0;

    if (argc < 2) {
        print_usage();
        return 1;
    }

    num = atoi(argv[1]);

    // Open the device
    beagle = bg_open(port);
    if (beagle <= 0) {
        printf("Unable to open Beagle device on port %d\n", port);
        printf("Error code = %d\n", beagle);
        return 1;
    }
    printf("Opened Beagle device on port %d\n", port);

    // Query the samplerate since Beagle USB 480 has a fixed sampling rate
    samplerate = bg_samplerate(beagle, samplerate);
    if (samplerate < 0) {
        printf("error: %s\n", bg_status_string(samplerate));
        return 1;
    }
    printf("Sampling rate set to %d KHz.\n", samplerate);

    // Set the idle timeout.
    // The Beagle read functions will return in the specified time
    // if there is no data available on the bus.
    bg_timeout(beagle, timeout);
    printf("Idle timeout set to %d ms.\n", timeout);

    // Set the latency.
    // The latency parameter allows the programmer to balance the
    // tradeoff between host side buffering and the latency to
    // receive a packet when calling one of the Beagle read
    // functions.
    bg_latency(beagle, latency);
    printf("Latency set to %d ms.\n", latency);

    printf("Host interface is %s.\n",
           (bg_host_ifce_speed(beagle)) ? "high speed" : "full speed");

    // Set up the digital input and output lines
    setup_digital_lines();

    printf("\n");
    fflush(stdout);

    // Capture the USB packets
    usb_dump(num);

    // Close the device
    bg_close(beagle);

    return 0;
}
