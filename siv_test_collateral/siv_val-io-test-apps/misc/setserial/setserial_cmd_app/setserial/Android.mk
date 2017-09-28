LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_SRC_FILES :=  setserial.c

LOCAL_MODULE := setserial

LOCAL_SHARED__LIBRARIES := libc libcutils

LOCAL_C_INCLUDES := $(KERNEL_HEADERS) 

LOCAL_CFLAGS := -O2 -g -W -Wall

LOCAL_MODULE_TAGS := optional

include $(BUILD_EXECUTABLE)
