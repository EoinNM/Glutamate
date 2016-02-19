__author__ = 'kanaan' 'July 24 2015'


import os
import subprocess
import shutil
from variables.subject_list import *
from utilities.utils import mkdir_path


def run_JN_frequency_and_phase_drift_correction(population, workspace_dir):

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

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                       Running Frequency  and Phase Drift Correction
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # inputs
        twix_dir = os.path.join(workspace_dir, subject, 'svs_twix')

        print 'ACC: Running Spectral Registration at 1.8ppm with 0,0,3.75,0 Phase drift correction'
        ### ACC spectral registration at at  1.8 PPM
        acc_dir = os.path.join(twix_dir, 'ACC')
        os.chdir(acc_dir)
        preproc_acc = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_LimitedRange(\'ACC\') ; quit;"']

        if not os.path.isfile(os.path.join(twix_dir, 'ACC', 'ACC', 'ACC_lcm')):
            subprocess.call(preproc_acc)

        print 'THA: Running Spectral Registration at 4.2ppm with 0,0,3.75,0 Phase drift correction'
        ### THA spectral registration at at  4.2 PPM
        tha_dir = os.path.join(twix_dir, 'THA')
        os.chdir(tha_dir)
        preproc_tha = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_WaterRange(\'THA\') ; quit;"']
        if not os.path.isfile(os.path.join(twix_dir, 'THA', 'THA', 'THA_lcm')):
            subprocess.call(preproc_tha)

        print 'STR: Running Spectral Registration at 4.2ppm with 0,0,3.75,0 Phase drift correction'
        # ### STR spectral registration at at  4.2 PPM
        str_dir = os.path.join(twix_dir, 'STR')
        os.chdir(str_dir)
        preproc_str = ['matlab',  '-nodesktop', '-nosplash', '-noFigureWindows', '-r "run_pressproc_WaterRange(\'STR\') ; quit;"']
        if not os.path.isfile(os.path.join(twix_dir, 'STR', 'STR', 'STR_lcm')):
            subprocess.call(preproc_str)

if __name__ == "__main__":
    # run_JN_frequency_and_phase_drift_correction(['TR4T'], workspace_controls_a)
    # run_JN_frequency_and_phase_drift_correction(controls_a, workspace_controls_a)
    # run_JN_frequency_and_phase_drift_correction(controls_b, workspace_controls_b)
    # run_JN_frequency_and_phase_drift_correction(patients_a_twix, workspace_patients_a)
    # run_JN_frequency_and_phase_drift_correction(patients_b_twix, workspace_patients_b)
    run_JN_frequency_and_phase_drift_correction(['NL2P'], workspace_patients_b)
