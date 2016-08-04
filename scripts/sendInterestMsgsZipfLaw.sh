PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
#PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite-original/bin:$PATH
if [ $# -lt  5 ] || [ $# -gt 5 ]
then
    echo "Usage: command <IPAddr/portNum> <my own ID> <Interest lifetime> <Time period inbetween> <Num. of interests to send> "
    exit 0
fi

#granularity 1 means every pkt, granularity 5 means every 5th pkt
COUNT=$5
TIME_PERIOD=$4
LIFETIME=$3


numOfPublishers=10
numOfStrPerPub=2
publisherIDs=( 6 7 8 9 10 11 12 13 14 15 )
numOfConsumers1=10

N=$(($numOfPublishers * $numOfStrPerPub)) # number of content objects
sm=0

for i in {1..$N}
do
   sm=`awk "BEGIN {print ($sm + (1/$i))}"`
done
c=`awk "BEGIN {print (1/$sm)}"`

maxy=1000
prev=0
for i in {1..$N}
do
   probMarker[$(($i-1))]=`awk "BEGIN {print ((($c/$i)*$maxy) + $prev)}"`
   prev=${probMarker[$(($i-1))]}
   


i=1
while [ $i -le $COUNT ]
do
   rand_pub_ind=`awk "BEGIN {print ($RANDOM%$numOfPublishers)}"`
   rand_pub=${publisherIDs[$rand_pub_ind]}
   rand_str=`awk "BEGIN {print ($RANDOM%$numOfStrPerPub)+1}"`
   if [ $rand_pub -ne $2 ]
   then
      ccn-lite-peek -s ccnx2015 -w $LIFETIME -u $1 "/n=s$rand_pub/n=st$rand_str" &
   fi
   i=`expr $i + 1`
   sleep $TIME_PERIOD
done
