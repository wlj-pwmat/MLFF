#!/usr/bin/env python
import argparse
import re
import itertools
import numpy as np
import subprocess
from os import system
from pymatgen.io.vasp import Poscar
from pymatgen.core import Lattice, Structure

ELEMENTS=['H','He','Li','Be','B','C','N','O','F','Ne','Na','Mg','Al','Si','P','S','Cl','Ar','K',  
	'Ca','Sc','Ti','V','Cr','Mn','Fe','Co','Ni','Cu','Zn','Ga','Ge','As','Se','Br','Kr','Rb','Sr','Y','Zr', 
	'Nb','Mo','Tc','Ru','Rh','Pd','Ag','Cd','In','Sn','Sb','Te','I','Xe','Cs','Ba','La','Ce','Pr','Nd',  
	'Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg', 
	'Tl','Pb','Bi','Po','At','Rn','Fr','Ra','Ac','Th','Pa','U','Np','Pu','Am','Cm','Bk','Cf','Es','Fm', 
	'Md','No','Lr']

def vasp2pwmat(inputfile, outputfile, iteration):
	parser = Poscar.from_file(inputfile)
	structure = parser.structure
	
	#lattice
	latt = structure.lattice
	if np.linalg.det(latt.matrix) < 0:
		latt = Lattice(-latt.matrix)
		#print latt
	#symbols
	syms = [site.specie.symbol for site in structure]
	symbols = [a[0] for a in itertools.groupby(syms)]
	pattern = re.compile(r'\s+')
	formula = re.sub(pattern,'',structure.formula)
	#natoms
	syms = [site.specie.symbol for site in structure]
	natoms = [len(tuple(a[1])) for a in itertools.groupby(syms)]
	totatoms = sum(natoms)
	#frac_coords
	frac_coords= ""
	forces=""
	velocitys=""
	atomicenergys=""
	format_str = "{{:.{0}f}}".format(6)
	for (i, site) in enumerate(structure):
		coords = site.frac_coords
		atom_symbol = site.specie.symbol
		line = str(ELEMENTS.index(atom_symbol)+1)+" "
		forces += line +"0.000000 0.000000 0.000000\n"
		velocitys += line +"0.000000 0.000000 0.000000\n"
		atomicenergys += line +"0.000000 0.000000 0.000000\n"
		line +=  " ".join([format_str.format(c) for c in coords])
		if parser.selective_dynamics is not None:
			sd = ["1" if j else "0" for j in parser.selective_dynamics[i]]
			line += " %s %s %s" % (sd[0], sd[1], sd[2])+"\n"
		else:
			line += " %s %s %s" % (1, 1, 1)+"\n"
		frac_coords +=line
	#write file
	get_lines = ' '+str(totatoms)+' atoms,Iteration (fs) =    '+iteration+', Etot,Ep,Ek (eV) =   , SCF ='+'\n     MD_INFO: METHOD(1-VV,2-NH,3-LV,4-LVPR,5-NHRP) TIME(fs) TEMP(K) DESIRED_TEMP(K) AVE_TEMP(K) TIME_INTERVAL(fs) TOT_TEMP(K)\n              0 0 0 0 0 0 0\n     MD_LV_INFO:\n'+' Lattice vector (Angstrom)\n'+str(latt)+'\n Position (normalized), move_x, move_y, move_z\n'+frac_coords+' Force (-force, eV/Angstrom)\n'+forces+' Velocity (bohr/fs)\n'+velocitys+' Atomic-Energy, Etot(eV),E_nonloc(eV),Q_atom:dE(eV)=  0\n'+atomicenergys+' -------------------------------------------------\n'
	output_file=open(outputfile,"a+")
	output_file.write(get_lines)
	output_file.close()




parser = argparse.ArgumentParser('manual')
parser.add_argument("-f",type=str,default="XDATCAR")
parser.add_argument("-o",type=str,default="MOVEMENT")
args = parser.parse_args()

frames = int(subprocess.getoutput('grep -c Direct ' + args.f))
for frame in range(frames):
	system('xdat2poscar ' + str(frame))
	vasp2pwmat("POSCAR",args.o,str(frame))
