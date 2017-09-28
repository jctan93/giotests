#!/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_i2c.py
#--------------------------------------------------------------------------
# Simple Capture Example for I2C
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


#==========================================================================
# UTILITY FUNCTIONS
#==========================================================================
def TIMESTAMP_TO_NS (stamp, samplerate_khz):
    return (stamp * 1000L) / (samplerate_khz/1000L)

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

def print_i2c_status (status):
    """I2C status codes"""
    if (status & BG_READ_I2C_NO_STOP):
        print "I2C_NO_STOP",


#==========================================================================
# I2C DUMP FUNCTION
#==========================================================================
def i2cdump (max_bytes, num_packets):
    # Get the size of the timing information for a transaction of
    # max_bytes length
    timing_size = bg_bit_timing_size(BG_PROTOCOL_I2C, max_bytes)

    # Get the current sampling rate
    samplerate_khz = bg_samplerate(beagle, 0)

    i = 0

    # Start the capture
    if (bg_enable(beagle, BG_PROTOCOL_I2C) != BG_OK):
        print "error: could not enable I2C capture; exiting..."
        sys.exit(1)

    print "index,time(ns),I2C,status,<addr:r/w>(*),data0 ... dataN(*)"
    sys.stdout.flush()

    # Allocate the arrays to be passed into the read function
    data_in = array_u16(max_bytes)
    timing  = array_u32(timing_size)

    # Capture and print each transaction
    while (i < num_packets or num_packets == 0):
        # Read transaction with bit timing data
        (count, status, time_sop, time_duration,
         time_dataoffset, data_in, timing) = \
            bg_i2c_read_bit_timing(beagle, data_in, timing)

        # Translate timestamp to ns
        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz)

        print "%d,%u,I2C,(" % (i, long(time_sop_ns)),

        if (count < 0):
            print "error=%d," % count,

        print_general_status(status)
        print_i2c_status(status)
        sys.stdout.write( " )")

        # Check for errors
        i += 1
        if (count <= 0):
            print ""
            sys.stdout.flush()
            if (count < 0):
                break

            # If zero data captured, continue
            continue

        # Print the address and read/write
        sys.stdout.write(",")
        offset = 0
        if (not (status & BG_READ_ERR_MIDDLE_OF_PACKET)):
            # Display the start condition
            sys.stdout.write( "[S] ")

            if (count >= 1):
                # Determine if byte was NACKed
                nack = (data_in[0] & BG_I2C_MONITOR_NACK)

                # Determine if this is a 10-bit address
                if (count == 1 or (data_in[0] & 0xf9) != 0xf0 or nack):
                    # Display 7-bit address
                    print "<%02x:" % (long(data_in[0] & 0xff) >> 1),
                    if (data_in[0] & 0x01):
                        sys.stdout.write("r>")
                    else:
                        sys.stdout.write("w>")

                    if (nack):
                        sys.stdout.write("* ")
                    else:
                        sys.stdout.write(" ")
                    offset = 1

                else:
                    # Display 10-bit address
                    print "<%03x:" %  ((data_in[0] << 7) & 0x300) \
                                     | (data_in[1] & 0xff),
                    if (data_in[0] & 0x01):
                        sys.stdout.write("r>")
                    else:
                        sys.stdout.write("w>")

                    if (nack):
                        sys.stdout.write("* ")
                    else:
                        sys.stdout.write(" ")
                    offset = 2

        # Display rest of transaction
        count = count - offset
        for n in range(count):
            # Determine if byte was NACKed
            nack = (data_in[offset] & BG_I2C_MONITOR_NACK)

            sys.stdout.write("%02x" % long(data_in[offset] & 0xff))
            if (nack):
                sys.stdout.write("* ")
            else:
                sys.stdout.write(" ")
            offset += 1

        # Display the stop condition
        if (not (status & BG_READ_I2C_NO_STOP)):
            sys.stdout.write("[P]")

        print ""
        sys.stdout.flush()

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: capture_i2c max_packet_len num_events
Example utility for capturing I2C data from Beagle protocol analyzers.

  The parameter max_packet_len is set to the maximum expected packet length
  throughout the entire capture session.

  The parameter num_events is set to the number of events to process
  before exiting.  If num_events is set to zero, the capture will continue
  indefinitely.

For product documentation and specifications, see www.totalphase.com."""
    sys.stdout.flush()


#==========================================================================
# MAIN PROGRAM ENTRY POINT
#==========================================================================
port       = 0      # open port 0 by default
samplerate = 10000  # in kHz
timeout    = 500    # in milliseconds
latency    = 200    # in milliseconds
length     = 0
pullups    = BG_I2C_PULLUP_OFF
target_pow = BG_TARGET_POWER_OFF
num        = 0

if (len(sys.argv) < 3):
    print_usage()
    sys.exit(1)

length = int(sys.argv[1])
num = int(sys.argv[2])

# Open the device
beagle = bg_open(port)
if (beagle <= 0):
    print "Unable to open Beagle device on port %d" % port
    print "Error code = %d" % beagle
    sys.exit(1)

print "Opened Beagle device on port %d" % port

# Set the samplerate
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
bg_i2c_pullup(beagle, pullups)
bg_target_power(beagle, target_pow)

print ""
sys.stdout.flush()

i2cdump(length, num)

# Close the device
bg_close(beagle)

sys.exit(0)
