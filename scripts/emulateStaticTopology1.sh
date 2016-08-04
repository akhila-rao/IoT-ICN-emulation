PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite/bin:$PATH
#PATH=/lhome/akhila/Desktop/ICNforIoT/code_data_ccnlite_svn/efficientiot/code_data/ccn-lite-original/bin:$PATH



# THIS IS A TEST TOPPOLOGY WITH ONLY 1 OR 2 NODES





# configuration parameters

#Start relays and log output into files
numOfNodes=3
nodeNum=1
while [ $nodeNum -le $numOfNodes ]
do
   portNum=`expr $nodeNum + 9000`
#   valgrind --leak-check=yes ccn-lite-relay -v trace -s ccnx2015 -u $portNum -x "/tmp/mgmt-relay-$nodeNum.sock" 2>"log_node$nodeNum.txt" &
   ccn-lite-relay -v trace -s ccnx2015 -u $portNum -x "/tmp/mgmt-relay-$nodeNum.sock" 2>"log_node$nodeNum.txt" &
   nodeNum=`expr $nodeNum + 1`
done


sleep 5

#connect relays and add forwarding rules
FACEID=`ccn-lite-ctrl -x /tmp/mgmt-relay-1.sock newUDPface any 127.0.0.1 9002 | ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/'`
ccn-lite-ctrl -x /tmp/mgmt-relay-1.sock prefixreg /n=s $FACEID ccnx2015 | ccn-lite-ccnb2xml

FACEID=`ccn-lite-ctrl -x /tmp/mgmt-relay-2.sock newUDPface any 127.0.0.1 9003 | ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/'`
ccn-lite-ctrl -x /tmp/mgmt-relay-2.sock prefixreg /n=s $FACEID ccnx2015 | ccn-lite-ccnb2xml
