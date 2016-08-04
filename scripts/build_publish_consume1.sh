pkill ccn-lite-relay
sleep 5
rm -rf log*
rm -rf ICNIoTlog*
rm -rf *.ccntlv
#rm -rf *.ccntlv
#publishData2.sh <Publisher socketID> <Name without seqnum> <Num. of objects to publish> <periodic/random> <Time period inbetween>
#SendInterestMsgs.sh <IPAddr/portNum> <Name without seqnum> <Interest lifetime> <Time period inbetween> <granularity> <Num. of interests to send>

bash emulateStaticTopology1.sh
sleep 1

bash publishData.sh /tmp/mgmt-relay-3.sock /n=s 200 periodic 0.3 &
#bash publishAll.sh /tmp/mgmt-relay-2.sock /n=s 10

sleep 1
numOfConsumers1=1
# consumers with granularity #1
consumerIDs1=( 1 )
i=0
while [ $i -lt $numOfConsumers1 ]
do
   portNum=`expr ${consumerIDs1[$i]} + 9000`
   bash sendInterestMsgs.sh "127.0.0.1/$portNum" /n=s 1 0.3 1 200 &
   sleep 0.05
   i=`expr $i + 1`
done

tim=$((60 + 9))
sleep $tim
echo DONE
