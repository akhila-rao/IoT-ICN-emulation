######## Low traffic #### Lossless links ######
logFileStr="numberOfTransmissionsLog.txt"
resultsFolderStr="lossless_lowTraffic_topologyBA1_LRU_probability_based_caching2"
numOfRuns=5
cd ../src/
cp LRU_ccnl-core.h ccnl-core.h
make clean all
echo "make done"
cd ../scripts/
#for Pout in 0.50
#do
   echo 0 > active_linkErrorProb.txt
   echo 0 > outage_linkErrorProb.txt
   cp producer_lossyLinks.txt lossyLinks.txt
   sleep 5
   for Tretx in 4.0
   do
      > $logFileStr
#      s=`echo "scale=0;$Tretx*1000" | bc`
#      t=$( printf "%.0f" $s )
#      u=`echo "scale=0;$Pout*100" | bc`
#      v=$( printf "%.0f" $u )
      resultsFolder="${resultsFolderStr}/"
      mkdir "$resultsFolder"
      # loop over cache probabilities
      for cp in 100 80 60
      do
         folder1="${resultsFolder}cacheProb$cp"
         mkdir $folder1
         echo $cp > cacheProb.txt
         #loop over CSsize
         for CSs in 0 2 4 6 8 10 12 14 16 18 20 22 24 26 28 30
         do
            folder2="$folder1/CSsize$CSs"
            mkdir $folder2
            echo $CSs > cacheSize.txt
            i=1
            while [ $i -le $numOfRuns ]
            do
               bash build_publish_consumeBA1_lowTraffic.sh $Tretx 2> ccnlitePeek_log.txt
               pkill ccn-lite-relay
               sleep 2
               str=`bash networkStatistics.sh`
               folder3="$folder2/run$i"
               mkdir $folder3
               mv log_node* $folder3
               echo $str >> "$resultsFolder$logFileStr"
               mv ccnlitePeek_log.txt $folder3
               i=`expr $i + 1`
               sleep 1
            done
         done
      done
   done
#done
sleep 10

