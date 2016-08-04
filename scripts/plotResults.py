import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True
PLOT_CACHE_DIVERSITY = False
PLOT_RECEPTION_RATE = True


numOfNodes=15
#srcNodes=[1, 6, 10]
srcNodes=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
consumerNodes=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
runTime=100
dataFolderStr="topology4Setup4LossyLinks_20Per/"
avgNumPktsFilename="topology4ProbCaching_lossyLinks_20per.txt"

fo = open(dataFolderStr+avgNumPktsFilename, "r")
CSsizes=np.array([1, 2, 3, 5, 15, 25, 50, 0])
xAxisCSsizes=np.array([0, 1, 2, 3, 5, 15, 25, 50])
cacheProbs=np.array([100, 90, 70, 50])
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
avgCD=np.zeros([len(CSsizes)-1,len(cacheProbs)])
CDerrorBar=np.zeros([len(CSsizes)-1,len(cacheProbs)])
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


# function to compute cache diversity for one run 
def computeCacheDiversity( numOfNodes, srcNodes, fileNameStr, CSentry, CSnextEntry, maxCacheSize ):
	print fileNameStr
	numOfBlocks=10000
	relayCount=0.0
	filecount=0
	cacheDiv=0.0
	for n in range(numOfNodes):
#		print "node index is ",n
		list2=[]
		countlist=[]
		relayCount += 1.0
		list1=[]
		lineCount=0
		for line in open(fileNameStr+str(n+1)+".txt"):
			lineCount+=1
			if CSentry not in line:
				continue
			else:
				if CSnextEntry not in line:
					components=line.split(":")
					if len(components) != 4:
						break
					else:
						list1.append(components[3])
				else:
					list2.append(list1)
					countlist.append(len(list1))
					list1=[]


 
		filecount += 1
		numOfBlocks = min(numOfBlocks,len(list2))
		if filecount==1:
			unionlist2=copy.deepcopy(list2)
			sumcountlist=copy.deepcopy(countlist)
		else:
			for b in range(numOfBlocks):
				unionlist2[b] = list(set(unionlist2[b]) | set(list2[b]))
				sumcountlist[b] = int(sumcountlist[b]) + int(countlist[b])


	divCount=0
	print "numOfBlocks is ",numOfBlocks
	for b in range(numOfBlocks):
		if (sumcountlist[b] != 0) and (b > float(numOfBlocks)/2):
			cacheDiv += float(len(unionlist2[b]))
         		divCount += 1


	cacheDiv = cacheDiv/divCount
	return [ cacheDiv ]

#---------------------- MAIN -----------------------------------------

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
			nameStr1 = dataFolderStr+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/log_node"
			nameStr2 = dataFolderStr+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/ccnlitePeek_log.txt"
			# for finding cache diversity
			if PLOT_CACHE_DIVERSITY:
				if CSsizes[j] != 0:
					tempCDarr.append(computeCacheDiversity( numOfNodes, srcNodes, nameStr1, CSentry, CSnextEntry, CSsizes[j] ))
			# for finding reception rate
			if PLOT_RECEPTION_RATE:
				tempRecepRate.append(computeReceptionRate( consumerNodes, nameStr2, COreceived, COnotReceived ))

		avgNumPkts[i,j]=np.mean(tempArr)
		errorBar[i,j]= 2.262*np.std(tempArr)/(math.sqrt(numRuns))

		if PLOT_RECEPTION_RATE:
			avgReceptionRate[i,j] = np.mean(tempRecepRate)
			avgReceptionRateErrorBar[i,j] = 2.262*np.std(tempRecepRate)/(math.sqrt(numRuns))

		if PLOT_CACHE_DIVERSITY:
			if CSsizes[j] != 0:
				avgCD[j,i]=np.mean(tempCDarr)
				CDerrorBar[j,i]=2.262*np.std(tempCDarr)/(math.sqrt(numRuns))



fo.close()
# this is because the x axis is not in increasing order we have added the zero 
#cache size in the end, so we need to flip it to the other side
ind=len(CSsizes)-1

tempy1=copy.deepcopy(avgNumPkts[:,ind])
for i in range(len(CSsizes)-1):
	avgNumPkts[:,ind-i] = avgNumPkts[:,ind-(i+1)]

avgNumPkts[:,0] = tempy1

