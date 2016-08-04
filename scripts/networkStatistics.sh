PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH

numInterestString="outgoing_interest"
numContentString="outgoing_data"
contentPublished="contentObject_published"
PITcount="PITcount"
contentCount="contentCount"


numOfNodes=30
i=0
totalInterestPropagates=0
totalContentPropagates=0
while [ $i -lt $numOfNodes ]
do
   numOfInterestPropagates[$i]=`grep -c -w "$numInterestString" "log_node$((i+1)).txt"`
   numOfContentSends[$i]=`grep -c -w "$numContentString" "log_node$((i+1)).txt"`
   numOfCOpublished[$i]=`grep -c -w "$contentPublished" "log_node$((i+1)).txt"`
   totalInterestPropagates=`expr $totalInterestPropagates + ${numOfInterestPropagates[$i]}`
   totalContentPropagates=`expr $totalContentPropagates + ${numOfContentSends[$i]}`
   i=`expr $i + 1`
done
echo "Total_interests:$totalInterestPropagates:Total_contents:$totalContentPropagates"
