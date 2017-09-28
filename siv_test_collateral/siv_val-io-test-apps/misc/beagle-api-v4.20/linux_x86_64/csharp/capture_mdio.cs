/*=========================================================================
| (C) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_mdio.cs
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
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_mdio {


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

    static void print_mdio_status (uint status)
    {
        // MDIO status codes
        if ((status &
             unchecked((uint)BeagleStatus.BG_MDIO_BAD_TURNAROUND)) != 0)
            Console.Write("MDIO_BAD_TURNAROUND ");
    }

    public static void mdiodump (int num_packets)
    {
        // Get the size of the timing information for a transaction of
        // max_bytes length
        int timing_size =
             BeagleApi.bg_bit_timing_size(BeagleProtocol.BG_PROTOCOL_MDIO, 0);

        uint[] timing  = new uint[timing_size];

        // Get the current sampling rate
        int samplerate_khz = BeagleApi.bg_samplerate(beagle, 0);

        // Start the capture
        if (BeagleApi.bg_enable(beagle, BeagleProtocol.BG_PROTOCOL_MDIO) !=
            (int)BeagleStatus.BG_OK) {
            Console.Write("error: could not enable MDIO capture; " +
               "exiting...\n");
            Environment.Exit(1);
        }

        Console.Write("index,time(ns),MDIO,status,<clause:opcode>," +
                "<addr1>,<addr2>,data\n");
        Console.Out.Flush();

        // Capture and print each transaction
        int i;
        for (i = 0; i < num_packets || num_packets == 0; ++i) {
            uint  packet = 0;
            uint  status = 0;
            ulong time_sop = 0, time_sop_ns = 0;
            ulong time_duration = 0;
            uint  time_dataoffset = 0;

            // Read transaction with bit timing data
            int count = BeagleApi.bg_mdio_read_bit_timing(
                            beagle, ref status, ref time_sop,
                            ref time_duration, ref time_dataoffset,
                            ref packet, timing_size, timing);

            // Translate timestamp to ns
            time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

            // Check for errors
            if (count < 0) {
                Console.Write("{0,4:d},{1,13:d},MDIO,( error={2:d},",
                       i, time_sop_ns, count);
                print_general_status(status);
                print_mdio_status(status);
                Console.Write(")\n");
                Console.Out.Flush();
                continue;
            }

            // Parse the MDIO frame
            byte clause = 0;
            byte opcode = 0;
            byte addr1 = 0;
            byte addr2 = 0;
            ushort data = 0;
            int ret = BeagleApi.bg_mdio_parse(packet, ref clause,
                ref opcode, ref addr1, ref addr2, ref data);

            Console.Write("{0:d},{1:d},MDIO,(", i, time_sop_ns);
            print_general_status(status);
            if ((status & BeagleApi.BG_READ_TIMEOUT) == 0)
                print_mdio_status((uint)ret);
            Console.Write(")");

            // If zero data captured, continue
            if (count == 0) {
                Console.Write("\n");
                Console.Out.Flush();
                continue;
            }

            // Print the clause and opcode
            Console.Write(",");
            if ((status & BeagleApi.BG_READ_ERR_MIDDLE_OF_PACKET) == 0) {
                if (clause == (byte)BeagleMdioClause.BG_MDIO_CLAUSE_22) {
                    Console.Write("<22:");
                    switch (opcode) {
                      case BeagleApi.BG_MDIO_OPCODE22_WRITE:
                        Console.Write("W");
                        break;
                      case BeagleApi.BG_MDIO_OPCODE22_READ:
                        Console.Write("R");
                        break;
                      case BeagleApi.BG_MDIO_OPCODE22_ERROR:
                        Console.Write("?");
                        break;
                    }
                }
                else if (clause == (byte)BeagleMdioClause.BG_MDIO_CLAUSE_45) {
                    Console.Write("<45:");
                    switch (opcode) {
                      case BeagleApi.BG_MDIO_OPCODE45_ADDR:
                        Console.Write("A");
                        break;
                      case BeagleApi.BG_MDIO_OPCODE45_WRITE:
                        Console.Write("W");
                        break;
                      case BeagleApi.BG_MDIO_OPCODE45_READ_POSTINC:
                        Console.Write("RI");
                        break;
                      case BeagleApi.BG_MDIO_OPCODE45_READ:
                        Console.Write("R");
                        break;
                    }
                }
                else
                    Console.Write("<?:?");

                // Recall that for Clause 22:
                //     PHY  Addr = addr1, Reg Addr = addr2
                // and for Clause 45:
                //     Port Addr = addr1, Dev Addr = addr2
                Console.Write(">,<{0:X2}>,<{1:X2}>,{2:X4}\n",
                        addr1, addr2, data);
            }
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
        Console.Write(
"Usage: capture_mdio num_events\n" +
"Example utility for capturing MDIO data from Beagle protocol analyzers.\n" +
"\n" +
"  The parameter num_events is set to the number of events to process\n" +
"  before exiting.  If num_events is set to zero, the capture will continue\n" +
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
       uint timeout    = 500;    // in milliseconds
       uint latency    = 200;    // in milliseconds
       byte target_pow = BeagleApi.BG_TARGET_POWER_OFF;
       int  num        = 0;

       if (args.Length < 1)
       {
           print_usage();
           Environment.Exit(1);
       }
       num = Convert.ToInt32(args[0]);

       // Open the device
       beagle = BeagleApi.bg_open(port);
       if (beagle <= 0) {
           Console.Write("Unable to open Beagle device on port {0:d}\n", port);
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
       BeagleApi.bg_target_power(beagle, target_pow);

       Console.Write("\n");
       Console.Out.Flush();

       mdiodump(num);

       // Close the device
       BeagleApi.bg_close(beagle);

       return;
   }
}
