import random
import sys
import numpy as np

if len(sys.argv) != 3:
	print 'ERROR !!'
	print 'usage shuffleArray.py <original names filenale> <consumer ID>'
	exit(0)


with open(sys.argv[1]) as f:
	names = np.array(f.readlines())

random.shuffle(names)

#np.savetxt('src'+str(sys.argv[2])+'_'+str(sys.argv[1]), names, ,delimiter '', fmt="%s")
thefile = open('src'+str(sys.argv[2])+'_'+str(sys.argv[1]), 'w')
for item in names:
  thefile.write("%s" % item)
