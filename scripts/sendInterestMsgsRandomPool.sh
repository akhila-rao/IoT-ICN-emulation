PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
if [ $# -lt  6 ] || [ $# -gt 6 ]
then
    echo "Usage: command <IPAddr/portNum> <my own ID> <Interest lifetime> <Time period inbetween> <Num. of interests to send> <File to read names from>"
    exit 0
fi

#granularity 1 means every pkt, granularity 5 means every 5th pkt
COUNT=$5
TIME_PERIOD=$4
LIFETIME=$3
i=0

readarray -t shuffledNames < "src$2_$6"

echo "done reading shuffled prefixes from file for node "$2
# start with a random sleep time within one time period
rand_time=`awk "BEGIN {print (($RANDOM%(1*100))+1)/100}"`
sleep $rand_time

while [ $i -lt $COUNT ]
do
   if [[ "${shuffledNames[$i]}" != *"/n=s$2/"* ]]
   then
      ccn-lite-peek -s ccnx2015 -w $LIFETIME -u $1 "${shuffledNames[$i]}" &
   fi
   i=`expr $i + 1`
   sleep $TIME_PERIOD
done
