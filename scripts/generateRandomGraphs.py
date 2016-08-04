import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

numOfNodes=30
numSrc=10
allNodes=range(0,numOfNodes)

#srcNodes=random.sample(range(0, numOfNodes), numSrc)
#consumerNodes=[node for node in allNodes if node not in srcNodes]
srcNodes=[29,24,0,22,18,25,5,23,6,15]
consumerNodes=[1,2,3,4,7,8,9,10,11,12,13,14,16,17,19,20,21,26,27,28]

#f=open('srcConsumerNodesBA1_large_network.txt','w')
#f.writelines(["%d," % (item+1)  for item in srcNodes])
#f.write('\n')
#f.writelines(["%d," % (item+1)  for item in consumerNodes])
#f.write('\n')

#f=open('srcConsumerNodes.txt','r')
#srcNodes=[int(x) for x in f.readline().split(',')]
#consumerNodes=[int(x) for x in f.readline().split(',')]


#BA network
edgeAttachments=1
G=nx.barabasi_albert_graph(numOfNodes,edgeAttachments)
#WS network
#rewire=5
#rewireProb=0.5
#G=nx.connected_watts_strogatz_graph(numOfNodes, rewire, rewireProb, tries=100, seed=None)

nx.write_edgelist(G, "graphBA1_second.edgelist")
#f.write('%s\n'%G)
#f.close()

#G=nx.read_edgelist("graphBA1.edgelist")


faceStr1="FACEID=`ccn-lite-ctrl -x /tmp/mgmt-relay-"
faceStr2=".sock newUDPface any 127.0.0.1 "
faceStr3=" | ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\\1/'`"
prefixStr1="ccn-lite-ctrl -x /tmp/mgmt-relay-"
prefixStr2=".sock prefixreg "
prefixStr3=" $FACEID ccnx2015 | ccn-lite-ccnb2xml"
linkMat = [[None for x in range(numOfNodes)] for y in range(numOfNodes)]

#average and maximum path length from the chosen sources to the consumers ------------------------
avgPathLenUsed=0.0
maxPathLenUsed=0.0
count=0.0
for i in range(len(srcNodes)):
	for j in range(len(consumerNodes)):
		if (srcNodes[i] != consumerNodes[j]):
			pathLen = nx.shortest_path_length(G,source=srcNodes[i],target=consumerNodes[j])
			avgPathLenUsed += pathLen
			count+=1.0
			if (pathLen > maxPathLenUsed):
				maxPathLenUsed = pathLen

avgPathLenUsed=avgPathLenUsed/count
print ('Average path len = %f'%avgPathLenUsed)
print ('Max path len = %d'%maxPathLenUsed)
print('\n\n\n\n\n')
# to print the required FIB entry commands for the chosen network ---------------------
for src in srcNodes:
        for req in consumerNodes:
                p=nx.shortest_path(G,source=req,target=src) # the source for the shortest path is the consumer and the target is the publisher or the src
                for i in range(len(p)-1):
                        prefix="/n=s"+str(src+1)
                        if linkMat[p[i]][p[i+1]] is None:
                                linkMat[p[i]][p[i+1]]=[]
                        linkMat[p[i]][p[i+1]].append(prefix)
                        


for i in range(numOfNodes):
        for j in range(numOfNodes):
                if linkMat[i][j] is not None:
                        # create FACE
                        print faceStr1+str(i+1)+faceStr2+str(9000+j+1)+faceStr3
                        uniquePrefix = set(linkMat[i][j])
                        for pr in list(uniquePrefix):
                                # create prefix
                                print prefixStr1+str(i+1)+prefixStr2+pr+prefixStr3



# graphs------------------------------
degrees = nx.degree_histogram(G)
degreeDist=np.array(degrees)/float(sum(degrees))
plt.figure(1)
plt.bar(range(0,len(degreeDist)), degreeDist)
plt.rcParams.update({'font.size': 40})
plt.xlabel('Degree')
plt.ylabel('Fraction of nodes')
plt.title('Degree distibution of %s'%G)
#nx.convert_node_labels_to_integers(G, first_label=100, ordering='default', label_attribute=None)

colorStr=np.array(['k' for x in range(numOfNodes)])
colorStr[srcNodes]='r'
colorStr[consumerNodes]='c'
plt.figure(2)
#nx.draw_circular(G, arrows=True, with_labels=True,node_color=colorStr)
nx.draw_networkx(G,pos=None, arrows=True, with_labels=True,node_color=colorStr)
#nx.convert_node_labels_to_integers(G, first_label=1, ordering='default', label_attribute=None)
#nx.draw_networkx(G,pos=None, arrows=True, with_labels=True)
plt.title('Network visualization of %s'%G)
plt.show()

