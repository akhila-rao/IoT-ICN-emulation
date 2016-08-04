import numpy as np
import matplotlib.pyplot as plt
import itertools
import cStringIO
import copy
import math


#------------------------------------------------------------------
PLOT_NUM_OF_PKTS = True
PLOT_DROPPED_PKTS = True
PLOT_RECEPTION_RATE = True
PLOT_NUM_OF_PKTS_LOSSY_OVER_LOSSLESS = True
PLOT_NUM_OF_MSGS_OVER_TRETX = True

#BA1
numOfNodes=30
srcNodes=[30, 25, 1, 23, 19, 26, 6, 24, 7, 16]
consumerNodes=[2, 3, 4, 5, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 21, 22, 27, 28, 29]
runTime=200
avgNumPktsFilename="numberOfTransmissionsLog.txt"
cacheProbs=np.array([100])
CSsizes=np.array([0, 5, 10, 15, 20, 25, 30, 35, 40, 45]) #highh traffic
#CSsizes=np.array([0, 2, 5, 8, 10, 13, 16, 18, 20]) # low traffic
Tretx=np.array([240, 1000])
#Tretx=np.array([240, 480, 720, 1000])
folders=["highTraffic_Pout50per_topologyBA1_UTS_LRU_240ms_Tretx/","highTraffic_Pout50per_topologyBA1_UTS_LRU_1000ms_Tretx/", "highTraffic_lossless_topologyBA1_UTS_LRU/"]
#folders=["highTraffic_Pout50per_topologyBA1_UTS_LRU_240ms_Tretx/", "highTraffic_Pout50per_topologyBA1_UTS_LRU_480ms_Tretx/", "highTraffic_Pout50per_topologyBA1_UTS_LRU_720ms_Tretx/",
#"highTraffic_Pout50per_topologyBA1_UTS_LRU_1000ms_Tretx/", "highTraffic_lossless_topologyBA1_UTS_LRU/"]

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

numPktsSent_over_Tretx=np.zeros([4,len(folders)])
numPktsSent_over_Tretx_errorBar=np.zeros([4,len(folders)])

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
#	fo = open(dataFolders+avgNumPktsFilename, "r")
#	print "Reading file "+dataFolders+avgNumPktsFilename
	# Fix prob caching
	for i in range(len(cacheProbs)):
		for j in range(len(CSsizes)):
			temp1=[]
			temp2=[]
#			temp3=[]
			temp4=[]
			for k in range(numRuns):
				nameStr=dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/log_node"
				[sentCount, droppedCount]=findNumOfSentAndDropped( numOfNodes, nameStr, pktSent, pktDropped )
				temp1.append(sentCount)
                                temp2.append(droppedCount)
				#temp3.append(droppedCount/sentCount)
				nameStr = dataFolders+"cacheProb"+str(cacheProbs[i])+"/CSsize"+str(CSsizes[j])+"/run"+str(k+1)+"/ccnlitePeek_log.txt"
				temp4.append(computeReceptionRate( nameStr, COreceived, COnotReceived ))

			numPktsSent[i+offset,j]=np.mean(temp1)
			numPktsSent_errorBar[i+offset,j]= 2.262*np.std(temp1)/(math.sqrt(numRuns))
                        numPktsDropped[i+offset,j]=np.mean(temp2)
                        numPktsDropped_errorBar[i+offset,j]= 2.262*np.std(temp2)/(math.sqrt(numRuns))
#			linkDropRate[i+offset,j]=np.mean(temp3)
#			linkDropRate_errorBar[i+offset,j] = 2.262*np.std(temp3)/(math.sqrt(numRuns))
                        receptionRate[i+offset,j] = np.mean(temp4)
			receptionRate_errorBar[i+offset,j] = 2.262*np.std(temp4)/(math.sqrt(numRuns))
		
#	fo.close()
	offset+=len(cacheProbs)


# create the data array for metric versus Tretx
numPktsSent_over_Tretx[0,:]=numPktsSent[:,0] # cache size 0
numPktsSent_over_Tretx[1,:]=numPktsSent[:,2] # cache size 10
numPktsSent_over_Tretx[2,:]=numPktsSent[:,4] # cache size 20
numPktsSent_over_Tretx[3,:]=numPktsSent[:,8] # cache size 40
numPktsSent_over_Tretx_errorBar[0,:]=numPktsSent_errorBar[:,0] # cache size 0
numPktsSent_over_Tretx_errorBar[1,:]=numPktsSent_errorBar[:,2] # cache size 10
numPktsSent_over_Tretx_errorBar[2,:]=numPktsSent_errorBar[:,4] # cache size 20
numPktsSent_over_Tretx_errorBar[3,:]=numPktsSent_errorBar[:,8] # cache size 40

