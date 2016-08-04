PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
# publish data
if [ $# -lt 5 ] || [ $# -gt 5 ]
then
    echo "Usage: command <Publisher socketID> <Name without seqnum> <Num. of objects to publish> <periodic/random> <Time period inbetween>"
    exit 0
fi

COUNT=$3
TIME_PERIOD=$5
seqnum=1


while [ $seqnum -le $COUNT ]
do
   rm "$n.ccntlv"
   n=$RANDOM
   echo $RANDOM | ccn-lite-mkC -s ccnx2015 -o "$n.ccntlv" "$2/sq=$seqnum" 
   ccn-lite-ctrl -x $1 addContentToCache "$n.ccntlv" | ccn-lite-ccnb2xml &
   seqnum=`expr $seqnum + 1`
   if [ "$4" == "periodic" ]
   then
       sleep $TIME_PERIOD
   elif [ "$4" == "random" ]
   then
       rand_time=`awk "BEGIN {print ($RANDOM%($TIME_PERIOD*200))/100}"`
       sleep $rand_time
   else
        echo "Usage: command <Publisher socketID> <Name without seqnum> <Num. of objects to publish> <periodic/random> <Time period inbetween> <Start seqnum>"
        exit 0
   fi
done
