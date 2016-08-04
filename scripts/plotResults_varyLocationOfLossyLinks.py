import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True
PLOT_RECEPTION_RATE = True

numOfNodes=28
srcNodes=[1, 2, 3, 4]
consumerNodes=[5, 6, 7, 8, 9, 10]
runTime=100
avgNumPktsFilename="numberOfTransmissionsLog.txt"

CSsizes=np.array([1, 2, 3, 5, 15, 25, 50, 0])
xAxisCSsizes=np.array([0, 1, 2, 3, 5, 15, 25, 50])
cacheProbs=np.array([100, 50])
lossRate=10
folders=["topology5ProbCaching_EdgeLossyLinks_10per/", "topology5ProbCaching_CoreLossyLinks_10per/"]
numRuns=10

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

avgNumPkts=np.zeros([len(cacheProbs)*2,len(CSsizes)])
errorBar=np.zeros([len(cacheProbs)*2,len(CSsizes)])
avgReceptionRate=np.zeros([len(cacheProbs)*2,len(CSsizes)])
avgReceptionRateErrorBar=np.zeros([len(cacheProbs)*2,len(CSsizes)])

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
for lo in folders:
	dataFolders = lo
	fo = open(dataFolders+avgNumPktsFilename, "r")
	print "Reading file "+dataFolders+avgNumPktsFilename
	# Fix prob caching
	for i in range(len(cacheProbs)):
		for j in range(len(CSsizes)):
			tempArr=[]
			tempCDarr=[]
			tempRecepRate=[]
			for k in range(numRuns):
				ln=fo.readline()
				lnlist=ln.split(":")
				numInt=int(lnlist[1])
				numCnt=int(lnlist[3])
				totalPkts=numInt + numCnt
				tempArr.append(totalPkts)
				nameStr1 = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/log_node"
				nameStr2 = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/ccnlitePeek_log.txt"
				# for finding reception rate
				if PLOT_RECEPTION_RATE:
					tempRecepRate.append(computeReceptionRate( consumerNodes, nameStr2, COreceived, COnotReceived ))
	
			avgNumPkts[i+offset,j]=np.mean(tempArr)
			errorBar[i+offset,j]= 2.262*np.std(tempArr)/(math.sqrt(numRuns))
	
			if PLOT_RECEPTION_RATE:
				avgReceptionRate[i+offset,j] = np.mean(tempRecepRate)
				avgReceptionRateErrorBar[i+offset,j] = 2.262*np.std(tempRecepRate)/(math.sqrt(numRuns))
		
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
	
	if PLOT_RECEPTION_RATE:
		tempy2=copy.deepcopy(avgReceptionRate[offset:(offset+len(cacheProbs)),ind])
		tempy22=copy.deepcopy(avgReceptionRateErrorBar[offset:(offset+len(cacheProbs)),ind])
		for i in range(len(CSsizes)-1):
        		avgReceptionRate[offset:(offset+len(cacheProbs)),ind-i] = avgReceptionRate[offset:(offset+len(cacheProbs)),ind-(i+1)]
			avgReceptionRateErrorBar[offset:(offset+len(cacheProbs)),ind-i] = avgReceptionRateErrorBar[offset:(offset+len(cacheProbs)),ind-(i+1)]
	
		avgReceptionRate[offset:(offset+len(cacheProbs)),0] = tempy2
		avgReceptionRateErrorBar[offset:(offset+len(cacheProbs)),0] = tempy22
		
	offset=len(cacheProbs)
# end of the lossrate for 


#-------------------------- PLOTTING--------------------------------------

# Plot for number of pkts transmitted versus cache size
if PLOT_NUM_OF_PKTS:
	p, ax = plt.subplots()
	p1 = ax.errorbar(xAxisCSsizes, avgNumPkts[0,:], yerr=errorBar[0,:], fmt='kD-', linewidth=3.0, ms=7.0)
	p2 = ax.errorbar(xAxisCSsizes, avgNumPkts[1,:], yerr=errorBar[1,:], fmt='ro-', linewidth=3.0, ms=7.0)

	p3 = ax.errorbar(xAxisCSsizes, avgNumPkts[2,:], yerr=errorBar[2,:], fmt='bs--', linewidth=3.0, ms=7.0)
	p4 = ax.errorbar(xAxisCSsizes, avgNumPkts[3,:], yerr=errorBar[3,:], fmt='g^--', linewidth=3.0, ms=7.0)
	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Content store size')
	plt.ylabel('Number of messages transmitted')
	plt.title('Fixed_Random + LRU \n 10% link error rate')
	plt.legend([p1, p2, p3, p4], ['Loss near consumers, Cache prob. 100%', 'Loss near consumers, Cache prob. 50%', 
	'Loss near publishers, Cache prob. 100%', 'Loss near publishers, Cache prob. 50%'], loc='best')
#	plt.xlim([-5, 55])
	plt.grid()
	plt.show()

# Plot for reception rate versus CS size fore different cache probabilities
if PLOT_RECEPTION_RATE:
	r, axr = plt.subplots()
	r1 = axr.errorbar(xAxisCSsizes, avgReceptionRate[0,:], yerr=avgReceptionRateErrorBar[0,:], fmt='kD-', linewidth=3.0, ms=7.0)
	r2 = axr.errorbar(xAxisCSsizes, avgReceptionRate[1,:], yerr=avgReceptionRateErrorBar[1,:], fmt='ro-', linewidth=3.0, ms=7.0)

	r3 = axr.errorbar(xAxisCSsizes, avgReceptionRate[2,:], yerr=avgReceptionRateErrorBar[2,:], fmt='bs--', linewidth=3.0, ms=7.0)
	r4 = axr.errorbar(xAxisCSsizes, avgReceptionRate[3,:], yerr=avgReceptionRateErrorBar[3,:], fmt='g^--', linewidth=3.0, ms=7.0)
	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Content store size')
	plt.ylabel('Reception rate')
	plt.title('Fixed_Random + LRU \n 10% link error rate')
	plt.legend([r1, r2, r3, r4], ['Loss near consumers, Cache prob. 100%', 'Loss near consumers, Cache prob. 50%',
        'Loss near publishers, Cache prob. 100%', 'Loss near publishers, Cache prob. 50%'], loc='best')
#	plt.xlim([-5, 55])
	plt.ylim([0.85, 1.0])
	plt.grid()
	plt.show()

