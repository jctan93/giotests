#!/usr/bin/expect -f

set TEST [lindex $argv 0]
exec /usr/sbin/resourcemgr &
sleep 2

log_file -noappend tpmtest_$TEST.log

spawn /usr/bin/tpmtest

puts "Test $TEST started. =========================="
send_log "Test $TEST started. =========================="

expect "Please select an action:"
send -- "$TEST\n"

expect "Please select an action:"
send -- "0\n"

expect {
    "Tearing down Resource Manager Interface"{
	exp_continue
    }
    "Please select an action:"{
        send -- "Q\n"
    }
    "Please select an action:"{
        send -- "Q\n"
    }
}

puts "Checking test $TEST. ========================"
send_log "Checking test $TEST. ========================"

sleep 2
spawn /home/siv_test_collateral/siv_val-io-test-apps/tpm/TPM2.0_test_script/tpmtest_log_cmp.py -t /home/root/tpmtest_$TEST.log
expect "Final Verdict"
expect "FINAL VERDICT"
interact
exit 0
