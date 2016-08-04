import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_RECEPTION_RATE = True
PLOT_NUM_OF_PKTS_VS_LOSS_RATE = True

numOfNodes=15
srcNodes=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
consumerNodes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
runTime=100
dataFolderStr="topology4ProbCaching_lossyLinks_"
avgNumPktsFilename="numberOfTransmissionsLog.txt"

CSsizes=np.array([1, 2, 3, 5, 15, 25, 50, 0])
xAxisCSsizes=np.array([0, 1, 2, 3, 5, 15, 25, 50])
cacheProbs=np.array([100, 90, 70, 50])
lossRates=np.array([5, 10, 15, 20, 25])
lossyLinksCSsizes=np.array([0, 5, 25, 50])
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

#------------------------------------------------------------------

avgNumPkts=np.zeros([len(cacheProbs),len(CSsizes)])
errorBar=np.zeros([len(cacheProbs),len(CSsizes)])

avgNumPktsLossyLinks=np.zeros([len(lossyLinksCSsizes),len(lossRates)])
errorBarLossyLinks=np.zeros([len(lossyLinksCSsizes),len(lossRates)])

avgReceptionRateLossyLinks=np.zeros([len(lossyLinksCSsizes),len(lossRates)])
avgReceptionRateErrorBarLossyLinks=np.zeros([len(lossyLinksCSsizes),len(lossRates)])

avgReceptionRate=np.zeros([len(cacheProbs),len(CSsizes)])
avgReceptionRateErrorBar=np.zeros([len(cacheProbs),len(CSsizes)])

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

for lr in range(len(lossRates)):
	dataFolders = dataFolderStr+str(lossRates[lr])+"per/"
	fo = open(dataFolders+avgNumPktsFilename, "r")
	print "Reading file "+dataFolders+avgNumPktsFilename
	# Fix prob caching
	for i in range(len(cacheProbs)):
		for j in range(len(CSsizes)):
			tempArr=[]
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
	
			avgNumPkts[i,j]=np.mean(tempArr)
			errorBar[i,j]= 2.262*np.std(tempArr)/(math.sqrt(numRuns))
	
			if PLOT_RECEPTION_RATE:
				avgReceptionRate[i,j] = np.mean(tempRecepRate)
				avgReceptionRateErrorBar[i,j] = 2.262*np.std(tempRecepRate)/(math.sqrt(numRuns))
	
	
	
	fo.close()

	# this is because the x axis is not in increasing order we have added the zero 
	#cache size in the end, so we need to flip it to the other side
	ind=len(CSsizes)-1
	
	tempy1=copy.deepcopy(avgNumPkts[:,ind])
	tempy11=copy.deepcopy(errorBar[:,ind])
	for i in range(len(CSsizes)-1):
		avgNumPkts[:,ind-i] = avgNumPkts[:,ind-(i+1)]
		errorBar[:,ind-i] = errorBar[:,ind-(i+1)]
	
	avgNumPkts[:,0] = tempy1
	errorBar[:,0] = tempy11
	
	if PLOT_RECEPTION_RATE:
		tempy2=copy.deepcopy(avgReceptionRate[:,ind])
		tempy22=copy.deepcopy(avgReceptionRateErrorBar[:,ind])
		for i in range(len(CSsizes)-1):
        		avgReceptionRate[:,ind-i] = avgReceptionRate[:,ind-(i+1)]
			avgReceptionRateErrorBar[:,ind-i] = avgReceptionRateErrorBar[:,ind-(i+1)]
	
		avgReceptionRate[:,0] = tempy2
		avgReceptionRateErrorBar[:,0] = tempy22
		
	# to save only the required terms for the loss rate plot
	avgNumPktsLossyLinks[0,lr] = avgNumPkts[0,0]
	avgNumPktsLossyLinks[1,lr] = avgNumPkts[0,4]
	avgNumPktsLossyLinks[2,lr] = avgNumPkts[0,6]
	avgNumPktsLossyLinks[3,lr] = avgNumPkts[0,7]
	errorBarLossyLinks[0,lr]  = errorBar[0,0]
	errorBarLossyLinks[1,lr]  = errorBar[0,4]
	errorBarLossyLinks[2,lr]  = errorBar[0,6]
	errorBarLossyLinks[3,lr]  = errorBar[0,7]

        avgReceptionRateLossyLinks[0,lr] = avgReceptionRate[0,0]
        avgReceptionRateLossyLinks[1,lr] = avgReceptionRate[0,4]
        avgReceptionRateLossyLinks[2,lr] = avgReceptionRate[0,6]
        avgReceptionRateLossyLinks[3,lr] = avgReceptionRate[0,7]
        avgReceptionRateErrorBarLossyLinks[0,lr]  = avgReceptionRateErrorBar[0,0]
        avgReceptionRateErrorBarLossyLinks[1,lr]  = avgReceptionRateErrorBar[0,4]
        avgReceptionRateErrorBarLossyLinks[2,lr]  = avgReceptionRateErrorBar[0,6]
        avgReceptionRateErrorBarLossyLinks[3,lr]  = avgReceptionRateErrorBar[0,7]

