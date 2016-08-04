PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
#PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite-original/bin:$PATH
if [ $# -lt  7 ] || [ $# -gt 7 ]
then
    echo "Usage: command <IPAddr/portNum> <Name without seqnum> <Interest lifetime> <Time period inbetween> <granularity> <seqNum range of COs> <Num. of interests to send> "
    exit 0
fi

#granularity 1 means every pkt, granularity 5 means every 5th pkt
COUNT=$7
TIME_PERIOD=$4
num=1
granularity=$5
numObjects=$6

while [ $num -le $COUNT ]
do
   rand_num=`awk "BEGIN {print ($RANDOM%$numObjects)+1}"`
   echo "rand_CO:$2/sq=$rand_num"
   ccn-lite-peek -s ccnx2015 -w $3 -u $1 "$2/sq=$rand_num" &
#   ccn-lite-peek -s ccnx2015 -w $3 -u $1 "$2/sq=$rand_num" | ccn-lite-pktdump -f 0 &
   num=`expr $num + $granularity`
   sleepTime=`awk "BEGIN {print ($TIME_PERIOD * $granularity)}"`
   sleep $sleepTime
done
