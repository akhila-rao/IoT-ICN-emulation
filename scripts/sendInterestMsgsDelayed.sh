PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
#PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite-original/bin:$PATH
if [ $# -lt  6 ] || [ $# -gt 6 ]
then
    echo "Usage: command <IPAddr/portNum> <Name without seqnum> <Interest lifetime> <Time period inbetween> <granularity> <Num. of interests to send>"
    exit 0
fi

#granularity 1 means every pkt, granularity 5 means every 5th pkt
COUNT=$6
TIME_PERIOD=$4
seqnum=1
granularity=$5

while [ $seqnum -lt $COUNT ]
do
   sleepTime=`awk "BEGIN {print ($TIME_PERIOD * $granularity)}"`
   sleep $sleepTime
   ccn-lite-peek -s ccnx2015 -w $3 -u $1 "$2/sq=$seqnum" &
#   ccn-lite-peek -s ccnx2015 -w $3 -u $1 "$2/sq=$seqnum" | ccn-lite-pktdump -f 0 &
   seqnum=`expr $seqnum + $granularity`
done
