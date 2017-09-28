/*=========================================================================
| Beagle Interface Library
|--------------------------------------------------------------------------
| Copyright (c) 2004-2011 Total Phase, Inc.
| All rights reserved.
| www.totalphase.com
|
| Redistribution and use in source and binary forms, with or without
| modification, are permitted provided that the following conditions
| are met:
|
| - Redistributions of source code must retain the above copyright
|   notice, this list of conditions and the following disclaimer.
|
| - Redistributions in binary form must reproduce the above copyright
|   notice, this list of conditions and the following disclaimer in the
|   documentation and/or other materials provided with the distribution.
|
| - Neither the name of Total Phase, Inc. nor the names of its
|   contributors may be used to endorse or promote products derived from
|   this software without specific prior written permission.
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
|--------------------------------------------------------------------------
| To access Total Phase Beagle devices through the API:
|
| 1) Use one of the following shared objects:
|      beagle.so        --  Linux shared object
|          or
|      beagle.dll       --  Windows dynamic link library
|
| 2) Along with one of the following language modules:
|      beagle.c/h       --  C/C++ API header file and interface module
|      beagle_py.py     --  Python API
|      beagle.bas       --  Visual Basic 6 API
|      beagle.cs        --  C# .NET source
|      beagle_net.dll   --  Compiled .NET binding
 ========================================================================*/


/*=========================================================================
| INCLUDES
 ========================================================================*/
/* This #include can be customized to conform to the user's build paths. */
#include "beagle.h"


/*=========================================================================
| VERSION CHECK
 ========================================================================*/
#define BG_CFILE_VERSION   0x0414   /* v4.20 */
#define BG_REQ_SW_VERSION  0x0414   /* v4.20 */

/*
 * Make sure that the header file was included and that
 * the version numbers match.
 */
#ifndef BG_HEADER_VERSION
#  error Unable to include header file. Please check include path.

#elif BG_HEADER_VERSION != BG_CFILE_VERSION
#  error Version mismatch between source and header files.

#endif


/*=========================================================================
| DEFINES
 ========================================================================*/
#define API_NAME                     "beagle"
#define API_DEBUG                    BG_DEBUG
#define API_OK                       BG_OK
#define API_UNABLE_TO_LOAD_LIBRARY   BG_UNABLE_TO_LOAD_LIBRARY
#define API_INCOMPATIBLE_LIBRARY     BG_INCOMPATIBLE_LIBRARY
#define API_UNABLE_TO_LOAD_FUNCTION  BG_UNABLE_TO_LOAD_FUNCTION
#define API_HEADER_VERSION           BG_HEADER_VERSION
#define API_REQ_SW_VERSION           BG_REQ_SW_VERSION


/*=========================================================================
| LINUX AND DARWIN SUPPORT
 ========================================================================*/
#if defined(__APPLE_CC__) && !defined(DARWIN)
#define DARWIN
#endif

#if defined(linux) || defined(DARWIN)

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <fcntl.h>

#ifdef DARWIN
#define DLOPEN_NO_WARN
extern int _NSGetExecutablePath (char *buf, unsigned long *bufsize);
#endif

#include <dlfcn.h>

#define DLL_HANDLE  void *
#define MAX_SO_PATH 256

static char SO_NAME[MAX_SO_PATH+1] = API_NAME ".so";

/*
 * These functions allow the Linux behavior to emulate
 * the Windows behavior as specified below in the Windows
 * support section.
 * 
 * First, search for the shared object in the application
 * binary path, then in the current working directory.
 * 
 * Searching the application binary path requires /proc
 * filesystem support, which is standard in 2.4.x kernels.
 * 
 * If the /proc filesystem is not present, the shared object
 * will not be loaded from the execution path unless that path
 * is either the current working directory or explicitly
 * specified in LD_LIBRARY_PATH.
 */
static int _checkPath (const char *path) {
    char *filename = (char *)malloc(strlen(path) +1 + strlen(SO_NAME) +1);
    int   fd;

    // Check if the file is readable
    sprintf(filename, "%s/%s", path, SO_NAME);
    fd = open(filename, O_RDONLY);
    if (fd >= 0) {
        strncpy(SO_NAME, filename, MAX_SO_PATH);
        close(fd);
    }

    // Clean up and exit
    free(filename);
    return (fd >= 0);
}

static int _getExecPath (char *path, unsigned long maxlen) {
#ifdef linux
    return readlink("/proc/self/exe", path, maxlen);
#endif

#ifdef DARWIN
    _NSGetExecutablePath(path, &maxlen);
    return maxlen;
#endif
}

static void _setSearchPath () {
    char  path[MAX_SO_PATH+1];
    int   count;
    char *p;

    /* Make sure that SO_NAME is not an absolute path. */
    if (SO_NAME[0] == '/')  return;

    /* Check the execution directory name. */
    memset(path, 0, sizeof(path));
    count = _getExecPath(path, MAX_SO_PATH);

    if (count > 0) {
        char *p = strrchr(path, '/');
        if (p == path)  ++p;
        if (p != 0)     *p = '\0';

        /* If there is a match, return immediately. */
        if (_checkPath(path))  return;
    }

    /* Check the current working directory. */
    p = getcwd(path, MAX_SO_PATH);
    if (p != 0)  _checkPath(path);
}

#endif


/*=========================================================================
| WINDOWS SUPPORT
 ========================================================================*/
#if defined(WIN32) || defined(_WIN32)

#include <stdio.h>
#include <windows.h>

#define DLL_HANDLE           HINSTANCE
#define dlopen(name, flags)  LoadLibraryA(name)
#define dlsym(handle, name)  GetProcAddress(handle, name)
#define dlerror()            "Exiting program"
#define SO_NAME              API_NAME ".dll"

/*
 * Use the default Windows DLL loading rules:
 *   1.  The directory from which the application binary was loaded.
 *   2.  The application's current directory.
 *   3a. [Windows NT/2000/XP only] 32-bit system directory
 *       (default: c:\winnt\System32)
 *   3b. 16-bit system directory
 *       (default: c:\winnt\System or c:\windows\system)
 *   4.  The windows directory
 *       (default: c:\winnt or c:\windows)
 *   5.  The directories listed in the PATH environment variable
 */
static void _setSearchPath () {
    /* Do nothing */
}

#endif


/*=========================================================================
| SHARED LIBRARY LOADER
 ========================================================================*/
