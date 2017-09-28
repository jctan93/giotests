/*=========================================================================
| (c) 2005-2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_i2c.c
|--------------------------------------------------------------------------
| Simple Capture Example for I2C
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
// This will only work for sample rates that
// are multiples of 1MHz.  If any other rates
// are desired, this code needs to be changed.
#define TIMESTAMP_TO_NS(stamp, samplerate_khz) \
    (u64)(stamp * (u64)1000 / (u64)(samplerate_khz/1000))

// The printf format strings are different for 64-bit integers
// between Windows and Linux
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

static void print_i2c_status (u32 status)
{
    // I2C status codes
    if (status & BG_READ_I2C_NO_STOP)
        printf("I2C_NO_STOP ");
}


/*=========================================================================
| I2C DUMP FUNCTION
 ========================================================================*/
static void i2cdump (int max_bytes, int num_packets) {
    // Get the size of the timing information for a transaction of
    // max_bytes length
    int timing_size = bg_bit_timing_size(BG_PROTOCOL_I2C, max_bytes);

    u16 *data_pointer;
    u16 *data_in = (u16 *)malloc(max_bytes*sizeof(u16));
    u32 *timing  = (u32 *)malloc(timing_size*sizeof(u32));

    // Get the current sampling rate
    u32 samplerate_khz = bg_samplerate(beagle, 0);

    int i, n;

    // Start the capture
    if (bg_enable(beagle, BG_PROTOCOL_I2C) != BG_OK) {
        printf("error: could not enable I2C capture; exiting...\n");
        exit(1);
    }

    printf("index,time(ns),I2C,status,<addr:r/w>(*),data0 ... dataN(*)\n");
    fflush(stdout);

    // Capture and print each transaction
    for (i = 0; i < num_packets || !num_packets; ++i) {
        u32 status;
        u64 time_sop, time_sop_ns;
        u64 time_duration;
        u32 time_dataoffset;

        // Read transaction with bit timing data
        int count = bg_i2c_read_bit_timing(beagle, &status,
                                           &time_sop, &time_duration,
                                           &time_dataoffset,
                                           max_bytes, data_in,
                                           timing_size, timing);

        // Translate timestamp to ns
        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        printf("%d,%" U64_FORMAT_STR ",I2C,(", i, time_sop_ns);

        if (count < 0)
            printf("error=%d,", count);

        print_general_status(status);
        print_i2c_status(status);
        printf(")");

        // Check for errors
        if (count <= 0) {
            printf("\n");
            fflush(stdout);

            if (count < 0)
                break;

            // If zero data captured, continue
            continue;
        }

        // Print the address and read/write
        printf(",");
        if (!(status & BG_READ_ERR_MIDDLE_OF_PACKET)) {
            // Display the start condition
            printf("[S] ");

            if (count >= 1) {
                // Determine if byte was NACKed
                int nack = (data_in[0] & BG_I2C_MONITOR_NACK);

                // Determine if this is a 10-bit address
                if (count == 1 || (data_in[0] & 0xf9) != 0xf0 || nack) {
                    // Display 7-bit address
                    printf("<%02x:%c>%s ", (data_in[0] & 0xff) >> 1,
                           data_in[0] & 0x01 ? 'r' : 'w',
                           nack ? "*" : "");
                    count--;
                    data_pointer = data_in + 1;
                }
                else {
                    // Display 10-bit address
                    printf("<%03x:%c>%s ",
                           ((data_in[0] << 7) & 0x300) | (data_in[1] & 0xff),
                           data_in[0] & 0x01 ? 'r' : 'w',
                           nack ? "*" : "");
                    count -= 2;
                    data_pointer = data_in + 2;
                }
            }
        }

        // Display rest of transaction
        for (n = 0; n < count; ++n) {
            // Determine if byte was NACKed
            int nack = (*data_pointer & BG_I2C_MONITOR_NACK);

            printf("%02x%s ", *data_pointer & 0xff, nack ? "*" : "");
            ++data_pointer;
        }

        // Display the stop condition
        if (!(status & BG_READ_I2C_NO_STOP))
            printf("[P]");

        printf("\n");
        fflush(stdout);
    }

    free(data_in);
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
"Usage: capture_i2c max_packet_len num_events\n"
"Example utility for capturing I2C data from Beagle protocol analyzers.\n"
"\n"
"  The parameter max_packet_len is set to the maximum expected packet length\n"
"  throughout the entire capture session.\n"
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
    int samplerate = 10000;  // in kHz
    int timeout    = 500;    // in milliseconds
    int latency    = 200;    // in milliseconds
    int len        = 0;
    int pullups    = BG_I2C_PULLUP_OFF;
    int target_pow = BG_TARGET_POWER_OFF;
    int num        = 0;

    if (argc < 3)
    {
        print_usage();
	exit(1);
    }
    len = atoi(argv[1]);
    num = atoi(argv[2]);

    // Open the device
    beagle = bg_open(port);
    if (beagle <= 0) {
        printf("Unable to open Beagle device on port %d\n", port);
        printf("Error code = %d\n", beagle);
        return 1;
    }
    printf("Opened Beagle device on port %d\n", port);

    // Set the samplerate
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
    bg_i2c_pullup(beagle, (u08)pullups);
    bg_target_power(beagle, (u08)target_pow);

    printf("\n");
    fflush(stdout);

    i2cdump(len, num);

    // Close the device
    bg_close(beagle);

    return 0;
}
