#!/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_usb12.py
#--------------------------------------------------------------------------
# Simple Capture Example for Beagle USB 12
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
beagle = 0
samplerate_khz = 0;
IDLE_THRESHOLD = 2000

#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def TIMESTAMP_TO_NS (stamp, samplerate_khz):
    return int((stamp * 1000) / (samplerate_khz/1000))

def print_general_status (status):
    """ General status codes """

    if (status == BG_READ_OK) :
        print "OK",

    if (status & BG_READ_TIMEOUT):
        print "TIMEOUT",

    if (status & BG_READ_ERR_MIDDLE_OF_PACKET):
        print "MIDDLE",

    if (status & BG_READ_ERR_SHORT_BUFFER):
        print "SHORT BUFFER",

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

def print_usb_events (events):
    """USB event codes"""
    if (events & BG_EVENT_USB_HOST_DISCONNECT):   print "HOST_DISCON;",
    if (events & BG_EVENT_USB_TARGET_DISCONNECT): print "TGT_DISCON;",
    if (events & BG_EVENT_USB_RESET):             print "RESET;",
    if (events & BG_EVENT_USB_HOST_CONNECT):      print "HOST_CONNECT;",
    if (events & BG_EVENT_USB_TARGET_CONNECT):    print "TGT_CONNECT/UNRST;",

def usb_print_summary (i, count_sop, summary):
    count_sop_ns =  TIMESTAMP_TO_NS(count_sop, samplerate_khz)
    print "%d,%u,USB,( ),%s" % (i, count_sop_ns, summary)


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

# Dump saved summary information
def usb_print_summary_packet (packet_number, count_sop, sof_count, pre_count,
                              in_ack_count, in_nak_count, sync_errors):
    offset = 0
    summary = ""
    if (sof_count or in_ack_count or in_nak_count or pre_count):
        summary +=  "COLLAPSED "

        if (sof_count > 0):
            summary += "[%d SOF] " %  sof_count

        if (pre_count > 0):
            summary += "[%d PRE/ERR] " % pre_count

        if (in_ack_count > 0):
            summary += "[%d IN/ACK] " % in_ack_count

        if (in_nak_count > 0):
            summary += "[%d IN/NAK] " % in_nak_count

        usb_print_summary(packet_number+offset, count_sop, summary)
        offset += 1

    # Output any sync errors
    if (sync_errors > 0):
        summary += "<%d SYNC ERRORS>" %  sync_errors
        usb_print_summary(packet_number+offset, count_sop, summary)
        offset += 1
    return offset

# If the packet is not one that we're aggregating,
# this function returns 1, else 0.
def usb_trigger (pid):
    return ((pid != BG_USB_PID_SOF)  and
            (pid != BG_USB_PID_PRE)  and
            (pid != BG_USB_PID_IN)   and
            (pid != BG_USB_PID_ACK)  and
            (pid != BG_USB_PID_NAK))

