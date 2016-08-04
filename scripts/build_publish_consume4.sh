pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology4.sh
sleep 5
bash publishAll.sh /tmp/mgmt-relay-6.sock /n=s6 67
sleep 0.05
bash publishAll.sh /tmp/mgmt-relay-7.sock /n=s7 59
sleep 0.05
bash publishAll.sh /tmp/mgmt-relay-8.sock /n=s8 91
sleep 0.05



bash publishData.sh /tmp/mgmt-relay-9.sock /n=s9 100 periodic 1 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-10.sock /n=s10 84 periodic 1.2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-11.sock /n=s11 63 periodic 1.6 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-12.sock /n=s12 50 periodic 2 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-13.sock /n=s13 44 periodic 2.3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-14.sock /n=s14 34 periodic 3 &
sleep 0.05
bash publishData.sh /tmp/mgmt-relay-15.sock /n=s15 25 periodic 4 &
sleep 0.05



rand_sleep=`awk "BEGIN {print ($RANDOM%10+1)}"`
sleepyTime=`awk "BEGIN {print ($rand_sleep / 10)}"`
echo "random sleepy time is $sleepyTime"
sleep $sleepyTime

numOfConsumers1=10
# consumers with granularity #1
consumerIDs1=( 1 2 3 4 5 6 7 8 9 10 )
i=0
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   if [ $i -lt 5 ]
   then
      if [ ${consumerIDs1[$i]} -ne 10 ]
      then
         bash sendInterestMsgsDelayed.sh "127.0.0.1/$portNum" /n=s10 1 1.2 3 84 &
      fi
      if [ ${consumerIDs1[$i]} -ne 13 ]
      then
         bash sendInterestMsgsDelayed.sh "127.0.0.1/$portNum" /n=s13 1 2.3 3 44 &  
      fi
   else
      if [ ${consumerIDs1[$i]} -ne 10 ]
      then
         bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s10 1 1.2 1 84 &
      fi
      if [ ${consumerIDs1[$i]} -ne 13 ]
      then
         bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s13 1 2.3 1 44 &
      fi
   fi

   sleep 0.05
   if [ ${consumerIDs1[$i]} -ne 6 ]
   then
      bash sendInterestMsgsRandom.sh "127.0.0.1/$portNum" /n=s6 1 1.5 1 67 67 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 7 ]
   then
      bash sendInterestMsgsRandom.sh "127.0.0.1/$portNum" /n=s7 1 1.7 1 59 59 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 8 ]
   then
      bash sendInterestMsgsRandom.sh "127.0.0.1/$portNum" /n=s8 1 1.1 1 91 91 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 9 ]
   then
      bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s9 1 1 1 100 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 11 ]
   then
      bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s11 1 1.6 1 63 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 12 ]
   then
      bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s12 1 2 1 50 &
      sleep 0.05
   fi
   if [ ${consumerIDs1[$i]} -ne 14 ]
   then
      bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s14 1 3 1 34 &
      sleep 0.05
   fi 
   if [ ${consumerIDs1[$i]} -ne 15 ]
   then
      bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s15 1 4 1 25 &
      sleep 0.05
   fi
   i=`expr $i + 1`
done

tim=$((100 + 10))
sleep $tim
echo DONE
