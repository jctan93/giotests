/*=========================================================================
| (C) 2006-2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_usb12.cs
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
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_usb12 {


    /*=====================================================================
    | CONSTANTS
     ====================================================================*/
    private const int IDLE_THRESHOLD = 2000;


    /*=====================================================================
    | STATIC GLOBALS
     ====================================================================*/
    static int beagle;
    static int samplerateKhz;


    /*=====================================================================
    | STATIC FUNCTIONS
     ====================================================================*/
    public static ulong TIMESTAMP_TO_NS (ulong stamp, int samplerateKhz) {
        return (ulong)(stamp * 1000 / (ulong)(samplerateKhz/1000));
    }

    static void printGeneralStatus (uint status) {
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

    static void printUsbStatus (uint status) {
        /* USB status codes */
        if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SIGNALS) != 0)
            Console.Write("BAD_SIGNAL; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SYNC) != 0)
            Console.Write("BAD_SYNC; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_BIT_STUFF) != 0)
            Console.Write("BAD_STUFF; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_FALSE_EOP) != 0)
            Console.Write("BAD_EOP; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_LONG_EOP) != 0)
            Console.Write("LONG_EOP; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_BAD_PID) != 0)
            Console.Write("BAD_PID; ");

        if ((status & BeagleApi.BG_READ_USB_ERR_BAD_CRC) != 0)
            Console.Write("BAD_CRC; ");

    }

    static void printUsbEvents (uint events) {
        /* USB event codes */
        if ((events & BeagleApi.BG_EVENT_USB_HOST_DISCONNECT) != 0)
            Console.Write("HOST_DISCON; ");

        if ((events & BeagleApi.BG_EVENT_USB_TARGET_DISCONNECT) != 0)
            Console.Write("TGT_DISCON; ");

        if ((events & BeagleApi.BG_EVENT_USB_RESET) != 0)
            Console.Write("RESET; ");

        if ((events & BeagleApi.BG_EVENT_USB_HOST_CONNECT) != 0)
            Console.Write("HOST_CONNECT; ");

        if ((events & BeagleApi.BG_EVENT_USB_TARGET_CONNECT) != 0)
            Console.Write("TGT_CONNECT/UNRST; ");
    }

    static void usbPrintSummary (int    i,
                                 ulong  countSop,
                                 String summary)
    {
        Console.Write("{0:d},{1:d},USB,( ),{2:s}\n",
                i, TIMESTAMP_TO_NS(countSop, samplerateKhz), summary);
    }

    // Renders packet data for printing.
    // The returned string needs to be free'd
    static String usbPrintDataPacket (ref byte[] packet,
                                          int    length)
    {
        String packetstring = "";
        byte pid;

        if (length == 0) {
            packetstring = null;
            return packetstring;
        }

        /* Get the packet identifier */
        pid = packet[0];

        /* Print the packet identifier */
        String pidstr = "";
        switch (pid) {
          case BeagleApi.BG_USB_PID_OUT:      pidstr = "OUT";      break;
          case BeagleApi.BG_USB_PID_IN:       pidstr = "IN";       break;
          case BeagleApi.BG_USB_PID_SOF:      pidstr = "SOF";      break;
          case BeagleApi.BG_USB_PID_SETUP:    pidstr = "SETUP";    break;

          case BeagleApi.BG_USB_PID_DATA0:    pidstr = "DATA0";    break;
          case BeagleApi.BG_USB_PID_DATA1:    pidstr = "DATA1";    break;
          case BeagleApi.BG_USB_PID_DATA2:    pidstr = "DATA2";    break;
          case BeagleApi.BG_USB_PID_MDATA:    pidstr = "MDATA";    break;

          case BeagleApi.BG_USB_PID_ACK:      pidstr = "ACK";      break;
          case BeagleApi.BG_USB_PID_NAK:      pidstr = "NAK";      break;
          case BeagleApi.BG_USB_PID_STALL:    pidstr = "STALL";    break;
          case BeagleApi.BG_USB_PID_NYET:     pidstr = "NYET";     break;

          case BeagleApi.BG_USB_PID_PRE:      pidstr = "PRE";      break;
          case BeagleApi.BG_USB_PID_SPLIT:    pidstr = "SPLIT";    break;
          case BeagleApi.BG_USB_PID_PING:     pidstr = "PING";     break;
          case BeagleApi.BG_USB_PID_EXT:      pidstr = "EXT";      break;

          default:
            pidstr = "INVALID";
            break;
        }

        packetstring += "," + pidstr + ",";

        int n = 0;
        for (n = 0; n < length; ++n) {
            packetstring += String.Format("{0,2:x2} ", packet[n]);
        }
        return packetstring;
    }

    // Print common packet header information
    static void usbPrintPacket (int    packetNumber,
                                ulong  timeSop,
                                uint   status,
                                uint   events,
                                String errorStatus,
                                String packetData)
    {
       if (errorStatus == null)  errorStatus = "";
       Console.Write("{0:d},{1:d},USB,({2:s}",
                    packetNumber, timeSop, errorStatus);
       printGeneralStatus(status);
       printUsbStatus(status);
       printUsbEvents(events);

       if (packetData == null)  packetData = "";
       Console.Write("){0:s}\n",packetData);
       Console.Out.Flush();
    }

    // Dump saved summary information
    static int usbPrintSummaryPacket (int   packetNumber,
                                      ulong countSop,
                                      int   sofCount,
                                      int   preCount,
                                      int   inAckCount,
                                      int   inNakCount,
                                      int   syncErrors)
    {
        int offset = 0;

        String summary = "";
        if ((sofCount != 0) || (inAckCount != 0) || (inNakCount != 0) ||
                (preCount != 0))
        {
            summary +=  "COLLAPSED ";

            if (sofCount > 0)
                summary += String.Format("[{0:d} SOF] ",  sofCount);

            if (preCount > 0)
                summary += String.Format("[{0:d} PRE/ERR] ", preCount);

            if (inAckCount > 0)
                summary += String.Format("[{0:d} IN/ACK] ", inAckCount);

            if (inNakCount > 0)
                summary += String.Format("[{0:d} IN/NAK] ", inNakCount);

            usbPrintSummary(packetNumber+offset, countSop, summary);
            offset++;
        }

        /* Output any sync errors */
        if (syncErrors > 0) {
            summary += String.Format("<{0:d} SYNC ERRORS>", syncErrors);

            usbPrintSummary(packetNumber+offset, countSop, summary);
            ++offset;
        }
        return offset;
    }

    static bool usbTrigger (int pid)
    {
        return (pid != BeagleApi.BG_USB_PID_SOF)  &&
               (pid != BeagleApi.BG_USB_PID_PRE)  &&
               (pid != BeagleApi.BG_USB_PID_IN)   &&
               (pid != BeagleApi.BG_USB_PID_ACK)  &&
               (pid != BeagleApi.BG_USB_PID_NAK);
    }

    static void usbDump (int numPackets) {
        // Set up variables
        byte[]  packet = new byte[1024];

        int  timingSize =
             BeagleApi.bg_bit_timing_size(BeagleProtocol.BG_PROTOCOL_USB, 1024);
        uint[] timing  = new uint[timingSize];

        byte[]  savedIn       = new byte[64];
        uint[]  savedInTiming = new uint[8*64];
        ulong   savedInSop    = 0;
        int     savedInLength = 0;
        uint    savedInStatus = 0;
        uint    savedInEvents = 0;

        ulong countSop  = 0;
        int  sofCount   = 0;
        int  preCount   = 0;
        int  inAckCount = 0;
        int  inNakCount = 0;

        byte pid        = 0;
        int  syncErrors = 0;
        int  packetnum  = 0;

        samplerateKhz = BeagleApi.bg_samplerate(beagle, 0);

        int  idleSamples = IDLE_THRESHOLD * samplerateKhz;

        // Open the connection to the Beagle.  Default to port 0.
        if (BeagleApi.bg_enable(beagle, BeagleProtocol.BG_PROTOCOL_USB) !=
           (int)BeagleStatus.BG_OK) {
            Console.Write("error: could not enable USB capture; exiting...\n");
            Environment.Exit(1);
        }

        // Output the header...
        Console.Write("index,time(ns),USB,status,pid,data0 ... dataN(*)\n");
        Console.Out.Flush();

        // ...then start decoding packets
        while (packetnum < numPackets || (numPackets == 0)) {
            uint  status         = 0;
            uint  events         = 0;
            ulong timeSop        = 0;
            ulong timeSopNS      = 0;
            ulong timeDuration   = 0;
            uint  timeDataOffset = 0;

            int length = BeagleApi.bg_usb12_read_bit_timing(
                             beagle, ref status, ref events, ref timeSop,
                             ref timeDuration, ref timeDataOffset,
                             1024, packet, timingSize, timing);

            timeSopNS = TIMESTAMP_TO_NS(timeSop, samplerateKhz);

            // Check for invalid packet or Beagle error
            if (length < 0) {
                String errorStatus = "";
                errorStatus += String.Format("error={0:d}", length);
                usbPrintPacket(packetnum, timeSopNS, status, events,
                               errorStatus, null);
                break;
            }

            // Check for USB error
            if (status == BeagleApi.BG_READ_USB_ERR_BAD_SYNC)
                ++syncErrors;

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
            if (status != BeagleApi.BG_READ_OK || usbTrigger(pid) ||
                ((int)(timeSop - countSop) >= idleSamples) ) {
                int offset =
                    usbPrintSummaryPacket(packetnum, countSop,
                                          sofCount, preCount, inAckCount,
                                          inNakCount, syncErrors);

                sofCount   = 0;
                preCount   = 0;
                inAckCount = 0;
                inNakCount = 0;
                syncErrors = 0;
                countSop   = timeSop;

                // Adjust the packet index if any events were printed by
                // usbPrintSummaryPacket.
                packetnum += offset;
            }

            // Now handle the current packet based on its packet ID
            switch (pid) {
              case BeagleApi.BG_USB_PID_SOF:
                // Increment the SOF counter
                ++sofCount;
                break;

              case BeagleApi.BG_USB_PID_PRE:
                // Increment the PRE counter
                ++preCount;
                break;

              case BeagleApi.BG_USB_PID_IN:
                // If the transaction is an IN, don't display it yet and
                // save the transaction.
                // If the following transaction is an ACK or NAK,
                // increment the appropriate IN/ACK or IN/NAK counter.
                // If the next transaction is not an ACK or NAK,
                // display the saved IN transaction .
                System.Array.Copy(packet, 0, savedIn, 0, length);
                System.Array.Copy(timing, 0, savedInTiming, 0, length*8);

                savedInSop    = timeSop;
                savedInLength = length;
                savedInStatus = status;
                savedInEvents = events;
                break;

              case BeagleApi.BG_USB_PID_NAK:
                goto case BeagleApi.BG_USB_PID_ACK;

              case BeagleApi.BG_USB_PID_ACK:
                // If the last transaction was IN, increment the appropriate
                // counter and don't display the transaction.
                if (savedInLength > 0) {
                    savedInLength = 0;

                    if (pid == BeagleApi.BG_USB_PID_ACK)
                        ++inAckCount;
                    else
                        ++inNakCount;

                    break;
                }
                goto default;

              default:
                // If the last transaction was IN, output it
                if (savedInLength > 0) {
                    ulong saved_in_sop_ns =
                        TIMESTAMP_TO_NS(savedInSop, samplerateKhz);

                    String packetData = usbPrintDataPacket
                                                  (ref savedIn,
                                                        savedInLength);
                    usbPrintPacket(packetnum, saved_in_sop_ns, savedInStatus,
                                   savedInEvents, null, packetData);
                    ++packetnum;

                    savedInLength = 0;
                }

                // Output the current transaction
                if (length > 0 || events != 0 ||
                (status != 0 && status != BeagleApi.BG_READ_TIMEOUT)) {
                    String packetData = usbPrintDataPacket(ref packet,
                                                            length);
                    usbPrintPacket(packetnum, timeSopNS, status,
                                   events, null, packetData);
                    ++packetnum;
                }
                countSop = timeSop + timeDuration;
                break;
            }
        }

        // Stop the capture
        BeagleApi.bg_disable(beagle);
    }


    /*=====================================================================
    | USAGE INFORMATION
     ====================================================================*/
    static void printUsage ()
    {
        Console.Write("Usage: capture_usb num_events\n" +
"Example utility for capturing USB data from Beagle protocol analyzers.\n" +
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
       int port       = 0;      // open port 0 by default
       int samplerate = 0;      // in kHz (query)
       uint timeout   = 500;    // in milliseconds
       uint latency   = 200;    // in milliseconds
       int num        = 0;

       if (args.Length < 1)
       {
           printUsage();
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

       // Query the samplerate since Beagle USB has a fixed sampling rate
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
       BeagleApi.bg_target_power(beagle, BeagleApi.BG_TARGET_POWER_OFF);

       Console.Write("\n");
       Console.Out.Flush();

       usbDump(num);

       // Close the device
       BeagleApi.bg_close(beagle);

       return;
   }
}