# The main packet dump routine
def usbdump (num_packets):
    timing_size = bg_bit_timing_size(BG_PROTOCOL_USB, 1024)

    count_sop    = 0
    sof_count    = 0
    pre_count    = 0
    in_ack_count = 0
    in_nak_count = 0

    pid        = 0
    last_sop   = 0
    last_pid   = 0

    sync_errors = 0

    packetnum = 0

    saved_in_length = 0
    saved_in_status = 0

    global samplerate_khz;
    samplerate_khz = bg_samplerate(beagle, 0)
    idle_samples   = IDLE_THRESHOLD * samplerate_khz


    # Open the connection to the Beagle.  Default to port 0.
    if (bg_enable(beagle, BG_PROTOCOL_USB) != BG_OK):
        print "error: could not enable USB capture; exiting..."
        sys.exit(1)

    # Output the header...
    print "index,time(ns),USB,status,pid,data0 ... dataN(*)"
    sys.stdout.flush()

    # Allocate the arrays to be passed into the read function
    packet = array_u08(1024)
    timing = array_u32(timing_size)

    # ...then start decoding packets
    while packetnum < num_packets or num_packets == 0:
        last_pid = pid
        (length, status, events, time_sop, time_duration,
         time_dataoffset, packet, timing) = \
            bg_usb12_read_bit_timing (beagle, packet, timing)


        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz)

        # Check for invalid packet or Beagle error
        if (length < 0):
            error_status = "error=%d" % length
            usb_print_packet(packetnum, time_sop_ns, status, events,
                             error_status, 0)
            break

        # Check for USB error
        if (status == BG_READ_USB_ERR_BAD_SYNC):
            sync_errors += 1

        if (length > 0):
            pid = packet[0]
        else:
            pid = 0

        # Check the PID and collapse appropriately:
        # SOF* PRE* (IN (ACK|NAK))*
        # If we have saved summary information, and we have
        # hit an error, received a non-summary packet, or
        # have exceeded the idle time, then dump out the
        # summary information before continuing
        if (status != BG_READ_OK or usb_trigger(pid) or
            (int(time_sop - count_sop) >= idle_samples)):
            offset = usb_print_summary_packet(packetnum, count_sop,
                                              sof_count, pre_count,
                                              in_ack_count, in_nak_count,
                                              sync_errors)
            sof_count    = 0
            pre_count    = 0
            in_ack_count = 0
            in_nak_count = 0
            sync_errors  = 0
            count_sop    = time_sop

            # Adjust the packet index if any events were printed by
            # usb_print_summary_packet.
            packetnum += offset

        # Now handle the current packet based on its packet ID
        if (pid == BG_USB_PID_SOF):
            # Increment the SOF counter
            sof_count += 1

        elif (pid ==  BG_USB_PID_PRE):
            # Increment the PRE counter
            pre_count += 1

        elif (pid == BG_USB_PID_IN):
            # If the transaction is an IN, don't display it yet and
            # save the transaction.
            # If the following transaction is an ACK or NAK,
            # increment the appropriate IN/ACK or IN/NAK counter.
            # If the next transaction is not an ACK or NAK,
            # display the saved IN transaction .
            saved_in            = packet[:length]
            saved_in_timing     = timing[:length*8]
            saved_in_sop        = time_sop
            saved_in_duration   = time_duration
            saved_in_dataoffset = time_dataoffset
            saved_in_length     = length
            saved_in_status     = status
            saved_in_events     = events

        else:
            if ((pid ==  BG_USB_PID_NAK or pid == BG_USB_PID_ACK) and
                # If the last transaction was IN, increment the appropriate
                # counter and don't display the transaction.
                saved_in_length > 0):
                saved_in_length = 0
                if (pid == BG_USB_PID_ACK):
                    in_ack_count += 1
                else:
                    in_nak_count += 1
            else:
                #If the last transaction was IN, output it
                if (saved_in_length > 0):
                    saved_in_sop_ns = \
                        TIMESTAMP_TO_NS(saved_in_sop, samplerate_khz)

                    packet_data = usb_print_data_packet(saved_in,
                                                        saved_in_length)
                    usb_print_packet(packetnum, saved_in_sop_ns,
                                     saved_in_status,
                                   saved_in_events, 0, packet_data)
                    packetnum += 1
                    saved_in_length = 0

                # Output the current transaction
                if (length > 0 or events != 0  or
                    (status != 0 and status != BG_READ_TIMEOUT)):
                    packet_data = usb_print_data_packet(packet, length)
                    usb_print_packet(packetnum, time_sop_ns, status,
                                     events, 0, packet_data)
                    packetnum += 1

                last_sop  = time_sop
                count_sop = time_sop + time_duration

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: capture_usb num_events
Example utility for capturing USB data from Beagle protocol analyzers.

  The parameter num_events is set to the number of events to process
  before exiting.  If num_events is set to zero, the capture will continue
  indefinitely.

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

if (len(sys.argv) < 2):
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

bg_host_ifce_speed_string = ""

if (bg_host_ifce_speed(beagle)):
    bg_host_ifce_speed_string = "high speed"
else:
    bg_host_ifce_speed_string = "full speed"

print "Host interface is %s." % bg_host_ifce_speed_string

# There is usually no need for pullups or target power
# when using the Beagle as a passive monitor.
bg_target_power(beagle, BG_TARGET_POWER_OFF)

print ""
sys.stdout.flush()

usbdump(num)

# Close the device
bg_close(beagle)

sys.exit(0)