#-------------------------- PLOTTING--------------------------------------
# Plot for number of pkts transmitted versus cache size
if PLOT_NUM_OF_PKTS:
	p, ax = plt.subplots()
        p1 = ax.errorbar(CSsizes, numPktsSent[0,:], yerr=numPktsSent_errorBar[0,:], fmt='rD-', linewidth=3.0, ms=10.0)
        p2 = ax.errorbar(CSsizes, numPktsSent[1,:], yerr=numPktsSent_errorBar[1,:], fmt='b*-', linewidth=3.0, ms=10.0)
        p3 = ax.errorbar(CSsizes, numPktsSent[2,:], yerr=numPktsSent_errorBar[2,:], fmt='ks--', linewidth=3.0, ms=10.0)
#        p4 = ax.errorbar(CSsizes, numPktsSent[3,:], yerr=numPktsSent_errorBar[3,:], fmt='co-', linewidth=3.0, ms=10.0)
#        p5 = ax.errorbar(CSsizes, numPktsSent[4,:], yerr=numPktsSent_errorBar[4,:], fmt='k*-', linewidth=3.0, ms=10.0)

	plt.rcParams.update({'font.size': 20})
	plt.xlabel('Content store size (number of content objects)')
	plt.ylabel('Number of messages transmitted')
	plt.title('Lossy links network Vs Lossless network')
	plt.legend([p1, p2, p3], ['T_retx=240 ms','T_retx=1000 ms','Lossless'], loc='best')
#	 plt.xlim([0, 30])
#	 plt.ylim([40000,160000])
	plt.grid()


# Plot the number of pkts dropped in the network
if PLOT_DROPPED_PKTS:
        q, ax = plt.subplots()
        q1 = ax.errorbar(CSsizes, numPktsDropped[0,:], yerr=numPktsDropped_errorBar[0,:], fmt='rD-', linewidth=3.0, ms=10.0)
        q2 = ax.errorbar(CSsizes, numPktsDropped[1,:], yerr=numPktsDropped_errorBar[1,:], fmt='bs-', linewidth=3.0, ms=10.0)
        q3 = ax.errorbar(CSsizes, numPktsDropped[2,:], yerr=numPktsDropped_errorBar[2,:], fmt='gx-', linewidth=3.0, ms=10.0)
        q4 = ax.errorbar(CSsizes, numPktsDropped[3,:], yerr=numPktsDropped_errorBar[3,:], fmt='co-', linewidth=3.0, ms=10.0)
#        q5 = ax.errorbar(CSsizes, numPktsDropped[4,:], yerr=numPktsDropped_errorBar[4,:], fmt='rs--', linewidth=3.0, ms=10.0)
#        q6 = ax.errorbar(CSsizes, numPktsDropped[5,:], yerr=numPktsDropped_errorBar[5,:], fmt='cx--', linewidth=3.0, ms=10.0)

        plt.rcParams.update({'font.size': 20})
        plt.xlabel('Content store size (number of content objects)')
        plt.ylabel('Number of messages dropped')
        plt.title('Lossy links network vs lossless network')
        plt.legend([q1, q2, q3, q4], ['T_retx=240 ms','T_retx=480 ms','T_retx=720 ms','T_retx=1000 ms'], loc='best')
        plt.grid()

# Plot the rate of pkt drop in the network
if PLOT_NUM_OF_PKTS_LOSSY_OVER_LOSSLESS:
        q, ax = plt.subplots()
#        q1 = ax.errorbar(CSsizes, numPktsSent[0,:] - numPktsSent[4,:], yerr=numPktsSent_errorBar[0,:], fmt='kD-', linewidth=3.0, ms=10.0)
#        q2 = ax.errorbar(CSsizes, numPktsSent[1,:] - numPktsSent[4,:], yerr=numPktsSent_errorBar[1,:], fmt='rs-', linewidth=3.0, ms=10.0)
#        q3 = ax.errorbar(CSsizes, numPktsSent[2,:] - numPktsSent[4,:], yerr=numPktsSent_errorBar[2,:], fmt='kx--', linewidth=3.0, ms=10.0)
#        q4 = ax.errorbar(CSsizes, numPktsSent[3,:] - numPktsSent[4,:], yerr=numPktsSent_errorBar[3,:], fmt='ro--', linewidth=3.0, ms=10.0)

        q1 = ax.errorbar(CSsizes, numPktsSent[0,:] - numPktsSent[4,:], yerr=np.sqrt((numPktsSent_errorBar[0,:]**2) - (numPktsSent_errorBar[4,:]**2)), fmt='rD-', linewidth=3.0, ms=10.0)
        q2 = ax.errorbar(CSsizes, numPktsSent[1,:] - numPktsSent[4,:], yerr=np.sqrt((numPktsSent_errorBar[1,:]**2) - (numPktsSent_errorBar[4,:]**2)), fmt='bs-', linewidth=3.0, ms=10.0)
