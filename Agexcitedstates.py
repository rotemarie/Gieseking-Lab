#!/usr/bin/python

#-------------------------------------------------------------------------
# Displace mopac geometry along a vibrational mode
#
# Rebecca Gieseking, 8/12/16
#
#-------------------------------------------------------------------------

import string,sys
import pandas as pd

atmasslist = {'H':1,'He':4,'B':11,'C':12,'N':14,'O':16,'F':19,'Na':23,'Mg':24,'Al':27,'Si':28,'P':31,'S':32,'Cl':35,'Cu':63,'As':75,'Se':80,'Br':79,'Ag':107,'Au':197}

# Get base file names
if len(sys.argv) <= 1:
    filename = raw_input("Enter the file name: ")
else:
    filename = sys.argv[1]

##if '.' in filename:
##    filename = filename[:filename.rfind('.')]

if len(sys.argv) <= 3:
    mode = raw_input("Enter the vibrational mode: ")
    disp = raw_input("Enter the displacement: ")
else:
    mode = sys.argv[2]
    disp = sys.argv[3]

# Open files and prepare input
#modes = open('nmodes.inp','r')
inp = open(filename+'.log','r')
new = open(filename+'_'+mode+'_'+disp+'.com','w')

mode = int(mode)
disp = float(disp)



#Read initial geometry from Gaussian
finded_opt = False
finded_std = False
counter = 0
xyzcoord = []
while True:
   iline = inp.readline()
   if finded_std == True:
      if counter == 4:
         while '-----' not in iline:
	    line = iline.split()
            if line[1] == '79':
	       line[1] = 'Au'
            elif line[1] == '16':
               line[1] = 'S'
            elif line[1] == '1':
               line[1] = 'H'
	    for i in [3,4,5]:
	        line[i] = float(line[i])
	    xyzcoord.append([line[1],line[3],line[4],line[5]])
            iline = inp.readline()
         break
      else:
         counter = counter + 1
         continue
   if finded_opt == True:
      if "Standard" in iline:
        finded_std = True
      continue
   if "Optimized" in iline:
      finded_opt = True
      continue
print(xyzcoord)

# Find the charge and spin of the cluster
charge = ''
spin = ''
line = inp.readline()
while 'Charge =' not in line:
    line = inp.readline()
    if 'Charge =' in line:
        cline = line.split()
        charge = cline[2]
        spin = cline[5]
        break



# Find and read the correct mode displacements
xyzmode = []
row = (mode - 1) // 3
col = (mode - 1) % 3
counter = 0
mline = inp.readline()

try:

 while 'Frequencies' not in mline:
    mline = inp.readline()
    if 'Frequencies' in mline:
        counter = counter + 1
	if counter == (row + 1):
	   mline = inp.readline()
           mline = inp.readline()
	   mline = inp.readline()
           mline = inp.readline()
           mline = inp.readline()
           while len(mline.split()) > 3:
              xyzmode.append(mline.split())
              mline = inp.readline()
           break
        else:
	   mline = inp.readline()
	   continue
    else:
      continue
except EOFError:
   print("end of file")

mode_disp = []
j = col*3
for i in range(len(xyzmode)):
   del xyzmode[i][ :2]
   mode_disp.append([float(xyzmode[i][j]),float(xyzmode[i][j+1]),float(xyzmode[i][j+2])])

print(mode_disp)


# Print new input file
new.write('%chk='+filename+'_'+str(mode)+'_'+str(disp)+'.chk'+'\n')
new.write('%nprocshared=16'+'\n')
new.write('%mem=38000mb'+'\n')
new.write('# EOMCCSD(NStates=10, maxcyc=500)genecp integral=dkh0 POP=Full scf=xqc'+'\n')
new.write('\n')
#new.write('Ag'+str(atoms)+' vibrational mode '+str(mode)+' with displacement of '+str(disp)+'\n')
new.write(filename+' '+'vibrational mode '+str(mode)+' with displacement of '+str(disp)+'\n')
new.write('\n')
#if int(atoms) % 2 == 0:
#   new.write('0 1'+'\n')
#else:
#   new.write('0 2'+'\n')
new.write(charge+' '+spin+'\n')
for i in range(0,len(xyzcoord)):
    new.write(string.ljust(str(xyzcoord[i][0]),4))
    for j in range(0,3):
        new.write(string.rjust('%6f'%(xyzcoord[i][j+1]+disp*mode_disp[i][j]),11))
    new.write('\n')
new.write('\n')
new.write('''Ag     0
S    3   1.00
      9.0884420000          -1.9808918797
      7.5407310000           2.7554513347
      2.7940050000           0.22715408381
S    1   1.00
      1.4918135849           1.0000000
S    1   1.00
      0.63579159445          1.0000000
S    1   1.00
      0.10368414161          1.0000000
S    1   1.00
      0.37460004363D-01      1.0000000
P    4   1.00
      4.4512400000          -0.99352103771
      3.6752630000           1.0500525237
      1.2610620905           0.64747532537
      0.54212477498          0.25621550723
P    1   1.00
      0.20221617026          1.0000000
P    1   1.00
      0.91300000000D-01      1.0000000
P    1   1.00
      0.0412000              1.0000000
D    4   1.00
      7.7956672292          -0.17042912377D-01
      2.8926510238           0.23446154803
      1.2474273203           0.44765877533
      0.49313817671          0.39064954560
D    1   1.00
      0.17285032603          1.0000000
F    1   1.00
      1.3971100              1.0000000
****

AG     0
AG-ECP     3     28
f potential
  2
2     14.2200000            -33.68992012
2      7.1100000             -5.53112021
s-f potential
  4
2     13.1300000            255.13936452
2      6.5100000             36.86612154
2     14.2200000             33.68992012
2      7.1100000              5.53112021
p-f potential
  4
2     11.7400000            182.18186871
2      6.2000000             30.35775148
2     14.2200000             33.68992012
2      7.1100000              5.53112021
d-f potential
  4
2     10.2100000             73.71926087
2      4.3800000             12.50211712
2     14.2200000             33.68992012
2      7.1100000              5.53112021


 ''')




#modes.close()
inp.close()
new.close()