/* The error conditions can be customized depending on the application. */
static void *_loadFunction (const char *name, int *result) {
    static DLL_HANDLE handle = 0;
    void * function = 0;

    /* Load the shared library if necessary */
    if (handle == 0) {
        u32 (*version) (void);
        u16 sw_version;
        u16 api_version_req;

        _setSearchPath();
        handle = dlopen(SO_NAME, RTLD_LAZY);
        if (handle == 0) {
#if API_DEBUG
            fprintf(stderr, "Unable to load %s\n", SO_NAME);
            fprintf(stderr, "%s\n", dlerror());
#endif
            *result = API_UNABLE_TO_LOAD_LIBRARY;
            return 0;
        }

        version = (void *)dlsym(handle, "bg_c_version");
        if (version == 0) {
#if API_DEBUG
            fprintf(stderr, "Unable to bind bg_c_version() in %s\n",
                    SO_NAME);
            fprintf(stderr, "%s\n", dlerror());
#endif
            handle  = 0;
            *result = API_INCOMPATIBLE_LIBRARY;
            return 0;
        }

        sw_version      = (u16)((version() >>  0) & 0xffff);
        api_version_req = (u16)((version() >> 16) & 0xffff);
        if (sw_version  < API_REQ_SW_VERSION ||
            API_HEADER_VERSION < api_version_req)
        {
#if API_DEBUG
            fprintf(stderr, "\nIncompatible versions:\n");

            fprintf(stderr, "  Header version  = v%d.%02d  ",
                    (API_HEADER_VERSION >> 8) & 0xff, API_HEADER_VERSION & 0xff);

            if (sw_version < API_REQ_SW_VERSION)
                fprintf(stderr, "(requires library >= %d.%02d)\n",
                        (API_REQ_SW_VERSION >> 8) & 0xff,
                        API_REQ_SW_VERSION & 0xff);
            else
                fprintf(stderr, "(library version OK)\n");
                        
                   
            fprintf(stderr, "  Library version = v%d.%02d  ",
                    (sw_version >> 8) & 0xff,
                    (sw_version >> 0) & 0xff);

            if (API_HEADER_VERSION < api_version_req)
                fprintf(stderr, "(requires header >= %d.%02d)\n",
                        (api_version_req >> 8) & 0xff,
                        (api_version_req >> 0) & 0xff);
            else
                fprintf(stderr, "(header version OK)\n");
#endif
            handle  = 0;
            *result = API_INCOMPATIBLE_LIBRARY;
            return 0;
        }
    }

    /* Bind the requested function in the shared library */
    function = (void *)dlsym(handle, name);
    *result  = function ? API_OK : API_UNABLE_TO_LOAD_FUNCTION;
    return function;
}


/*=========================================================================
| FUNCTIONS
 ========================================================================*/
static int (*c_bg_find_devices) (int, u16 *) = 0;
int bg_find_devices (
    int   num_devices,
    u16 * devices
)
{
    if (c_bg_find_devices == 0) {
        int res = 0;
        if (!(c_bg_find_devices = _loadFunction("c_bg_find_devices", &res)))
            return res;
    }
    return c_bg_find_devices(num_devices, devices);
}


static int (*c_bg_find_devices_ext) (int, u16 *, int, u32 *) = 0;
int bg_find_devices_ext (
    int   num_devices,
    u16 * devices,
    int   num_ids,
    u32 * unique_ids
)
{
    if (c_bg_find_devices_ext == 0) {
        int res = 0;
        if (!(c_bg_find_devices_ext = _loadFunction("c_bg_find_devices_ext", &res)))
            return res;
    }
    return c_bg_find_devices_ext(num_devices, devices, num_ids, unique_ids);
}


static Beagle (*c_bg_open) (int) = 0;
Beagle bg_open (
    int port_number
)
{
    if (c_bg_open == 0) {
        int res = 0;
        if (!(c_bg_open = _loadFunction("c_bg_open", &res)))
            return res;
    }
    return c_bg_open(port_number);
}


static Beagle (*c_bg_open_ext) (int, BeagleExt *) = 0;
Beagle bg_open_ext (
    int         port_number,
    BeagleExt * bg_ext
)
{
    if (c_bg_open_ext == 0) {
        int res = 0;
        if (!(c_bg_open_ext = _loadFunction("c_bg_open_ext", &res)))
            return res;
    }
    return c_bg_open_ext(port_number, bg_ext);
}


static int (*c_bg_close) (Beagle) = 0;
int bg_close (
    Beagle beagle
)
{
    if (c_bg_close == 0) {
        int res = 0;
        if (!(c_bg_close = _loadFunction("c_bg_close", &res)))
            return res;
    }
    return c_bg_close(beagle);
}


static int (*c_bg_port) (Beagle) = 0;
int bg_port (
    Beagle beagle
)
{
    if (c_bg_port == 0) {
        int res = 0;
        if (!(c_bg_port = _loadFunction("c_bg_port", &res)))
            return res;
    }
    return c_bg_port(beagle);
}


static int (*c_bg_features) (Beagle) = 0;
int bg_features (
    Beagle beagle
)
{
    if (c_bg_features == 0) {
        int res = 0;
        if (!(c_bg_features = _loadFunction("c_bg_features", &res)))
            return res;
    }
    return c_bg_features(beagle);
}


static int (*c_bg_unique_id_to_features) (u32) = 0;
int bg_unique_id_to_features (
    u32 unique_id
)
{
    if (c_bg_unique_id_to_features == 0) {
        int res = 0;
        if (!(c_bg_unique_id_to_features = _loadFunction("c_bg_unique_id_to_features", &res)))
            return res;
    }
    return c_bg_unique_id_to_features(unique_id);
}


static u32 (*c_bg_unique_id) (Beagle) = 0;
u32 bg_unique_id (
    Beagle beagle
)
{
    if (c_bg_unique_id == 0) {
        int res = 0;
        if (!(c_bg_unique_id = _loadFunction("c_bg_unique_id", &res)))
            return res;
    }
    return c_bg_unique_id(beagle);
}


static const char * (*c_bg_status_string) (int) = 0;
const char * bg_status_string (
    int status
)
{
    if (c_bg_status_string == 0) {
        int res = 0;
        if (!(c_bg_status_string = _loadFunction("c_bg_status_string", &res)))
            return 0;
    }
    return c_bg_status_string(status);
}


static int (*c_bg_version) (Beagle, BeagleVersion *) = 0;
int bg_version (
    Beagle          beagle,
    BeagleVersion * version
)
{
    if (c_bg_version == 0) {
        int res = 0;
        if (!(c_bg_version = _loadFunction("c_bg_version", &res)))
            return res;
    }
    return c_bg_version(beagle, version);
}


