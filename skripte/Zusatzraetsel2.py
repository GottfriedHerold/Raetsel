#!/usr/bin/python
 
file = open("/usr/share/dict/ngerman","r")

L = [
"PHAWEAQNOQMENNAO".lower() +
"LOOWIESUJEPELJRF".lower(),
"STCEHXNPELQWOBLN".lower(),
"ILHLRUWHAPRTTLLY".lower(),
"JBOESJKJGDUZQNGI".lower(),
"STTWANKAPAOSFHSG".lower()]

for line in file:
	m = L[0][:]
	b = False
	for char in line[0:-1]:
		pos = m.find(char)
		if pos == -1:
			b = True
			continue
		m = m[pos:]
	if b:
		continue
	print(line)
	
		    
	

file.close()






