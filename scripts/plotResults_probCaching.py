import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True
PLOT_RECEPTION_RATE = False
PLOT_CACHE_DIVERSITY = False
#BA1
numOfNodes=30
srcNodes=[30, 25, 1, 23, 19, 26, 6, 24, 7, 16]
consumerNodes=[2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 21, 22, 27, 28, 29]
runTime=200
avgNumPktsFilename="numberOfTransmissionsLog.txt"
cacheProbs=np.array([100, 80, 60])
# low traffic cache sizes
CSsizes=np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30])
numOfObjectsPerSec=5.0
folders=["lossless_lowTraffic_topologyBA1_LRU_probability_based_caching/"]
#folders=["lossless_lowTraffic_topologyBA1_second_LRU_probability_based_caching/"]
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

avgNumPkts=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
errorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

avgReceptionRate=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])
avgReceptionRateErrorBar=np.zeros([len(cacheProbs)*len(folders),len(CSsizes)])

avgCD=np.zeros([len(CSsizes)-1,len(cacheProbs)*len(folders)])
CDerrorBar=np.zeros([len(CSsizes)-1,len(cacheProbs)*len(folders)])
#-------------------------------- CACHE DIVERSITY --------------------------

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


def computeCacheDiversity( numOfNodes, srcNodes, fileNameStr, CSentry, CSnextEntry, maxCacheSize ):
        print fileNameStr
        numOfBlocks=10000
        relayCount=0.0
        filecount=0
        cacheDiv=0.0
        for n in range(numOfNodes):
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
                        	# for finding cache diversity
                        	if PLOT_CACHE_DIVERSITY:
                                	if CSsizes[j] != 0:
                                        	tempCDarr.append(computeCacheDiversity( numOfNodes, srcNodes, nameStr1, CSentry, CSnextEntry, CSsizes[j] ))
				# for finding reception rate
				if PLOT_RECEPTION_RATE:
					tempRecepRate.append(computeReceptionRate( consumerNodes, nameStr2, COreceived, COnotReceived ))
	
			avgNumPkts[i+offset,j]=np.mean(tempArr)
			errorBar[i+offset,j]= 2.262*np.std(tempArr)/(math.sqrt(numRuns))
	
			if PLOT_RECEPTION_RATE:
				avgReceptionRate[i+offset,j] = np.mean(tempRecepRate)
				avgReceptionRateErrorBar[i+offset,j] = 2.262*np.std(tempRecepRate)/(math.sqrt(numRuns))

	                if PLOT_CACHE_DIVERSITY:
        	                if CSsizes[j] != 0:
                	                avgCD[j,i+offset]=np.mean(tempCDarr)
                        	        CDerrorBar[j,i+offset]=2.262*np.std(tempCDarr)/(math.sqrt(numRuns))

		
	fo.close()
	offset+=len(cacheProbs)

#-------------------------- PLOTTING--------------------------------------
# Plot for number of pkts transmitted versus cache size
if PLOT_NUM_OF_PKTS:
	p, ax = plt.subplots()
        p1 = ax.errorbar(CSsizes, avgNumPkts[0,:]/1000.0, yerr=errorBar[0,:]/1000.0, fmt='rd-', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='r', markerfacecolor='r')
        p2 = ax.errorbar(CSsizes, avgNumPkts[1,:]/1000.0, yerr=errorBar[1,:]/1000.0, fmt='bo--', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='b', markerfacecolor='None')
        p3 = ax.errorbar(CSsizes, avgNumPkts[2,:]/1000.0, yerr=errorBar[2,:]/1000.0, fmt='g*-.', linewidth=5.0, ms=20.0, markeredgewidth=2, markeredgecolor='g', markerfacecolor='g')

	plt.rcParams.update({'font.size': 30})
	plt.xlabel('Cache size (number of content objects)')
	plt.ylabel('Number of messages transmitted (X1000)')
	plt.title('Random caching \n LRU')
        plt.legend([p1, p2, p3], ['Cache prob. 100%', 'Cache prob. 80%', 'Cache prob. 60%'], loc='best')
	plt.xlim([0, 30])
	plt.ylim([0,170])
	plt.grid()

# Plot cache diversity versus cache probability for different CS sizes
if PLOT_CACHE_DIVERSITY:
	off=len(cacheProbs)
        legendStr1 = 'Max. cache size 2'
        legendStr2 = 'Max. cache size 5'
        legendStr3 = 'Max. cache size 15'
        legendStr4 = 'Max. cache size 25'
        legendStr5 = 'Max. cache size 50'
#        f, (axq, axs) = plt.subplots(1, 2, sharey=True)
	f, axs = plt.subplots()
#        q1 = axq.errorbar(cacheProbs, avgCD[0,0:off], yerr=CDerrorBar[0,0:off], fmt='kD-', linewidth=2.0, ms=6.0)
#        q2 = axq.errorbar(cacheProbs, avgCD[1,0:off], yerr=CDerrorBar[1,0:off], fmt='ro-', linewidth=2.0, ms=6.0)
#        q3 = axq.errorbar(cacheProbs, avgCD[2,0:off], yerr=CDerrorBar[2,0:off], fmt='bs-', linewidth=2.0, ms=6.0)
#        q4 = axq.errorbar(cacheProbs, avgCD[3,0:off], yerr=CDerrorBar[3,0:off], fmt='g^-', linewidth=2.0, ms=6.0)
#        q5 = axq.errorbar(cacheProbs, avgCD[4,0:off], yerr=CDerrorBar[4,0:off], fmt='ch-', linewidth=2.0, ms=6.0)
        plt.rcParams.update({'font.size': 20})
        plt.xlabel('Caching probability %')
        plt.ylabel('Cache diversity without normalization')
#        axq.set_title('Fixed_Random + LRU \n Time series requests')
#        plt.legend([q1, q2, q3, q4, q5], [legendStr1, legendStr2, legendStr3, legendStr4, legendStr5], loc='best')
#        plt.xlim([50, 100])
	off2=len(cacheProbs)*2
        s1 = axs.errorbar(cacheProbs, avgCD[0,off:off2], yerr=CDerrorBar[0,off:off2], fmt='kD--', linewidth=2.0, ms=6.0)
        s2 = axs.errorbar(cacheProbs, avgCD[1,off:off2], yerr=CDerrorBar[1,off:off2], fmt='ro--', linewidth=2.0, ms=6.0)
        s3 = axs.errorbar(cacheProbs, avgCD[2,off:off2], yerr=CDerrorBar[2,off:off2], fmt='bs--', linewidth=2.0, ms=6.0)
        s4 = axs.errorbar(cacheProbs, avgCD[3,off:off2], yerr=CDerrorBar[3,off:off2], fmt='g^--', linewidth=2.0, ms=6.0)
        s5 = axs.errorbar(cacheProbs, avgCD[4,off:off2], yerr=CDerrorBar[4,off:off2], fmt='ch--', linewidth=2.0, ms=6.0)
	axs.set_title('Fixed_Random + LRU \n Uniform random requests')
        plt.grid()


plt.show()




