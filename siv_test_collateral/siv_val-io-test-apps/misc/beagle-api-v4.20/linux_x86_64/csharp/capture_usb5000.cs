/*=========================================================================
| (C) 2011  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_usb5000.cs
|--------------------------------------------------------------------------
| Simple Capture Example for Beagle USB 5000
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
| DEFINES
 ========================================================================*/
// Enable statistics mode rather than packet printing mode.
#define STATS_MODE


/*=========================================================================
| USING
 ========================================================================*/
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_usb5000 {


    /*=====================================================================
    | CONSTANTS
     ====================================================================*/
    private const int DISPLAY_TIME_TICKS = 10000000;

    private static string[] LTSSM_TABLE = new string[] {
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


    /*=====================================================================
    | STATIC GLOBALS
     ====================================================================*/
    static int beagle;
    static int samplerateKHz;


    /*=====================================================================
    | STATIC FUNCTIONS
     ====================================================================*/
    public static ulong timestampToNS (ulong stamp, int samplerateKHz) {
        return (ulong)(stamp * 1000 / (ulong)(samplerateKHz/1000));
    }

    static void printGeneralStatus (uint status) {
        Console.Write(" ");

        // General status codes
        if (status == BeagleApi.BG_READ_OK)
            Console.Write("OK ");

        if ((status & BeagleApi.BG_READ_TIMEOUT) != 0)
            Console.Write("TIMEOUT ");

        if ((status & BeagleApi.BG_READ_ERR_UNEXPECTED) != 0)
            Console.Write("UNEXPECTED ");

        if ((status & BeagleApi.BG_READ_ERR_MIDDLE_OF_PACKET) != 0)
            Console.Write("MIDDLE ");

        if ((status & BeagleApi.BG_READ_ERR_SHORT_BUFFER) != 0)
            Console.Write("SHORT BUFFER ");

        if ((status & BeagleApi.BG_READ_ERR_PARTIAL_LAST_BYTE) != 0)
            Console.Write("PARTIAL_BYTE(bit {0:d}) ", status & 0xff);

        if ((status & BeagleApi.BG_READ_USB_END_OF_CAPTURE) != 0)
            Console.Write("END_OF_CAPTURE ");
    }

    static void printSource (BeagleUsb5000Source source) {
        switch (source) {
          case BeagleUsb5000Source.BG_USB5000_SOURCE_ASYNC:
            Console.Write("Async");
            break;

          case BeagleUsb5000Source.BG_USB5000_SOURCE_RX:
            Console.Write("SSRX");
            break;
          case BeagleUsb5000Source.BG_USB5000_SOURCE_TX:
            Console.Write("SSTX");
            break;
          case BeagleUsb5000Source.BG_USB5000_SOURCE_USB2:
            Console.Write("USB2");
            break;
        }
    }

    static void printUsbStatus (BeagleUsb5000Source source, uint status) {
        if (source == BeagleUsb5000Source.BG_USB5000_SOURCE_USB2) {
            // USB 2 status codes
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

            if ((status & BeagleApi.BG_READ_USB_TRUNCATION_MODE) != 0)
                Console.Write("TRUNCATION_MODE; ");
        }
        else {
            // USB 3 status codes
            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_LINK) != 0) {
                Console.Write("LINK; ");
                if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SLC_CRC_1) != 0)
                    Console.Write("BAD_SLC_CRC_1; ");
                if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SLC_CRC_2) != 0)
                    Console.Write("BAD_SLC_CRC_2; ");
            }

            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_DP) != 0) {
                Console.Write("DATA; ");
                if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SDP_CRC) != 0)
                    Console.Write("BAD_SDP_CRC; ");
                if ((status & BeagleApi.BG_READ_USB_EDB_FRAMING) != 0)
                    Console.Write("SDP_EDB_FRAME; ");
            }

            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_HDR) != 0) {
                Console.Write("HDR; ");
                if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SHP_CRC_16) != 0)
                    Console.Write("BAD_SHP_CRC_16; ");
                if ((status & BeagleApi.BG_READ_USB_ERR_BAD_SHP_CRC_5) != 0)
                    Console.Write("BAD_SHP_CRC_5; ");
            }

            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_TSEQ) != 0)
                Console.Write("TSEQ; ");
            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_TS1) != 0)
                Console.Write("TS1; ");
            if ((status & BeagleApi.BG_READ_USB_PKT_TYPE_TS2) != 0)
                Console.Write("TS2; ");

            if ((status & BeagleApi.BG_READ_USB_ERR_UNK_END_OF_FRAME) != 0)
                Console.Write("BAD_UNK_EOF; ");
            if ((status & BeagleApi.BG_READ_USB_ERR_DATA_LEN_INVALID) != 0)
                Console.Write("BAD_DATA_LEN; ");
            if ((status & BeagleApi.BG_READ_USB_ERR_BAD_TS) != 0)
                Console.Write("BAD_TS; ");
            if ((status & BeagleApi.BG_READ_USB_ERR_FRAMING) != 0)
                Console.Write("FRAME_ERROR; ");
        }
    }

    static void printStatus (BeagleUsb5000Source source, uint status) {
        printGeneralStatus(status);
        printUsbStatus(source, status);
    }

    static void printUsb2Events (uint events) {
        // USB 2 event codes
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

        if ((events & BeagleApi.BG_EVENT_USB_DIGITAL_INPUT) != 0)
            Console.Write("INPUT_TRIGGER {0:x}; ",
                          events & BeagleApi.BG_EVENT_USB_DIGITAL_INPUT_MASK);

        if ((events & BeagleApi.BG_EVENT_USB_CHIRP_J) != 0)
            Console.Write("CHIRP_J; ");

        if ((events & BeagleApi.BG_EVENT_USB_CHIRP_K) != 0)
            Console.Write("CHIRP_K; ");

        if ((events & BeagleApi.BG_EVENT_USB_KEEP_ALIVE) != 0)
            Console.Write("KEEP_ALIVE; ");

        if ((events & BeagleApi.BG_EVENT_USB_SUSPEND) != 0)
            Console.Write("SUSPEND; ");

        if ((events & BeagleApi.BG_EVENT_USB_RESUME) != 0)
            Console.Write("RESUME; ");

        if ((events & BeagleApi.BG_EVENT_USB_LOW_SPEED) != 0)
            Console.Write("LOW_SPEED; ");

        if ((events & BeagleApi.BG_EVENT_USB_FULL_SPEED) != 0)
            Console.Write("FULL_SPEED; ");

        if ((events & BeagleApi.BG_EVENT_USB_HIGH_SPEED) != 0)
            Console.Write("HIGH_SPEED; ");

        if ((events & BeagleApi.BG_EVENT_USB_SPEED_UNKNOWN) != 0)
            Console.Write("UNKNOWN_SPEED; ");

        if ((events & BeagleApi.BG_EVENT_USB_LOW_OVER_FULL_SPEED) != 0)
            Console.Write("LOW_OVER_FULL_SPEED; ");
    }

    static void printEvents (BeagleUsb5000Source source, uint events) {
        // Print USB 2 events
        if (source == BeagleUsb5000Source.BG_USB5000_SOURCE_USB2) {
            printUsb2Events(events);
            return;
        }

        // Print USB 3 and Asynch events
        if ((events & BeagleApi.BG_EVENT_USB_LTSSM) != 0) {
            uint evt_idx = events & BeagleApi.BG_EVENT_USB_LTSSM_MASK;
            if (evt_idx < LTSSM_TABLE.Length) {
                Console.Write("LTSSM Transition: {0:s}; ",
                              LTSSM_TABLE[evt_idx]);
            }
            else
                Console.Write("Unknown LTSSM Transition: {0:d}; ", evt_idx);
        }

        if ((events & BeagleApi.BG_EVENT_USB_COMPLEX_TRIGGER) != 0) {
            uint state = events & BeagleApi.BG_EVENT_USB_TRIGGER_STATE_MASK;
            state    >>= BeagleApi.BG_EVENT_USB_TRIGGER_STATE_SHIFT;

            Console.Write("{0:s} trigger from state: {1:d}; ",
                          (events & BeagleApi.BG_EVENT_USB_TRIGGER_TIMER) != 0 ?
                          "Timer" : "Complex",
                          state);
        }

        if ((events & BeagleApi.BG_EVENT_USB_VBUS_PRESENT) != 0)
            Console.Write("VBUS Present; ");

        if ((events & BeagleApi.BG_EVENT_USB_VBUS_ABSENT) != 0)
            Console.Write("VBUS Absent; ");

        if ((events & BeagleApi.BG_EVENT_USB_SCRAMBLING_ENABLED) != 0)
            Console.Write("Scrambling On; ");

        if ((events & BeagleApi.BG_EVENT_USB_SCRAMBLING_DISABLED) != 0)
            Console.Write("Scrambling Off; ");

        if ((events & BeagleApi.BG_EVENT_USB_POLARITY_NORMAL) != 0)
            Console.Write("Polarity Normal; ");

        if ((events & BeagleApi.BG_EVENT_USB_POLARITY_REVERSED) != 0)
            Console.Write("Polarity Reversed; ");

        if ((events & BeagleApi.BG_EVENT_USB_PHY_ERROR) != 0)
            Console.Write("PHY Error; ");

        if ((events & BeagleApi.BG_EVENT_USB_HOST_DISCONNECT) != 0)
            Console.Write("SS Host Discon; ");

        if ((events & BeagleApi.BG_EVENT_USB_HOST_CONNECT) != 0)
            Console.Write("SS Host Conn; ");

        if ((events & BeagleApi.BG_EVENT_USB_TARGET_DISCONNECT) != 0)
            Console.Write("SS Trgt Discon; ");

        if ((events & BeagleApi.BG_EVENT_USB_TARGET_CONNECT) != 0)
            Console.Write("SS Trgt Conn; ");

        if ((events & BeagleApi.BG_EVENT_USB_LFPS) != 0)
            Console.Write("LFPS; ");

        if ((events & BeagleApi.BG_EVENT_USB_TRIGGER) != 0)
            Console.Write("Trigger; ");

        if ((events & BeagleApi.BG_EVENT_USB_EXT_TRIG_ASSERTED) != 0)
            Console.Write("Ext In Asserted; ");

        if ((events & BeagleApi.BG_EVENT_USB_EXT_TRIG_DEASSERTED) != 0)
            Console.Write("Ext In Deasserted; ");
    }

    // Renders USB3 packet data for printing
    static String usbPrintUsb3DataPacket (byte[] packet,
                                          byte[] k_packet_data,
                                          int    length)
    {
        String packetstring = "";

        if (length == 0) {
            packetstring = null;
            return packetstring;
        }

        int n = 0;
        for (n = 0; n < length; ++n) {
            int k_bit = (k_packet_data[n/8] >> (n % 8)) & 0x01;
            packetstring += String.Format("{0:x}{1,1:x2} ", k_bit, packet[n]);
        }
        return packetstring;
    }

    // Renders USB2 packet data for printing
    static String usbPrintUsb2DataPacket (byte[] packet,
                                          int    length)
    {
        String packetstring = "";
        byte pid;

        if (length == 0) {
            packetstring = null;
            return packetstring;
        }

        // Get the packet identifier
        pid = packet[0];

        // Print the packet identifier
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
    static void printPacket (BeagleUsb5000Source source,
                             byte[]     packet,
                             byte[]     k_packet_data,
                             int        length)
    {
        if (source == BeagleUsb5000Source.BG_USB5000_SOURCE_USB2)
            Console.Write("{0:s}", usbPrintUsb2DataPacket(packet, length));
        else {
            Console.Write("{0:s}", usbPrintUsb3DataPacket(packet,
                                                          k_packet_data,
                                                          length));
        }
        Console.Out.Flush();
    }

    static void usbDump (int numPackets, byte capMask)
    {
        // Setup variables
        byte[] packet      = new byte[1036];
        byte[] packetKBits = new byte[130];

        int packetnum = 0;

        BeagleUsb5000CaptureStatus captureStatus =
            BeagleUsb5000CaptureStatus.BG_USB5000_CAPTURE_STATUS_INACTIVE;
        uint pretrigAmt   = 0;
        uint pretrigTotal = 0;
        uint capAmt       = 0;
        uint capTotal     = 0;
        int  ret          = 0;

        #if STATS_MODE
            // Statistic mode variables
            ulong dispTimeSop     = 0;
            ulong sstxByteCount   = 0;
            ulong ssrxByteCount   = 0;
            ulong sstxPacketCount = 0;
            ulong ssrxPacketCount = 0;
            ulong usb2ByteCount   = 0;
            ulong usb2PacketCount = 0;
        #endif

        // Configure Beagle 480 for realtime capture
        if (BeagleApi.bg_usb5000_configure(
                beagle, capMask,
                BeagleUsb5000TriggerMode.BG_USB5000_TRIGGER_MODE_IMMEDIATE) !=
            (int)BeagleStatus.BG_OK)
        {
            Console.Write(
                "error: could not configure Beagle 5000 with desired mode\n");
            Environment.Exit(1);
        }

        // Start the capture
        if (BeagleApi.bg_enable(beagle, BeagleProtocol.BG_PROTOCOL_USB) !=
            (int)BeagleStatus.BG_OK) {
            Console.Write("error: could not enable USB capture; exiting...\n");
            Environment.Exit(1);
        }

        // Wait for the analyzer to trigger for up to 2 seconds...
        if ((capMask & BeagleApi.BG_USB5000_CAPTURE_USB2) != 0) {
            ret = BeagleApi.bg_usb5000_usb2_capture_status(
                beagle, 2000, ref captureStatus,
                ref pretrigAmt, ref pretrigTotal,
                ref capAmt,     ref capTotal);
        }
        else {
            ret = BeagleApi.bg_usb5000_usb3_capture_status(
                beagle, 2000, ref captureStatus,
                ref pretrigAmt, ref pretrigTotal,
                ref capAmt,     ref capTotal);
        }

        if (ret != (int)BeagleStatus.BG_OK) {
            Console.Write(
                "error: could not query capture status; exiting...\n");
            Environment.Exit(1);
        }

        if (captureStatus <= BeagleUsb5000CaptureStatus.
            BG_USB5000_CAPTURE_STATUS_PRE_TRIGGER)
        {
            Console.Write("did not trigger.\n");
            Environment.Exit(1);
        }

        // Output the header...
        #if STATS_MODE
            Console.Write(
                "   SSTX PACKETS ( MB/s )    SSRX PACKETS ( MB/s )    USB2 PACKETS ( MB/s )\n");
        #else
            Console.Write(
                "index,time(ns),source,event,status,data0 ... dataN(*)\n");
        #endif
        Console.Out.Flush();

        // ...then start decoding packets
        while (packetnum < numPackets || (numPackets == 0)) {
            uint                status         = 0;
            uint                events         = 0;
            ulong               timeSop        = 0;
            ulong               timeDuration   = 0;
            uint                timeDataOffset = 0;
            BeagleUsb5000Source source =
                BeagleUsb5000Source.BG_USB5000_SOURCE_ASYNC;

            int length = BeagleApi.bg_usb5000_read(
                beagle,
                ref status, ref events, ref timeSop, ref timeDuration,
                ref timeDataOffset, ref source,
                1036, packet, 130, packetKBits);

            // Make sure capture is triggered.
            if (length == (int)BeagleStatus.BG_CAPTURE_NOT_TRIGGERED)
                continue;

            // Check for invalid packet or Beagle error
            if (length < 0) {
                Console.Write("error={0:d}\n", length);
                break;
            }

            // Exit if observed end of capture
            if (status == BeagleApi.BG_READ_USB_END_OF_CAPTURE) {
                Console.Write("\n");
                Console.Write("End of capture\n");
                break;
            }

            #if STATS_MODE
                // Count the number of packets and bytes
                if (length > 0) {
                    switch (source) {
                      case BeagleUsb5000Source.BG_USB5000_SOURCE_USB2:
                        usb2PacketCount++;
                        usb2ByteCount += (ulong)length;
                        break;

                      case BeagleUsb5000Source.BG_USB5000_SOURCE_TX:
                        sstxPacketCount++;
                        sstxByteCount += (ulong)length;
                        break;

                      case BeagleUsb5000Source.BG_USB5000_SOURCE_RX:
                        ssrxPacketCount++;
                        ssrxByteCount += (ulong)length;
                        break;

                      default:
                        break;
                    }
                }

                // Periodically print out the stats
                if ((timeSop - dispTimeSop) > DISPLAY_TIME_TICKS) {
                    double timeS = (double) timestampToNS(timeSop - dispTimeSop,
                                                 samplerateKHz) / 1E9;
                    double sstxMBps =
                        ((double) sstxByteCount) / (1024*1024L) / timeS;
                    double ssrxMBps =
                        ((double) ssrxByteCount) / (1024*1024L) / timeS;
                    double usb2MBps =
                        ((double) usb2ByteCount) / (1024*1024L) / timeS;

                    Console.Write("\r{0,15:d} ({1,6:##0.00})" +
                                  " {2,15:d} ({3,6:##0.00})"  +
                                  " {4,15:d} ({5,6:##0.00})",
                                  sstxPacketCount, sstxMBps,
                                  ssrxPacketCount, ssrxMBps,
                                  usb2PacketCount, usb2MBps);

                    sstxByteCount = 0;
                    ssrxByteCount = 0;
                    usb2ByteCount = 0;
                    dispTimeSop = timeSop;
                }
            #else
                // Grab the next packet on a timeout.
                if (length == 0 &&
                    status == BeagleApi.BG_READ_TIMEOUT &&
                    events == 0)
                {
                    continue;
                }

                // Print the packet details
                Console.Write("{0},", packetnum);
                Console.Write("{0},", timestampToNS(timeSop, samplerateKHz));
                printSource(source);
                Console.Write(",");
                printEvents(source, events);
                Console.Write(",");
                printStatus(source, status);
                Console.Write(",");
                printPacket(source, packet, packetKBits, length);
                Console.Write("\n");
            #endif

            packetnum++;
        }

        // Stop the capture
        BeagleApi.bg_disable(beagle);
    }


    /*=====================================================================
    | USAGE INFORMATION
     ====================================================================*/
    static void printUsage ()
    {
        Console.Write(
"Usage: capture_usb5000 source num_events\n" +
"Example utility for capturing USB data from a Beagle 5000 protocol analyzer.\n"
+
"\n" +
"  The parameter source determines which USB source to capture on.\n" +
"  The source can be set to either: both, usb2, or usb3.\n" +
"  Note that only analyzers licensed for the simultaneous feature will\n" +
"  be able to capture both sources at the same time.\n" +
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
       int  port     = 0;      // open port 0 by default
       uint timeout  = 100;    // in milliseconds
       uint latency  = 200;    // in milliseconds
       int  num      = 0;
       byte capMask = 0;

       if (args.Length < 2) {
           printUsage();
           Environment.Exit(1);
       }

       if (args[0] == "usb2")
           capMask = BeagleApi.BG_USB5000_CAPTURE_USB2;
       else if (args[0] == "usb3")
           capMask = BeagleApi.BG_USB5000_CAPTURE_USB3;
       else if (args[0] == "both")
           capMask = BeagleApi.BG_USB5000_CAPTURE_USB3 |
               BeagleApi.BG_USB5000_CAPTURE_USB2;
       else {
           printUsage();
           Environment.Exit(1);
       }

       num = Convert.ToInt32(args[1]);

       // Open the device
       beagle = BeagleApi.bg_open(port);
       if (beagle <= 0) {
           Console.Write("Unable to open Beagle device on port {0:d}\n", port);
           Console.Write("Error code = {0:d}\n", beagle);
           Environment.Exit(1);
       }
       Console.Write("Opened Beagle device on port {0:d}\n", port);

       // Query the samplerate since Beagle USB has a fixed sampling rate
       samplerateKHz= BeagleApi.bg_samplerate(beagle, samplerateKHz);
       if (samplerateKHz < 0) {
           Console.Write("error: {0:s}\n",
                BeagleApi.bg_status_string(samplerateKHz));
           Environment.Exit(1);
       }
       Console.Write("Sampling rate set to {0:d} KHz.\n", samplerateKHz);

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

       Console.Write("\n");
       Console.Out.Flush();

       usbDump(num, capMask);

       // Close the device
       BeagleApi.bg_close(beagle);

       return;
   }
}
