#!/bin/bash

declare -a FORMAT_LIST
declare -a RESOLUTION_LIST
declare -a INTERLACED_MODE

FORMAT_LIST=([0]="raw8" [1]="raw8" [2]="raw8" [3]="raw8")
RESOLUTION_LIST=([0]="720x576" [1]="640x480" [2]="1920x1080" [3]="1280x720")
INTERLACED_MODE=([0]="false" [1]="false" [2]="false" [3]="false")

# Usage for cases insensitive to resolution
DEFAULT_RESULITON_INDEX=2