static int (*c_bg_latency) (Beagle, u32) = 0;
int bg_latency (
    Beagle beagle,
    u32    milliseconds
)
{
    if (c_bg_latency == 0) {
        int res = 0;
        if (!(c_bg_latency = _loadFunction("c_bg_latency", &res)))
            return res;
    }
    return c_bg_latency(beagle, milliseconds);
}


static int (*c_bg_timeout) (Beagle, u32) = 0;
int bg_timeout (
    Beagle beagle,
    u32    milliseconds
)
{
    if (c_bg_timeout == 0) {
        int res = 0;
        if (!(c_bg_timeout = _loadFunction("c_bg_timeout", &res)))
            return res;
    }
    return c_bg_timeout(beagle, milliseconds);
}


static u32 (*c_bg_sleep_ms) (u32) = 0;
u32 bg_sleep_ms (
    u32 milliseconds
)
{
    if (c_bg_sleep_ms == 0) {
        int res = 0;
        if (!(c_bg_sleep_ms = _loadFunction("c_bg_sleep_ms", &res)))
            return res;
    }
    return c_bg_sleep_ms(milliseconds);
}


static int (*c_bg_target_power) (Beagle, u08) = 0;
int bg_target_power (
    Beagle beagle,
    u08    power_flag
)
{
    if (c_bg_target_power == 0) {
        int res = 0;
        if (!(c_bg_target_power = _loadFunction("c_bg_target_power", &res)))
            return res;
    }
    return c_bg_target_power(beagle, power_flag);
}


static int (*c_bg_host_ifce_speed) (Beagle) = 0;
int bg_host_ifce_speed (
    Beagle beagle
)
{
    if (c_bg_host_ifce_speed == 0) {
        int res = 0;
        if (!(c_bg_host_ifce_speed = _loadFunction("c_bg_host_ifce_speed", &res)))
            return res;
    }
    return c_bg_host_ifce_speed(beagle);
}


static int (*c_bg_dev_addr) (Beagle) = 0;
int bg_dev_addr (
    Beagle beagle
)
{
    if (c_bg_dev_addr == 0) {
        int res = 0;
        if (!(c_bg_dev_addr = _loadFunction("c_bg_dev_addr", &res)))
            return res;
    }
    return c_bg_dev_addr(beagle);
}


static int (*c_bg_host_buffer_size) (Beagle, u32) = 0;
int bg_host_buffer_size (
    Beagle beagle,
    u32    num_bytes
)
{
    if (c_bg_host_buffer_size == 0) {
        int res = 0;
        if (!(c_bg_host_buffer_size = _loadFunction("c_bg_host_buffer_size", &res)))
            return res;
    }
    return c_bg_host_buffer_size(beagle, num_bytes);
}


static int (*c_bg_host_buffer_free) (Beagle) = 0;
int bg_host_buffer_free (
    Beagle beagle
)
{
    if (c_bg_host_buffer_free == 0) {
        int res = 0;
        if (!(c_bg_host_buffer_free = _loadFunction("c_bg_host_buffer_free", &res)))
            return res;
    }
    return c_bg_host_buffer_free(beagle);
}


static int (*c_bg_host_buffer_used) (Beagle) = 0;
int bg_host_buffer_used (
    Beagle beagle
)
{
    if (c_bg_host_buffer_used == 0) {
        int res = 0;
        if (!(c_bg_host_buffer_used = _loadFunction("c_bg_host_buffer_used", &res)))
            return res;
    }
    return c_bg_host_buffer_used(beagle);
}


static int (*c_bg_commtest) (Beagle, int, int) = 0;
int bg_commtest (
    Beagle beagle,
    int    num_samples,
    int    delay_count
)
{
    if (c_bg_commtest == 0) {
        int res = 0;
        if (!(c_bg_commtest = _loadFunction("c_bg_commtest", &res)))
            return res;
    }
    return c_bg_commtest(beagle, num_samples, delay_count);
}


static int (*c_bg_enable) (Beagle, BeagleProtocol) = 0;
int bg_enable (
    Beagle         beagle,
    BeagleProtocol protocol
)
{
    if (c_bg_enable == 0) {
        int res = 0;
        if (!(c_bg_enable = _loadFunction("c_bg_enable", &res)))
            return res;
    }
    return c_bg_enable(beagle, protocol);
}


static int (*c_bg_disable) (Beagle) = 0;
int bg_disable (
    Beagle beagle
)
{
    if (c_bg_disable == 0) {
        int res = 0;
        if (!(c_bg_disable = _loadFunction("c_bg_disable", &res)))
            return res;
    }
    return c_bg_disable(beagle);
}


static int (*c_bg_samplerate) (Beagle, int) = 0;
int bg_samplerate (
    Beagle beagle,
    int    samplerate_khz
)
{
    if (c_bg_samplerate == 0) {
        int res = 0;
        if (!(c_bg_samplerate = _loadFunction("c_bg_samplerate", &res)))
            return res;
    }
    return c_bg_samplerate(beagle, samplerate_khz);
}


static int (*c_bg_bit_timing_size) (BeagleProtocol, int) = 0;
int bg_bit_timing_size (
    BeagleProtocol protocol,
    int            num_data_bytes
)
{
    if (c_bg_bit_timing_size == 0) {
        int res = 0;
        if (!(c_bg_bit_timing_size = _loadFunction("c_bg_bit_timing_size", &res)))
            return res;
    }
    return c_bg_bit_timing_size(protocol, num_data_bytes);
}


static int (*c_bg_i2c_pullup) (Beagle, u08) = 0;
int bg_i2c_pullup (
    Beagle beagle,
    u08    pullup_flag
)
{
    if (c_bg_i2c_pullup == 0) {
        int res = 0;
        if (!(c_bg_i2c_pullup = _loadFunction("c_bg_i2c_pullup", &res)))
            return res;
    }
    return c_bg_i2c_pullup(beagle, pullup_flag);
}


static int (*c_bg_i2c_read) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u16 *) = 0;
int bg_i2c_read (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u16 *  data_in
)
{
    if (c_bg_i2c_read == 0) {
        int res = 0;
        if (!(c_bg_i2c_read = _loadFunction("c_bg_i2c_read", &res)))
            return res;
    }
    return c_bg_i2c_read(beagle, status, time_sop, time_duration, time_dataoffset, max_bytes, data_in);
}


static int (*c_bg_i2c_read_data_timing) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u16 *, int, u32 *) = 0;
int bg_i2c_read_data_timing (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u16 *  data_in,
    int    max_timing,
    u32 *  data_timing
)
{
    if (c_bg_i2c_read_data_timing == 0) {
        int res = 0;
        if (!(c_bg_i2c_read_data_timing = _loadFunction("c_bg_i2c_read_data_timing", &res)))
            return res;
    }
    return c_bg_i2c_read_data_timing(beagle, status, time_sop, time_duration, time_dataoffset, max_bytes, data_in, max_timing, data_timing);
}


