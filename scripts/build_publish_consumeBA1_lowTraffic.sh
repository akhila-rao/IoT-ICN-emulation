if [ $# -lt  1 ] || [ $# -gt 1 ]
then
    echo "Usage: command <retransmit time in seconds>"
    exit 0
fi
echo "T_retx is "$1

pkill ccn-lite-relay
sleep 2
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv

bash emulateStaticTopologyBA1.sh
sleep 1

numOfPublishers=10
numOfStrPerPub=1
# low traffic
publishTimePeriods=( 3.2 1.5 2.0 3.0 1.2 2.5 2.8 1.7 3.4 2.3 ) # also requesting time period
numOfConsumers1=20
publisherIDs=( 30 25 1 23 19 26 6 24 7 16 )
consumerIDs1=( 2 3 4 5 8 9 10 11 12 13 14 15 17 18 20 21 22 27 28 29 )
evalTime=200 #seconds

j=0
while [ $j -lt $numOfPublishers ]
do
   k=1
   while [ $k -le $numOfStrPerPub ]
   do
      ind=`echo "scale=0;$j*$numOfStrPerPub+$k-1" | bc`     
      ind=$( printf "%.0f" $ind )
      numOfCOsToPublish=`echo "scale=0;$evalTime/${publishTimePeriods[$ind]}" | bc`
      bash publishData.sh "/tmp/mgmt-relay-${publisherIDs[$j]}.sock" "/n=s${publisherIDs[$j]}/n=st$k" $numOfCOsToPublish periodic ${publishTimePeriods[$ind]} &      
      i=0
      while [ $i -lt $numOfConsumers1 ]
      do
         portNum=`expr ${consumerIDs1[$i]} + 9000`
         if [ ${publisherIDs[$j]} -ne ${consumerIDs1[$i]} ]
         then
            bash sendInterestMsgs.sh "127.0.0.1/$portNum" "/n=s${publisherIDs[$j]}/n=st$k" $1 ${publishTimePeriods[$ind]} 1 $numOfCOsToPublish & # ensure that this script starts with a random time sample
         fi
         i=`expr $i + 1`
      done  
      k=`expr $k + 1`
   done
   j=`expr $j + 1`
done

tim=$(($evalTime+10))
sleep $tim
echo DONE