#        q3 = ax.errorbar(CSsizes, numPktsSent[2,:] - numPktsSent[4,:], yerr=np.sqrt((numPktsSent_errorBar[2,:]**2) - (numPktsSent_errorBar[4,:]**2)), fmt='gx-', linewidth=3.0, ms=10.0)
#        q4 = ax.errorbar(CSsizes, numPktsSent[3,:] - numPktsSent[4,:], yerr=np.sqrt((numPktsSent_errorBar[3,:]**2) - (numPktsSent_errorBar[4,:]**2)), fmt='co-', linewidth=3.0, ms=10.0)

        plt.rcParams.update({'font.size': 20})
        plt.xlabel('Content store size (number of content objects)')
        plt.ylabel('number of pkts transmitted in lossy network - number of pkts transmitted in lossless network')
        plt.title('Lossy Vs Lossless network')
        plt.legend([q1, q2], ['T_retx=240 ms','T_retx=1000 ms'], loc='best')
        plt.grid()

# Plot for reception rate versus CS size fore different cache probabilities
if PLOT_RECEPTION_RATE:
	r, axr = plt.subplots()
	r1 = axr.errorbar(CSsizes, receptionRate[0,:], yerr=receptionRate_errorBar[0,:], fmt='rD-', linewidth=3.0, ms=10.0)
	r2 = axr.errorbar(CSsizes, receptionRate[1,:], yerr=receptionRate_errorBar[1,:], fmt='b*-', linewidth=3.0, ms=10.0)
        r3 = axr.errorbar(CSsizes, receptionRate[2,:], yerr=receptionRate_errorBar[2,:], fmt='kx--', linewidth=3.0, ms=10.0)
#        r4 = axr.errorbar(CSsizes, receptionRate[3,:], yerr=receptionRate_errorBar[3,:], fmt='co-', linewidth=3.0, ms=10.0)
#        r5 = axr.errorbar(CSsizes, receptionRate[4,:], yerr=receptionRate_errorBar[4,:], fmt='k*-', linewidth=3.0, ms=10.0)

	plt.rcParams.update({'font.size': 20})
	plt.ylabel('Reception rate')
        plt.xlabel('Content store size (number of content objects)')
        plt.title('Lossy links network')
        plt.legend([r1, r2, r3, r4, r5], ['T_retx=240 ms','T_retx=1000 ms','Lossless'], loc='best')
	plt.grid()

if PLOT_NUM_OF_MSGS_OVER_TRETX:
        p, ax = plt.subplots()
        p1 = ax.errorbar(Tretx, numPktsSent_over_Tretx[0,0:4], yerr=numPktsSent_over_Tretx_errorBar[0,0:4], fmt='rD-', linewidth=3.0, ms=10.0)
        p2 = ax.errorbar(Tretx, numPktsSent_over_Tretx[1,0:4], yerr=numPktsSent_over_Tretx_errorBar[1,0:4], fmt='bs-', linewidth=3.0, ms=10.0)
        p3 = ax.errorbar(Tretx, numPktsSent_over_Tretx[2,0:4], yerr=numPktsSent_over_Tretx_errorBar[2,0:4], fmt='gx-', linewidth=3.0, ms=10.0)
        p4 = ax.errorbar(Tretx, numPktsSent_over_Tretx[3,0:4], yerr=numPktsSent_over_Tretx_errorBar[3,0:4], fmt='co-', linewidth=3.0, ms=10.0)

        plt.rcParams.update({'font.size': 20})
        plt.xlabel('T_retx (ms)')
        plt.ylabel('Number of messages transmitted')
        plt.title('Lossy links network Vs Lossless network')
        plt.legend([p1, p2, p3, p4], ['cache_size = 0 objects', 'cache_size = 10 objects', 'cache_size = 20 objects', 'cache_size = 40 objects'], loc='best')
        plt.grid()


plt.show()
