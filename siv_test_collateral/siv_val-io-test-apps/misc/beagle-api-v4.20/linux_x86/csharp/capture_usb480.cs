/*=========================================================================
| (C) 2007  Total Phase, Inc.
|--------------------------------------------------------------------------
| Project : Beagle Sample Code
| File    : capture_usb480.cs
|--------------------------------------------------------------------------
| Simple Capture Example for Beable USB 480
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
// Disable COMBINE_SPLITS by commenting the line below.  Disabling
// will show individual split counts for each group (such as
// SPLIT/IN/ACK, SPLIT/IN/NYET, ...).  Enabling will show all the
// collapsed split counts combined.
#define COMBINE_SPLITS


/*=========================================================================
| USING
 ========================================================================*/
using System;
using System.IO;
using TotalPhase;


/*=========================================================================
| CLASS
 ========================================================================*/
public class Capture_usb480 {


    /*=====================================================================
    | CONSTANTS
     ====================================================================*/
    private const int IDLE_THRESHOLD = 2000;
    private enum PacketGroup : byte {
        SOF              = 0,
        IN_ACK           = 1,
        IN_NAK           = 2,
        PING_NAK         = 3,
        SPLIT_IN_ACK     = 4,
        SPLIT_IN_NYET    = 5,
        SPLIT_IN_NAK     = 6,
        SPLIT_OUT_NYET   = 7,
        SPLIT_SETUP_NYET = 8,
        KEEP_ALIVE       = 9
    }
    private const int NUM_COLLAPSE = 10;

    private enum CollapseState : int {
        IDLE        = 0,
        IN          = 1,
        PING        = 3,
        SPLIT       = 4,
        SPLIT_IN    = 5,
        SPLIT_OUT   = 7,
        SPLIT_SETUP = 8
    }

    private const int QUEUE_SIZE = 3;


    /*=====================================================================
    | CLASSES
     ====================================================================*/
    public class PacketInfo {
        public byte[] data;
        public ulong timeSop;
        public ulong timeSopNS;
        public ulong timeDuration;
        public uint  timeDataOffset;
        public uint  status;
        public uint  events;
        public int   length;

        public PacketInfo () {
            data           = new byte[1024];
            timeSop        = 0;
            timeSopNS      = 0;
            timeDuration   = 0;
            timeDataOffset = 0;
            status         = 0;
            events         = 0;
            length         = 0;
        }
    }

    // Used to store the packets that are saved during the collapsing
    // process.  The tail of the queue is always used to store
    // the current packet.
    public class PacketQueue {
        private int tail;
        private int head;
        private PacketInfo[] pkt;

        public PacketQueue () {
            tail  = 0;
            head = 0;

            pkt = new PacketInfo[QUEUE_SIZE];
            for (int i = 0; i < QUEUE_SIZE; i++)
                pkt[i] = new PacketInfo();
        }

        public PacketInfo dequeue () {
            if (head == tail) return null;
            int h = head;
            head = (head + 1) % QUEUE_SIZE;
            return pkt[h];
        }

        public bool isEmpty()        { return head == tail; }
        public PacketInfo getTail () { return pkt[tail]; }
        public void savePacket ()    { tail = (tail + 1) % QUEUE_SIZE; }
        public void clear ()         { head = tail; }
        public ulong headSop ()      { return pkt[head].timeSop; }
        public ulong tailSop ()      { return pkt[tail].timeSop; }
    }

    public class CollapseInfo {
        // Timestamp when collapsing begins
        public ulong  timeSop;
        // The number of packets collapsed for each packet group
        public int[] count;

        public CollapseInfo() {
            count = new int[NUM_COLLAPSE];
            clear();
        }

