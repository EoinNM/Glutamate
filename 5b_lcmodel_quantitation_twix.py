__author__ = 'kanaan' 'July 3 2015'


import os
import subprocess

from variables.subject_list import *
from utilities.utils import mkdir_path
import nibabel as nb
import numpy as np

def run_jamienear_drift_correction(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Running Freuquency and Phase Drift Correction for  subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'

        # inputs
        voxel_dir = os.path.join(workspace_dir, subject, 'ACC')
        run_pressproc = ['matlab', '--version', '8.2' ,'-r , "run_pressproc(\'%s\') ; quit;"'%voxel_dir]
        subprocess.call(run_pressproc)

if __name__ == "__main__":
    run_jamienear_drift_correction(test_subject, workspace_patients_a)

