/*=========================================================================
| (c) 2005-2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_usb12.c
|--------------------------------------------------------------------------
| Simple Capture Example for Beagle USB 12
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
   along with Beagle USB 12's sampling rate (in kHz) */
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


/*=========================================================================
| STATIC GLOBALS
 ========================================================================*/
static Beagle beagle;
static u32    samplerate_khz;


/*=========================================================================
| UTILITY FUNCTIONS
 ========================================================================*/
static void print_general_status (u32 status)
{
    printf(" ");

    // General status codes
    if (status == BG_READ_OK)
        printf("OK ");

    if (status & BG_READ_TIMEOUT)
        printf("TIMEOUT ");

    if (status & BG_READ_ERR_MIDDLE_OF_PACKET)
        printf("MIDDLE ");

    if (status & BG_READ_ERR_SHORT_BUFFER)
        printf("SHORT BUFFER ");

    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE)
        printf("PARTIAL_BYTE(bit %d) ", status & 0xff);
}


/*=========================================================================
| USB DUMP FUNCTIONS
 ========================================================================*/
static void print_usb_status (u32 status)
{
    // USB status codes
    if (status & BG_READ_USB_ERR_BAD_SIGNALS)    printf("BAD_SIGNAL; ");
    if (status & BG_READ_USB_ERR_BAD_SYNC)       printf("BAD_SYNC; ");
    if (status & BG_READ_USB_ERR_BIT_STUFF)      printf("BAD_STUFF; ");
    if (status & BG_READ_USB_ERR_FALSE_EOP)      printf("BAD_EOP; ");
    if (status & BG_READ_USB_ERR_LONG_EOP)       printf("LONG_EOP; ");
    if (status & BG_READ_USB_ERR_BAD_PID)        printf("BAD_PID; ");
    if (status & BG_READ_USB_ERR_BAD_CRC)        printf("BAD_CRC; ");
}

static void print_usb_events (u32 events)
{
    // USB event codes
    if (events & BG_EVENT_USB_HOST_DISCONNECT)   printf("HOST_DISCON; ");
    if (events & BG_EVENT_USB_TARGET_DISCONNECT) printf("TGT_DISCON; ");
    if (events & BG_EVENT_USB_RESET)             printf("RESET; ");
    if (events & BG_EVENT_USB_HOST_CONNECT)      printf("HOST_CONNECT; ");
    if (events & BG_EVENT_USB_TARGET_CONNECT)    printf("TGT_CONNECT/UNRST; ");
}

static void usb_print_summary (int   i,
                               u64   count_sop,
                               char *summary)
{
    printf("%d,%" U64_FORMAT_STR ",USB,( ),%s\n",
           i, TIMESTAMP_TO_NS(count_sop, samplerate_khz), summary);
}

// Renders packet data for printing.
// The returned string needs to be free'd
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
        sprintf(packetstring + offset,"%02x ", packet[n]);
    offset += 3;
    }

    return packetstring;
}

// Print common packet header information
static void usb_print_packet (int         packet_number,
                              u64         time_sop,
                              u32         status,
                              u32         events,
                              const char *error_status,
                              const char *packet_data)
{
    if (error_status == 0)  error_status = "";
    printf("%d,%" U64_FORMAT_STR ",USB,(%s",
                 packet_number, time_sop, error_status);
    print_general_status(status);
    print_usb_status(status);
    print_usb_events(events);

    if (packet_data == 0)  packet_data = "";
    printf(")%s\n",packet_data);
    fflush(stdout);
}

// Dump saved summary information
static int usb_print_summary_packet (int packet_number,
                                     u64 count_sop,
                                     int sof_count,
                                     int pre_count,
                                     int in_ack_count,
                                     int in_nak_count,
                                     int sync_errors)
{
    int offset = 0;

    char summary[128];
    if (sof_count || in_ack_count || in_nak_count || pre_count)
    {
        char *p = summary;
        sprintf(p, "COLLAPSED ");
        p += strlen(p);

        if (sof_count > 0) {
            sprintf(p, "[%d SOF] ", sof_count);
            p += strlen(p);
        }

        if (pre_count > 0) {
            sprintf(p, "[%d PRE/ERR] ", pre_count);
            p += strlen(p);
        }

        if (in_ack_count > 0) {
            sprintf(p, "[%d IN/ACK] ", in_ack_count);
            p += strlen(p);
        }

        if (in_nak_count > 0) {
            sprintf(p, "[%d IN/NAK] ", in_nak_count);
            p += strlen(p);
        }

        usb_print_summary(packet_number+offset, count_sop, summary);
        ++offset;
    }

    // Output any sync errors
    if (sync_errors > 0) {
        sprintf(summary, "<%d SYNC ERRORS>", sync_errors);

        usb_print_summary(packet_number+offset, count_sop, summary);
        ++offset;
    }

    return offset;
}

// If the packet is not one that we're aggregating,
// this function returns 1, else 0.
static char usb_trigger (int pid)
{
    return (pid != BG_USB_PID_SOF)  &&
           (pid != BG_USB_PID_PRE)  &&
           (pid != BG_USB_PID_IN)   &&
           (pid != BG_USB_PID_ACK)  &&
           (pid != BG_USB_PID_NAK);
}