static int (*c_bg_i2c_read_bit_timing) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u16 *, int, u32 *) = 0;
int bg_i2c_read_bit_timing (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u16 *  data_in,
    int    max_timing,
    u32 *  bit_timing
)
{
    if (c_bg_i2c_read_bit_timing == 0) {
        int res = 0;
        if (!(c_bg_i2c_read_bit_timing = _loadFunction("c_bg_i2c_read_bit_timing", &res)))
            return res;
    }
    return c_bg_i2c_read_bit_timing(beagle, status, time_sop, time_duration, time_dataoffset, max_bytes, data_in, max_timing, bit_timing);
}


static int (*c_bg_spi_configure) (Beagle, BeagleSpiSSPolarity, BeagleSpiSckSamplingEdge, BeagleSpiBitorder) = 0;
int bg_spi_configure (
    Beagle                   beagle,
    BeagleSpiSSPolarity      ss_polarity,
    BeagleSpiSckSamplingEdge sck_sampling_edge,
    BeagleSpiBitorder        bitorder
)
{
    if (c_bg_spi_configure == 0) {
        int res = 0;
        if (!(c_bg_spi_configure = _loadFunction("c_bg_spi_configure", &res)))
            return res;
    }
    return c_bg_spi_configure(beagle, ss_polarity, sck_sampling_edge, bitorder);
}


static int (*c_bg_spi_read) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u08 *, int, u08 *) = 0;
int bg_spi_read (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    mosi_max_bytes,
    u08 *  data_mosi,
    int    miso_max_bytes,
    u08 *  data_miso
)
{
    if (c_bg_spi_read == 0) {
        int res = 0;
        if (!(c_bg_spi_read = _loadFunction("c_bg_spi_read", &res)))
            return res;
    }
    return c_bg_spi_read(beagle, status, time_sop, time_duration, time_dataoffset, mosi_max_bytes, data_mosi, miso_max_bytes, data_miso);
}


static int (*c_bg_spi_read_data_timing) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u08 *, int, u08 *, int, u32 *) = 0;
int bg_spi_read_data_timing (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    mosi_max_bytes,
    u08 *  data_mosi,
    int    miso_max_bytes,
    u08 *  data_miso,
    int    max_timing,
    u32 *  data_timing
)
{
    if (c_bg_spi_read_data_timing == 0) {
        int res = 0;
        if (!(c_bg_spi_read_data_timing = _loadFunction("c_bg_spi_read_data_timing", &res)))
            return res;
    }
    return c_bg_spi_read_data_timing(beagle, status, time_sop, time_duration, time_dataoffset, mosi_max_bytes, data_mosi, miso_max_bytes, data_miso, max_timing, data_timing);
}


static int (*c_bg_spi_read_bit_timing) (Beagle, u32 *, u64 *, u64 *, u32 *, int, u08 *, int, u08 *, int, u32 *) = 0;
int bg_spi_read_bit_timing (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    mosi_max_bytes,
    u08 *  data_mosi,
    int    miso_max_bytes,
    u08 *  data_miso,
    int    max_timing,
    u32 *  bit_timing
)
{
    if (c_bg_spi_read_bit_timing == 0) {
        int res = 0;
        if (!(c_bg_spi_read_bit_timing = _loadFunction("c_bg_spi_read_bit_timing", &res)))
            return res;
    }
    return c_bg_spi_read_bit_timing(beagle, status, time_sop, time_duration, time_dataoffset, mosi_max_bytes, data_mosi, miso_max_bytes, data_miso, max_timing, bit_timing);
}


static int (*c_bg_usb12_read) (Beagle, u32 *, u32 *, u64 *, u64 *, u32 *, int, u08 *) = 0;
int bg_usb12_read (
    Beagle beagle,
    u32 *  status,
    u32 *  events,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u08 *  packet
)
{
    if (c_bg_usb12_read == 0) {
        int res = 0;
        if (!(c_bg_usb12_read = _loadFunction("c_bg_usb12_read", &res)))
            return res;
    }
    return c_bg_usb12_read(beagle, status, events, time_sop, time_duration, time_dataoffset, max_bytes, packet);
}


static int (*c_bg_usb12_read_data_timing) (Beagle, u32 *, u32 *, u64 *, u64 *, u32 *, int, u08 *, int, u32 *) = 0;
int bg_usb12_read_data_timing (
    Beagle beagle,
    u32 *  status,
    u32 *  events,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u08 *  packet,
    int    max_timing,
    u32 *  data_timing
)
{
    if (c_bg_usb12_read_data_timing == 0) {
        int res = 0;
        if (!(c_bg_usb12_read_data_timing = _loadFunction("c_bg_usb12_read_data_timing", &res)))
            return res;
    }
    return c_bg_usb12_read_data_timing(beagle, status, events, time_sop, time_duration, time_dataoffset, max_bytes, packet, max_timing, data_timing);
}


static int (*c_bg_usb12_read_bit_timing) (Beagle, u32 *, u32 *, u64 *, u64 *, u32 *, int, u08 *, int, u32 *) = 0;
int bg_usb12_read_bit_timing (
    Beagle beagle,
    u32 *  status,
    u32 *  events,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u08 *  packet,
    int    max_timing,
    u32 *  bit_timing
)
{
    if (c_bg_usb12_read_bit_timing == 0) {
        int res = 0;
        if (!(c_bg_usb12_read_bit_timing = _loadFunction("c_bg_usb12_read_bit_timing", &res)))
            return res;
    }
    return c_bg_usb12_read_bit_timing(beagle, status, events, time_sop, time_duration, time_dataoffset, max_bytes, packet, max_timing, bit_timing);
}


static int (*c_bg_usb480_capture_configure) (Beagle, BeagleUsb480CaptureMode, BeagleUsb2TargetSpeed) = 0;
int bg_usb480_capture_configure (
    Beagle                  beagle,
    BeagleUsb480CaptureMode capture_mode,
    BeagleUsb2TargetSpeed   target_speed
)
{
    if (c_bg_usb480_capture_configure == 0) {
        int res = 0;
        if (!(c_bg_usb480_capture_configure = _loadFunction("c_bg_usb480_capture_configure", &res)))
            return res;
    }
    return c_bg_usb480_capture_configure(beagle, capture_mode, target_speed);
}


