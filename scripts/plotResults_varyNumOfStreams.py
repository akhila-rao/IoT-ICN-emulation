import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True

numOfNodes=34
srcNodes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
consumerNodes=[13, 14, 15, 16, 17, 18, 19, 20]
runTime=300
avgNumPktsFilename="numberOfTransmissionsLog.txt"

CSsizes=np.array([1, 2, 3, 5, 15, 0])
xAxisCSsizes=np.array([0, 1, 2, 3, 5, 15])
cacheProbs=np.array([100, 50])
lossRate=0
numOfStreams = [2, 4, 8, 12]
numRuns=5
dataFolderStr1= "topology6_"
dataFolderStr2= "streams/"

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

#------------------------------------------------------------------

avgNumPkts=np.zeros([len(cacheProbs)*len(numOfStreams),len(CSsizes)])
errorBar=np.zeros([len(cacheProbs)*len(numOfStreams),len(CSsizes)])

#------------------------------------------------------------------

# function to compute average reception rate of COs in the network
def computeReceptionRate( consumerNodes, fileNameStr, COreceived, COnotReceived):
	receivedCount=0
	notReceivedCount=0
	for line in open(fileNameStr):
		if COreceived in line:
			receivedCount += 1
		elif COnotReceived in line:
			notReceivedCount += 1
				
		
		
	receptionRate = float(receivedCount)/float(receivedCount + notReceivedCount)
	return[receptionRate]

#---------------------- MAIN -----------------------------------------

offset=0;
for lo in numOfStreams:
	dataFolders = dataFolderStr1+str(lo)+dataFolderStr2
	fo = open(dataFolders+avgNumPktsFilename, "r")
	print "Reading file "+dataFolders+avgNumPktsFilename
	# Fix prob caching
	for i in range(len(cacheProbs)):
		for j in range(len(CSsizes)):
			tempArr=[]
			for k in range(numRuns):
				ln=fo.readline()
				lnlist=ln.split(":")
				numInt=int(lnlist[1])
				numCnt=int(lnlist[3])
				totalPkts=numInt + numCnt
				tempArr.append(totalPkts)
				nameStr1 = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/log_node"
				nameStr2 = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/ccnlitePeek_log.txt"
	
			avgNumPkts[i+offset,j]=np.mean(tempArr)
			errorBar[i+offset,j]= 2.262*np.std(tempArr)/(math.sqrt(numRuns))
	
		
	fo.close()
	# this is because the x axis is not in increasing order we have added the zero 
	#cache size in the end, so we need to flip it to the other side
	ind=len(CSsizes)-1
	tempy1=copy.deepcopy(avgNumPkts[offset:(offset+len(cacheProbs)),ind])
	tempy11=copy.deepcopy(errorBar[offset:(offset+len(cacheProbs)),ind])
	for i in range(len(CSsizes)-1):
		avgNumPkts[offset:(offset+len(cacheProbs)),ind-i] = avgNumPkts[offset:(offset+len(cacheProbs)),ind-(i+1)]
		errorBar[offset:(offset+len(cacheProbs)),ind-i] = errorBar[offset:(offset+len(cacheProbs)),ind-(i+1)]
	
	avgNumPkts[offset:(offset+len(cacheProbs)),0] = tempy1
	errorBar[offset:(offset+len(cacheProbs)),0] = tempy11
	
		
	offset +=len(cacheProbs)
# end of the lossrate for 


#-------------------------- PLOTTING--------------------------------------

# Plot for number of pkts transmitted versus cache size
p, ax = plt.subplots()
p1 = ax.errorbar(xAxisCSsizes, avgNumPkts[0,:], yerr=errorBar[0,:], fmt='kD-', linewidth=3.0, ms=6.0)
p2 = ax.errorbar(xAxisCSsizes, avgNumPkts[2,:], yerr=errorBar[2,:], fmt='ro-', linewidth=3.0, ms=6.0)
p3 = ax.errorbar(xAxisCSsizes, avgNumPkts[4,:], yerr=errorBar[4,:], fmt='bs-', linewidth=3.0, ms=6.0)
p4 = ax.errorbar(xAxisCSsizes, avgNumPkts[6,:], yerr=errorBar[6,:], fmt='g^-', linewidth=3.0, ms=6.0)
plt.rcParams.update({'font.size': 30})
plt.xlabel('Content store size')
plt.ylabel('Number of messages transmitted')
plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
plt.legend([p1, p2, p3, p4], ['Content streams 2, Caching probability 100%', 'Content streams 4, Caching probability 100%', 
'Content streams 8, Caching probability 100%', 'Content streams 12, Caching probability 100%'], loc='best')
#       plt.xlim([-5, 55])
plt.grid()
plt.show()






p, ax = plt.subplots()
p5 = ax.errorbar(xAxisCSsizes, avgNumPkts[1,:], yerr=errorBar[1,:], fmt='kD--', linewidth=3.0, ms=6.0)
p6 = ax.errorbar(xAxisCSsizes, avgNumPkts[3,:], yerr=errorBar[3,:], fmt='ro--', linewidth=3.0, ms=6.0)
p7 = ax.errorbar(xAxisCSsizes, avgNumPkts[5,:], yerr=errorBar[5,:], fmt='bs--', linewidth=3.0, ms=6.0)
p8 = ax.errorbar(xAxisCSsizes, avgNumPkts[7,:], yerr=errorBar[7,:], fmt='g^--', linewidth=3.0, ms=6.0)
plt.rcParams.update({'font.size': 30})
plt.xlabel('Content store size')
plt.ylabel('Number of messages transmitted')
plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
plt.legend([p5, p6, p7, p8], ['Content streams 2, Caching probability 50%', 'Content streams 4, Caching probability 50%', 
'Content streams 8, Caching probability 50%', 'Contentstreams 12, Caching probability 50%'], loc='best')
#	plt.xlim([-5, 55])
plt.grid()
plt.show()
