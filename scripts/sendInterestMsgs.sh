PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
if [ $# -lt  6 ] || [ $# -gt 6 ]
then
    echo "Usage: command 1<IPAddr/portNum> 2<Name without seqnum> 3<Interest lifetime> 4<Time period inbetween> 5<granularity> 6<Num. of interests to send>"
    exit 0
fi

#granularity 1 means every pkt, granularity 5 means every 5th pkt
COUNT=$6
TIME_PERIOD=$4
seqnum=1
granularity=$5

# start with a random sleep time within one time period
rand_time=`awk "BEGIN {print (($RANDOM%($TIME_PERIOD*100))+1)/100}"`
sleep $rand_time

while [ $seqnum -le $COUNT ]
do
   ccn-lite-peek -s ccnx2015 -w $3 -u $1 "$2/sq=$seqnum" &
   seqnum=`expr $seqnum + $granularity`
   sleepTime=`echo "scale=3;$TIME_PERIOD*$granularity" | bc`
   sleep $sleepTime
done