        public void clear () {
            timeSop = 0;
            for (int i = 0; i < NUM_COLLAPSE; i++)
                count[i] = 0;
        }
    }


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
    }

    static void printUsbStatus (uint status) {
        // USB status codes
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

    static void usbPrintSummary (int    i,
                                 ulong  countSop,
                                 String summary)
    {
        Console.Write("{0:d},{1:d},USB,( ),{2:s}\n",
                i, timestampToNS(countSop, samplerateKHz), summary);
    }

    // Renders packet data for printing
    static String usbPrintDataPacket (byte[] packet,
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
    static void usbPrintPacket (int        packetNumber,
                                PacketInfo packet,
                                String     errorStatus)
    {
        String packetData;

        if (errorStatus == null) {
            errorStatus = "";
            packetData = usbPrintDataPacket(packet.data, packet.length);
        } else {
            packetData = "";
        }
        Console.Write("{0:d},{1:d},USB,({2:s}",
                      packetNumber, packet.timeSop, errorStatus);
        printGeneralStatus(packet.status);
        printUsbStatus(packet.status);
        printUsbEvents(packet.events);

        Console.Write("){0:s}\n",packetData);
        Console.Out.Flush();
    }

    // Dump saved summary information
    static int usbPrintSummaryPacket (ref int      packetNumber,
                                      CollapseInfo collapseInfo,
                                      ref int      signalErrors)
    {
        int offset = 0;

        String summary = "";
        if (collapseInfo.count[(byte)PacketGroup.KEEP_ALIVE]       > 0 ||
            collapseInfo.count[(byte)PacketGroup.SOF]              > 0 ||
            collapseInfo.count[(byte)PacketGroup.PING_NAK]         > 0 ||
            collapseInfo.count[(byte)PacketGroup.SPLIT_IN_ACK]     > 0 ||
            collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NYET]    > 0 ||
            collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NAK]     > 0 ||
            collapseInfo.count[(byte)PacketGroup.SPLIT_OUT_NYET]   > 0 ||
            collapseInfo.count[(byte)PacketGroup.SPLIT_SETUP_NYET] > 0) {

            summary +=  "COLLAPSED ";

            if (collapseInfo.count[(byte)PacketGroup.KEEP_ALIVE] > 0)
                summary +=
                    String.Format("[{0:d} KEEP-ALIVE] ",
                      collapseInfo.count[(byte)PacketGroup.KEEP_ALIVE]);

            if (collapseInfo.count[(byte)PacketGroup.SOF] > 0)
                summary +=
                    String.Format("[{0:d} SOF] ",
                      collapseInfo.count[(byte)PacketGroup.SOF]);

            if (collapseInfo.count[(byte)PacketGroup.IN_ACK] > 0)
                summary +=
                    String.Format("[{0:d} IN/ACK] ",
                      collapseInfo.count[(byte)PacketGroup.IN_ACK]);

            if (collapseInfo.count[(byte)PacketGroup.IN_NAK] > 0)
                summary +=
                    String.Format("[{0:d} IN/NAK] ",
                      collapseInfo.count[(byte)PacketGroup.IN_NAK]);

            if (collapseInfo.count[(byte)PacketGroup.PING_NAK] > 0)
                summary +=
                    String.Format("[{0:d} PING/NAK] ",
                      collapseInfo.count[(byte)PacketGroup.PING_NAK]);

            #if COMBINE_SPLITS
                int split_count =
                    collapseInfo.count[(byte)PacketGroup.SPLIT_IN_ACK] +
                    collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NYET] +
                    collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NAK] +
                    collapseInfo.count[(byte)PacketGroup.SPLIT_OUT_NYET] +
                    collapseInfo.count[(byte)PacketGroup.SPLIT_SETUP_NYET];

                if (split_count > 0)
                    summary += String.Format("[{0:d} SPLITS] ", split_count);
            #else
                if (collapseInfo.count[(byte)PacketGroup.SPLIT_IN_ACK] > 0)
                    summary +=
                      String.Format("[{0:d} SPLIT/IN/ACK] ",
                        collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NAK]);

                if (collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NYET] > 0)
                    summary +=
                      String.Format("[{0:d} SPLIT/IN/NYET] ",
                         collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NYET]);

                if (collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NAK] > 0)
                    summary +=
                      String.Format("[{0:d} SPLIT/IN/NAK] ",
                         collapseInfo.count[(byte)PacketGroup.SPLIT_IN_NAK]);

                if (collapseInfo.count[(byte)PacketGroup.SPLIT_OUT_NYET] > 0)
                    summary +=
                      String.Format("[{0:d} SPLIT/OUT/NYET] ",
                        collapseInfo.count[(byte)PacketGroup.SPLIT_OUT_NYET]);

                if (collapseInfo.count[(byte)PacketGroup.SPLIT_SETUP_NYET] > 0)
                    summary +=
                      String.Format("[{0:d} SPLIT/SETUP/NYET] ",
                      collapseInfo.count[(byte)PacketGroup.SPLIT_SETUP_NYET]);
            #endif

            usbPrintSummary(packetNumber+offset, collapseInfo.timeSop,
                            summary);
            offset++;
        }

        // Output any signal errors
        if (signalErrors > 0) {
            summary += String.Format("<{0:d} SIGNAL ERRORS>", signalErrors);

            usbPrintSummary(packetNumber+offset, collapseInfo.timeSop,
                            summary);
            ++offset;
        }

        collapseInfo.clear();
        packetNumber += offset;
        return offset;
    }

    // Outputs any packets saved during the collapsing process
    static void outputSaved (ref int      packetnum,
                             ref int      signalErrors,
                             CollapseInfo collapseInfo,
                             PacketQueue  pktQ)
    {
        usbPrintSummaryPacket(ref packetnum, collapseInfo,
                              ref signalErrors);

        PacketInfo pkt = pktQ.dequeue();
        while (pkt != null) {
            usbPrintPacket(packetnum, pkt,  null);
            packetnum += 1;

            // Get the next packet or null if empty
            pkt = pktQ.dequeue();
        }
    }

    // Collapses a group of packets.  This involves incrementing the group
    // counter and clearing the savedPackets stack by moving top back to 0.
    // If this is the first group to be collapsed, the collapse time needs
    // to be set, which marks when this collapsing began.
    static void collapse (PacketGroup  group,
                          CollapseInfo collapseInfo,
                          PacketQueue  pktQ)
    {
        collapseInfo.count[(byte)group]++;
        if (collapseInfo.timeSop == 0) {
            if (!pktQ.isEmpty())
                collapseInfo.timeSop = pktQ.headSop();
            else
                collapseInfo.timeSop = pktQ.tailSop();
        }
        pktQ.clear();
    }

    static void usbDump (int numPackets)
    {
        // Packets are saved during the collapsing process
        PacketQueue pktQ = new PacketQueue();

        // Info for the packet that was just read
        PacketInfo curPacket;

        // Collapsing counts and time collapsing started
        CollapseInfo collapseInfo = new CollapseInfo();

        CollapseState state = CollapseState.IDLE;
        bool reRun = false;

        byte pid          = 0;
        int  signalErrors = 0;
        int  packetnum    = 0;

        samplerateKHz = BeagleApi.bg_samplerate(beagle, 0);

        int idle_samples   = IDLE_THRESHOLD * samplerateKHz;

        // Configure Beagle 480 for realtime capture
        BeagleApi.bg_usb480_capture_configure(beagle,
                BeagleUsb480CaptureMode.BG_USB480_CAPTURE_REALTIME,
                BeagleUsb2TargetSpeed.BG_USB2_AUTO_SPEED_DETECT);

        // Filter packets intended for the Beagle analyzer. This is only
        // relevant when one host controller is being used.
        BeagleApi.bg_usb480_hw_filter_config(beagle,
                BeagleApi.BG_USB2_HW_FILTER_SELF);

        // Start the capture
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
            curPacket = pktQ.getTail();

            curPacket.length = BeagleApi.bg_usb480_read(
                                               beagle,
                                               ref curPacket.status,
                                               ref curPacket.events,
                                               ref curPacket.timeSop,
                                               ref curPacket.timeDuration,
                                               ref curPacket.timeDataOffset,
                                               1024,
                                               curPacket.data);

            curPacket.timeSopNS =
                timestampToNS(curPacket.timeSop, samplerateKHz);

            // Exit if observed end of capture
            if ((curPacket.status &
                 BeagleApi.BG_READ_USB_END_OF_CAPTURE) != 0)
            {
                usbPrintSummaryPacket(ref packetnum, collapseInfo,
                                      ref signalErrors);
                break;
            }

            // Check for invalid packet or Beagle error
            if (curPacket.length < 0) {
                String errorStatus = "";
                errorStatus += String.Format("error={0:d}", curPacket.length);
                usbPrintPacket(packetnum, curPacket, errorStatus);
                break;
            }

            // Check for USB error
            if (curPacket.status == BeagleApi.BG_READ_USB_ERR_BAD_SIGNALS)
                ++signalErrors;

            // Set the PID for collapsing state machine below.  Treat
            // KEEP_ALIVEs as packets.
            if (curPacket.length > 0)
                pid = curPacket.data[0];
            else if ((curPacket.events &
                      BeagleApi.BG_EVENT_USB_KEEP_ALIVE) != 0 &&
                     (curPacket.status &
                      BeagleApi.BG_READ_USB_ERR_BAD_PID) == 0)
            {
                    pid = (byte)PacketGroup.KEEP_ALIVE;
            }
            else
                pid = 0;

            // Collapse these packets approprietly:
            // KEEP_ALIVE* SOF* (IN (ACK|NAK))* (PING NAK)*
            // (SPLIT (OUT|SETUP) NYET)* (SPLIT IN (ACK|NYET|NACK))*

            // If the time elapsed since collapsing began is greater than
            // the threshold, output the counts and zero out the counters.
            if (curPacket.timeSop - collapseInfo.timeSop >=
                (ulong)idle_samples)
                {
                    usbPrintSummaryPacket(ref packetnum, collapseInfo,
                                          ref signalErrors);
                }

            while(true) {
                reRun = false;
                switch (state) {
                    // The initial state of the state machine.  Collapse SOFs
                    // and KEEP_ALIVEs.  Save IN, PING, or SPLIT packets and
                    // move to the next state for the next packet.  Otherwise,
                    // print the collapsed packet counts and the current
                    // packet.
                  case CollapseState.IDLE:
                    switch (pid) {
                      case (byte)PacketGroup.KEEP_ALIVE:
                        collapse(PacketGroup.KEEP_ALIVE, collapseInfo, pktQ);
                        break;
                      case BeagleApi.BG_USB_PID_SOF:
                        collapse(PacketGroup.SOF, collapseInfo, pktQ);
                        break;
                      case BeagleApi.BG_USB_PID_IN:
                        pktQ.savePacket();
                        state = CollapseState.IN;
                        break;
                      case BeagleApi.BG_USB_PID_PING:
                        pktQ.savePacket();
                        state = CollapseState.PING;
                        break;
                      case BeagleApi.BG_USB_PID_SPLIT:
                        pktQ.savePacket();
                        state = CollapseState.SPLIT;
                        break;
                      default:
                        usbPrintSummaryPacket(ref packetnum, collapseInfo,
                                              ref signalErrors);

                        if (curPacket.length > 0 || curPacket.events != 0 ||
                            (curPacket.status != 0 &&
                             curPacket.status != BeagleApi.BG_READ_TIMEOUT)) {

                            usbPrintPacket(packetnum, curPacket, null);
                            packetnum++;
                        }
                        break;
                    }
                    break;

                    // Collapsing IN+ACK or IN+NAK.  Otherwise, output any
                    // saved packets and rerun the collapsing state machine
                    // on the current packet.
                  case CollapseState.IN:
                    state = CollapseState.IDLE;
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_ACK:
                        collapse(PacketGroup.IN_ACK, collapseInfo, pktQ);
                        break;
                      case BeagleApi.BG_USB_PID_NAK:
                        collapse(PacketGroup.IN_NAK, collapseInfo, pktQ);
                        break;
                      default:
                        reRun = true;
                        break;
                    }
                    break;

                    // Collapsing PING+NAK
                  case CollapseState.PING:
                    state = CollapseState.IDLE;
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_NAK:
                        collapse(PacketGroup.PING_NAK, collapseInfo, pktQ);
                        break;
                      default:
                        reRun = true;
                        break;
                    }
                    break;

                    // Expecting an IN, OUT, or SETUP
                  case CollapseState.SPLIT:
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_IN:
                        pktQ.savePacket();
                        state = CollapseState.SPLIT_IN;
                        break;
                      case BeagleApi.BG_USB_PID_OUT:
                        pktQ.savePacket();
                        state = CollapseState.SPLIT_OUT;
                        break;
                      case BeagleApi.BG_USB_PID_SETUP:
                        pktQ.savePacket();
                        state = CollapseState.SPLIT_SETUP;
                        break;
                      default:
                        state = CollapseState.IDLE;
                        reRun = true;
                        break;
                    }
                    break;

                    // Collapsing SPLIT+IN+NYET, SPLIT+IN+NAK, SPLIT+IN+ACK
                  case CollapseState.SPLIT_IN:
                    state = CollapseState.IDLE;
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_NYET:
                        collapse(PacketGroup.SPLIT_IN_NYET, collapseInfo,
                                 pktQ);
                        break;
                      case BeagleApi.BG_USB_PID_NAK:
                        collapse(PacketGroup.SPLIT_IN_NAK, collapseInfo,
                                 pktQ);
                        break;
                      case BeagleApi.BG_USB_PID_ACK:
                        collapse(PacketGroup.SPLIT_IN_ACK, collapseInfo,
                                 pktQ);
                        break;
                      default:
                        reRun = true;
                        break;
                    }
                    break;

                    // Collapsing SPLIT+OUT+NYET
                  case CollapseState.SPLIT_OUT:
                    state = CollapseState.IDLE;
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_NYET:
                        collapse(PacketGroup.SPLIT_OUT_NYET, collapseInfo,
                                 pktQ);
                        break;
                      default:
                        reRun = true;
                        break;
                    }
                    break;

                    // Collapsing SPLIT+SETUP+NYET
                  case CollapseState.SPLIT_SETUP:
                    state = CollapseState.IDLE;
                    switch (pid) {
                      case BeagleApi.BG_USB_PID_NYET:
                        collapse(PacketGroup.SPLIT_SETUP_NYET, collapseInfo,
                                 pktQ);
                        break;
                      default:
                        reRun = true;
                        break;
                    }
                    break;
                }

                if (reRun == false)
                    break;

                // The state machine is about to be re-run.  This
                // means that a complete packet sequence wasn't collapsed
                // and there are packets in the queue that need to be
                // output before we can process the current packet.
                outputSaved(ref packetnum, ref signalErrors,
                            collapseInfo, pktQ);

            }
        }

        // Stop the capture
        BeagleApi.bg_disable(beagle);
    }


    /*=========================================================================
    | DIGITAL INPIT/OUTPUT CONFIG
     ========================================================================*/
    static void setupDigitalLines ()
    {
        // Digital input mask
        byte input_enable_mask =
            BeagleApi.BG_USB2_DIGITAL_IN_ENABLE_PIN1 |
            BeagleApi.BG_USB2_DIGITAL_IN_ENABLE_PIN2 |
            BeagleApi.BG_USB2_DIGITAL_IN_ENABLE_PIN3 |
            BeagleApi.BG_USB2_DIGITAL_IN_ENABLE_PIN4;

        // Define the packet and data match structures.  By using 'new'
        // to define these structures, their value type elements are
        // initialized to 0 and the reference type elements (including
        // the arrays) are set to null.
        BeagleApi.BeagleUsb2PacketMatch packet_match =
            new BeagleApi.BeagleUsb2PacketMatch();
        BeagleApi.BeagleUsb2DataMatch data_match =
            new BeagleApi.BeagleUsb2DataMatch();

        // Enable digital input pins
        BeagleApi.bg_usb480_digital_in_config(beagle, input_enable_mask);
        Console.Write("Configuring digital input with {0:x}\n",
                      input_enable_mask);

        // Configure digital out pins.  Only those fields that we want
        // enabled need to be set here since everything was initialized
        // above.
        packet_match.pid_match_type =
            BeagleUsb2MatchType.BG_USB2_MATCH_TYPE_EQUAL;
        packet_match.pid_match_val  = BeagleApi.BG_USB_PID_PING;

        // Enable digital output pin 4
        BeagleApi.bg_usb480_digital_out_config(beagle,
                           BeagleApi.BG_USB2_DIGITAL_OUT_ENABLE_PIN4,
                           BeagleApi.BG_USB2_DIGITAL_OUT_PIN4_ACTIVE_HIGH);

        // Configure digital output pin 4 match pattern
        BeagleApi.bg_usb480_digital_out_match(beagle,
           BeagleUsb2DigitalOutMatchPins.BG_USB2_DIGITAL_OUT_MATCH_PIN4,
           packet_match, data_match);

        Console.Write("Configuring digital output pin 4.\n");
    }


    /*=====================================================================
    | USAGE INFORMATION
     ====================================================================*/
    static void printUsage ()
    {
        Console.Write("Usage: capture_usb480 num_events\n" +
"Example utility for capturing USB data from a Beagle 480 protocol analyzer.\n" +
"Certain packet groups (such as IN/NAK, SPLIT/IN/ACK, etc.) are collapsed\n" +
"in software.  See the source code for more details about packet collapsing.\n"+
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

       Console.Write("\n");
       Console.Out.Flush();

       // Setup the digital I/O lines
       setupDigitalLines();

       usbDump(num);

       // Close the device
       BeagleApi.bg_close(beagle);

       return;
   }
}
