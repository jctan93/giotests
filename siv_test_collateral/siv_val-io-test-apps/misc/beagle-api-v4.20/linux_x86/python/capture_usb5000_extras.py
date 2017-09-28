#!/bin/env python
#==========================================================================
# (c) 2011  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_usb5000_extras.py
#--------------------------------------------------------------------------
# Complex Match and Circular Buffer Example for Beagle USB 5000
#--------------------------------------------------------------------------
# Redistribution and use of this file in source and binary forms, with
# or without modification, are permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#==========================================================================

#==========================================================================
# IMPORTS
#==========================================================================
from beagle_py import *


#==========================================================================
# GLOBALS
#==========================================================================
beagle         = 0
samplerate_khz = 0

LTSSM_TABLE = [
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
]


#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def timestamp_to_ns (stamp, samplerate_khz):
    return int((stamp * 1000) / (samplerate_khz/1000))

def print_source (source):
    if   (source == BG_USB5000_SOURCE_ASYNC): print "ASYNC",
    elif (source == BG_USB5000_SOURCE_RX):    print "SSRX",
    elif (source == BG_USB5000_SOURCE_TX):    print "SSTX",
    elif (source == BG_USB5000_SOURCE_USB2):  print "USB2",

def print_general_status (status):
    """ General status codes """

    if (status == BG_READ_OK) :                  print "OK",
    if (status & BG_READ_TIMEOUT):               print "TIMEOUT",
    if (status & BG_READ_ERR_UNEXPECTED):        print "UNEXPECTED",
    if (status & BG_READ_ERR_MIDDLE_OF_PACKET):  print "MIDDLE",
    if (status & BG_READ_ERR_SHORT_BUFFER):      print "SHORT BUFFER",
    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE):
        print "PARTIAL_BYTE(bit %d)" % (status & 0xff),
    if (status & BG_READ_USB_END_OF_CAPTURE):    print "END_OF_CAPTURE",

def print_usb_status (source, status):
    if source == BG_USB5000_SOURCE_USB2:
        """USB 2 status codes"""
        if (status & BG_READ_USB_ERR_BAD_SIGNALS):   print "BAD_SIGNAL;",
        if (status & BG_READ_USB_ERR_BAD_SYNC):      print "BAD_SYNC;",
        if (status & BG_READ_USB_ERR_BIT_STUFF):     print "BAD_STUFF;",
        if (status & BG_READ_USB_ERR_FALSE_EOP):     print "BAD_EOP;",
        if (status & BG_READ_USB_ERR_LONG_EOP):      print "LONG_EOP;",
        if (status & BG_READ_USB_ERR_BAD_PID):       print "BAD_PID;",
        if (status & BG_READ_USB_ERR_BAD_CRC):       print "BAD_CRC;",
        if (status & BG_READ_USB_TRUNCATION_MODE):   print "TRUNCATION_MODE;",
    else:
        """USB 3 status codes"""
        if (status & BG_READ_USB_PKT_TYPE_LINK):
            print "LINK; ",
            if (status & BG_READ_USB_ERR_BAD_SLC_CRC_1):
                print "BAD_SLC_CRC_1; ",
            if (status & BG_READ_USB_ERR_BAD_SLC_CRC_2):
                print "BAD_SLC_CRC_2; ",

        if (status & BG_READ_USB_PKT_TYPE_DP):
            print "DATA; ",
            if (status & BG_READ_USB_ERR_BAD_SDP_CRC):
                print "BAD_SDP_CRC; ",
            if (status & BG_READ_USB_EDB_FRAMING):
                print "SDP_EDB_FRAME; ",

        if (status & BG_READ_USB_PKT_TYPE_HDR):
            print "HDR; ",
            if (status & BG_READ_USB_ERR_BAD_SHP_CRC_16):
                print "BAD_SHP_CRC_16; ",
            if (status & BG_READ_USB_ERR_BAD_SHP_CRC_5):
                print "BAD_SHP_CRC_5; ",

        if (status & BG_READ_USB_PKT_TYPE_TSEQ):      print "TSEQ; ",
        if (status & BG_READ_USB_PKT_TYPE_TS1):       print "TS1; ",
        if (status & BG_READ_USB_PKT_TYPE_TS2):       print "TS2; ",

        if (status & BG_READ_USB_ERR_BAD_TS):           print "BAD_TS; ",
        if (status & BG_READ_USB_ERR_UNK_END_OF_FRAME): print "BAD_UNK_EOF; ",
        if (status & BG_READ_USB_ERR_DATA_LEN_INVALID): print "BAD_DATA_LEN; ",
        if (status & BG_READ_USB_ERR_FRAMING):          print "FRAME_ERROR; ",

