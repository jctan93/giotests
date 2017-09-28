import os, re, sys, json, time, argparse, datetime, GenericCommand
from ssh_util import *

script_name = str(sys.argv[0])
usage = "Ethernet Test"
parser = argparse.ArgumentParser(prog=script_name, description=usage)
parser.add_argument('-sut_ip', help='SUT IP')
args = parser.parse_args()

if args.sut_ip is not None:
	sut_ip = args.sut_ip

sut = GenericCommand.GenericCommand()
sut.login(sut_ip)
splitter_colon = re.compile(":")
splitter_tab = re.compile("\t")
splitter_next = re.compile("\n")
	
def check_eth(i):
	data = sut.execute("ethtool enp" + str(i) + "s0 | grep -i 'Link detected'")
	if data != "":
		port_name = "enp" + str(i) + "s0"
	else:
		port_name = "eth" + str(i-1)
		data = sut.execute("ethtool " + port_name + " | grep -i 'Link detected'")
	print "Ethernet Port Used : " + port_name
	if splitter_colon.split(splitter_next.split(splitter_tab.split(data)[1])[0])[1] == " yes":
		sut.execute("ethtool " + port_name + " | grep Speed >> /home/siv_test_collateral/siv_val-io-test-apps/eth/current_eth_log")
		sut.execute("ethtool -s " + port_name + " autoneg on")
		sut.execute("ethtool -s " + port_name + " speed 100 duplex full autoneg off")
		time.sleep(5)
		sut.execute("ethtool " + port_name + " | grep Speed >> /home/siv_test_collateral/siv_val-io-test-apps/eth/current_eth_log")
		sut.execute("ethtool -s " + port_name + " autoneg on")
		time.sleep(5)
		sut.execute("ethtool " + port_name + " | grep Speed >> /home/siv_test_collateral/siv_val-io-test-apps/eth/current_eth_log")
		if sut.execute("diff /home/siv_test_collateral/siv_val-io-test-apps/eth/current_eth_log /home/siv_test_collateral/siv_val-io-test-apps/eth/ori_eth_log") == "":
			print "Ethernet test PASS!"
			sys.exit(0)
		else:
			print "Ethernet test FAIL!"
			sys.exit(1)

def main():
    print "SUT IP : " + sut_ip
    if sut.execute("ls -l /home/siv_test_collateral/siv_val-io-test-apps/eth/ | grep -i current_eth_log"):
        sut.execute("rm -rf /home/siv_test_collateral/siv_val-io-test-apps/eth/current_eth_log")
    for i in range(1,3):
        check_eth(i)

main()