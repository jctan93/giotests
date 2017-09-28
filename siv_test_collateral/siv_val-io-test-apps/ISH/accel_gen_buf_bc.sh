# -------------- modprobe ISH driver ----------------------------
# !/bin/bash

# sh accel_name_mod.sh

# sleep 1s

# # device 0
# cd /iiotest
# ./generic_buffer_0 -n accel_3d -c 3 &

# sleep 2s

# name0=`cat /sys/bus/iio/devices/iio:device0/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name0 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x0=`cat /sys/bus/iio/devices/iio:device0/in_accel_x_raw`
# y0=`cat /sys/bus/iio/devices/iio:device0/in_accel_y_raw`
# z0=`cat /sys/bus/iio/devices/iio:device0/in_accel_z_raw`

# echo "x0 = $x0"
# echo "y0 = $y0"
# echo "z0 = $z0"

# x_check0=$(echo "($x0)" | bc)
# y_check0=$(echo "($y0)" | bc)
# z_check0=$(echo "($z0)" | bc)

# # To make sure the x,y,z value received are not all zero.	
# zero=0;
# null= ;

# if [[ $x_check0 != "$zero" && $x_check0 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check0 != "$zero" && $y_check0 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check0 != "$zero" && $z_check0 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi

# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_1 -n accel_3d -c 3 &

# sleep 2s

# name1=`cat /sys/bus/iio/devices/iio:device1/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name1 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x1=`cat /sys/bus/iio/devices/iio:device1/in_accel_x_raw`
# y1=`cat /sys/bus/iio/devices/iio:device1/in_accel_y_raw`
# z1=`cat /sys/bus/iio/devices/iio:device1/in_accel_z_raw`

# echo "x1 = $x1"
# echo "y1 = $y1"
# echo "z1 = $z1"

# x_check1=$(echo "($x1)" | bc)
# y_check1=$(echo "($y1)" | bc)
# z_check1=$(echo "($z1)" | bc)

# # To make sure the x,y,z value received are not all zero.	
# zero=0;
# null= ;

# if [[ $x_check1 != "$zero" && $x_check1 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check1 != "$zero" && $y_check1 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check1 != "$zero" && $z_check1 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""

# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_2 -n accel_3d -c 3 &

# sleep 2s

# name2=`cat /sys/bus/iio/devices/iio:device2/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name2 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/


# x2=`cat /sys/bus/iio/devices/iio:device2/in_accel_x_raw`
# y2=`cat /sys/bus/iio/devices/iio:device2/in_accel_y_raw`
# z2=`cat /sys/bus/iio/devices/iio:device2/in_accel_z_raw`

# echo "x2 = $x2"
# echo "y2 = $y2"
# echo "z2 = $z2"

# x_check2=$(echo "($x2)" | bc)
# y_check2=$(echo "($y2)" | bc)
# z_check2=$(echo "($z2)" | bc)

# zero=0;
# null= ;

# if [[ $x_check2 != "$zero" && $x_check2 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check2 != "$zero" && $y_check2 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check2 != "$zero" && $z_check2 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_3 -n accel_3d -c 3 &

# sleep 2s

# name3=`cat /sys/bus/iio/devices/iio:device3/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name3 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x3=`cat /sys/bus/iio/devices/iio:device3/in_accel_x_raw`
# y3=`cat /sys/bus/iio/devices/iio:device3/in_accel_y_raw`
# z3=`cat /sys/bus/iio/devices/iio:device3/in_accel_z_raw`

# echo "x3 = $x3"
# echo "y3 = $y3"
# echo "z3 = $z3"

# x_check3=$(echo "($x3)" | bc)
# y_check3=$(echo "($y3)" | bc)
# z_check3=$(echo "($z3)" | bc)

# zero=0;
# null= ;

# if [[ $x_check3 != "$zero" && $x_check3 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check3 != "$zero" && $y_check3 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check3 != "$zero" && $z_check3 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_4 -n accel_3d -c 3 &