def print_status (source, status):
    print_general_status(status)
    print_usb_status(source, status)

def print_usb2_events (events):
    """USB 2 event codes"""
    if (events & BG_EVENT_USB_HOST_DISCONNECT):   print "HOST_DISCON;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT): print "TGT_DISCON;",
    if (events & BG_EVENT_USB_RESET):             print "RESET;",
    if (events & BG_EVENT_USB_HOST_CONNECT):      print "HOST_CONNECT;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):    print "TGT_CONNECT/UNRST;",
    if (events & BG_EVENT_USB_DIGITAL_INPUT):     print "INPUT_TRIGGER %X" % \
       (events & BG_EVENT_USB_DIGITAL_INPUT_MASK),
    if (events & BG_EVENT_USB_CHIRP_J):           print "CHIRP_J;",
    if (events & BG_EVENT_USB_CHIRP_K):           print "CHIRP_K;",
    if (events & BG_EVENT_USB_KEEP_ALIVE):        print "KEEP_ALIVE;",
    if (events & BG_EVENT_USB_SUSPEND):           print "SUSPEND;",
    if (events & BG_EVENT_USB_RESUME):            print "RESUME;",
    if (events & BG_EVENT_USB_LOW_SPEED):         print "LOW_SPEED;",
    if (events & BG_EVENT_USB_FULL_SPEED):        print "FULL_SPEED;",
    if (events & BG_EVENT_USB_HIGH_SPEED):        print "HIGH_SPEED;",
    if (events & BG_EVENT_USB_SPEED_UNKNOWN):     print "UNKNOWN_SPEED;",
    if (events & BG_EVENT_USB_LOW_OVER_FULL_SPEED):
        print "LOW_OVER_FULL_SPEED;",

def print_events (source, events):
    """Print USB 2 events"""
    if source == BG_USB5000_SOURCE_USB2:
        print_usb2_events(events)
        return

    """Print USB 3 and Async events"""
    if events & BG_EVENT_USB_LTSSM:
        idx = events & BG_EVENT_USB_LTSSM_MASK
        if idx < len(LTSSM_TABLE):
            print "LTSSM Transition: %s;" % LTSSM_TABLE[idx],
        else:
            print "Unknown LTSSM Transition: %d;" % idx,

    if events & BG_EVENT_USB_COMPLEX_TRIGGER:
        state   = events & BG_EVENT_USB_TRIGGER_STATE_MASK
        state >>= BG_EVENT_USB_TRIGGER_STATE_SHIFT
        print "%s trigger from state: %d" % (
            "Timer" if (events & BG_EVENT_USB_TRIGGER_TIMER) else "Complex",
            state)

    if (events & BG_EVENT_USB_VBUS_PRESENT):        print "VBUS Present;",
    if (events & BG_EVENT_USB_VBUS_ABSENT):         print "VBUS Absent;",
    if (events & BG_EVENT_USB_SCRAMBLING_ENABLED):  print "Scrambling On;",
    if (events & BG_EVENT_USB_SCRAMBLING_DISABLED): print "Scrambling Off;",
    if (events & BG_EVENT_USB_POLARITY_NORMAL):     print "Polarity Normal;",
    if (events & BG_EVENT_USB_POLARITY_REVERSED):   print "Polarity Reversed;",
    if (events & BG_EVENT_USB_PHY_ERROR):           print "PHY Error;",
    if (events & BG_EVENT_USB_HOST_DISCONNECT):     print "SS Host Discon;",
    if (events & BG_EVENT_USB_HOST_CONNECT):        print "SS Host Conn;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT):   print "SS Trgt Discon;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):      print "SS Trgt Conn;",
    if (events & BG_EVENT_USB_LFPS):                print "LFPS;",
    if (events & BG_EVENT_USB_TRIGGER):             print "Trigger;",
    if (events & BG_EVENT_USB_EXT_TRIG_ASSERTED):   print "Ext In Asserted;",
    if (events & BG_EVENT_USB_EXT_TRIG_DEASSERTED): print "Ext In Deasserted;",


