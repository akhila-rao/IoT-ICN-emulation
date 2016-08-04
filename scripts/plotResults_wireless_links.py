import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True
PLOT_DROPPED_PKTS = False
PLOT_RECEPTION_RATE = False
PLOT_NUM_OF_PKTS_LOSSY_OVER_LOSSLESS = False
PLOT_NUM_OF_PKTS_LOSSY_OVER_LOSSLESS_PERCENTAGE = False
#BA1
numOfNodes=30
srcNodes=[30, 25, 1, 23, 19, 26, 6, 24, 7, 16]
consumerNodes=[2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 21, 22, 27, 28, 29]
runTime=200
avgNumPktsFilename="numberOfTransmissionsLog.txt"
cacheProbs=np.array([100])
# low traffic
CSsizes=np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
numOfObjectsPerSec=5.0
# high traffic cache sizes
#CSsizes=np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45])

#folders=["edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/", "edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/",
#"edgeLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/", "lossless_lowTraffic_topologyBA1_UTS_LRU/"]
#folders=["producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/", "producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/",
#"producerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/","lossless_lowTraffic_topologyBA1_UTS_LRU/"]
folders=["consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/", "consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/",
"consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/","lossless_lowTraffic_topologyBA1_UTS_LRU/"]


#folders=["edgeLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx100ms/", "edgeLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx1000ms/", 
#"edgeLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx4000ms/", "lossless_lowTraffic_topologyBA1_second_UTS_LRU/"]
#folders=["producerLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx100ms/", "producerLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx1000ms/", 
#"producerLossy_lowTraffic_topologyBA1_second_UTS_LRU_Pout50_Tretx4000ms/", "lossless_lowTraffic_topologyBA1_second_UTS_LRU/"]
#folders=["consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx100ms/", "consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx1000ms/", 
#"consumerLossy_lowTraffic_topologyBA1_UTS_LRU_Pout50_Tretx4000ms/", "lossless_lowTraffic_topologyBA1_UTS_LRU/"]

numRuns=5
#------------------------------------------------------------------

# strings in the log files used to obtain metrics
numInterestString="outgoing_interest"
numContentString="outgoing_data"
contentPublished="contentObject_published"
PITcount="PITcount"
contentCount="contentCount"
CSentry="ContentStoreItem"
CSnextEntry="ContentStoreItem contentCount"
COreceived="ccn-lite-peek recieved CO at node"
COnotReceived="timeout"
pktDropped=" dropped"
pktSent="outgoing_"
#------------------------------------------------------------------

numPktsSent=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
numPktsSent_errorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

receptionRate=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
receptionRate_errorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

numPktsDropped=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
numPktsDropped_errorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

pktsSentLossyVsLossless=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
pktsSentLossyVsLossless_errorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

#-------------------------------- CACHE DIVERSITY --------------------------

# function to compute average reception rate of COs in the network
def computeReceptionRate( fileNameStr, COreceived, COnotReceived):
        receivedCount=0
        notReceivedCount=0
        for line in open(fileNameStr):
                if COreceived in line:
                        receivedCount += 1
                elif COnotReceived in line:
                        notReceivedCount += 1

        receptionRate = float(receivedCount)/float(receivedCount + notReceivedCount)
        return[receptionRate]

def findNumOfSentAndDropped( numOfNodes, fileNameStr, sentStr, droppedStr ):
        print fileNameStr
        sent_count=0
	dropped_count=0
        for n in range(numOfNodes):
		fp = open(fileNameStr+str(n+1)+".txt","r")
                for line in fp:
                        if sentStr in line:
                        	sent_count+=1
                        if droppedStr in line:
				dropped_count+=1
		fp.close()

        return [ sent_count, dropped_count ]

#---------------------- MAIN -----------------------------------------

offset=0;
for lo in folders:
	dataFolders = lo
	fo = open(dataFolders+avgNumPktsFilename, "r")
	print "Reading file "+dataFolders+avgNumPktsFilename
	# Fix prob caching
	for i in range(len(cacheProbs)):
		for j in range(len(CSsizes)):
			temp1=[]
			temp2=[]
			temp4=[]
			for k in range(numRuns):
                                ln=fo.readline()
                                lnlist=ln.split(":")
                                numInt=int(lnlist[1])
                                numCnt=int(lnlist[3])
                                totalPkts=numInt + numCnt
                                temp1.append(totalPkts)
