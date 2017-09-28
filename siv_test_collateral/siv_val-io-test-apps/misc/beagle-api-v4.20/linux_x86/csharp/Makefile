#==========================================================================
# (c) 2007-2008  Total Phase, Inc.
#--------------------------------------------------------------------------
# Project : Beagle Sample Code
# File    : Makefile
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
# CONFIGURATION
#==========================================================================
# Uncomment the following lines for Linux and Darwin
#CSC=mcs
#OPT=-

# Uncomment the following lines for Windows
CSC=csc
OPT=/


#==========================================================================
# CONSTANTS
#==========================================================================
OUTDIR=_output


#==========================================================================
# TARGETS
#==========================================================================
TARGETS=detect          capture_i2c     \
        capture_spi     capture_mdio    \
        capture_usb12   capture_usb480  \
        capture_usb480_extras \
        capture_usb5000 capture_usb5000_extras

BINARIES=$(TARGETS:%=$(OUTDIR)/%)

all : $(OUTDIR) $(BINARIES)
	-@if [ -r beagle.so ];  then cp -f beagle.so  \
		$(OUTDIR)/libbeagle.so; fi
	-@if [ -r beagle.dll ]; then cp -f beagle.dll \
		$(OUTDIR); fi

$(BINARIES) : % : $(OUTDIR) %.exe


#==========================================================================
# RULES
#==========================================================================
$(OUTDIR)/%.exe : %.cs
	$(CSC) $(OPT)out:$@ beagle.cs $<

$(OUTDIR) :
	-@mkdir $(OUTDIR)

clean:
	rm -fr $(OUTDIR)
	rm -f .bak* *~