# sleep 2s

# name4=`cat /sys/bus/iio/devices/iio:device4/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name4 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x4=`cat /sys/bus/iio/devices/iio:device4/in_accel_x_raw`
# y4=`cat /sys/bus/iio/devices/iio:device4/in_accel_y_raw`
# z4=`cat /sys/bus/iio/devices/iio:device4/in_accel_z_raw`

# echo "x4 = $x4"
# echo "y4 = $y4"
# echo "z4 = $z4"

# x_check4=$(echo "($x4)" | bc)
# y_check4=$(echo "($y4)" | bc)
# z_check4=$(echo "($z4)" | bc)

# zero=0;
# null= ;

# if [[ $x_check4 != "$zero" && $x_check4 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check4 != "$zero" && $y_check4 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check4 != "$zero" && $z_check4 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_5 -n accel_3d -c 3 &

# sleep 2s

# name5=`cat /sys/bus/iio/devices/iio:device5/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name5 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x5=`cat /sys/bus/iio/devices/iio:device5/in_accel_x_raw`
# y5=`cat /sys/bus/iio/devices/iio:device5/in_accel_y_raw`
# z5=`cat /sys/bus/iio/devices/iio:device5/in_accel_z_raw`

# echo "x5 = $x5"
# echo "y5 = $y5"
# echo "z5 = $z5"

# x_check5=$(echo "($x5)" | bc)
# y_check5=$(echo "($y5)" | bc)
# z_check5=$(echo "($z5)" | bc)
# zero=0;
# null= ;

# if [[ $x_check5 != "$zero" && $x_check5 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check5 != "$zero" && $y_check5 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check5 != "$zero" && $z_check5 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_6 -n accel_3d -c 3 &

# sleep 2s

# name6=`cat /sys/bus/iio/devices/iio:device6/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name6 ]]
# then 
# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x6=`cat /sys/bus/iio/devices/iio:device6/in_accel_x_raw`
# y6=`cat /sys/bus/iio/devices/iio:device6/in_accel_y_raw`
# z6=`cat /sys/bus/iio/devices/iio:device6/in_accel_z_raw`

# echo "x6 = $x6"
# echo "y6 = $y6"
# echo "z6 = $z6"

# x_check6=$(echo "($x6)" | bc)
# y_check6=$(echo "($y6)" | bc)
# z_check6=$(echo "($z6)" | bc)
# zero=0;
# null= ;

# if [[ $x_check6 != "$zero" && $x_check6 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check6 != "$zero" && $y_check6 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check6 != "$zero" && $z_check6 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi

# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_7 -n accel_3d -c 3 &

# sleep 2s

# name7=`cat /sys/bus/iio/devices/iio:device7/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name7 ]]
# then

# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x7=`cat /sys/bus/iio/devices/iio:device7/in_accel_x_raw`
# y7=`cat /sys/bus/iio/devices/iio:device7/in_accel_y_raw`
# z7=`cat /sys/bus/iio/devices/iio:device7/in_accel_z_raw`

# echo "x7 = $x7"
# echo "y7 = $y7"
# echo "z7 = $z7"

# x_check7=$(echo "($x7)" | bc)
# y_check7=$(echo "($y7)" | bc)
# z_check7=$(echo "($z7)" | bc)
# zero=0;
# null= ;

# if [[ $x_check7 != "$zero" && $x_check7 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check7 != "$zero" && $y_check7 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check7 != "$zero" && $z_check7 != "$null" ]]; then
# echo "pass"
# fi

# done
# fi

# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_8 -n accel_3d -c 3 &

# sleep 2s

# name8=`cat /sys/bus/iio/devices/iio:device8/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name8 ]]
# then 
# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x8=`cat /sys/bus/iio/devices/iio:device8/in_accel_x_raw`
# y8=`cat /sys/bus/iio/devices/iio:device8/in_accel_y_raw`
# z8=`cat /sys/bus/iio/devices/iio:device8/in_accel_z_raw`