#==========================================================================
# USB DUMP FUNCTIONS
#==========================================================================
# Renders USB 3 packet data for printing.
def usb_print_data3_packet (packet, k_packet_data, length):
    packetstring = ""

    if (length == 0):
        return packetstring

    # Print the packet data
    for n in range(length):
        k_bit = (k_packet_data[n/8] >> (n % 8)) & 0x01
        packetstring += "%d%02x " % (k_bit, packet[n])

    return packetstring

# Renders USB 2 packet data for printing.
def usb_print_data2_packet (packet, length):
    packetstring = ""

    if (length == 0):
        return packetstring

    # Get the packet identifier
    pid = packet[0]

    # Print the packet identifier
    if    (pid ==  BG_USB_PID_OUT):      pidstr = "OUT"
    elif  (pid ==  BG_USB_PID_IN):       pidstr = "IN"
    elif  (pid ==  BG_USB_PID_SOF):      pidstr = "SOF"
    elif  (pid ==  BG_USB_PID_SETUP):    pidstr = "SETUP"
    elif  (pid ==  BG_USB_PID_DATA0):    pidstr = "DATA0"
    elif  (pid ==  BG_USB_PID_DATA1):    pidstr = "DATA1"
    elif  (pid ==  BG_USB_PID_DATA2):    pidstr = "DATA2"
    elif  (pid ==  BG_USB_PID_MDATA):    pidstr = "MDATA"
    elif  (pid ==  BG_USB_PID_ACK):      pidstr = "ACK"
    elif  (pid ==  BG_USB_PID_NAK):      pidstr = "NAK"
    elif  (pid ==  BG_USB_PID_STALL):    pidstr = "STALL"
    elif  (pid ==  BG_USB_PID_NYET):     pidstr = "NYET"
    elif  (pid ==  BG_USB_PID_PRE):      pidstr = "PRE"
    elif  (pid ==  BG_USB_PID_SPLIT):    pidstr = "SPLIT"
    elif  (pid ==  BG_USB_PID_PING):     pidstr = "PING"
    elif  (pid ==  BG_USB_PID_EXT):      pidstr = "EXT"
    else: pidstr = "INVALID"

    packetstring += pidstr + ","

    # Print the packet data
    for n in range(length):
        packetstring += "%02x " % packet[n]

    return packetstring

# Print the data of the packet
def print_packet (source, packet, k_packet_data, length):
    if source == BG_USB5000_SOURCE_USB2:
        print usb_print_data2_packet(packet, length),
    else:
        print usb_print_data3_packet(packet, k_packet_data, length),

