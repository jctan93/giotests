/*=========================================================================
| (C) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_usb480_extras.cs
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
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_usb480 {


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

    public static long timeMicroseconds () {
        DateTime CurrTime = DateTime.Now;
        return CurrTime.Ticks / 10;
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

        if ((status & BeagleApi.BG_READ_USB_TRUNCATION_MODE) != 0)
            Console.Write("TRUNCATION_MODE; ");

        if ((status & BeagleApi.BG_READ_USB_END_OF_CAPTURE) != 0)
            Console.Write("END_OF_CAPTURE; ");
    }

    static void printUsbEvents (uint events) {
        // USB event codes
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

    static String space (int num) {
        return new string(' ', num);
    }

    static void printProgress (uint   percent,
                               double elapsedTime,
                               uint   bufferUsed,
                               uint   bufferSize)
    {
        String progressbar = "";
        int tenths = (int)percent/5;
        progressbar += String.Format("[" + space(tenths) + '#' +
                                     space(20-tenths)+ ']');
        Console.Write("\r{0:s} {1,3:d}% {2,7:d} of {3,5:d} KB {4:f2} seconds",
                      progressbar, percent, bufferUsed / 1024,
                      bufferSize / 1024, elapsedTime);
        Console.Out.Flush();
    }

    static void usbDump (int numPackets, int timeoutMS) {
        long start, elapsedTime;

        // Set up variables
        byte[] packet      = new byte[1024];
        int    packetnum   = 0;

        samplerateKhz = BeagleApi.bg_samplerate(beagle, 0);

        // Configure Beagle 480 for delayed-download capture
        BeagleApi.bg_usb480_capture_configure(beagle,
                BeagleUsb480CaptureMode.BG_USB480_CAPTURE_DELAYED_DOWNLOAD,
                BeagleUsb2TargetSpeed.BG_USB2_AUTO_SPEED_DETECT);

        // Enable the hardware filtering.  This will filter out packets with
        // the same device address as the Beagle analyzer and also filter
        // the PID packet groups listed below.
        BeagleApi.bg_usb480_hw_filter_config(beagle,
                BeagleApi.BG_USB2_HW_FILTER_SELF     |
                BeagleApi.BG_USB2_HW_FILTER_PID_SOF  |
                BeagleApi.BG_USB2_HW_FILTER_PID_IN   |
                BeagleApi.BG_USB2_HW_FILTER_PID_PING |
                BeagleApi.BG_USB2_HW_FILTER_PID_PRE  |
                BeagleApi.BG_USB2_HW_FILTER_PID_SPLIT);

        // Start the capture portion of the delayed-download capture
        if (BeagleApi.bg_enable(beagle, BeagleProtocol.BG_PROTOCOL_USB) !=
            (int)BeagleStatus.BG_OK) {
            Console.Write("error: could not enable USB capture; exiting...\n");
            Environment.Exit(1);
        }

        // Wait until timeout period elapses or the hardware buffer on
        // the Beagle USB 480 fills
        Console.Write("Hardware buffer usage:\n");
        start = timeMicroseconds();

        while (true) {
            uint bufferSize  = 0;
            uint bufferUsage = 0;
            byte bufferFull  = 0;

            // Poll the hardware buffer status
            BeagleApi.bg_usb480_hw_buffer_stats(beagle, ref bufferSize,
                                                ref bufferUsage,
                                                ref bufferFull);

            // Print out the progress
            elapsedTime = (timeMicroseconds() - start) / 1000;

            printProgress(bufferUsage / (bufferSize / 100),
                          ((double)elapsedTime) / 1000,
                          bufferUsage, bufferSize);

            // If timed out or buffer is full, exit loop
            if (bufferFull != 0 ||
                (timeoutMS != 0 && elapsedTime > timeoutMS))
                break;

            // Sleep for 150 milliseconds
            BeagleApi.bg_sleep_ms(150);
        }

        // Start the download portion of the delayed-download capture
        //
        // Output the header...
        Console.Write("\nindex,time(ns),USB,status,pid,data0 ... dataN(*)\n");
        Console.Out.Flush();

        // ...then start decoding packets
        while (packetnum < numPackets || (numPackets == 0)) {
            uint   status         = 0;
            uint   events         = 0;
            ulong  timeSop        = 0;
            ulong  timeSopNS      = 0;
            ulong  timeDuration   = 0;
            uint   timeDataOffset = 0;

            // Calling bg_usb480_read will automatically stop the
            // capture portion of the delayed-download capture and
            // will begin downloading the capture results.
            int length = BeagleApi.bg_usb480_read(
                                beagle, ref status, ref events,
                                ref timeSop, ref timeDuration,
                                ref timeDataOffset, 1024, packet);

            timeSopNS = TIMESTAMP_TO_NS(timeSop, samplerateKhz);

            // Check for invalid packet or Beagle error
            if (length < 0) {
                String errorStatus = "";
                errorStatus += String.Format("error={0:d}", length);
                usbPrintPacket(packetnum, timeSopNS, status, events,
                               errorStatus, null);
                break;
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

            // Exit if observe end of capture
            if ((status & BeagleApi.BG_READ_USB_END_OF_CAPTURE) != 0) {
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
        Console.Write("Usage: capture_usb480_extras num_events timeout\n" +
"Example utility for executing a delayed-download capture of USB data from\n" +
"a Beagle 480 protocol analyzer with hardware filtering enabled." +
"\n\n" +
"In delayed-download capture, the captured data is stored in the Beagle USB\n" +
"480's hardware buffer while capture is in progress.  The capture data\n" +
"is downloaded from the hardware after the capture has been halted.\n" +
"\n" +
"  The parameter num_events is set to the number of events to process\n" +
"  before exiting.  If num_events is set to zero, the capture will continue\n" +
"  indefinitely.\n" +
"\n" +
"  The parameter timeout is is the number of seconds to run the capture\n" +
"  before downloading the results.  If timeout is set to zero, the capture\n" +
"  portion will run until the hardware buffer is full.\n" +
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

       if (args.Length < 2)
       {
           printUsage();
           Environment.Exit(1);
       }
       int num             = Convert.ToInt32(args[0]);
       int capture_timeout = Convert.ToInt32(args[1]);

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

       Console.Write("\n");
       Console.Out.Flush();

       usbDump(num, capture_timeout * 1000);

       // Close the device
       BeagleApi.bg_close(beagle);

       return;
   }
}
