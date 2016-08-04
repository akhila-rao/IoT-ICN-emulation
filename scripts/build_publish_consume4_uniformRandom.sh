PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology4.sh
sleep 5


namesFile="COnames.txt"
numOfPublishers=10

numOfCOPerPublisher=200

numOfRequests=2000
requestTimePeriod=0.1 # also requesting time period
numOfConsumers1=10
publisherIDs=( 6 7 8 9 10 11 12 13 14 15 )
consumerIDs1=( 1 2 3 4 5 6 7 8 9 10 )

> "$namesFile"
# publish all the data
j=0
while [ $j -lt $numOfPublishers ]
do
   k=1
   while [ $k -le $numOfCOPerPublisher ]
   do
      n=$RANDOM
      echo $RANDOM | ccn-lite-mkC -s ccnx2015 -o "$n.ccntlv" "/n=s${publisherIDs[$j]}/CO=$k"
      ccn-lite-ctrl -x "/tmp/mgmt-relay-${publisherIDs[$j]}.sock" addContentToCache "$n.ccntlv" | ccn-lite-ccnb2xml
      echo "/n=s${publisherIDs[$j]}/CO=$k" >> "$namesFile"
      sleep 0.05
      rm "$n.ccntlv"
      k=`expr $k + 1`
   done
   j=`expr $j + 1`
done

# sleep for random time to randomize over runs
sleep 2
rand_sleep=`awk "BEGIN {print ($RANDOM%10+1)}"`
sleepyTime=`awk "BEGIN {print ($rand_sleep / 20)}"`
sleep $sleepyTime

# in a loop shuffle files for all consumers
i=0
while [ $i -lt $numOfConsumers1 ]
do
   python shuffleArray.py "$namesFile" "${consumerIDs1[$i]}"
   echo "done shuffling for consumer ${consumerIDs1[$i]}"
   i=`expr $i + 1`
done


#request for the COs periodically by selecting from a random pool of COs
i=0
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   bash sendInterestMsgsRandomPool.sh "127.0.0.1/$portNum" ${consumerIDs1[$i]} 1 $requestTimePeriod $numOfRequests "$namesFile" &
   sleep 0.05
   i=`expr $i + 1`
done

tim=`awk "BEGIN {print (($numOfRequests*$requestTimePeriod)+10)}"`
echo "going to sleep for $tim time"
sleep $tim
echo DONE
