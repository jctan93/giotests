#!/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_usb480_extras.py
#--------------------------------------------------------------------------
# Delayed Download Capture Example for Beagle USB 480 with hardware filters
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
from time import time


#==========================================================================
# GLOBALS
#==========================================================================
beagle         = 0
samplerate_khz = 0;


#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def TIMESTAMP_TO_NS (stamp, samplerate_khz):
    return int((stamp * 1000) / (samplerate_khz/1000))

def print_general_status (status):
    """ General status codes """

    if (status == BG_READ_OK)                  : print "OK",
    if (status & BG_READ_TIMEOUT)              : print "TIMEOUT",
    if (status & BG_READ_ERR_UNEXPECTED)       : print "UNEXPECTED",
    if (status & BG_READ_ERR_MIDDLE_OF_PACKET) : print "MIDDLE",
    if (status & BG_READ_ERR_SHORT_BUFFER)     : print "SHORT BUFFER",
    if (status & BG_READ_ERR_PARTIAL_LAST_BYTE):
        print "PARTIAL_BYTE(bit %d)" % (status & 0xff),

def print_usb_status (status):
    """USB status codes"""
    if (status & BG_READ_USB_ERR_BAD_SIGNALS):   print "BAD_SIGNAL;",
    if (status & BG_READ_USB_ERR_BAD_SYNC):      print "BAD_SYNC;",
    if (status & BG_READ_USB_ERR_BIT_STUFF):     print "BAD_STUFF;",
    if (status & BG_READ_USB_ERR_FALSE_EOP):     print "BAD_EOP;",
    if (status & BG_READ_USB_ERR_LONG_EOP):      print "LONG_EOP;",
    if (status & BG_READ_USB_ERR_BAD_PID):       print "BAD_PID;",
    if (status & BG_READ_USB_ERR_BAD_CRC):       print "BAD_CRC;",
    if (status & BG_READ_USB_TRUNCATION_MODE):   print "TRUNCATION_MODE;",
    if (status & BG_READ_USB_END_OF_CAPTURE):    print "END_OF_CAPTURE;",

def print_usb_events (events):
    """USB event codes"""
    if (events & BG_EVENT_USB_HOST_DISCONNECT):   print "HOST_DISCON;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT): print "TGT_DISCON;",
    if (events & BG_EVENT_USB_RESET):             print "RESET;",
    if (events & BG_EVENT_USB_HOST_CONNECT):      print "HOST_CONNECT;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):    print "TGT_CONNECT/UNRST;",
    if (events & BG_EVENT_USB_DIGITAL_INPUT):     print "INPUT_TRIGGER %X" % \
       (events & BG_EVENT_USB_DIGITAL_INPUT_MASK),
    if (events & BG_EVENT_USB_CHIRP_J):           print "CHIRP_J; ",
    if (events & BG_EVENT_USB_CHIRP_K):           print "CHIRP_K; ",
    if (events & BG_EVENT_USB_KEEP_ALIVE):        print "KEEP_ALIVE; ",
    if (events & BG_EVENT_USB_SUSPEND):           print "SUSPEND; ",
    if (events & BG_EVENT_USB_RESUME):            print "RESUME; ",
    if (events & BG_EVENT_USB_LOW_SPEED):         print "LOW_SPEED; ",
    if (events & BG_EVENT_USB_FULL_SPEED):        print "FULL_SPEED; ",
    if (events & BG_EVENT_USB_HIGH_SPEED):        print "HIGH_SPEED; ",
    if (events & BG_EVENT_USB_SPEED_UNKNOWN):     print "UNKNOWN_SPEED; ",
    if (events & BG_EVENT_USB_LOW_OVER_FULL_SPEED):
        print "LOW_OVER_FULL_SPEED; ",

def print_progress (percent, elapsed_time, buffer_used, buffer_size):
    tenths = percent/5 + 1
    progressbar = "[%*c%*c" % (tenths, '#', 22-tenths, ']')
    print "\r%s %3d%% %7d of %5d KB %.2lf seconds" % \
          (progressbar, percent, buffer_used / 1024,
           buffer_size / 1024, elapsed_time),
    sys.stdout.flush()


#==========================================================================
# USB DUMP FUNCTIONS
#==========================================================================
# Renders packet data for printing.
def usb_print_data_packet (packet, length):
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

# Print common packet header information
def usb_print_packet (packet_number, time_sop, status, events, error_status,
                    packet_data):
    if (error_status == 0):  error_status = ""

    sys.stdout.write("%d,%u,USB,(%s " % (packet_number, time_sop,
                                         error_status))
    print_general_status(status)
    print_usb_status(status)
    print_usb_events(events)

    if (packet_data == 0):  packet_data = ""
    print "),%s" % packet_data
    sys.stdout.flush()

