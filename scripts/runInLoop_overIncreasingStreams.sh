logFileStr="numberOfTransmissionsLog.txt"
resultsFolderStr="topology6_"
numOfRuns=5


for NumStreams in 2 4 8 12
  do
  resultsFolder="${resultsFolderStr}${NumStreams}streams/"
  mkdir "$resultsFolder"
#  echo $lr > linkErrorProb.txt
  # loop over cache probabilities
  for cp in 100 50
    do
    folder1="${resultsFolder}cacheProb$cp"
    mkdir $folder1
    echo $cp > cacheProb.txt
    #loop over CSsize
    for CSs in 1 2 3 5 15 0
    do
      folder2="$folder1/CSsize$CSs"
      mkdir $folder2
      echo $CSs > cacheSize.txt
      i=1
      sumInt=0
      sumCnt=0
      while [ $i -le $numOfRuns ]
      do
        pkill ccn-lire-relay
        sleep 2
        echo 0 > linkErrorProb.txt
        bash build_publish_consume6_${NumStreams}streams.sh 2> ccnlitePeek_log.txt
        pkill ccn-lite-relay
        sleep 5
        str=`bash networkStatistics.sh`
        folder3="$folder2/run$i"
        mkdir $folder3 
        mv log_node* $folder3
        echo $str >> "$resultsFolder$logFileStr"
        mv ccnlitePeek_log.txt $folder3
        spl=(${str//:/ })
        sumInt=`expr $sumInt + ${spl[1]}`
        sumCnt=`expr $sumCnt + ${spl[3]}`
        i=`expr $i + 1`
        sleep 1
      done
      sumInt=`awk "BEGIN {print $sumInt/$numOfRuns}"`
      sumCnt=`awk "BEGIN {print $sumCnt/$numOfRuns}"`
      # echo "avgNumInt:$sumInt:avgNumCnt:$sumCnt" >> "$resultsFolder$logFileStr" 
    done
  done
done


sleep 10

