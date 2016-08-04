if [ $# -lt  1 ] || [ $# -gt 1 ]
then
    echo "Usage: command <retransmit time in seconds>"
    exit 0
fi
echo "T_retx is "$1
PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
pkill ccn-lite-relay
sleep 2
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopologyBA1.sh
sleep 1

numOfPublishers=10
numOfStrPerPub=3
# low traffic
#publishTimePeriods=( 3.2 1.5 2.0 3.0 1.2 2.5 2.8 1.7 3.4 2.3 ) # also requesting time period
#high traffic
publishTimePeriods=( 3.2 1.5 2.0 3.0 1.2 2.5 2.8 1.7 3.4 2.3 1.0 1.4 2.7 3.3 2.1 1.9 1.2 1.7 2.9 1.5 3.2 1.5 2.0 3.0 1.2 2.5 2.8 1.7 3.4 2.3 )
numOfConsumers1=20
publisherIDs=( 30 25 1 23 19 26 6 24 7 16 )
consumerIDs1=( 2 3 4 5 8 9 10 11 12 13 14 15 17 18 20 21 22 27 28 29 )
evalTime=200 #seconds

namesFile="COnames.txt"
> "$namesFile"
# publish all the data
j=0
totalNumOfCOPub=0
while [ $j -lt $numOfPublishers ]
do
   n=1
   numOfCOsToPublish=0
   while [ $n -le $numOfStrPerPub ]
   do
      ind=`echo "scale=0;$j*$numOfStrPerPub+$n-1" | bc`
      ind=$( printf "%.0f" $ind )
      numOfCOsToPublish=`echo "scale=0;($evalTime/${publishTimePeriods[$ind]})+$numOfCOsToPublish" | bc`
      n=`expr $n + 1`
   done
   echo "number of CO s to publish for node "${publisherIDs[$j]}" is "$numOfCOsToPublish
   totalNumOfCOPub=`expr $totalNumOfCOPub + $numOfCOsToPublish`
   k=1
   while [ $k -le $numOfCOsToPublish ]
   do
      n=$RANDOM
      echo $RANDOM | ccn-lite-mkC -s ccnx2015 -o "$n.ccntlv" "/n=s${publisherIDs[$j]}/CO=$k"
      ccn-lite-ctrl -x "/tmp/mgmt-relay-${publisherIDs[$j]}.sock" addContentToCache "$n.ccntlv" | ccn-lite-ccnb2xml
      echo "/n=s${publisherIDs[$j]}/CO=$k" >> "$namesFile"
      rm "$n.ccntlv"
      k=`expr $k + 1`
   done
   j=`expr $j + 1`
done

# in a loop shuffle files for all consumers
i=0
while [ $i -lt $numOfConsumers1 ]
do
   python shuffleArray.py "$namesFile" "${consumerIDs1[$i]}"
   echo "done shuffling for consumer ${consumerIDs1[$i]}"
   i=`expr $i + 1`
done

echo "Total number of COs published are "$totalNumOfCOPub
#request for the COs periodically by selecting from a random pool of COs
i=0
requestTimePeriod=`echo "scale=3;$evalTime/$totalNumOfCOPub" | bc`
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   bash sendInterestMsgsRandomPool.sh "127.0.0.1/$portNum" ${consumerIDs1[$i]} $1 $requestTimePeriod $totalNumOfCOPub "$namesFile" &
   i=`expr $i + 1`
done

tim=$(($evalTime+5))
echo "going to sleep for $tim time"
sleep $tim
echo DONE

