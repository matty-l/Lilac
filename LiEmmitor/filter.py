""" This script filters color maps """

read = open('../colormap.txt','r')
write = open('colormap.txt','w')
write.write("{")

for i,line in enumerate(read):
	if i != 0:
		write.write(",\n")
		
	part = line.split()
	temp = part[0]
	hex = '0x'+part[-1][1:]
	write.write(''.join(['{',temp,',',hex,'}']))
	
print(i)

write.write("}")
write.close()
read.close()