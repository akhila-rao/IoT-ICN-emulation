pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology6.sh
sleep 5



# publishing
bash publishData.sh /tmp/mgmt-relay-1.sock /n=s1 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-2.sock /n=s2 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-4.sock /n=s4 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-5.sock /n=s5 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-7.sock /n=s7 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-8.sock /n=s8 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-10.sock /n=s10 150 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-11.sock /n=s11 150 periodic 2 &
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
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s1 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s2 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s4 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s5 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s7 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s8 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s10 1 2 1 150 &
   sleep 0.05
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s11 1 2 1 150 &
   sleep 0.05
   i=`expr $i + 1`
   sleep $sleepyTime
done

tim=$((300 + 20))
sleep $tim
echo DONE
