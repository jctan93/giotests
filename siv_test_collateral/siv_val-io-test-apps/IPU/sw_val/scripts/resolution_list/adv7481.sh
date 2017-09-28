#!/bin/bash

declare -a FORMAT_LIST
declare -a RESOLUTION_LIST
declare -a INTERLACED_MODE

FORMAT_LIST=([0]="yuv422" [1]="yuv422" [2]="yuv422" [3]="yuv422" [4]="yuv422" [5]="yuv422" \
             [6]="yuv422" [7]="rgb24"  [8]="rgb24"  [9]="rgb565" [10]="rgb565" \
             [11]="rgb24" [12]="rgb24" [13]="rgb24" [14]="rgb24" [15]="rgb24" \
             [16]="rgb565" [17]="rgb565" [18]="rgb565" [19]="rgb565" [20]="rgb565")

RESOLUTION_LIST=([0]="720x576"   [1]="640x480"  [2]="1920x1080" [3]="1280x720" [4]="720x576" [5]="720x480" \
                 [6]="1920x1080" [7]="1280x720" [8]="1920x1080" [9]="1280x720" [10]="1920x1080" \
                 [11]="640x480" [12]="720x576" [13]="1920x1080" [14]="720x480" [15]="720x576" \
                 [16]="640x480" [17]="720x576" [18]="1920x1080" [19]="720x480" [20]="720x576")

INTERLACED_MODE=([0]="false" [1]="false" [2]="false" [3]="false" [4]="true" [5]="true" \
                 [6]="true"  [7]="false" [8]="false" [9]="false" [10]="false" \
                 [11]="false" [12]="false" [13]="true" [14]="true" [15]="true" \
                 [16]="false" [17]="false" [18]="true" [19]="true" [20]="true")

# Usage for cases insensitive to resolution
DEFAULT_RESULITON_INDEX=2