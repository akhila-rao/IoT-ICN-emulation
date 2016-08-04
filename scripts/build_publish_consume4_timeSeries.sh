pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology4.sh
sleep 5

numOfPublishers=10
numOfStrPerPub=2
numOfCOsToPublish=100  # number of sequence numbers published 
publishTimePeriod=2 # also requesting time period
numOfConsumers1=10
publisherIDs=( 6 7 8 9 10 11 12 13 14 15 )
consumerIDs1=( 1 2 3 4 5 6 7 8 9 10 )



j=0
while [ $j -lt $numOfPublishers ]
do
   k=1
   while [ $k -le $numOfStrPerPub ]
   do
      bash publishData.sh "/tmp/mgmt-relay-${publisherIDs[$j]}.sock" "/n=s${publisherIDs[$j]}/n=st$k" $numOfCOsToPublish periodic $publishTimePeriod &
      sleep 0.05
      k=`expr $k + 1`
   done
   j=`expr $j + 1`
#   sleep 0.01
done

sleep 2    
rand_sleep=`awk "BEGIN {print ($RANDOM%10+1)}"`
sleepyTime=`awk "BEGIN {print ($rand_sleep / 20)}"`
sleep $sleepyTime

i=0
while [ $i -lt $numOfConsumers1 ]
do
   j=0
   while [ $j -lt $numOfPublishers ]
   do
      k=1
      while [ $k -le $numOfStrPerPub ]
      do
         portNum=`expr ${consumerIDs1[$i]} + 9000`
         if [ ${publisherIDs[$j]} -ne ${consumerIDs1[$i]} ]
         then
            bash sendInterestMsgs.sh "127.0.0.1/$portNum" "/n=s${publisherIDs[$j]}/n=st$k" 1 $publishTimePeriod 1 $numOfCOsToPublish &    
            sleep 0.05
         fi
         k=`expr $k + 1`
      done
      j=`expr $j + 1`
   done
   i=`expr $i + 1`
done


tim=$(($numOfCOsToPublish * $publishTimePeriod+ 10))
sleep $tim
echo DONE