if PLOT_RECEPTION_RATE:
	tempy2=copy.deepcopy(avgReceptionRate[:,ind])
	for i in range(len(CSsizes)-1):
        	avgReceptionRate[:,ind-i] = avgReceptionRate[:,ind-(i+1)]

	avgReceptionRate[:,0] = tempy2


# Plot for number of pkts transmitted versus cache size
p, ax = plt.subplots()
p1 = ax.errorbar(xAxisCSsizes, avgNumPkts[0,:], yerr=errorBar[0,:], fmt='kD-', linewidth=3.0, ms=6.0)
p2 = ax.errorbar(xAxisCSsizes, avgNumPkts[1,:], yerr=errorBar[1,:], fmt='ro-', linewidth=3.0, ms=6.0)
p3 = ax.errorbar(xAxisCSsizes, avgNumPkts[2,:], yerr=errorBar[2,:], fmt='bs-', linewidth=3.0, ms=6.0)
p4 = ax.errorbar(xAxisCSsizes, avgNumPkts[3,:], yerr=errorBar[3,:], fmt='g^-', linewidth=3.0, ms=6.0)
plt.rcParams.update({'font.size': 30})
plt.xlabel('Content store size')
plt.ylabel('Number of messages transmitted')
plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
plt.legend([p1, p2, p3, p4], ['Caching probability 100%', 'Caching probability 90%', 'Caching probability 70%', 'Caching probability 50%'], loc='best')
#plt.xlim([0, 50])
plt.grid()
plt.show()

# Plot cache diversity versus cache probability for different CS sizes
if PLOT_CACHE_DIVERSITY:
	legendStr1 = 'Max. cache size 1'
	legendStr2 = 'Max. cache size 2'
	legendStr3 = 'Max. cache size 3'
	legendStr4 = 'Max. cache size 5'
	legendStr5 = 'Max. cache size 15'
	q, axq = plt.subplots()
	q1 = axq.errorbar(cacheProbs, avgCD[0,:], yerr=CDerrorBar[0,:], fmt='kD-', linewidth=2.0, ms=6.0)
	q2 = axq.errorbar(cacheProbs, avgCD[1,:], yerr=CDerrorBar[1,:], fmt='ro-', linewidth=2.0, ms=6.0)
	q3 = axq.errorbar(cacheProbs, avgCD[2,:], yerr=CDerrorBar[2,:], fmt='bs-', linewidth=2.0, ms=6.0)
	q4 = axq.errorbar(cacheProbs, avgCD[3,:], yerr=CDerrorBar[3,:], fmt='g^-', linewidth=2.0, ms=6.0)
	q5 = axq.errorbar(cacheProbs, avgCD[4,:], yerr=CDerrorBar[4,:], fmt='ch-', linewidth=2.0, ms=6.0)
	plt.rcParams.update({'font.size': 20})
	plt.xlabel('Caching probability %')
	plt.ylabel('Cache diversity without normalization')
	plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
	plt.legend([q1, q2, q3, q4, q5], [legendStr1, legendStr2, legendStr3, legendStr4, legendStr5], loc='best')
	plt.xlim([50, 100])
	plt.grid()
	plt.show()


# Plot for reception rate versus CS size fore different cache probabilities
if PLOT_RECEPTION_RATE:
	r, axr = plt.subplots()
	r1 = axr.errorbar(xAxisCSsizes, avgReceptionRate[0,:], yerr=avgReceptionRateErrorBar[0,:], fmt='kD-', linewidth=3.0, ms=6.0)
	r2 = axr.errorbar(xAxisCSsizes, avgReceptionRate[1,:], yerr=avgReceptionRateErrorBar[1,:], fmt='ro-', linewidth=3.0, ms=6.0)
	r3 = axr.errorbar(xAxisCSsizes, avgReceptionRate[2,:], yerr=avgReceptionRateErrorBar[2,:], fmt='bs-', linewidth=3.0, ms=6.0)
	r4 = axr.errorbar(xAxisCSsizes, avgReceptionRate[3,:], yerr=avgReceptionRateErrorBar[3,:], fmt='g^-', linewidth=3.0, ms=6.0)
	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Content store size')
	plt.ylabel('Reception rate')
	plt.title('Cache decision policies: cache all, fixed probability \n Cache replacement policy: Least recently used')
	plt.legend([r1, r2, r3, r4], ['Caching probability 100%', 'Caching probability 90%', 'Caching probability 70%', 'Caching probability 50%'], loc='best')
#	plt.xlim([0, 50])
	plt.grid()
	plt.show()