# end of the lossrate for 







#-------------------------- PLOTTING--------------------------------------

#plot number of pkts versus loss rate
if PLOT_NUM_OF_PKTS_VS_LOSS_RATE:
	s, axs = plt.subplots()
	s1 = axs.errorbar(lossRates, avgNumPktsLossyLinks[0,:], yerr=errorBarLossyLinks[0,:], fmt='kD-', linewidth=3.0, ms=6.0)
	s2 = axs.errorbar(lossRates, avgNumPktsLossyLinks[1,:], yerr=errorBarLossyLinks[1,:], fmt='ro-', linewidth=3.0, ms=6.0)
	s3 = axs.errorbar(lossRates, avgNumPktsLossyLinks[2,:], yerr=errorBarLossyLinks[2,:], fmt='bs-', linewidth=3.0, ms=6.0)
	s4 = axs.errorbar(lossRates, avgNumPktsLossyLinks[3,:], yerr=errorBarLossyLinks[3,:], fmt='g^-', linewidth=3.0, ms=6.0)
	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Link error rate %')
	plt.ylabel('Number of messages transmitted')
	plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
	plt.legend([s1, s2, s3, s4], ['CS size 0', 'CS size 5', 'CS size 25', 'CS size 50'], loc='best')
	#plt.xlim([0, 50])
	plt.grid()
	plt.show()


# Plot for reception rate versus CS size fore different cache probabilities
if PLOT_RECEPTION_RATE:
	r, axr = plt.subplots()
	r1 = axr.errorbar(lossRates, avgReceptionRateLossyLinks[0,:], yerr=avgReceptionRateErrorBarLossyLinks[0,:], fmt='kD-', linewidth=3.0, ms=6.0)
	r2 = axr.errorbar(lossRates, avgReceptionRateLossyLinks[1,:], yerr=avgReceptionRateErrorBarLossyLinks[1,:], fmt='ro-', linewidth=3.0, ms=6.0)
	r3 = axr.errorbar(lossRates, avgReceptionRateLossyLinks[2,:], yerr=avgReceptionRateErrorBarLossyLinks[2,:], fmt='bs-', linewidth=3.0, ms=6.0)
	r4 = axr.errorbar(lossRates, avgReceptionRateLossyLinks[3,:], yerr=avgReceptionRateErrorBarLossyLinks[3,:], fmt='g^-', linewidth=3.0, ms=6.0)
	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Link error rate %')
	plt.ylabel('Reception rate')
	plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
	plt.legend([r1, r2, r3, r4], ['CS size 0', 'CS size 5', 'CS size 25', 'CS size 50'], loc='best')
#	plt.xlim([0, 50])
	plt.grid()
	plt.show()