static int (*c_bg_usb480_digital_out_config) (Beagle, u08, u08) = 0;
int bg_usb480_digital_out_config (
    Beagle beagle,
    u08    out_enable_mask,
    u08    out_polarity_mask
)
{
    if (c_bg_usb480_digital_out_config == 0) {
        int res = 0;
        if (!(c_bg_usb480_digital_out_config = _loadFunction("c_bg_usb480_digital_out_config", &res)))
            return res;
    }
    return c_bg_usb480_digital_out_config(beagle, out_enable_mask, out_polarity_mask);
}


static int (*c_bg_usb480_digital_out_match) (Beagle, BeagleUsb2DigitalOutMatchPins, const BeagleUsb2PacketMatch *, const BeagleUsb2DataMatch *) = 0;
int bg_usb480_digital_out_match (
    Beagle                        beagle,
    BeagleUsb2DigitalOutMatchPins pin_num,
    const BeagleUsb2PacketMatch * packet_match,
    const BeagleUsb2DataMatch *   data_match
)
{
    if (c_bg_usb480_digital_out_match == 0) {
        int res = 0;
        if (!(c_bg_usb480_digital_out_match = _loadFunction("c_bg_usb480_digital_out_match", &res)))
            return res;
    }
    return c_bg_usb480_digital_out_match(beagle, pin_num, packet_match, data_match);
}


static int (*c_bg_usb480_digital_in_config) (Beagle, u08) = 0;
int bg_usb480_digital_in_config (
    Beagle beagle,
    u08    in_enable_mask
)
{
    if (c_bg_usb480_digital_in_config == 0) {
        int res = 0;
        if (!(c_bg_usb480_digital_in_config = _loadFunction("c_bg_usb480_digital_in_config", &res)))
            return res;
    }
    return c_bg_usb480_digital_in_config(beagle, in_enable_mask);
}


static int (*c_bg_usb480_hw_filter_config) (Beagle, u08) = 0;
int bg_usb480_hw_filter_config (
    Beagle beagle,
    u08    filter_enable_mask
)
{
    if (c_bg_usb480_hw_filter_config == 0) {
        int res = 0;
        if (!(c_bg_usb480_hw_filter_config = _loadFunction("c_bg_usb480_hw_filter_config", &res)))
            return res;
    }
    return c_bg_usb480_hw_filter_config(beagle, filter_enable_mask);
}


static int (*c_bg_usb480_hw_buffer_stats) (Beagle, u32 *, u32 *, u08 *) = 0;
int bg_usb480_hw_buffer_stats (
    Beagle beagle,
    u32 *  buffer_size,
    u32 *  buffer_usage,
    u08 *  buffer_full
)
{
    if (c_bg_usb480_hw_buffer_stats == 0) {
        int res = 0;
        if (!(c_bg_usb480_hw_buffer_stats = _loadFunction("c_bg_usb480_hw_buffer_stats", &res)))
            return res;
    }
    return c_bg_usb480_hw_buffer_stats(beagle, buffer_size, buffer_usage, buffer_full);
}


static int (*c_bg_usb480_read) (Beagle, u32 *, u32 *, u64 *, u64 *, u32 *, int, u08 *) = 0;
int bg_usb480_read (
    Beagle beagle,
    u32 *  status,
    u32 *  events,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    int    max_bytes,
    u08 *  packet
)
{
    if (c_bg_usb480_read == 0) {
        int res = 0;
        if (!(c_bg_usb480_read = _loadFunction("c_bg_usb480_read", &res)))
            return res;
    }
    return c_bg_usb480_read(beagle, status, events, time_sop, time_duration, time_dataoffset, max_bytes, packet);
}


static int (*c_bg_usb480_reconstruct_timing) (BeagleUsb2TargetSpeed, int, const u08 *, int, u32 *) = 0;
int bg_usb480_reconstruct_timing (
    BeagleUsb2TargetSpeed speed,
    int                   num_bytes,
    const u08 *           packet,
    int                   max_timing,
    u32 *                 bit_timing
)
{
    if (c_bg_usb480_reconstruct_timing == 0) {
        int res = 0;
        if (!(c_bg_usb480_reconstruct_timing = _loadFunction("c_bg_usb480_reconstruct_timing", &res)))
            return res;
    }
    return c_bg_usb480_reconstruct_timing(speed, num_bytes, packet, max_timing, bit_timing);
}


static int (*c_bg_usb5000_license_read) (Beagle, int, u08 *) = 0;
int bg_usb5000_license_read (
    Beagle beagle,
    int    length,
    u08 *  license_key
)
{
    if (c_bg_usb5000_license_read == 0) {
        int res = 0;
        if (!(c_bg_usb5000_license_read = _loadFunction("c_bg_usb5000_license_read", &res)))
            return res;
    }
    return c_bg_usb5000_license_read(beagle, length, license_key);
}


static int (*c_bg_usb5000_license_write) (Beagle, int, const u08 *) = 0;
int bg_usb5000_license_write (
    Beagle      beagle,
    int         length,
    const u08 * license_key
)
{
    if (c_bg_usb5000_license_write == 0) {
        int res = 0;
        if (!(c_bg_usb5000_license_write = _loadFunction("c_bg_usb5000_license_write", &res)))
            return res;
    }
    return c_bg_usb5000_license_write(beagle, length, license_key);
}


static int (*c_bg_usb5000_features) (Beagle) = 0;
int bg_usb5000_features (
    Beagle beagle
)
{
    if (c_bg_usb5000_features == 0) {
        int res = 0;
        if (!(c_bg_usb5000_features = _loadFunction("c_bg_usb5000_features", &res)))
            return res;
    }
    return c_bg_usb5000_features(beagle);
}


static int (*c_bg_usb5000_configure) (Beagle, u08, BeagleUsb5000TriggerMode) = 0;
int bg_usb5000_configure (
    Beagle                   beagle,
    u08                      cap_mask,
    BeagleUsb5000TriggerMode trigger_mode
)
{
    if (c_bg_usb5000_configure == 0) {
        int res = 0;
        if (!(c_bg_usb5000_configure = _loadFunction("c_bg_usb5000_configure", &res)))
            return res;
    }
    return c_bg_usb5000_configure(beagle, cap_mask, trigger_mode);
}


static int (*c_bg_usb5000_target_power) (Beagle, BeagleUsbTargetPower) = 0;
int bg_usb5000_target_power (
    Beagle               beagle,
    BeagleUsbTargetPower power_flag
)
{
    if (c_bg_usb5000_target_power == 0) {
        int res = 0;
        if (!(c_bg_usb5000_target_power = _loadFunction("c_bg_usb5000_target_power", &res)))
            return res;
    }
    return c_bg_usb5000_target_power(beagle, power_flag);
}


