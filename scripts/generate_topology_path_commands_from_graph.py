
def find_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = find_path(graph, node, end, path)
                if newpath: return newpath
        return None


def find_all_paths(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not graph.has_key(start):
            return []
        paths = []
        for node in graph[start]:
            if node not in path:
                newpaths = find_all_paths(graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths


def find_shortest_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        shortest = None
        for node in graph[start]:
            if node not in path:
                newpath = find_shortest_path(graph, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest




graph = {'1': ['21'],
             '2': ['21'],
             '3': ['21'],
             '4': ['22'],
             '5': ['22'],
             '6': ['22'],
             '7': ['23'],
             '8': ['23'],
             '9': ['23'],
             '10': ['24'],
             '11': ['24'],
             '12': ['24'],
             '13': ['31'],
             '14': ['31'],
             '15': ['32'],
             '16': ['32'],
             '17': ['33'],
             '18': ['33'],
             '19': ['34'],
             '20': ['34'],
             '21': ['1', '2', '3', '25'],
             '22': ['4', '5', '6', '25'],
             '23': ['7', '8', '9', '26'],
             '24': ['10', '11', '12', '26'],
             '25': ['21', '22', '27'],
             '26': ['23', '24', '28'],
             '27': ['25', '28', '29'],
             '28': ['26', '27', '30'],
             '29': ['27', '31', '32'],
             '30': ['28', '33', '34'],
             '31': ['13', '14', '29'],
             '32': ['15', '16', '29'],
             '33': ['17', '18', '30'],
             '34': ['19', '20', '30']}


#sources=['6','7','8','9','10','11','12','13','14','15']
#requesters=['1','2','3','4','5','6','7','8','9','10']
#numOfNodes=15

sources=['1','2','3','4', '5', '6','7','8','9','10', '11','12']
requesters=['13','14','15', '16', '17', '18', '19', '20']
numOfNodes=34

faceStr1="FACEID=`ccn-lite-ctrl -x /tmp/mgmt-relay-"
faceStr2=".sock newUDPface any 127.0.0.1 "
faceStr3=" | ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\\1/'`"
prefixStr1="ccn-lite-ctrl -x /tmp/mgmt-relay-"
prefixStr2=".sock prefixreg "
prefixStr3=" $FACEID ccnx2015 | ccn-lite-ccnb2xml"
linkMat = [[None for x in range(numOfNodes)] for y in range(numOfNodes)]

for src in sources:
	for req in requesters:
		p=find_shortest_path(graph, req, src)
		for i in range(len(p)-1):
			prefix="/n=s"+src
			if linkMat[int(int(p[i])-1)][int(int(p[i+1])-1)] is None:
				linkMat[int(int(p[i])-1)][int(int(p[i+1])-1)]=[]
			linkMat[int(int(p[i])-1)][int(int(p[i+1])-1)].append(prefix)


for i in range(numOfNodes):
	for j in range(numOfNodes):
		if linkMat[i][j] is not None:
			# create FACE
			print faceStr1+str(i+1)+faceStr2+str(9000+j+1)+faceStr3
			uniquePrefix = set(linkMat[i][j])
			for pr in list(uniquePrefix):
				# create prefix
				print prefixStr1+str(i+1)+prefixStr2+pr+prefixStr3


#print graph