// The main USB dump routine
static void usbdump (int num_packets)
{
    // Set up variables
    u08  packet[1024];

    int  timing_size = bg_bit_timing_size(BG_PROTOCOL_USB, 1024);
    u32 *timing      = malloc(timing_size*sizeof(u32));

    u08  saved_in[64];
    u32  saved_in_timing[8*64];
    u64  saved_in_sop        = 0;
    u64  saved_in_duration   = 0;
    u32  saved_in_dataoffset = 0;
    u32  saved_in_status     = 0;
    u32  saved_in_events     = 0;
    int  saved_in_length     = 0;

    u64  count_sop    = 0;
    int  sof_count    = 0;
    int  pre_count    = 0;
    int  in_ack_count = 0;
    int  in_nak_count = 0;

    u08  pid         = 0;
    u64  last_sop    = 0;
    u08  last_pid    = 0;

    int  sync_errors = 0;
    int  packetnum   = 0;

    samplerate_khz = bg_samplerate(beagle, 0);

    // Open the connection to the Beagle.  Default to port 0.
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK) {
        printf("error: could not enable USB capture; exiting...\n");
        exit(1);
    }

    // Output the header...
    printf("index,time(ns),USB,status,pid,data0 ... dataN(*)\n");
    fflush(stdout);

    // ...then start decoding packets
    while (packetnum < num_packets || !num_packets) {
        u32   status;
        u32   events;
        u64   time_sop, time_sop_ns;
        u64   time_duration;
        u32   time_dataoffset;

        int length = bg_usb12_read_bit_timing(beagle, &status, &events,
                                            &time_sop, &time_duration,
                                            &time_dataoffset,
                                            1024, packet,
                                            timing_size, timing);

        last_pid = pid;

        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        // Check for invalid packet or Beagle error
        if (length < 0) {
            char error_status[32];
            sprintf(error_status, "error=%d", length);
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             error_status, 0);
            break;
        }

        // Check for USB error
        if (status == BG_READ_USB_ERR_BAD_SYNC)
            ++sync_errors;

        if (length > 0)
            pid = packet[0];
        else
            pid = 0;

        // Check the PID and collapse appropriately:
        // SOF* PRE* (IN (ACK|NAK))*
        // If we have saved summary information, and we have
        // hit an error, received a non-summary packet, or
        // have exceeded the idle time, then dump out the
        // summary information before continuing
        if ( status != BG_READ_OK || usb_trigger(pid) ||
              ((int)(time_sop - count_sop) >= IDLE_SAMPLES) ) {
            int offset =
                usb_print_summary_packet(packetnum, count_sop,
                                         sof_count, pre_count,
                                         in_ack_count, in_nak_count,
                                         sync_errors);
            sof_count    = 0;
            pre_count    = 0;
            in_ack_count = 0;
            in_nak_count = 0;
            sync_errors  = 0;
            count_sop    = time_sop;

            // Adjust the packet index if any events were printed by
            // usb_print_summary_packet.
            packetnum += offset;
        }

        // Now handle the current packet based on its packet ID
        switch (pid) {
          case BG_USB_PID_SOF:
            // Increment the SOF counter
            ++sof_count;
          break;

          case BG_USB_PID_PRE:
            // Increment the PRE counter
            ++pre_count;
            break;

          case BG_USB_PID_IN:
            // If the transaction is an IN, don't display it yet and
            // save the transaction.
            // If the following transaction is an ACK or NAK,
            // increment the appropriate IN/ACK or IN/NAK counter.
            // If the next transaction is not an ACK or NAK,
            // display the saved IN transaction .
            memcpy(saved_in, packet, length);
            memcpy(saved_in_timing, timing, length*8*sizeof(u32));

            saved_in_status     = status;
            saved_in_events     = events;
            saved_in_sop        = time_sop;
            saved_in_duration   = time_duration;
            saved_in_dataoffset = time_dataoffset;
            saved_in_length     = length;

            break;

          case BG_USB_PID_NAK:
          case BG_USB_PID_ACK:
            // If the last transaction was IN, increment the appropriate
            // counter and don't display the transaction.
            if (saved_in_length > 0) {
                saved_in_length = 0;

                if (pid == BG_USB_PID_ACK)
                    ++in_ack_count;
                else
                    ++in_nak_count;

                break;
            }

          default:
            // If the last transaction was IN, output it
            if (saved_in_length > 0) {
                u64 saved_in_sop_ns =
                    TIMESTAMP_TO_NS(saved_in_sop, samplerate_khz);

                const char *packet_data = usb_print_data_packet(
                                              saved_in, saved_in_length);
                usb_print_packet(packetnum, saved_in_sop_ns, saved_in_status,
                                 saved_in_events, 0, packet_data);
                ++packetnum;

                saved_in_length = 0;
            }

            // Output the current transaction
            if (length > 0 || events != 0 ||
                (status != 0 && status != BG_READ_TIMEOUT)) {
                const char *packet_data = usb_print_data_packet(packet,
                                                                length);
                usb_print_packet(packetnum, time_sop_ns, status,
                                 events, 0, packet_data);
                ++packetnum;
            }

            last_sop  = time_sop;
            count_sop = time_sop + time_duration;
        }
    }

    free(timing);

    // Stop the capture
    bg_disable(beagle);
}


/*=========================================================================
| USAGE INFORMATION
 ========================================================================*/
static void print_usage (void)
{
    printf(
"Usage: capture_usb num_events\n"
"Example utility for capturing USB data from Beagle protocol analyzers.\n"
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
    int port       = 0;      // open port 0 by default
    int samplerate = 0;      // in kHz (query)
    int timeout    = 500;    // in milliseconds
    int latency    = 200;    // in milliseconds
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

    // Query the samplerate since Beagle USB 12 has a fixed sampling rate
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

    // There is usually no need for pullups or target power
    // when using the Beagle as a passive monitor.
    bg_target_power(beagle, BG_TARGET_POWER_OFF);

    printf("\n");
    fflush(stdout);

    usbdump(num);

    // Close the device
    bg_close(beagle);

    return 0;
}
