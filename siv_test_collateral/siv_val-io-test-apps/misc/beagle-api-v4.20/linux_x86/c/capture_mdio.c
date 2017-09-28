/*=========================================================================
| (c) 2006-2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Examples
| File    : capture_mdio.c
|--------------------------------------------------------------------------
| Simple Capture Example for MDIO
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

// The printf format strings are differenct for 64-bit integers
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

    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE)
        printf("PARTIAL_BYTE(bit %d) ", status & 0xff);
}

static void print_mdio_status (u32 status)
{
    // MDIO status codes
    if (status & BG_MDIO_BAD_TURNAROUND)
        printf("MDIO_BAD_TURNAROUND ");
}


/*=========================================================================
| MDIO DUMP FUNCTION
 ========================================================================*/
static void mdiodump (int num_packets) {
    // Get the size of the timing information for a transaction of
    // max_bytes length
    int  timing_size = bg_bit_timing_size(BG_PROTOCOL_MDIO, 0);
    u32 *timing  = (u32 *)malloc(timing_size*sizeof(u32));

    // Get the current sampling rate
    u32 samplerate_khz = bg_samplerate(beagle, 0);
    int i;

    // Start the capture
    if (bg_enable(beagle, BG_PROTOCOL_MDIO) != BG_OK) {
        printf("error: could not enable MDIO capture; exiting...\n");
        exit(1);
    }

    printf("index,time(ns),MDIO,status,<clause:opcode>,<addr1>,<addr2>,data\n");
    fflush(stdout);

    // Capture and print each transaction
    for (i = 0; i < num_packets || !num_packets; ++i) {
        u32 packet;
        u32 status;
        u64 time_sop, time_sop_ns;
        u64 time_duration;
        u32 time_dataoffset;
        u08 clause;
        u08 opcode;
        u08 addr1;
        u08 addr2;
        u16 data;
        int ret;

        // Read transaction with bit timing data
        int count = bg_mdio_read_bit_timing(beagle, &status,
                                            &time_sop, &time_duration,
                                            &time_dataoffset,
                                            &packet,
                                            timing_size, timing);

        // Translate timestamp to ns
        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        // Check for errors
        if (count < 0) {
            printf("%d,%" U64_FORMAT_STR ",MDIO,( error=%d,",
                   i, time_sop_ns, count);
            print_general_status(status);
            print_mdio_status(status);
            printf(")\n");
            fflush(stdout);
            continue;
        }

        // Parse the MDIO frame
        ret = bg_mdio_parse(packet, &clause, &opcode, &addr1, &addr2, &data);

        printf("%d,%" U64_FORMAT_STR ",MDIO,(", i, time_sop_ns);
        print_general_status(status);
        if (!(status & BG_READ_TIMEOUT))
            print_mdio_status(ret);
        printf(")");

        // If zero data captured, continue
        if (count == 0) {
            printf("\n");
            fflush(stdout);
            continue;
        }

        // Print the clause and opcode
        printf(",");
        if (!(status & BG_READ_ERR_MIDDLE_OF_PACKET)) {
            if (clause == BG_MDIO_CLAUSE_22) {
                printf("<22:");
                switch (opcode) {
                  case BG_MDIO_OPCODE22_WRITE:
                    printf("W");
                    break;
                  case BG_MDIO_OPCODE22_READ:
                    printf("R");
                    break;
                  case BG_MDIO_OPCODE22_ERROR:
                    printf("?");
                    break;
                }
            }
            else if (clause == BG_MDIO_CLAUSE_45) {
                printf("<45:");
                switch (opcode) {
                  case BG_MDIO_OPCODE45_ADDR:
                    printf("A");
                    break;
                  case BG_MDIO_OPCODE45_WRITE:
                    printf("W");
                    break;
                  case BG_MDIO_OPCODE45_READ_POSTINC:
                    printf("RI");
                    break;
                  case BG_MDIO_OPCODE45_READ:
                    printf("R");
                    break;
                }
            }
            else
                printf("<?:?");

            // Recall that for Clause 22:  PHY  Addr = addr1, Reg Addr = addr2
            //         and for Clause 45:  Port Addr = addr1, Dev Addr = addr2
            printf(">,<%02X>,<%02X>,%04X\n", addr1, addr2, data);
        }
        fflush(stdout);
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
"Usage: capture_mdio num_events\n"
"Example utility for capturing MDIO data from Beagle protocol analyzers.\n"
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
    int target_pow = BG_TARGET_POWER_OFF;
    int num        = 0;

    if (argc < 2)
    {
        print_usage();
        exit(1);
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

    // There is usually no need for target power when using the
    // Beagle as a passive monitor.
    bg_target_power(beagle, (u08)target_pow);

    printf("\n");

    mdiodump(num);

    // Close the device
    bg_close(beagle);

    return 0;
}
