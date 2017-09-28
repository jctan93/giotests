#!/bin/env python
#==========================================================================
# (c) 2007  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : capture_mdio.py
#--------------------------------------------------------------------------
# Simple Capture Example for MDIO
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

def print_mdio_status (status):
    """MDIO status codes"""
    if (status & BG_MDIO_BAD_TURNAROUND):
        print "MDIO_BAD_TURNAROUND",


#==========================================================================
# MDIO DUMP FUNCTION
#==========================================================================
def mdiodump (num_packets):
    # Get the size of the timing information for a transaction of
    # max_bytes length
    timing_size = bg_bit_timing_size(BG_PROTOCOL_MDIO, 0)

    # Get the current sampling rate
    samplerate_khz = bg_samplerate(beagle, 0)

    # Start the capture
    if (bg_enable(beagle, BG_PROTOCOL_MDIO) != BG_OK):
        print "error: could not enable MDIO capture; exiting..."
        sys.exit(1)

    print "index,time(ns),MDIO,status,<clause:opcode>,<addr1>,<addr2>,data"
    sys.stdout.flush()

    # Allocate the array to be passed into the read function
    timing = array_u32(timing_size)

    # Capture and print each transaction
    i = 0
    while (i < num_packets or num_packets == 0):
        # Read transaction with bit timing data
        (count, status, time_sop, time_duration,
         time_dataoffset, packet, timing) = \
            bg_mdio_read_bit_timing (beagle, timing)

        # Translate timestamp to ns
        time_sop_ns = TIMESTAMP_TO_NS(time_sop, samplerate_khz);

        # Check for errors
        if (count < 0):
            print "%d,%u,MDIO,( error=%d," % (i , time_sop_ns, count),
            print_general_status(status)
            print_mdio_status(status)
            print ")"
            sys.stdout.flush()
            i += 1
            continue

        # Parse the MDIO frame
        (ret, clause, opcode, addr1, addr2, data) = bg_mdio_parse(packet)

        print "%d,%u,MDIO,(" % (i , time_sop_ns),
        print_general_status(status),
        if (not (status & BG_READ_TIMEOUT)):
            print_mdio_status(ret)
        sys.stdout.write(" )")

        # If zero data captured, continue
        i += 1
        if (count == 0):
            print ""
            sys.stdout.flush()
            continue;

        # Print the clause and opcode
        sys.stdout.write(",")
        if ( not (status & BG_READ_ERR_MIDDLE_OF_PACKET)):
            if (clause == BG_MDIO_CLAUSE_22):
                sys.stdout.write("<22:")

                if (opcode == BG_MDIO_OPCODE22_WRITE):
                    sys.stdout.write("W")

                elif (opcode == BG_MDIO_OPCODE22_READ):
                    sys.stdout.write("R")

                elif (opcode == BG_MDIO_OPCODE22_ERROR):
                    sys.stdout.write("?")

            elif (clause == BG_MDIO_CLAUSE_45):
                sys.stdout.write( "<45:")

                if (opcode == BG_MDIO_OPCODE45_ADDR):
                    sys.stdout.write("A")

                elif (opcode == BG_MDIO_OPCODE45_WRITE):
                    sys.stdout.write("W")

                elif (opcode == BG_MDIO_OPCODE45_READ_POSTINC):
                    sys.stdout.write("RI")

                elif (opcode == BG_MDIO_OPCODE45_READ):
                    sys.stdout.write("R")

            else:
                sys.stdout.write("<?:?")

            # Recall that for Clause 22:  PHY  Addr = addr1, Reg Addr = addr2
            #         and for Clause 45:  Port Addr = addr1, Dev Addr = addr2
            print ">,<%02X>,<%02X>,%04X" % (addr1, addr2, data)
            sys.stdout.flush()

    # Stop the capture
    bg_disable(beagle)


#==========================================================================
# USAGE INFORMATION
# =========================================================================
def print_usage ():
    print """
Usage: capture_mdio num_events
Example utility for capturing MDIO data from Beagle protocol analyzers.

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
target_pow = BG_TARGET_POWER_OFF
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

bg_target_power(beagle, target_pow)

print ""

mdiodump(num)

# Close the device
bg_close(beagle)

sys.exit(0)
