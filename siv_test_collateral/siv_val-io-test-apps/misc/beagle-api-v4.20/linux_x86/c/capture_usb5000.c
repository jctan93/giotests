/*=========================================================================
| (c) 2011  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_usb5000.c
|--------------------------------------------------------------------------
| Simple Capture Example for Beagle USB 5000
|--------------------------------------------------------------------------
| Redistribution and use of this file in source and binary forms, with
| or without modification, are permitted.
|
| THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
| "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
| LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
| FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  9IN NO EVENT SHALL THE
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
    (u64)((stamp) * (u64)1000 / (u64)(samplerate_khz/1000))

/* The printf format strings are differenct for 64-bit integers
   between Windows and Linux */
#if defined(WIN32) || defined(_WIN32)
#  define U64_FORMAT_STR "I64u"
#else
#  include <inttypes.h>
#  define U64_FORMAT_STR PRIu64
#endif


/*=========================================================================
| STATIC GLOBALS
 ========================================================================*/
// Enable statistics mode rather than packet printing mode.
#define STATS_MODE 1

#define DISPLAY_TIME_TICKS 10000000

static Beagle beagle;
static u32    samplerate_khz;

static const char *LTSSM_TABLE[] = {
    "Unknown",
    "SS.Disabled",
    "SS.Inactive",
    "Rx Detect.Reset",
    "Rx Detect.Active",
    "Polling.LFPS",
    "Polling.RxEQ",
    "Polling.Active",
    "Polling.Config",
    "Polling.Idle",
    "U0",
    "U1",
    "U2",
    "U3",
    "Recovery.Active",
    "Recovery.Config",
    "Recovery.Idle",
    "Hot Reset.Active",
    "Hot Reset.Exit",
    "Loopback.Active",
    "Loopback.Exit",
};


/*=========================================================================
| UTILITY FUNCTIONS
 ========================================================================*/
static void print_general_status (const u32 status)
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
    if (status & BG_READ_USB_END_OF_CAPTURE)   printf("END_OF_CAPTURE ");
}

static void print_source (const BeagleUsb5000Source source)
{
    switch (source) {
      case BG_USB5000_SOURCE_ASYNC: printf("Async"); break;
      case BG_USB5000_SOURCE_RX:    printf("SSRX"); break;
      case BG_USB5000_SOURCE_TX:    printf("SSTX"); break;
      case BG_USB5000_SOURCE_USB2:  printf("USB2"); break;
    };
}


/*=========================================================================
| USB DUMP FUNCTIONS
 ========================================================================*/
static void print_usb_status (const BeagleUsb5000Source source,
                              const u32 status)
{
    if (source == BG_USB5000_SOURCE_USB2) {
        // USB 2 status codes
        if (status & BG_READ_USB_ERR_BAD_SIGNALS)  printf("BAD_SIGNAL; ");
        if (status & BG_READ_USB_ERR_BAD_PID)      printf("BAD_PID; ");
        if (status & BG_READ_USB_ERR_BAD_CRC)      printf("BAD_CRC; ");
    }
    else {
        // USB 3 status codes
        if (status & BG_READ_USB_PKT_TYPE_LINK) {
            printf("LINK; ");
            if (status & BG_READ_USB_ERR_BAD_SLC_CRC_1)
                printf("BAD_SLC_CRC_1; ");
            if (status & BG_READ_USB_ERR_BAD_SLC_CRC_2)
                printf("BAD_SLC_CRC_2; ");
        }

        if (status & BG_READ_USB_PKT_TYPE_DP) {
            printf("DATA; ");
            if (status & BG_READ_USB_ERR_BAD_SDP_CRC)
                printf("BAD_SDP_CRC; ");
            if (status & BG_READ_USB_EDB_FRAMING)
                printf("SDP_EDB_FRAME; ");
        }

        if (status & BG_READ_USB_PKT_TYPE_HDR) {
            printf("HDR; ");
            if (status & BG_READ_USB_ERR_BAD_SHP_CRC_16)
                printf("BAD_SHP_CRC_16; ");
            if (status & BG_READ_USB_ERR_BAD_SHP_CRC_5)
                printf("BAD_SHP_CRC_5; ");
        }

        if (status & BG_READ_USB_PKT_TYPE_TSEQ)      printf("TSEQ; ");
        if (status & BG_READ_USB_PKT_TYPE_TS1)       printf("TS1; ");
        if (status & BG_READ_USB_PKT_TYPE_TS2)       printf("TS2; ");

        if (status & BG_READ_USB_ERR_BAD_TS)           printf("BAD_TS; ");
        if (status & BG_READ_USB_ERR_UNK_END_OF_FRAME) printf("BAD_UNK_EOF; ");
        if (status & BG_READ_USB_ERR_DATA_LEN_INVALID) printf("BAD_DATA_LEN; ");
        if (status & BG_READ_USB_ERR_FRAMING)          printf("FRAME_ERROR; ");
    }
}

