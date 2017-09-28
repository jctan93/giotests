/*=========================================================================
| (C) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_i2c.cs
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
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_i2c {

    /*=====================================================================
    | CONSTANTS
     ====================================================================*/
    private const int I2C_BITRATE = 100; // kHz

    /*=====================================================================
    | STATIC GLOBALS
     ====================================================================*/
    static int beagle;


    /*=====================================================================
    | STATIC FUNCTIONS
     ====================================================================*/
    public static ulong TIMESTAMP_TO_NS (ulong stamp, int samplerate_khz)
    {
        return (ulong)(stamp * 1000 / (ulong)(samplerate_khz/1000));
    }

    static void print_general_status (uint status)
    {
        Console.Write(" ");

        // General status codes
        if (status == BeagleApi.BG_READ_OK)
            Console.Write("OK ");

        if ((status & BeagleApi.BG_READ_TIMEOUT) != 0)
            Console.Write("TIMEOUT ");

        if ((status & BeagleApi.BG_READ_ERR_MIDDLE_OF_PACKET) != 0)
            Console.Write("MIDDLE ");

        if ((status & BeagleApi.BG_READ_ERR_SHORT_BUFFER) != 0)
            Console.Write("SHORT BUFFER ");

        if ((status & BeagleApi.BG_READ_ERR_PARTIAL_LAST_BYTE) != 0)
            Console.Write("PARTIAL_BYTE(bit {0:d}) ", status & 0xff);
    }


    static void print_i2c_status (uint status)
    {
        // I2C status codes
        if ((status & BeagleApi.BG_READ_I2C_NO_STOP) != 0)
            Console.Write("I2C_NO_STOP ");
    }

    public static void i2cdump (int max_bytes, int num_packets)
    {
        // Get the size of the timing information for a transaction of
        // max_bytes length
        int timing_size = BeagleApi.bg_bit_timing_size(
            BeagleProtocol.BG_PROTOCOL_I2C, max_bytes);

        ushort[] data_in = new ushort[max_bytes];
        uint[]   timing  = new uint[timing_size];

        // Get the current sampling rate
        int samplerate_khz = BeagleApi.bg_samplerate(beagle, 0);

        int i;

        // Start the capture
        if (BeagleApi.bg_enable(beagle, BeagleProtocol.BG_PROTOCOL_I2C) !=
            (int)BeagleStatus.BG_OK) {
            Console.Write("error: could not enable I2C capture; exiting...\n");
            Environment.Exit(1);
        }

        Console.Write("index,time(ns),I2C,status,<addr:r/w>" +
                "(*),data0 ... dataN(*)\n");
        Console.Out.Flush();

        // Capture and print each transaction
        for (i = 0; i < num_packets || num_packets == 0; ++i) {
            uint status = 0;
            ulong time_sop = 0, time_sop_ns = 0;
            ulong time_duration = 0;
            uint  time_dataoffset = 0;

            // Read transaction with bit timing data
            int count = BeagleApi.bg_i2c_read_bit_timing(
                            beagle, ref status, ref time_sop,
                            ref time_duration, ref time_dataoffset,
                            max_bytes, data_in, timing_size, timing);

            // Translate timestamp to ns
            time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

            Console.Write("{0:d},{1:d}", i, time_sop_ns);
            Console.Write(",I2C,(");

            if (count < 0)
                Console.Write("error={0:d},", count);

            print_general_status(status);
            print_i2c_status(status);
            Console.Write(")");

            // Check for errors
            if (count <= 0) {
                Console.Write("\n");
                Console.Out.Flush();

                if (count < 0)
                    break;

                // If zero data captured, continue
                continue;
            }


            // Print the address and read/write
            Console.Write(",");
            int offset = 0;
            if ((status & BeagleApi.BG_READ_ERR_MIDDLE_OF_PACKET) == 0) {
                // Display the start condition
                Console.Write("[S] ");

                if (count >= 1) {
                    // Determine if byte was NACKed
                    int nack = (data_in[0] & BeagleApi.BG_I2C_MONITOR_NACK);

                    // Determine if this is a 10-bit address
                    if (count == 1 || (data_in[0] & 0xf9) != 0xf0 ||
                        (nack != 0)) {
                        // Display 7-bit address
                        Console.Write("<{0:x2}:{1:s}>{2:s} ",
                               (data_in[0] & 0xff) >> 1,
                               ((data_in[0] & 0x01) != 0) ? 'r' : 'w',
                               (nack != 0) ? "*" : "");
                        offset = 1;
                    }
                    else {
                        // Display 10-bit address
                        Console.Write("<{0:x3}:{1:s}>{2:s} ",
                               ((data_in[0] << 7) & 0x300) |
                                                (data_in[1] & 0xff),
                               ((data_in[0] & 0x01) != 0) ? 'r' : 'w',
                               (nack != 0) ? "*" : "");
                        offset = 2;
                    }
                }
            }

            // Display rest of transaction
            count = count - offset;
            for (int n = 0; n < count; ++n) {
                // Determine if byte was NACKed
                int nack = (data_in[offset] & BeagleApi.BG_I2C_MONITOR_NACK);

                Console.Write("{0:x2}{1:s} ",
                        data_in[offset] & 0xff, (nack != 0) ? "*" : "");
                ++offset;
            }

            // Display the stop condition
            if ((status & BeagleApi.BG_READ_I2C_NO_STOP) == 0)
                Console.Write("[P]");

            Console.Write("\n");
            Console.Out.Flush();
        }

        // Stop the capture
        BeagleApi.bg_disable(beagle);
    }


    /*=====================================================================
    | USAGE INFORMATION
     ====================================================================*/
    static void print_usage ()
    {
        Console.Write("Usage: capture_i2c max_packet_len num_events\n" +
"Example utility for capturing i2c data from Beagle protocol analyzers.\n" +
"\n" +
"  The parameter max_packet_len is set to the maximum expected packet length\n"+ "  throughout the entire capture session.\n" +
"\n" +
"  The parameter num_events is set to the number of events to process\n" +
"  before exiting. If num_events is set to zero, the capture will continue\n" +
"  indefinitely.\n" +
"\n" +
"For product documentation and specifications, see www.totalphase.com.\n");
        Console.Out.Flush();
    }

    /*=====================================================================
    | MAIN PROGRAM
     ====================================================================*/
    public static void Main (String[] args) {
        int  port       = 0;      // open port 0 by default
        int  samplerate = 10000;  // in kHz
        uint  timeout   = 500;    // in milliseconds
        uint  latency   = 200;    // in milliseconds
        int  len        = 0;
        byte pullups    = BeagleApi.BG_I2C_PULLUP_OFF;
        byte target_pow = BeagleApi.BG_TARGET_POWER_OFF;
        int  num        = 0;

        if (args.Length < 2)
        {
            print_usage();
            Environment.Exit(1);
        }
        len = Convert.ToInt32(args[0]);
        num = Convert.ToInt32(args[1]);

        // Open the device
        beagle = BeagleApi.bg_open(port);
        if (beagle <= 0) {
            Console.Write("Unable to open Beagle device on port {0:d}\n",
                          port);
            Console.Write("Error code = {0:d}\n", beagle);
            Environment.Exit(1);
        }
        Console.Write("Opened Beagle device on port {0:d}\n", port);

        // Set the samplerate
        samplerate = BeagleApi.bg_samplerate(beagle, samplerate);
        if (samplerate < 0) {
            Console.Write("error: {0:s}\n",
                 BeagleApi.bg_status_string(samplerate));
            Environment.Exit(1);
        }
        Console.Write("Sampling rate set to {0:d} KHz.\n", samplerate);

        // Set the idle timeout.
        // The Beagle read functions will return in the specified time
        // if there is no data available on the bus.
        BeagleApi.bg_timeout(beagle, timeout);
        Console.Write("Idle timeout set to {0:d} ms.\n", timeout);

        // Set the latency.
        // The latency parameter allows the programmer to balance the
        // tradeoff between host side buffering and the latency to
        // receive a packet when calling one of the Beagle read
        // functions.
        BeagleApi.bg_latency(beagle, latency);
        Console.Write("Latency set to {0:d} ms.\n", latency);

        Console.Write("Host interface is {0:s}.\n",
               ((BeagleApi.bg_host_ifce_speed(beagle)) != 0) ?
                                                 "high speed" : "full speed");

        // There is usually no need for pullups or target power
        // when using the Beagle as a passive monitor.
        BeagleApi.bg_i2c_pullup(beagle, pullups);
        BeagleApi.bg_target_power(beagle, target_pow);

        Console.Write("\n");
        Console.Out.Flush();

        i2cdump(len, num);

        // Close the device
        BeagleApi.bg_close(beagle);

        return;
    }
}
