#!/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_spi.py
#--------------------------------------------------------------------------
# Simple Capture Example for SPI
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
def TIMESTAMP_TO_NS(stamp, samplerate_khz):
    return (stamp * 1000L) / (samplerate_khz/1000L)

def print_general_status (status):
    """ General status codes """
    print "",
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


def print_spi_status (status):
    """No specific SPI status codes"""
    pass


#==========================================================================
# DUMP FUNCTIONS
#==========================================================================
# The main packet dump routine
def spidump (max_bytes, num_packets):

    # Get the size of timing information for each transaction of size
    # max_bytes
    timing_size = bg_bit_timing_size(BG_PROTOCOL_SPI, max_bytes)

    # Get the current sampling rate
    samplerate_khz = bg_samplerate(beagle, 0)

    # Start the capture
    if (bg_enable(beagle, BG_PROTOCOL_SPI) != BG_OK):
        print "error: could not enable SPI capture; exiting..."
        sys.exit(1)

    print "index,time(ns),SPI,status,mosi0/miso0 ... mosiN/misoN"
    sys.stdout.flush()

    i = 0

    # Allocate the arrays to be passed into the read function
    data_mosi  = array_u08(max_bytes)
    data_miso  = array_u08(max_bytes)
    bit_timing = array_u32(timing_size)

    # Capture and print information for each transaction
    while (i < num_packets or num_packets == 0):

        # Read transaction with bit timing data
        (count, status, time_sop, time_duration, time_dataoffset, data_mosi, \
         data_miso, bit_timing) = \
         bg_spi_read_bit_timing(beagle, data_mosi, data_miso, bit_timing)

        # Translate timestamp to ns
        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        sys.stdout.write( "%d,%u,SPI,(" % (i, time_sop_ns))

        if (count < 0):
            print "error=%d,", count

        print_general_status(status)
        print_spi_status(status)
        sys.stdout.write( ")")

        # Check for errors
        i += 1
        if (count <= 0):
            print ""
            sys.stdout.flush()

            if (count < 0):
                break;

            # If zero data captured, continue
            continue;

        # Display the data
        for n in range(count):
            if (n != 0):         sys.stdout.write(", ")
            if ((n & 0xf) == 0): sys.stdout.write("\n    ")
            print "%02x/%02x" % (data_mosi[n], data_miso[n]),
        sys.stdout.write("\n")
        sys.stdout.flush()

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """Usage: capture_spi max_packet_len num_events
Example utility for capturing SPI data from Beagle protocol analyzers.

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

speed = ""
if (bg_host_ifce_speed(beagle)):
    speed = "high speed"
else:
    speed = "full speed"

print("Host interface is %s." % speed)

# Configure the device for SPI
bg_spi_configure(beagle,
                 BG_SPI_SS_ACTIVE_LOW,
                 BG_SPI_SCK_SAMPLING_EDGE_RISING,
                 BG_SPI_BITORDER_MSB)

# There is usually no need for target power when using the
# Beagle as a passive monitor.
bg_target_power(beagle, BG_TARGET_POWER_OFF);

print ""
sys.stdout.flush()

spidump(length, num)

# Close the device
bg_close(beagle)

sys.exit(0)