# The main packet dump routine
def usbdump (num_packets, timeout):
    packetnum   = 0

    global samplerate_khz;
    samplerate_khz = bg_samplerate(beagle, 0)

    # Configure Beagle 480 for delayed download capture
    bg_usb480_capture_configure(beagle,
                                BG_USB480_CAPTURE_DELAYED_DOWNLOAD,
                                BG_USB2_AUTO_SPEED_DETECT)

    # Enable the hardware filtering.  This will filter out packets with
    # the same device address as the Beagle analyzer and also filter
    # the PID packet groups listed below.
    bg_usb480_hw_filter_config(beagle,
                               BG_USB2_HW_FILTER_SELF     |
                               BG_USB2_HW_FILTER_PID_SOF  |
                               BG_USB2_HW_FILTER_PID_IN   |
                               BG_USB2_HW_FILTER_PID_PING |
                               BG_USB2_HW_FILTER_PID_PRE  |
                               BG_USB2_HW_FILTER_PID_SPLIT)

    # Start the capture portion of the delayed-download capture
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK):
        print "error: could not enable USB capture; exiting..."
        sys.exit(1)

    # Wait until timeout period elapses or the hardware buffer on
    # the Beagle USB 480 fills
    print "Hardware buffer usage:"
    start = time()

    while True:
        # Poll the hardware buffer status
        (ret, buffer_size, buffer_usage, buffer_full) = \
              bg_usb480_hw_buffer_stats(beagle)

        # Print out the progress
        elapsed_time = time() - start
        print_progress(buffer_usage / (buffer_size / 100),
                       elapsed_time, buffer_usage, buffer_size)

        # If timed out or buffer is full, exit loop
        if buffer_full or (timeout and elapsed_time > timeout):
            break

        # Sleep for 150 milliseconds
        bg_sleep_ms(150)

    # Start the download portion of the delayed-download capture

    # Output the header...
    print "index,time(ns),USB,status,pid,data0 ... dataN(*)"
    sys.stdout.flush()

    # Allocate the array to be passed into the read function
    packet = array_u08(1024)

    # ...then start decoding packets
    while packetnum < num_packets or num_packets == 0:
        # Calling bg_usb480_read will automatically stop the
        # capture portion of the delayed-download capture and
        # will begin downloading the capture results.
        ( length, status, events , time_sop, time_duration ,
          time_dataoffset, packet ) = bg_usb480_read(beagle, packet);

        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz)

        # Check for invalid packet or Beagle error
        if (length < 0):
            error_status = "error=%d" % length
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             error_status, 0)
            break

        # Output the current transaction
        if (length > 0 or events != 0  or
            (status != 0 and status != BG_READ_TIMEOUT)):
            packet_data = usb_print_data_packet(packet, length)
            usb_print_packet(packetnum, time_sop_ns, status,
                             events, 0, packet_data)
            packetnum += 1

        # Exit if observe end of capture
        if status & BG_READ_USB_END_OF_CAPTURE:
            break

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: capture_usb480_extras num_events timeout
Example utility for executing a delayed-download capture of USB data from
a Beagle 480 protocol analyzer with hardware filtering enabled.

In delayed-download capture, the captured data is stored in the Beagle USB
480's hardware buffer while capture is in progress.  The capture data
is downloaded from the hardware after the capture has been halted.

  The parameter num_events is set to the number of events to process
  before exiting.  If num_events is set to zero, the capture will continue
  indefinitely.

  The parameter timeout is is the number of seconds to run the capture
  before downloading the results.  If timeout is set to zero, the capture
  portion will run until the hardware buffer is full.

For product documentation and specifications, see www.totalphase.com."""
    sys.stdout.flush()


#==========================================================================
# MAIN PROGRAM ENTRY POINT
#==========================================================================
port       = 0      # open port 0 by default
samplerate = 0      # in kHz (query)
timeout    = 500    # in milliseconds
latency    = 200    # in milliseconds
num        = 0

if (len(sys.argv) < 3):
    print_usage()
    sys.exit(1)

num             = int(sys.argv[1])
capture_timeout = int(sys.argv[2])

# Open the device
beagle = bg_open(port)
if (beagle <= 0):
    print "Unable to open Beagle device on port %d" % port
    print "Error code = %d" % beagle
    sys.exit(1)

print "Opened Beagle device on port %d" % port

# Query the samplerate since Beagle USB has a fixed sampling rate
samplerate = bg_samplerate(beagle, samplerate)
if (samplerate < 0):
    print "error: %s" % bg_status_string(samplerate)
    sys.exit(1)

print "Sampling rate set to %d KHz." % samplerate

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

usbdump(num, capture_timeout)

# Close the device
bg_close(beagle)

sys.exit(0)