static int (*c_bg_usb5000_usb2_hw_filter_config) (Beagle, u08) = 0;
int bg_usb5000_usb2_hw_filter_config (
    Beagle beagle,
    u08    filter_enable_mask
)
{
    if (c_bg_usb5000_usb2_hw_filter_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_hw_filter_config = _loadFunction("c_bg_usb5000_usb2_hw_filter_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_hw_filter_config(beagle, filter_enable_mask);
}


static int (*c_bg_usb5000_usb2_digital_in_config) (Beagle, u08) = 0;
int bg_usb5000_usb2_digital_in_config (
    Beagle beagle,
    u08    in_enable_mask
)
{
    if (c_bg_usb5000_usb2_digital_in_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_digital_in_config = _loadFunction("c_bg_usb5000_usb2_digital_in_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_digital_in_config(beagle, in_enable_mask);
}


static int (*c_bg_usb5000_usb2_digital_out_config) (Beagle, u08, u08) = 0;
int bg_usb5000_usb2_digital_out_config (
    Beagle beagle,
    u08    out_enable_mask,
    u08    out_polarity_mask
)
{
    if (c_bg_usb5000_usb2_digital_out_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_digital_out_config = _loadFunction("c_bg_usb5000_usb2_digital_out_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_digital_out_config(beagle, out_enable_mask, out_polarity_mask);
}


static int (*c_bg_usb5000_usb2_digital_out_match) (Beagle, BeagleUsb2DigitalOutMatchPins, const BeagleUsb2PacketMatch *, const BeagleUsb2DataMatch *) = 0;
int bg_usb5000_usb2_digital_out_match (
    Beagle                        beagle,
    BeagleUsb2DigitalOutMatchPins pin_num,
    const BeagleUsb2PacketMatch * packet_match,
    const BeagleUsb2DataMatch *   data_match
)
{
    if (c_bg_usb5000_usb2_digital_out_match == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_digital_out_match = _loadFunction("c_bg_usb5000_usb2_digital_out_match", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_digital_out_match(beagle, pin_num, packet_match, data_match);
}


static int (*c_bg_usb5000_usb2_target_configure) (Beagle, BeagleUsb2TargetSpeed) = 0;
int bg_usb5000_usb2_target_configure (
    Beagle                beagle,
    BeagleUsb2TargetSpeed target_speed
)
{
    if (c_bg_usb5000_usb2_target_configure == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_target_configure = _loadFunction("c_bg_usb5000_usb2_target_configure", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_target_configure(beagle, target_speed);
}


static int (*c_bg_usb5000_usb2_simple_match_config) (Beagle, u08, u08, u08) = 0;
int bg_usb5000_usb2_simple_match_config (
    Beagle beagle,
    u08    dig_in_pin_pos_edge_mask,
    u08    dig_in_pin_neg_edge_mask,
    u08    dig_out_match_pin_mask
)
{
    if (c_bg_usb5000_usb2_simple_match_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_simple_match_config = _loadFunction("c_bg_usb5000_usb2_simple_match_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_simple_match_config(beagle, dig_in_pin_pos_edge_mask, dig_in_pin_neg_edge_mask, dig_out_match_pin_mask);
}


static int (*c_bg_usb5000_usb2_complex_match_enable) (Beagle) = 0;
int bg_usb5000_usb2_complex_match_enable (
    Beagle beagle
)
{
    if (c_bg_usb5000_usb2_complex_match_enable == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_complex_match_enable = _loadFunction("c_bg_usb5000_usb2_complex_match_enable", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_complex_match_enable(beagle);
}


static int (*c_bg_usb5000_usb2_complex_match_disable) (Beagle) = 0;
int bg_usb5000_usb2_complex_match_disable (
    Beagle beagle
)
{
    if (c_bg_usb5000_usb2_complex_match_disable == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_complex_match_disable = _loadFunction("c_bg_usb5000_usb2_complex_match_disable", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_complex_match_disable(beagle);
}


static int (*c_bg_usb5000_usb2_complex_match_config) (Beagle, u08, u08, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *, const BeagleUsb5000Usb2ComplexMatchState *) = 0;
int bg_usb5000_usb2_complex_match_config (
    Beagle                                     beagle,
    u08                                        validate,
    u08                                        digout,
    const BeagleUsb5000Usb2ComplexMatchState * state_0,
    const BeagleUsb5000Usb2ComplexMatchState * state_1,
    const BeagleUsb5000Usb2ComplexMatchState * state_2,
    const BeagleUsb5000Usb2ComplexMatchState * state_3,
    const BeagleUsb5000Usb2ComplexMatchState * state_4,
    const BeagleUsb5000Usb2ComplexMatchState * state_5,
    const BeagleUsb5000Usb2ComplexMatchState * state_6,
    const BeagleUsb5000Usb2ComplexMatchState * state_7
)
{
    if (c_bg_usb5000_usb2_complex_match_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_complex_match_config = _loadFunction("c_bg_usb5000_usb2_complex_match_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_complex_match_config(beagle, validate, digout, state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7);
}


static int (*c_bg_usb5000_usb2_complex_match_config_single) (Beagle, u08, u08, const BeagleUsb5000Usb2ComplexMatchState *) = 0;
int bg_usb5000_usb2_complex_match_config_single (
    Beagle                                     beagle,
    u08                                        validate,
    u08                                        digout,
    const BeagleUsb5000Usb2ComplexMatchState * state
)
{
    if (c_bg_usb5000_usb2_complex_match_config_single == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_complex_match_config_single = _loadFunction("c_bg_usb5000_usb2_complex_match_config_single", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_complex_match_config_single(beagle, validate, digout, state);
}


static int (*c_bg_usb5000_usb2_extout_config) (Beagle, BeagleUsb5000ExtoutType) = 0;
int bg_usb5000_usb2_extout_config (
    Beagle                  beagle,
    BeagleUsb5000ExtoutType extout_modulation
)
{
    if (c_bg_usb5000_usb2_extout_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_extout_config = _loadFunction("c_bg_usb5000_usb2_extout_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_extout_config(beagle, extout_modulation);
}


static int (*c_bg_usb5000_usb2_memory_test) (Beagle) = 0;
int bg_usb5000_usb2_memory_test (
    Beagle beagle
)
{
    if (c_bg_usb5000_usb2_memory_test == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_memory_test = _loadFunction("c_bg_usb5000_usb2_memory_test", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_memory_test(beagle);
}


static int (*c_bg_usb5000_usb2_capture_config) (Beagle, u32, u32) = 0;
int bg_usb5000_usb2_capture_config (
    Beagle beagle,
    u32    pretrig_kb,
    u32    capture_kb
)
{
    if (c_bg_usb5000_usb2_capture_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_capture_config = _loadFunction("c_bg_usb5000_usb2_capture_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_capture_config(beagle, pretrig_kb, capture_kb);
}


static int (*c_bg_usb5000_usb2_capture_config_query) (Beagle, u32 *, u32 *) = 0;
int bg_usb5000_usb2_capture_config_query (
    Beagle beagle,
    u32 *  pretrig_kb,
    u32 *  capture_kb
)
{
    if (c_bg_usb5000_usb2_capture_config_query == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_capture_config_query = _loadFunction("c_bg_usb5000_usb2_capture_config_query", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_capture_config_query(beagle, pretrig_kb, capture_kb);
}


static int (*c_bg_usb5000_usb3_phy_config) (Beagle, u08, u08) = 0;
int bg_usb5000_usb3_phy_config (
    Beagle beagle,
    u08    tx,
    u08    rx
)
{
    if (c_bg_usb5000_usb3_phy_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_phy_config = _loadFunction("c_bg_usb5000_usb3_phy_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_phy_config(beagle, tx, rx);
}


static int (*c_bg_usb5000_usb3_memory_test) (Beagle, BeagleUsb3MemoryTestType) = 0;
int bg_usb5000_usb3_memory_test (
    Beagle                   beagle,
    BeagleUsb3MemoryTestType test
)
{
    if (c_bg_usb5000_usb3_memory_test == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_memory_test = _loadFunction("c_bg_usb5000_usb3_memory_test", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_memory_test(beagle, test);
}


static int (*c_bg_usb5000_usb3_capture_config) (Beagle, u32, u32) = 0;
int bg_usb5000_usb3_capture_config (
    Beagle beagle,
    u32    pretrig_kb,
    u32    capture_kb
)
{
    if (c_bg_usb5000_usb3_capture_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_capture_config = _loadFunction("c_bg_usb5000_usb3_capture_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_capture_config(beagle, pretrig_kb, capture_kb);
}


static int (*c_bg_usb5000_usb3_capture_config_query) (Beagle, u32 *, u32 *) = 0;
int bg_usb5000_usb3_capture_config_query (
    Beagle beagle,
    u32 *  pretrig_kb,
    u32 *  capture_kb
)
{
    if (c_bg_usb5000_usb3_capture_config_query == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_capture_config_query = _loadFunction("c_bg_usb5000_usb3_capture_config_query", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_capture_config_query(beagle, pretrig_kb, capture_kb);
}


static int (*c_bg_usb5000_usb3_capture_status) (Beagle, u32, BeagleUsb5000CaptureStatus *, u32 *, u32 *, u32 *, u32 *) = 0;
int bg_usb5000_usb3_capture_status (
    Beagle                       beagle,
    u32                          timeout_ms,
    BeagleUsb5000CaptureStatus * status,
    u32 *                        pretrig_remaining_kb,
    u32 *                        pretrig_total_kb,
    u32 *                        capture_remaining_kb,
    u32 *                        capture_total_kb
)
{
    if (c_bg_usb5000_usb3_capture_status == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_capture_status = _loadFunction("c_bg_usb5000_usb3_capture_status", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_capture_status(beagle, timeout_ms, status, pretrig_remaining_kb, pretrig_total_kb, capture_remaining_kb, capture_total_kb);
}


static int (*c_bg_usb5000_usb2_capture_status) (Beagle, u32, BeagleUsb5000CaptureStatus *, u32 *, u32 *, u32 *, u32 *) = 0;
int bg_usb5000_usb2_capture_status (
    Beagle                       beagle,
    u32                          timeout_ms,
    BeagleUsb5000CaptureStatus * status,
    u32 *                        pretrig_remaining_kb,
    u32 *                        pretrig_total_kb,
    u32 *                        capture_remaining_kb,
    u32 *                        capture_total_kb
)
{
    if (c_bg_usb5000_usb2_capture_status == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb2_capture_status = _loadFunction("c_bg_usb5000_usb2_capture_status", &res)))
            return res;
    }
    return c_bg_usb5000_usb2_capture_status(beagle, timeout_ms, status, pretrig_remaining_kb, pretrig_total_kb, capture_remaining_kb, capture_total_kb);
}


static int (*c_bg_usb5000_capture_abort) (Beagle) = 0;
int bg_usb5000_capture_abort (
    Beagle beagle
)
{
    if (c_bg_usb5000_capture_abort == 0) {
        int res = 0;
        if (!(c_bg_usb5000_capture_abort = _loadFunction("c_bg_usb5000_capture_abort", &res)))
            return res;
    }
    return c_bg_usb5000_capture_abort(beagle);
}


static int (*c_bg_usb5000_capture_trigger) (Beagle) = 0;
int bg_usb5000_capture_trigger (
    Beagle beagle
)
{
    if (c_bg_usb5000_capture_trigger == 0) {
        int res = 0;
        if (!(c_bg_usb5000_capture_trigger = _loadFunction("c_bg_usb5000_capture_trigger", &res)))
            return res;
    }
    return c_bg_usb5000_capture_trigger(beagle);
}


static int (*c_bg_usb5000_usb3_truncation_mode) (Beagle, u08, u08) = 0;
int bg_usb5000_usb3_truncation_mode (
    Beagle beagle,
    u08    tx_truncation_mode,
    u08    rx_truncation_mode
)
{
    if (c_bg_usb5000_usb3_truncation_mode == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_truncation_mode = _loadFunction("c_bg_usb5000_usb3_truncation_mode", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_truncation_mode(beagle, tx_truncation_mode, rx_truncation_mode);
}


static int (*c_bg_usb5000_usb3_simple_match_config) (Beagle, u32, u32, BeagleUsb5000Usb3ExtoutMode, u08, BeagleUsb5000Usb3IPSType, BeagleUsb5000Usb3IPSType) = 0;
int bg_usb5000_usb3_simple_match_config (
    Beagle                      beagle,
    u32                         trigger_mask,
    u32                         extout_mask,
    BeagleUsb5000Usb3ExtoutMode extout_mode,
    u08                         extin_edge_mask,
    BeagleUsb5000Usb3IPSType    tx_ips_type,
    BeagleUsb5000Usb3IPSType    rx_ips_type
)
{
    if (c_bg_usb5000_usb3_simple_match_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_simple_match_config = _loadFunction("c_bg_usb5000_usb3_simple_match_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_simple_match_config(beagle, trigger_mask, extout_mask, extout_mode, extin_edge_mask, tx_ips_type, rx_ips_type);
}


static int (*c_bg_usb5000_usb3_complex_match_enable) (Beagle) = 0;
int bg_usb5000_usb3_complex_match_enable (
    Beagle beagle
)
{
    if (c_bg_usb5000_usb3_complex_match_enable == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_complex_match_enable = _loadFunction("c_bg_usb5000_usb3_complex_match_enable", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_complex_match_enable(beagle);
}


static int (*c_bg_usb5000_usb3_complex_match_disable) (Beagle) = 0;
int bg_usb5000_usb3_complex_match_disable (
    Beagle beagle
)
{
    if (c_bg_usb5000_usb3_complex_match_disable == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_complex_match_disable = _loadFunction("c_bg_usb5000_usb3_complex_match_disable", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_complex_match_disable(beagle);
}


static int (*c_bg_usb5000_usb3_complex_match_config) (Beagle, u08, u08, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *, const BeagleUsb5000Usb3ComplexMatchState *) = 0;
int bg_usb5000_usb3_complex_match_config (
    Beagle                                     beagle,
    u08                                        validate,
    u08                                        extout,
    const BeagleUsb5000Usb3ComplexMatchState * state_0,
    const BeagleUsb5000Usb3ComplexMatchState * state_1,
    const BeagleUsb5000Usb3ComplexMatchState * state_2,
    const BeagleUsb5000Usb3ComplexMatchState * state_3,
    const BeagleUsb5000Usb3ComplexMatchState * state_4,
    const BeagleUsb5000Usb3ComplexMatchState * state_5,
    const BeagleUsb5000Usb3ComplexMatchState * state_6,
    const BeagleUsb5000Usb3ComplexMatchState * state_7
)
{
    if (c_bg_usb5000_usb3_complex_match_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_complex_match_config = _loadFunction("c_bg_usb5000_usb3_complex_match_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_complex_match_config(beagle, validate, extout, state_0, state_1, state_2, state_3, state_4, state_5, state_6, state_7);
}


static int (*c_bg_usb5000_usb3_complex_match_config_single) (Beagle, u08, u08, const BeagleUsb5000Usb3ComplexMatchState *) = 0;
int bg_usb5000_usb3_complex_match_config_single (
    Beagle                                     beagle,
    u08                                        validate,
    u08                                        extout,
    const BeagleUsb5000Usb3ComplexMatchState * state
)
{
    if (c_bg_usb5000_usb3_complex_match_config_single == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_complex_match_config_single = _loadFunction("c_bg_usb5000_usb3_complex_match_config_single", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_complex_match_config_single(beagle, validate, extout, state);
}


static int (*c_bg_usb5000_usb3_ext_io_config) (Beagle, u08, BeagleUsb5000ExtoutType) = 0;
int bg_usb5000_usb3_ext_io_config (
    Beagle                  beagle,
    u08                     extin_enable,
    BeagleUsb5000ExtoutType extout_modulation
)
{
    if (c_bg_usb5000_usb3_ext_io_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_ext_io_config = _loadFunction("c_bg_usb5000_usb3_ext_io_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_ext_io_config(beagle, extin_enable, extout_modulation);
}


static int (*c_bg_usb5000_usb3_link_config) (Beagle, const BeagleUsb5000Usb3Channel *, const BeagleUsb5000Usb3Channel *) = 0;
int bg_usb5000_usb3_link_config (
    Beagle                           beagle,
    const BeagleUsb5000Usb3Channel * tx,
    const BeagleUsb5000Usb3Channel * rx
)
{
    if (c_bg_usb5000_usb3_link_config == 0) {
        int res = 0;
        if (!(c_bg_usb5000_usb3_link_config = _loadFunction("c_bg_usb5000_usb3_link_config", &res)))
            return res;
    }
    return c_bg_usb5000_usb3_link_config(beagle, tx, rx);
}


static int (*c_bg_usb5000_read) (Beagle, u32 *, u32 *, u64 *, u64 *, u32 *, BeagleUsb5000Source *, int, u08 *, int, u08 *) = 0;
int bg_usb5000_read (
    Beagle                beagle,
    u32 *                 status,
    u32 *                 events,
    u64 *                 time_sop,
    u64 *                 time_duration,
    u32 *                 time_dataoffset,
    BeagleUsb5000Source * source,
    int                   max_bytes,
    u08 *                 packet,
    int                   max_k_bytes,
    u08 *                 k_data
)
{
    if (c_bg_usb5000_read == 0) {
        int res = 0;
        if (!(c_bg_usb5000_read = _loadFunction("c_bg_usb5000_read", &res)))
            return res;
    }
    return c_bg_usb5000_read(beagle, status, events, time_sop, time_duration, time_dataoffset, source, max_bytes, packet, max_k_bytes, k_data);
}


static int (*c_bg_mdio_read) (Beagle, u32 *, u64 *, u64 *, u32 *, u32 *) = 0;
int bg_mdio_read (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    u32 *  data_in
)
{
    if (c_bg_mdio_read == 0) {
        int res = 0;
        if (!(c_bg_mdio_read = _loadFunction("c_bg_mdio_read", &res)))
            return res;
    }
    return c_bg_mdio_read(beagle, status, time_sop, time_duration, time_dataoffset, data_in);
}


static int (*c_bg_mdio_read_bit_timing) (Beagle, u32 *, u64 *, u64 *, u32 *, u32 *, int, u32 *) = 0;
int bg_mdio_read_bit_timing (
    Beagle beagle,
    u32 *  status,
    u64 *  time_sop,
    u64 *  time_duration,
    u32 *  time_dataoffset,
    u32 *  data_in,
    int    max_timing,
    u32 *  bit_timing
)
{
    if (c_bg_mdio_read_bit_timing == 0) {
        int res = 0;
        if (!(c_bg_mdio_read_bit_timing = _loadFunction("c_bg_mdio_read_bit_timing", &res)))
            return res;
    }
    return c_bg_mdio_read_bit_timing(beagle, status, time_sop, time_duration, time_dataoffset, data_in, max_timing, bit_timing);
}


static int (*c_bg_mdio_parse) (u32, u08 *, u08 *, u08 *, u08 *, u16 *) = 0;
int bg_mdio_parse (
    u32   packet,
    u08 * clause,
    u08 * opcode,
    u08 * addr1,
    u08 * addr2,
    u16 * data
)
{
    if (c_bg_mdio_parse == 0) {
        int res = 0;
        if (!(c_bg_mdio_parse = _loadFunction("c_bg_mdio_parse", &res)))
            return res;
    }
    return c_bg_mdio_parse(packet, clause, opcode, addr1, addr2, data);
}


