PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH

numInterestString="outgoing_interest"
numContentString="outgoing_data"
contentPublished="contentObject_published"
PITcount="PITcount"
contentCount="contentCount"

numOfNodes=30

#folder="edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/"
#folder="edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/"
#folder="edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/"
#folder="edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/"
#folder="lossless_lowTraffic_topologyBA1_UTS_LRU/"
#folder="producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/"
#folder="producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/"
#folder="producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/"
#folder="producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/"
#folder="consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/"
#folder="consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/"
#folder="consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/"
#folder="consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/"

folders=[ "edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/" "edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/" "edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/" "edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/" "lossless_lowTraffic_topologyBA1_UTS_LRU/" "producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/" "producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/" "producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/" "producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/" "consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/" "consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx240ms/" "consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/" ]

for m in 0 1 2 3 4 5 6 7 8 9 10 11 12
do
logfile="${folders[$m]}numberOfTransmissionsLog.txt"
echo $logfile
> $logfile
for i in 100
do
   for j in 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30
   do
      for k in 1 2 3 4 5
      do
         loc="${folders[$m]}cacheProb${i}/CSsize${j}/run${k}/log_node"
         l=0
         totalInterestPropagates=0
         totalContentPropagates=0
         while [ $l -lt $numOfNodes ]
         do
            numOfInterestPropagates[$l]=`grep -c -w "$numInterestString" "${loc}$((l+1)).txt"`
            numOfContentSends[$l]=`grep -c -w "$numContentString" "${loc}$((l+1)).txt"`
            numOfCOpublished[$l]=`grep -c -w "$contentPublished" "${loc}$((l+1)).txt"`
            totalInterestPropagates=`expr $totalInterestPropagates + ${numOfInterestPropagates[$l]}`
            totalContentPropagates=`expr $totalContentPropagates + ${numOfContentSends[$l]}`
            l=`expr $l + 1`
         done
         echo "Total_interests:$totalInterestPropagates:Total_contents:$totalContentPropagates" >> "$logfile"
      done
   done
done
done