# echo "x8 = $x8"
# echo "y8 = $y8"
# echo "z8 = $z8"

# x_check8=$(echo "($x8)" | bc)
# y_check8=$(echo "($y8)" | bc)
# z_check8=$(echo "($z8)" | bc)
# zero=0;
# null= ;

# if [[ $x_check8 != "$zero" && $x_check8 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check8 != "$zero" && $y_check8 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check8 != "$zero" && $z_check8 != "$null" ]]; then
# echo "pass"
# fi

# done

# fi
# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_9 -n accel_3d -c 3 &

# sleep 2s

# name9=`cat /sys/bus/iio/devices/iio:device9/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name8 ]]
# then
# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x9=`cat /sys/bus/iio/devices/iio:device9/in_accel_x_raw`
# y9=`cat /sys/bus/iio/devices/iio:device9/in_accel_y_raw`
# z9=`cat /sys/bus/iio/devices/iio:device9/in_accel_z_raw`

# echo "x9 = $x9"
# echo "y9 = $y9"
# echo "z9 = $z9"

# x_check9=$(echo "($x9)" | bc)
# y_check9=$(echo "($y9)" | bc)
# z_check9=$(echo "($z9)" | bc)
# zero=0;
# null= ;

# if [[ $x_check9 != "$zero" && $x_check9 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check9 != "$zero" && $y_check9 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check9 != "$zero" && $z_check9 != "$null" ]]; then
# echo "pass"
# fi


# done
# fi

# echo ""
# sleep 5s

# # device 1
# cd /iiotest
# ./generic_buffer_10 -n accel_3d -c 3 &

# sleep 2s

# name10=`cat /sys/bus/iio/devices/iio:device10/name`
# exp_string="accel_3d"
# if [[ "$exp_string" == $name10 ]]
# then
# a=0;

# while [ $a -ne 3 ]
# do
# echo $((a++))

# # to read real-time data
# # cd /sys/bus/iio/devices/iio:device9/
# # cat in_accel_x_raw in_accel_y_raw in_accel_z_raw

# x10=`cat /sys/bus/iio/devices/iio:device10/in_accel_x_raw`
# y10=`cat /sys/bus/iio/devices/iio:device10/in_accel_y_raw`
# z10=`cat /sys/bus/iio/devices/iio:device10/in_accel_z_raw`

# echo "x10 = $x10"
# echo "y10 = $y10"
# echo "z10 = $z10"

# x_check10=$(echo "($x10)" | bc)
# y_check10=$(echo "($y10)" | bc)
# z_check10=$(echo "($z10)" | bc)
# zero=0;
# null= ;

# if [[ $x_check10 != "$zero" && $x_check10 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $y_check10 != "$zero" && $y_check10 != "$null" ]]; then
# echo "pass"
# fi
# if [[ $z_check10 != "$zero" && $z_check10 != "$null" ]]; then
# echo "pass"
# fi

# done
# fi

# echo ""
# sleep 5s


# check
b=0;
# while [ $b -ne 3 ]
# do
# echo $((b++))
sleep 2s
echo "dummy check"

c=0;
while [ $c -ne 11 ]
do
echo $((c++))

nameall=`cat /sys/bus/iio/devices/iio:device$c/name`
exp_string="accel_3d"
if [[ "$exp_string" == $nameall ]]
then 

cx=`cat /sys/bus/iio/devices/iio:device$c/in_accel_x_raw`
cy=`cat /sys/bus/iio/devices/iio:device$c/in_accel_y_raw`
cz=`cat /sys/bus/iio/devices/iio:device$c/in_accel_z_raw`

echo "x$c = ($cx)"
echo "y$c = ($cy)"
echo "z$c = ($cz)"

fi

done

# done

exit

# cx1=`cat /sys/bus/iio/devices/iio:device1/in_accel_x_raw`
# cy1=`cat /sys/bus/iio/devices/iio:device1/in_accel_y_raw`
# cz1=`cat /sys/bus/iio/devices/iio:device1/in_accel_z_raw`