static void print_status (const BeagleUsb5000Source source, const u32 status) {
    print_general_status(status);
    print_usb_status(source, status);
}

static void print_usb2_events (const u32 events)
{
    // USB 2 event codes
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

static void print_events (const BeagleUsb5000Source source, const u32 events)
{
    // Print USB 2 events
    if (source == BG_USB5000_SOURCE_USB2) {
        print_usb2_events(events);
        return;
    }

    // Print USB 3 and Async events
    if (events & BG_EVENT_USB_LTSSM) {
        int evt_idx = events & BG_EVENT_USB_LTSSM_MASK;
        if (evt_idx < (sizeof(LTSSM_TABLE)/sizeof(const char *)))
            printf("LTSSM Transition: %s; ", LTSSM_TABLE[evt_idx]);
        else
            printf("Unknown LTSSM Transition: %d; ", evt_idx);
    }

    if (events & BG_EVENT_USB_COMPLEX_TRIGGER) {
        int state = events & BG_EVENT_USB_TRIGGER_STATE_MASK;
        state   >>= BG_EVENT_USB_TRIGGER_STATE_SHIFT;
        printf("%s trigger from state: %d; ",
               events & BG_EVENT_USB_TRIGGER_TIMER ? "Timer" : "Complex",
               state);
    }

    if (events & BG_EVENT_USB_VBUS_PRESENT)        printf("VBUS Present; ");
    if (events & BG_EVENT_USB_VBUS_ABSENT)         printf("VBUS Absent; ");
    if (events & BG_EVENT_USB_SCRAMBLING_ENABLED)  printf("Scrambling On; ");
    if (events & BG_EVENT_USB_SCRAMBLING_DISABLED) printf("Scrambling Off; ");
    if (events & BG_EVENT_USB_POLARITY_NORMAL)     printf("Polarity Normal; ");
    if (events & BG_EVENT_USB_POLARITY_REVERSED)   printf("Polarity Reversed; ");
    if (events & BG_EVENT_USB_PHY_ERROR)           printf("PHY Error; ");
    if (events & BG_EVENT_USB_HOST_DISCONNECT)     printf("SS Host Discon; ");
    if (events & BG_EVENT_USB_HOST_CONNECT)        printf("SS Host Conn; ");
    if (events & BG_EVENT_USB_TARGET_DISCONNECT)   printf("SS Trgt Discon; ");
    if (events & BG_EVENT_USB_TARGET_CONNECT)      printf("SS Trgt Conn; ");
    if (events & BG_EVENT_USB_LFPS)                printf("LFPS; ");
    if (events & BG_EVENT_USB_TRIGGER)             printf("Trigger; ");
    if (events & BG_EVENT_USB_EXT_TRIG_ASSERTED)   printf("Ext In Asserted; ");
    if (events & BG_EVENT_USB_EXT_TRIG_DEASSERTED) printf("Ext In Deasserted; ");
}

// Renders USB3 packet data for printing
static const char *usb_print_usb3_data_packet (const u08  *packet,
                                               const u08  *k_packet_data,
                                               const int   length)
{
    static char packetstring[4*1036];
    int offset = 0;
    int n;

    if (length == 0) {
        packetstring[0] = 0;
        return packetstring;
    }

    // Print the packet data
    for (n = 0; n < length; ++n) {
        int k_bit = (k_packet_data[n/8] >> (n % 8)) & 0x01;
        sprintf(packetstring + offset, "%03x ", (k_bit << 8) | packet[n]);
        offset += 4;
    }

    return packetstring;
}

// Renders USB2 packet data for printing
static const char *usb_print_usb2_data_packet (const u08  *packet,
                                               const int   length)
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

// Print the data of the packet
static void print_packet (const BeagleUsb5000Source   source,
                          const int                   length,
                          const u08                 * packet,
                          const u08                 * packet_k_data)
{
    if (source == BG_USB5000_SOURCE_USB2)
        printf("%s", usb_print_usb2_data_packet(packet, length));
    else
        printf("%s", usb_print_usb3_data_packet(packet, packet_k_data, length));
}

// The main USB dump routine
static void usb_dump (const int num_packets, const int cap_mask)
{
    // Setup variables
    u08                 packet[1036];
    u08                 packet_k_bits[130];
    BeagleUsb5000Source source;
    u32                 status;
    u32                 events;
    u64                 time_sop;
    u64                 time_duration;
    u32                 time_dataoffset;

    int packetnum = 0;

    // Statistic mode variables
    u64 disp_time_sop     = 0;
    u64 sstx_byte_count   = 0;
    u64 ssrx_byte_count   = 0;
    u64 sstx_packet_count = 0;
    u64 ssrx_packet_count = 0;
    u64 usb2_byte_count   = 0;
    u64 usb2_packet_count = 0;

    BeagleUsb5000CaptureStatus capture_status;
    int                        ret;

    // Configure Beagle 5000 for immediate trigger.
    if (bg_usb5000_configure(beagle,
                             cap_mask,
                             BG_USB5000_TRIGGER_MODE_IMMEDIATE) != BG_OK)
    {
        printf("error: could not configure Beagle 5000 with desired mode\n");
        exit(1);
    }


    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK) {
        printf("error: could not enable USB capture; exiting...\n");
        exit(1);
    }

    // Wait for the analyzer to trigger for up to 2 seconds...
    if (cap_mask & BG_USB5000_CAPTURE_USB2) {
        ret = bg_usb5000_usb2_capture_status(
            beagle, 2000, &capture_status, 0, 0, 0, 0);
    }
    else {
        ret = bg_usb5000_usb3_capture_status(
            beagle, 2000, &capture_status, 0, 0, 0, 0);
    }

    if (ret != BG_OK) {
        printf("error: could not query capture status; exiting...\n");
        exit(1);
    }

    if (capture_status <= BG_USB5000_CAPTURE_STATUS_PRE_TRIGGER) {
        printf("did not trigger.\n");
        exit(1);
    }

    // Output the header...
    if (STATS_MODE) {
        printf("   SSTX PACKETS ( MB/s )    SSRX PACKETS ( MB/s )    USB2 PACKETS ( MB/s )\n");
    }
    else {
        printf("index,time(ns),source,event,status,data0 ... dataN(*)\n");
    }
    fflush(stdout);


    // ...then start decoding packets
    while (packetnum < num_packets || !num_packets) {
        int length = bg_usb5000_read(beagle, &status, &events,
                                     &time_sop, &time_duration,
                                     &time_dataoffset, &source,
                                     1036, packet, 130, packet_k_bits);

        // Make sure capture is triggered.
        if (length == BG_CAPTURE_NOT_TRIGGERED)
            continue;

        // Check for invalid packet or Beagle error
        if (length < 0) {
            printf("error=%d\n", length);
            break;
        }

        // Exit if observed end of capture
        if (status == BG_READ_USB_END_OF_CAPTURE) {
            printf("\n");
            printf("End of capture\n");
            break;
        }

        if (STATS_MODE) {
            // Count the number of packets and bytes
            if (length > 0) {
                switch (source) {
                  case BG_USB5000_SOURCE_USB2:
                    usb2_packet_count++; usb2_byte_count += length; break;
                  case BG_USB5000_SOURCE_TX:
                    sstx_packet_count++; sstx_byte_count += length; break;
                  case BG_USB5000_SOURCE_RX:
                    ssrx_packet_count++; ssrx_byte_count += length; break;
                  default:
                    break;
                }
            }

            // Periodically print out the stats
            if ((time_sop - disp_time_sop) > DISPLAY_TIME_TICKS) {
                double time_s = TIMESTAMP_TO_NS(time_sop - disp_time_sop,
                                                samplerate_khz) / 1E9;
                double sstx_mbps =
                    ((double) sstx_byte_count) / (1024*1024L) / time_s;
                double ssrx_mbps =
                    ((double) ssrx_byte_count) / (1024*1024L) / time_s;
                double usb2_mbps =
                    ((double) usb2_byte_count) / (1024*1024L) / time_s;

                printf("\r%15" U64_FORMAT_STR " (%6.2f)"
                       " %15" U64_FORMAT_STR " (%6.2f)"
                       " %15" U64_FORMAT_STR " (%6.2f)",
                       sstx_packet_count, sstx_mbps,
                       ssrx_packet_count, ssrx_mbps,
                       usb2_packet_count, usb2_mbps);

                sstx_byte_count = 0;
                ssrx_byte_count = 0;
                usb2_byte_count = 0;
                disp_time_sop = time_sop;
            }
        }

        else {
            // Grab the next packet on a timeout.
            if (length == 0 && status == BG_READ_TIMEOUT && events == 0)
                continue;

            // Print the packet details
            printf("%d,", packetnum);
            printf("%" U64_FORMAT_STR ",",
                   TIMESTAMP_TO_NS(time_sop, samplerate_khz));
            print_source(source);
            printf(",");
            print_events(source, events);
            printf(",");
            print_status(source, status);
            printf(",");
            print_packet(source, length, packet, packet_k_bits);
            printf("\n");
        }

        packetnum++;
    }

    // Stop the capture
    bg_disable(beagle);
}


