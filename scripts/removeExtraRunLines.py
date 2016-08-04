fi = open("numberOfTransmissionsLog10runs.txt", "r")
fo = open("numberOfTransmissionsLog5runs.txt", "w")

lineCount=0
for line in fi:
	if ((lineCount % 10) <= 4):
		fo.write(line)
	
	lineCount += 1



