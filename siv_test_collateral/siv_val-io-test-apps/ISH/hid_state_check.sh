
#!/bin/bash
echo 0 > /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto/enable_sensor
cat /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto/enable_sensor

cd /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto
cat enable_sensor

cd /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto/feature-0-200316
ls
cat *

cd /sys/bus/hid/devices/0044:8086:22D8.0002/HID-SENSOR-2000e1.1.auto/feature-3-200319
ls
cat *

exit


	
