PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
#PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite-original/bin:$PATH
# publish data
if [ $# -lt 3 ] || [ $# -gt 3 ]
then
    echo "Usage: command <Publisher socketID> <Name without seqnum> <Num. of objects to publish>"
    exit 0
fi

COUNT=$3
seqnum=1


while [ $seqnum -le $COUNT ]
do
   rm "$n.ccntlv"
   n=$RANDOM
   echo $RANDOM | ccn-lite-mkC -s ccnx2015 -o "$n.ccntlv" "$2/sq=$seqnum" 
   ccn-lite-ctrl -x $1 addContentToCache "$n.ccntlv" | ccn-lite-ccnb2xml
   seqnum=`expr $seqnum + 1`
   sleep 0.05
done