# The main packet dump routine
def usb_dump (num_packets):

    # Setup variables
    packetnum = 0

    packet        = array_u08(1036)
    packet_k_bits = array_u08(130)

    tries = 10

    # Disable VBUS to the device
    bg_usb5000_target_power(beagle, BG_USB5000_TARGET_POWER_OFF)

    # Open the connection to the Beagle.  Default to port 0.
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK):
        print "error: could not enable USB capture; exiting..."
        sys.exit(1)

    # Enable VBUS to the device
    bg_usb5000_target_power(beagle, BG_USB5000_TARGET_POWER_HOST_SUPPLIED)

    # Wait for the analyzer to trigger for up to 10 seconds...
    while tries != 0:
        (ret, status, _, _, _, _) = bg_usb5000_usb3_capture_status(beagle, 1000)
        if ret != BG_OK:
            print ret
            print "error: could not query capture status; exiting..."
            sys.exit(1)

        if status <= BG_USB5000_CAPTURE_STATUS_PRE_TRIGGER:
            print "waiting for trigger..."
        else:
            break

        tries -= 1
    else:
        print "did not trigger, make sure a host and a device " \
            "is connected to the analyzer."
        sys.exit(1)

    print "index,time(ns),source,event,status,data0 ... dataN(*)\n"
    sys.stdout.flush()

    # ...then start decoding packets
    while packetnum < num_packets or num_packets == 0:
        ( length, status, events ,time_sop, time_duration,
          time_dataoffset, source, packet, packet_k_bits ) = \
          bg_usb5000_read(beagle, packet, packet_k_bits)

        # Make sure capture is triggered.
        if length == BG_CAPTURE_NOT_TRIGGERED:
            continue

        # Check for invalid packet or Beagle error
        if length < 0:
            print "error=%d" % length
            break

        # Exit if observed end of capture
        if status == BG_READ_USB_END_OF_CAPTURE:
            print
            print "End of capture"
            break

        """Grab the next packet on a timeout."""
        if length == 0 and status == BG_READ_TIMEOUT and events == 0:
            continue

        """Print the packet details"""
        print "%d," % packetnum,
        print "%u," % timestamp_to_ns(time_sop, samplerate_khz),
        print_source(source)
        print ",",
        print_events(source, events)
        print ",",
        print_status(source, status)
        print ",",
        print_packet(source, packet, packet_k_bits, length)
        print

        packetnum += 1

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# COMPLEX MATCH CONFIGURATION
#==========================================================================
def usb_config_complex_match (beagle):
    # Figure out if the Beagle 5000 is licensed for more than one
    # complex match state.
    features = bg_usb5000_features(beagle)
    if features < 0:
        print "error: could not retrieve features"
        sys.exit(1)

    adv = bool(features & BG_USB5000_FEATURE_CMP_TRIG)

    # Setup the first state.
    # Do a capture trigger on seeing a SET ADDRESS setup packet.

    # Match on a SET ADDRESS request.  We also construct a data valid mask
    # which masks out the device address from the request as that is variable.
    setup_data       = array('B', [0x00, 0x05, 0x00, 0x00,
                                      0x00, 0x00, 0x00, 0x00])
    setup_data_valid = array('B', [0xff, 0xff, 0x00, 0xff,
                                      0xff, 0xff, 0xff, 0xff])

    # Configure the data match properties.  Since SET ADDRESS only comes
    # on device 0 and ep 0, we can match only on those parameters.
    prop = BeagleUsb5000Usb3DataProperties()
    prop.source_match_type    = BG_USB5000_MATCH_TYPE_EQUAL
    prop.source_match_val     = BG_USB5000_SOURCE_TX
    prop.ep_match_type        = BG_USB5000_MATCH_TYPE_EQUAL
    prop.ep_match_val         = 0
    prop.dev_match_type       = BG_USB5000_MATCH_TYPE_EQUAL
    prop.dev_match_val        = 0
    prop.stream_id_match_type = BG_USB5000_MATCH_TYPE_DISABLED
    prop.data_len_match_type  = BG_USB5000_MATCH_TYPE_EQUAL
    prop.data_len_match_val   = 8

    # Setup the struct for the Data Match Unit
    match0 = BeagleUsb5000Usb3DataMatchUnit()
    match0.packet_type           = BG_USB5000_USB3_MATCH_PACKET_SHP_SDP
    match0.data_length           = 8
    match0.data                  = setup_data
    match0.data_valid_length     = 8
    match0.data_valid            = setup_data_valid
    match0.err_match             = BG_USB5000_USB3_MATCH_CRC_BOTH_VALID
    match0.data_properties_valid = 1
    match0.data_properties       = prop
    match0.match_modifier        = BG_USB5000_USB3_MATCH_MODIFIER_0
    match0.repeat_count          = 0 # Match just once.
    match0.sticky_action         = 0 # Match just once.
    match0.action_mask           = BG_USB5000_COMPLEX_MATCH_ACTION_TRIGGER

    if adv:
        # Configure state0's data match to goto state1
        # on it's match of the SET ADDRESS.
        match0.goto_selector = 0 # Use the first goto selector.
        match0.action_mask  |= BG_USB5000_COMPLEX_MATCH_ACTION_GOTO

    # Configure the State 0 struct.
    state0 = BeagleUsb5000Usb3ComplexMatchState()
    state0.tx_data_0_valid = 1
    state0.tx_data_0       = match0
    state0.tx_data_1_valid = 0
    state0.tx_data_2_valid = 0
    state0.rx_data_0_valid = 0
    state0.rx_data_1_valid = 0
    state0.rx_data_2_valid = 0
    state0.timer_valid     = 0
    state0.async_valid     = 0
    # For units licensed for advanced complex trigger, go to state 1.
    state0.goto_0          = 1

    # Setup state 2 to filter out all link layer packets on both streams.
    match_slc = BeagleUsb5000Usb3DataMatchUnit()
    match_slc.packet_type           = BG_USB5000_USB3_MATCH_PACKET_SLC
    match_slc.data_length           = 0 # Match all SLCs.
    match_slc.data_valid_length     = 0
    match_slc.err_match             = BG_USB5000_USB3_MATCH_CRC_BOTH_VALID
    match_slc.data_properties_valid = 0
    match_slc.match_modifier        = BG_USB5000_USB3_MATCH_MODIFIER_0
    match_slc.repeat_count          = 0
    match_slc.sticky_action         = 0
    match_slc.action_mask           = BG_USB5000_COMPLEX_MATCH_ACTION_FILTER

    state1 = BeagleUsb5000Usb3ComplexMatchState()
    state1.tx_data_0_valid = 1
    state1.tx_data_0       = match_slc
    state1.tx_data_1_valid = 0
    state1.tx_data_2_valid = 0
    state1.rx_data_0_valid = 1
    state1.rx_data_0       = match_slc
    state1.rx_data_1_valid = 0
    state1.rx_data_2_valid = 0
    state1.timer_valid     = 0
    state1.async_valid     = 0

    ret = bg_usb5000_usb3_complex_match_config(
        beagle,
        0, # Validate and program it into the Beagle 5000.
        0, # Not using extout.
        state0,
        state1 if adv else None, # Can only use more than 1 state if licensed.
        None, None, None, None, None, None)

    if ret != BG_OK:
        print "error: could not configure complex match"
        sys.exit(1)

    if bg_usb5000_usb3_complex_match_enable(beagle) != BG_OK:
        print "error: could not enable complex match"
        sys.exit(1)


