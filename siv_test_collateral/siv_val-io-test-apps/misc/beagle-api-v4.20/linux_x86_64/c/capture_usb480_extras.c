/*=========================================================================
| (c) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_usb480_extras.c
|--------------------------------------------------------------------------
| Delayed Download Capture Example for Beagle USB 480 with hardware filters
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

#ifdef _WIN32
#include <time.h>
#else
#include <sys/time.h>
#endif


/*=========================================================================
| MACROS
 ========================================================================*/
/* This will only work for sample rates that
   are multiples of 1MHz.  If any other rates
   are desired, this code needs to be changed.*/
#define TIMESTAMP_TO_NS(stamp, samplerate_khz) \
    (u64)(stamp * (u64)1000 / (u64)(samplerate_khz/1000))

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
static s64 time_microseconds () {
#ifdef _WIN32
    return ((s64)clock()) * 1000000 / CLOCKS_PER_SEC;
#else
    struct timeval tv;
    gettimeofday(&tv, 0);
    return ((s64)tv.tv_sec * 1000000L) + (s64)(tv.tv_usec);
#endif
}


/*=========================================================================
| USB DUMP FUNCTIONS
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
    if (status & BG_READ_USB_TRUNCATION_MODE)    printf("TRUNCATION_MODE; ");
    if (status & BG_READ_USB_END_OF_CAPTURE)     printf("END_OF_CAPTURE; ");
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
        sprintf(packetstring + offset, "%02x ", packet[n]);
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

static void print_progress (int percent, double elapsedTime, u32 bufferUsed,
                            u32 bufferSize)
{
    static char progressbar[32];
    int tenths = percent/5 + 1;
    sprintf(progressbar, "[%*c%*c", tenths, '#', 22-tenths, ']');
    printf("\r%s %3d%% %7d of %5d KB %.2lf seconds",
           progressbar, percent, bufferUsed / 1024, bufferSize / 1024,
           elapsedTime);
    fflush(stdout);
}

// The main USB dump routine
static void usbdump (int num_packets, u32 timeout_ms)
{
    // Set up variables
    s64  start, elapsed_time;
    u08  packet[1024];
    int  packetnum   = 0;

    samplerate_khz = bg_samplerate(beagle, 0);

    // Configure Beagle 480 for delayed-download
    bg_usb480_capture_configure(beagle,
                                BG_USB480_CAPTURE_DELAYED_DOWNLOAD,
                                BG_USB2_AUTO_SPEED_DETECT);

    // Enable the hardware filtering.  This will filter out packets with
    // the same device address as the Beagle analyzer and also filter
    // the PID packet groups listed below.
    bg_usb480_hw_filter_config(beagle,
                               BG_USB2_HW_FILTER_SELF     |
                               BG_USB2_HW_FILTER_PID_SOF  |
                               BG_USB2_HW_FILTER_PID_IN   |
                               BG_USB2_HW_FILTER_PID_PING |
                               BG_USB2_HW_FILTER_PID_PRE  |
                               BG_USB2_HW_FILTER_PID_SPLIT);

    // Start the capture portion of the delayed-download capture
    printf("Starting delayed-download capture.\n");
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK) {
        printf("error: could not enable USB capture; exiting...\n");
        exit(1);
    }

    // Wait until timeout period elapses or the hardware buffer on
    // the Beagle USB 480 fills
    printf("Hardware buffer usage:\n");
    start = time_microseconds();

    while (1) {
        u32 buffer_size;
        u32 buffer_usage;
        u08 buffer_full;

        // Poll the hardware buffer status
        bg_usb480_hw_buffer_stats(beagle, &buffer_size, &buffer_usage,
                                  &buffer_full);

        // Print out the progress.
        elapsed_time = (time_microseconds() - start) / 1000;

        print_progress(buffer_usage / (buffer_size / 100),
                       ((double)elapsed_time) / 1000,
                       buffer_usage, buffer_size);

        // If timed out or buffer is full, exit loop
        if (buffer_full || (timeout_ms && elapsed_time > timeout_ms))
            break;

        // Sleep for 150 milliseconds
        bg_sleep_ms(150);
    }

    // Start the download portion of the delayed-download capture
    //
    // Output the header...
    printf("\n\nindex,time(ns),USB,status,pid,data0 ... dataN(*)\n");
    fflush(stdout);

    // ...then start decoding packets
    while (packetnum < num_packets || !num_packets) {
        u32   status;
        u32   events;
        u64   time_sop, time_sop_ns;
        u64   time_duration;
        u32   time_dataoffset;

        // Calling bg_usb480_read will automatically stop the
        // capture portion of the delayed-download capture and
        // will begin downloading the capture results.
        int length = bg_usb480_read(beagle, &status, &events,
                                    &time_sop, &time_duration,
                                    &time_dataoffset,
                                    1024, packet);

        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        // Check for invalid packet or Beagle error
        if (length < 0) {
            char error_status[32];
            sprintf(error_status, "error=%d", length);
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             error_status, 0);
            break;
        }

        // Output the current transaction
        if (length > 0 || events ||
            (status != 0 && status != BG_READ_TIMEOUT))
        {
            const char *packet_data = usb_print_data_packet(packet, length);
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             0, packet_data);
            ++packetnum;
        }

        // Exit if observe end of capture
        if (status & BG_READ_USB_END_OF_CAPTURE)  break;
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
"Usage: capture_usb480_extras num_events timeout\n"
"Example utility for executing a delayed-download capture of USB data from\n"
"a Beagle 480 protocol analyzer with hardware filtering enabled."
"\n\n"
"In delayed-download capture, the captured data is stored in the Beagle USB\n"
"480's hardware buffer while capture is in progress.  The capture data\n"
"is downloaded from the hardware after the capture has been halted.\n"
"\n"
"  The parameter num_events is set to the number of events to process\n"
"  before exiting.  If num_events is set to zero, the capture will continue\n"
"  indefinitely.\n"
"\n"
"  The parameter timeout is is the number of seconds to run the capture\n"
"  before downloading the results.  If timeout is set to zero, the capture\n"
"  portion will run until the hardware buffer is full.\n"
"\n"
"For product documentation and specifications, see www.totalphase.com.\n");
    fflush(stdout);
};


/*=========================================================================
| MAIN PROGRAM ENTRY POINT
 ========================================================================*/
int main (int argc, char *argv[])
{
    int port            = 0;      // open port 0 by default
    int samplerate      = 0;      // in kHz (query)
    int timeout         = 500;    // in milliseconds
    int latency         = 200;    // in milliseconds
    int num             = 0;
    int capture_timeout = 0;

    if (argc < 3) {
        print_usage();
        return 1;
    }

    num             = atoi(argv[1]);
    capture_timeout = atoi(argv[2]);

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

    printf("\n");
    fflush(stdout);

    // Capture the USB packets.
    usbdump(num, capture_timeout * 1000);

    // Close the device
    bg_close(beagle);

    return 0;
}
