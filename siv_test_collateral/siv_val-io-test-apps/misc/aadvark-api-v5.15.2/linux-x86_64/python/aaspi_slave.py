# (c) 2004  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Aardvark Sample Code
# File    : aaspi_slave.py
#--------------------------------------------------------------------------
# Configure the device as an SPI slave and watch incoming data.
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
import sys
import string

from aardvark_py import *


#==========================================================================
# CONSTANTS
#==========================================================================
BUFFER_SIZE      = 65535

#SLAVE_RESP_SIZE  =    10


#==========================================================================
# FUNCTIONS
#==========================================================================
def dump (handle, timeout_ms):
    print "Watching slave SPI data..."
    result = aa_async_poll(handle, timeout_ms)
    
    if (result != AA_ASYNC_SPI):
        print "No data available."
        return
    
    print ""
    
    trans_num = 0

    # Loop until aa_spi_slave_read times out
    for trans_num in range(0,5):
        # Read the SPI message.
        # This function has an internal timeout (see datasheet).
        # To use a variable timeout the function aa_async_poll could
        # be used for subsequent messages.
        (num_read, data_in) = aa_spi_slave_read(handle, BUFFER_SIZE)

        if (num_read < 0 and num_read != AA_SPI_SLAVE_TIMEOUT):
            print "error: %s" % aa_status_string(num_read)
            return

        elif (num_read == 0 or num_read == AA_SPI_SLAVE_TIMEOUT):
            print "No more data available from SPI master"
            return

        else:
            # Dump the data to the screen
            sys.stdout.write("*** Transaction #%02d\n" % trans_num)
            sys.stdout.write("Data read from device:")
            for i in range(num_read):
                if ((i&0x0f) == 0):
                    sys.stdout.write("\n%04x: " % i)

                var = "%02x " % (data_in[i] & 0xff)
                os.system("echo " + var + ">> /root/spi.log")
                if (((i+1)&0x07) == 0):
                    sys.stdout.write(" ")

            sys.stdout.write("\n\n")

            #trans_num = trans_num +1


#==========================================================================
# MAIN PROGRAM
#==========================================================================
if (len(sys.argv) < 4):
    print "usage: aaspi_slave PORT MODE ORDER ADDR TIMEOUT_MS LENGTH BYTES [DATA]"
    print "  mode 0 : pol = 0, phase = 0"
    print "  mode 1 : pol = 0, phase = 1"
    print "  mode 2 : pol = 1, phase = 0"
    print "  mode 3 : pol = 1, phase = 1\n"
    print "  Order - msb = MSB First"
    print "  Order - lsb = LSB First\n"
    print "  Addr - Address in Hexadecimal 0X<Address>"
    print "  The timeout value specifies the time to"
    print "  block until the first packet is received."
    print "  If the timeout is -1, the program will"
    print "  block indefinitely."
    sys.exit()

port       = int(sys.argv[1])
mode       = int(sys.argv[2])

if sys.argv[3].upper() == "LSB":
    spi_bit_order = AA_SPI_BITORDER_LSB
else:
    spi_bit_order = AA_SPI_BITORDER_MSB

slave_address = int(sys.argv[4],0)

timeout_ms = int(sys.argv[5])

if int(sys.argv[6]) == 8:
    padding = 2
elif int(sys.argv[6]) == 16:
    padding = 4
elif int(sys.argv[6]) == 32:
    padding = 8

SLAVE_RESP_SIZE = int(sys.argv[7]) + padding

handle = aa_open(port)
if (handle <= 0):
    print "Unable to open Aardvark device on port %d" % port
    print "Error code = %d" % handle
    sys.exit()
    
# ensure that the SPI subsystem is enabled
aa_configure(handle,  AA_CONFIG_SPI_I2C)
    
# Disable the Aardvark adapter's power pins.
# This command is only effective on v2.0 hardware or greater.
# The power pins on the v1.02 hardware are not enabled by default.
aa_target_power(handle, AA_TARGET_POWER_NONE)

# Set the bitrate
#bitrate = aa_spi_bitrate(handle, bitrate)
#print "Bitrate set to %d kHz" % bitrate

# Setup the clock phase
aa_spi_configure(handle, mode >> 1, mode & 1, spi_bit_order)

# Set the slave response
slave_resp = array('B', [ 0 for i in range(SLAVE_RESP_SIZE) ])
slave_resp[0] = int(str(0),16)
slave_resp[1] = slave_address

for i in range(SLAVE_RESP_SIZE - 2):
    slave_resp[i+2] = int(sys.argv[8+i],16)
    

aa_spi_slave_set_response(handle, slave_resp)

# Enable the slave
aa_spi_slave_enable(handle)

# Watch the SPI port
dump(handle, timeout_ms)

# Disable the slave and close the device
aa_spi_slave_disable(handle)
aa_close(handle)