#				nameStr=dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/log_node"
#				[sentCount, droppedCount]=findNumOfSentAndDropped( numOfNodes, nameStr, pktSent, pktDropped )
#				temp1.append(sentCount)
#                                temp2.append(droppedCount)
				nameStr = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/ccnlitePeek_log.txt"
				temp4.append(computeReceptionRate( nameStr, COreceived, COnotReceived ))

			numPktsSent[i+offset,j]=np.mean(temp1)
			numPktsSent_errorBar[i+offset,j]= 2.262*np.std(temp1)/(math.sqrt(numRuns))
                        #numPktsDropped[i+offset,j]=np.mean(temp2)
                        #numPktsDropped_errorBar[i+offset,j]= 2.262*np.std(temp2)/(math.sqrt(numRuns))
                        receptionRate[i+offset,j] = np.mean(temp4)
			receptionRate_errorBar[i+offset,j] = 2.262*np.std(temp4)/(math.sqrt(numRuns))
		
	fo.close()
	offset+=len(cacheProbs)

#-------------------------- PLOTTING--------------------------------------
# Plot for number of pkts transmitted versus cache size
if PLOT_NUM_OF_PKTS:
	p, ax = plt.subplots()
        p1 = ax.errorbar(CSsizes, numPktsSent[0,:]/1000, yerr=numPktsSent_errorBar[0,:]/1000, fmt='rd:', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='r', markerfacecolor='r')
        p2 = ax.errorbar(CSsizes, numPktsSent[1,:]/1000, yerr=numPktsSent_errorBar[1,:]/1000, fmt='bo-.', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='b', markerfacecolor='None')
        p3 = ax.errorbar(CSsizes, numPktsSent[2,:]/1000, yerr=numPktsSent_errorBar[2,:]/1000, fmt='g*--', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='g', markerfacecolor='g')
        p4 = ax.errorbar(CSsizes, numPktsSent[3,:]/1000, yerr=numPktsSent_errorBar[3,:]/1000, fmt='k.-', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='k', markerfacecolor='None')


	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Cache size (number of content objects)')
	plt.ylabel('Number of messages transmitted (X1000)')
	plt.title('Lossy network \n Cache all, UTS-LRU')
	plt.legend([p1, p2, p3, p4], ['T_retx=0.1 s', 'T_retx=1 s', 'T_retx=4 s', 'Lossless'], loc='best')
	plt.xlim([0, 30])
	plt.ylim([0,170])
	plt.grid()

# Plot for reception rate versus CS size fore different cache probabilities
if PLOT_RECEPTION_RATE:
	r, axr = plt.subplots()
	r1 = axr.errorbar(CSsizes, receptionRate[0,:], yerr=receptionRate_errorBar[0,:], fmt='rD-', linewidth=3.0, ms=10.0)
	r2 = axr.errorbar(CSsizes, receptionRate[1,:], yerr=receptionRate_errorBar[1,:], fmt='b^-.', linewidth=3.0, ms=10.0)
        r3 = axr.errorbar(CSsizes, receptionRate[2,:], yerr=receptionRate_errorBar[2,:], fmt='g*--', linewidth=3.0, ms=10.0)
        r4 = axr.errorbar(CSsizes, receptionRate[3,:], yerr=receptionRate_errorBar[3,:], fmt='ko-', linewidth=3.0, ms=10.0)

	plt.rcParams.update({'font.size': 30})
	plt.ylabel('Reception rate')
        plt.xlabel('Cache size (number of content objects)')
        plt.title('Lossy network \n Cache all, UTS-LRU')
        plt.legend([r1, r2, r3, r4], ['T_retx=0.1 s', 'T_retx=1 s', 'T_retx=4 s', 'Lossless'], loc='best')
        plt.xlim([0, 30])
	plt.ylim([0.95, 1.0])
	plt.grid()

plt.show()