#==========================================================================
# BUFFER CONFIGURATION
#==========================================================================
def usb_config_buffer (beagle):
    """ Configure Beagle 5000 for capturing USB 3.0, and waiting for a
        trigger event."""

    if bg_usb5000_configure(beagle,
                            BG_USB5000_CAPTURE_USB3,
                            BG_USB5000_TRIGGER_MODE_EVENT) != BG_OK:
        print "error: could not configure Beagle 5000 with desired mode"
        sys.exit(1)

    # Configure the onboard USB 3.0 buffer for 1MB of pretrigger and
    # 3MB of posttrigger.
    if bg_usb5000_usb3_capture_config(beagle, 1024, 4096) < 0:
        print "error: configuring capture buffer failed!"
        sys.exit(1)

    status, pretrig_kb, capture_kb = \
        bg_usb5000_usb3_capture_config_query(beagle)
    print "Configured capture buffer: pretrig = %dKB total capture = %dKB" \
        % (pretrig_kb, capture_kb)
    print


#==========================================================================
# USAGE INFORMATION
#==========================================================================
def print_usage ():
    print """Usage: capture_usb5000_extras num_events
Example utility for capturing USB 3.0 data from a Beagle 5000 protocol analyzer.
This also demonstrates the use of target power control, and complex match
units of the Beagle 5000 protocol analyzer.

Due to the large amount of data generated by this example, it is best
to redirect the output of this program to a file.

  The parameter num_events is set to the number of events to process
  before exiting.  If num_events is set to zero, the capture will continue
  indefinitely.

For product documentation and specifications, see www.totalphase.com."""
    sys.stdout.flush()


#==========================================================================
# MAIN PROGRAM ENTRY POINT
#==========================================================================
port       = 0      # open port 0 by default
timeout    = 100    # in milliseconds
latency    = 200    # in milliseconds
num        = 0

if len(sys.argv) < 2:
    print_usage()
    sys.exit(1)

num = int(sys.argv[1])

# Open the device
beagle = bg_open(port)
if (beagle <= 0):
    print "Unable to open Beagle device on port %d" % port
    print "Error code = %d" % beagle
    sys.exit(1)

print "Opened Beagle device on port %d" % port

# Query the samplerate since Beagle USB has a fixed sampling rate
samplerate_khz = bg_samplerate(beagle, samplerate_khz)
if (samplerate_khz < 0):
    print "error: %s" % bg_status_string(samplerate_khz)
    sys.exit(1)

print "Sampling rate set to %d KHz." % samplerate_khz

# Set the idle timeout.
# The Beagle read functions will return in the specified time
# if there is no data available on the bus.
bg_timeout(beagle, timeout)
print "Idle timeout set to %d ms." %  timeout

# Set the latency.
# The latency parameter allows the programmer to balance the
# tradeoff between host side buffering and the latency to
# receive a packet when calling one of the Beagle read
# functions.
bg_latency(beagle, latency)
print "Latency set to %d ms." % latency

print "Host interface is %s." % \
      (bg_host_ifce_speed(beagle) and "high speed" or "full speed")

print ""
sys.stdout.flush()

# Configure the capture buffer
usb_config_buffer(beagle)

# Configure the complex match
usb_config_complex_match(beagle)

# Capture the USB packets
usb_dump(num)

# Close the device
bg_close(beagle)

sys.exit(0)
