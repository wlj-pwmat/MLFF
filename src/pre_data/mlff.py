#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# liuliping: do NOT change the order of "import" and "path operation"
import os
import sys
codepath=os.path.abspath(sys.path[0])
sys.path.append(codepath+'/../src/lib')
sys.path.append(os.getcwd())

os.system('mkdir -p input output fread_dfeat')
# liuliping: diy parameters in calculation_dir/parameters.py; other parameters use src/lib/default_para.py===old parameters.py
import use_para as pm
import parse_input
parse_input.parse_input()
# liuliping: parameters changed
pm.fortranFitSourceDir = codepath + '/../src/fit'
import prepare as pp
#import lppData as lppData
import fortran_fitting as ff
# genFeatInputFile='./gen_feature.in'


pp.prepare_dir_info()

if pm.isCalcFeat:
    # delete trainData if old files exist
    print('deleting old features and feature logs')
    os.system('rm -f ' + pm.trainSetDir + '/t*')
    os.system('rm -f ' + pm.trainSetDir + '/i*')
    #os.system('rm -f ' + pm.trainSetDir + '/lppData.txt')

    if pm.dR_neigh:
        os.system('rm ' + pm.dRneigh_path)

    pp.collectAllSourceFiles()
    pp.savePath()
    pp.combineMovement()
    pp.writeGenFeatInput()
    os.system('cp '+ pm.fbinListPath +' ./input/')
    
    calFeatGrid=False

    for i in range(pm.atomTypeNum):
        if pm.Ftype1_para['iflag_grid'][i] == 3 or pm.Ftype2_para['iflag_grid'][i] == 3:
            calFeatGrid=True
            pp.calFeatGrid()
    print('generating feature')
    for i in pm.use_Ftype:
        # liuliping: gen_2b_feature in PATH
        # command=pm.genFeatDir+"/"+pm.Ftype_name[i]+".x > ./output/out"+str(i)
        command=pm.Ftype_name[i]+".x > ./output/out"+str(i)
        print(command)
        os.system(command)
else:
    os.system('cp '+pm.fbinListPath+' ./input/')
    pp.writeGenFeatInput()
    pp.collectAllSourceFiles()

if pm.isFitVdw:
    print('fitting vdw')
    ff.fit_vdw()
else:
    if hasattr(pm, 'vdwInput'):
        print("vdwInput found; use diy vdw parameters in parameters.py")
        pp.writeVdwInput(pm.fitModelDir, vdw_input)
    pp.prepare_novdw()    # create 0 vdw

if pm.isFitLinModel:
    ff.fit()

if pm.isRunMd:
    # import preparatory_work as ppw
    from md_runner import MdRunner

    mdRunner=MdRunner()
    if pm.mdRunModel=='opt':
        mdRunner.runOPT(fmax=pm.mdOptfmax,steps=pm.mdOptsteps)
    else:
        for i in range(pm.mdStepNum):
            mdRunner.runStep()
    mdRunner.final()

# liuliping MD_code.NEW, md100 workflow
if pm.isNewMd100:
    os.system('rm -f MOVEMENT')
    import md100
    imodel = 1    # 1:linear;  2:VV;   3:NN;
    num_process = 1
    #print (pm.imodel)
    if hasattr(pm, 'imodel'):
        imodel = pm.imodel

    if hasattr(pm, 'num_process'):
        num_process = pm.num_process
    print (imodel)
    md100.run_md100(imodel=imodel, atom_type=pm.atomType, num_process=num_process)

