device=$1
partition_number=$2
partition1=$3
partition2=$4
partition3=$5
partition4=$6
partition5=$7

if [ $partition_number -eq 5 ]; then
echo "5 partitions will be created"
fdisk $device <<! > /dev/null
o
n
p
1

+${partition1}M
n
p
2

+${partition2}M
n
p
3

+${partition3}M
n
e


n

+${partition4}M
n

+${partition5}M
n


w
q
!
exit 0
elif [ $partition_number -eq 2 ]; then
echo "2 partition will be created"

fdisk $device <<! > /dev/null
o
n
p
1

+${partition1}M
n
p
2

+${partition2}M
w
q
!
elif [ $partition_number -eq 1 ]; then
echo "1 partition will be created"

fdisk $device <<! > /dev/null
o
n
p
1


w
q
!
exit 0
else
echo "The script only supports 2 or 5 partitions"
fi