/*=========================================================================
| USAGE INFORMATION
 ========================================================================*/
static void print_usage (void)
{
    printf(
"Usage: capture_usb5000 source num_events\n"
"Example utility for capturing USB data from a Beagle 5000 protocol analyzer.\n"
"\n"
"  The parameter source determines which USB source to capture on.\n"
"  The source can be set to either: both, usb2, or usb3.\n"
"  Note that only analyzers licensed for the simultaneous feature will\n"
"  be able to capture both sources at the same time.\n"
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
    int timeout    = 100; // in milliseconds
    int latency    = 200; // in milliseconds
    int num        = 0;
    int cap_mask   = 0;

    if (argc < 3) {
        print_usage();
        return 1;
    }

    if (strcmp(argv[1], "usb2") == 0)
        cap_mask = BG_USB5000_CAPTURE_USB2;
    else if (strcmp(argv[1], "usb3") == 0)
        cap_mask = BG_USB5000_CAPTURE_USB3;
    else if (strcmp(argv[1], "both") == 0)
        cap_mask = BG_USB5000_CAPTURE_USB3 | BG_USB5000_CAPTURE_USB2;
    else {
        print_usage();
        return 1;
    }

    num = atoi(argv[2]);

    // Open the device
    beagle = bg_open(port);
    if (beagle <= 0) {
        printf("Unable to open Beagle device on port %d\n", port);
        printf("Error code = %d\n", beagle);
        return 1;
    }
    printf("Opened Beagle device on port %d\n", port);

    // Query the samplerate since Beagle USB 5000 has a fixed sampling rate
    samplerate_khz = bg_samplerate(beagle, samplerate_khz);
    if (samplerate_khz < 0) {
        printf("error: %s\n", bg_status_string(samplerate_khz));
        return 1;
    }
    printf("Sampling rate set to %d KHz.\n", samplerate_khz);

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

    printf("\n");
    fflush(stdout);

    // Capture the USB packets
    usb_dump(num, cap_mask);

    // Close the device
    bg_close(beagle);

    return 0;
}
