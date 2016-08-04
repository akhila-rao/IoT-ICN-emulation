pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology6.sh
sleep 5



# publishing
bash publishData.sh /tmp/mgmt-relay-1.sock /n=s1 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-2.sock /n=s2 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-3.sock /n=s3 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-4.sock /n=s4 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-5.sock /n=s5 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-6.sock /n=s6 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-7.sock /n=s7 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-8.sock /n=s8 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-9.sock /n=s9 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-10.sock /n=s10 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-11.sock /n=s11 100 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-12.sock /n=s12 100 periodic 3 &
sleep 0.05

# random sleep time between 0.1 and 1.0 seconds
rand_sleep=`awk "BEGIN {print ($RANDOM%5+1)}"`
sleepyTime=`awk "BEGIN {print ($rand_sleep / 10)}"`
echo "random sleepy time is $sleepyTime"

numOfConsumers1=8
# consumers with granularity #1
consumerIDs1=( 13 14 15 16 17 18 19 20 )
i=0
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s1 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s2 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s3 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s4 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s5 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s6 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s7 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s8 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s9 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s10 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s11 1 3 1 100 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s12 1 3 1 100 &
   sleep 0.05
   i=`expr $i + 1`
   sleep $sleepyTime
done

tim=$((300 + 20))
sleep $tim
echo DONE
