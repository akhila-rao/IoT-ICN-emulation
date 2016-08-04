PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopology4.sh
sleep 5



numOfPublishers=10
numOfStrPerPub=2
numOfCOsToPublish=100
publishTimePeriod=2 # also requesting time period
numOfConsumers1=10
publisherIDs=( 6 7 8 9 10 11 12 13 14 15 )
consumerIDs1=( 1 2 3 4 5 6 7 8 9 10 )

requestTimePeriod=`awk "BEGIN {print ($publishTimePeriod / ($numOfPublishers * $numOfStrPerPub))}"`
numOfRequests=$(($numOfPublishers * $numOfStrPerPub * $numOfCOsToPublish))
#numOfRequests=5
#requestTimePeriod=1

j=0
while [ $j -lt $numOfPublishers ]
do
   k=1
   while [ $k -le $numOfStrPerPub ]
   do
      n=$RANDOM
      echo $RANDOM | ccn-lite-mkC -s ccnx2015 -o "$n.ccntlv" "/n=s${publisherIDs[$j]}/n=st$k" 
      ccn-lite-ctrl -x "/tmp/mgmt-relay-${publisherIDs[$j]}.sock" addContentToCache "$n.ccntlv" | ccn-lite-ccnb2xml
      sleep 0.05
      rm "$n.ccntlv"
      k=`expr $k + 1`
   done
   j=`expr $j + 1`
done

rand_sleep=`awk "BEGIN {print ($RANDOM%10+1)}"`
sleepyTime=`awk "BEGIN {print ($rand_sleep / 20)}"`
sleep $sleepyTime


i=0
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   bash sendInterestMsgsRandomPool.sh "127.0.0.1/$portNum" ${consumerIDs1[$i]} 1 $requestTimePeriod $numOfRequests &
   sleep 0.01
   i=`expr $i + 1`
done

tim=$(($numOfCOsToPublish * $publishTimePeriod+ 10))
sleep $tim
echo DONE