# cx2=`cat /sys/bus/iio/devices/iio:device2/in_accel_x_raw`
# cy2=`cat /sys/bus/iio/devices/iio:device2/in_accel_y_raw`
# cz2=`cat /sys/bus/iio/devices/iio:device2/in_accel_z_raw`

# cx3=`cat /sys/bus/iio/devices/iio:device3/in_accel_x_raw`
# cy3=`cat /sys/bus/iio/devices/iio:device3/in_accel_y_raw`
# cz3=`cat /sys/bus/iio/devices/iio:device3/in_accel_z_raw`

# cx4=`cat /sys/bus/iio/devices/iio:device4/in_accel_x_raw`
# cy4=`cat /sys/bus/iio/devices/iio:device4/in_accel_y_raw`
# cz4=`cat /sys/bus/iio/devices/iio:device4/in_accel_z_raw`

# cx5=`cat /sys/bus/iio/devices/iio:device5/in_accel_x_raw`
# cy5=`cat /sys/bus/iio/devices/iio:device5/in_accel_y_raw`
# cz5=`cat /sys/bus/iio/devices/iio:device5/in_accel_z_raw`

# cx6=`cat /sys/bus/iio/devices/iio:device6/in_accel_x_raw`
# cy6=`cat /sys/bus/iio/devices/iio:device6/in_accel_y_raw`
# cz6=`cat /sys/bus/iio/devices/iio:device6/in_accel_z_raw`

# cx7=`cat /sys/bus/iio/devices/iio:device7/in_accel_x_raw`
# cy7=`cat /sys/bus/iio/devices/iio:device7/in_accel_y_raw`
# cz7=`cat /sys/bus/iio/devices/iio:device7/in_accel_z_raw`

# cx8=`cat /sys/bus/iio/devices/iio:device8/in_accel_x_raw`
# cy8=`cat /sys/bus/iio/devices/iio:device8/in_accel_y_raw`
# cz8=`cat /sys/bus/iio/devices/iio:device8/in_accel_z_raw`

# cx9=`cat /sys/bus/iio/devices/iio:device9/in_accel_x_raw`
# cy9=`cat /sys/bus/iio/devices/iio:device9/in_accel_y_raw`
# cz9=`cat /sys/bus/iio/devices/iio:device9/in_accel_z_raw`

# cx10=`cat /sys/bus/iio/devices/iio:device10/in_accel_x_raw`
# cy10=`cat /sys/bus/iio/devices/iio:device10/in_accel_y_raw`
# cz10=`cat /sys/bus/iio/devices/iio:device10/in_accel_z_raw`

# echo "cx0 = $cx0"
# echo "cy0 = $cy0"
# echo "cz0 = $cz0"
# echo "cx1 = $cx1"
# echo "cy1 = $cy1"
# echo "cz1 = $cz1"
# echo "cx2 = $cx2"
# echo "cy2 = $cy2"
# echo "cz2 = $cz2"
# echo "cx3 = $cx3"
# echo "cy3 = $cy3"
# echo "cz3 = $cz3"
# echo "cx4 = $cx4"
# echo "cy4 = $cy4"
# echo "cz4 = $cz4"
# echo "cx5 = $cx5"
# echo "cy5 = $cy5"
# echo "cz5 = $cz5"
# echo "cx6 = $cx6"
# echo "cy6 = $cy6"
# echo "cz6 = $cz6"
# echo "cx7 = $cx7"
# echo "cy7 = $cy7"
# echo "cz7 = $cz7"
# echo "cx8 = $cx8"
# echo "cy8 = $cy8"
# echo "cz8 = $cz8"
# echo "cx9 = $cx9"
# echo "cy9 = $cy9"
# echo "cz9 = $cz9"
# echo "cx10 = $cx10"
# echo "cy10 = $cy10"
# echo "cz10 = $cz10"

# done
# echo ""

# exit 