__author__ = 'kanaan' 'July 3 2015'

import os
from variables.subject_list import *
from utilities.utils import mkdir_path
import nibabel as nb
import numpy as np

def calculate_voxel_statistics(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Calculating Voxel statistics for subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'


        print '1. grabbing correct files'
        print ''
        # input files
        spm_dir       = os.path.join(workspace_dir, subject, 'segmentation_spm')

        acc_mask      = os.path.join(workspace_dir, subject, 'svs_voxel_mask', '%s%s_ACC_RDA_MASK.nii'%(subject,workspace_dir[-10:-9]))
        tha_mask      = os.path.join(workspace_dir, subject, 'svs_voxel_mask', '%s%s_THA_RDA_MASK.nii'%(subject,workspace_dir[-10:-9]))
        str_mask      = os.path.join(workspace_dir, subject, 'svs_voxel_mask', '%s%s_STR_RDA_MASK.nii'%(subject,workspace_dir[-10:-9]))

        spm_gm        = os.path.join(spm_dir, 'TISSUE_CLASS_1_GM_BIN.nii.gz')
        spm_wm        = os.path.join(spm_dir, 'TISSUE_CLASS_2_WM_BIN.nii.gz')
        spm_cm        = os.path.join(spm_dir, 'TISSUE_CLASS_3_CSF_BIN.nii.gz')

        # output folders
        mkdir_path(os.path.join(workspace_dir, subject, 'svs_voxel_stats'))
        stats_dir = os.path.join(workspace_dir, subject, 'svs_voxel_stats')

        print '2. Calculating tissue proportions'
        def calc_props(mask_file, seg_gm, seg_wm, seg_cm, voxel_name):

            if not os.path.isfile(mask_file):
                print 'IOError: [Errno 2] SVS %s mask Does not exist, create masks and come back' %voxel_name

            else:
                if os.path.isfile(os.path.join(stats_dir, '%s_voxel_statistics_spm.txt'%voxel_name)):
                    print 'Voxel statistics already calculated ... moving on'

                else:
                    #grab data
                    spm_gm_data = nb.load(seg_gm).get_data().squeeze()
                    spm_wm_data = nb.load(seg_wm).get_data().squeeze()
                    spm_cm_data = nb.load(seg_cm).get_data().squeeze()
                    vox_data    = nb.load(mask_file).get_data().squeeze()

                    #multiply SVS ROI with segmented data for ACC
                    vox_spm_gm = vox_data * spm_gm_data
                    vox_spm_wm = vox_data * spm_wm_data
                    vox_spm_cm = vox_data * spm_cm_data

                    #extract stats from segmentation for acc
                    vox_total_svs    = np.sum(vox_data)
                    vox_total_spm_gm = np.sum(vox_spm_gm)
                    vox_total_spm_wm = np.sum(vox_spm_wm)
                    vox_total_spm_cm = np.sum(vox_spm_cm)

                    percent_svs      = float(vox_total_svs)/ float(vox_total_svs)
                    percent_spm_gm   = np.round(float(vox_total_spm_gm) / float(vox_total_svs), 3)
                    percent_spm_wm   = np.round(float(vox_total_spm_wm) / float(vox_total_svs), 3)
                    percent_spm_cm   = np.round(float(vox_total_spm_cm) / float(vox_total_svs), 3)
                    sum_spm          =  np.round(float(percent_spm_gm + percent_spm_wm + percent_spm_cm), 3)

                    print '%s.....' %voxel_name
                    print '...%s SPM NewSegment Tissue Proportions = %s%% GM, %s%% WM, %s%% CSF = %s'  %(voxel_name, percent_spm_gm, percent_spm_wm, percent_spm_cm, sum_spm)

                    spm_txt  = os.path.join(stats_dir, '%s_voxel_statistics_spm.txt'%voxel_name)
                    write_spm = open(spm_txt, 'w')
                    write_spm.write('%s, %s, %s, %s'%(percent_spm_gm, percent_spm_wm, percent_spm_cm, sum_spm))
                    write_spm.close()

        calc_props(acc_mask, spm_gm, spm_wm, spm_cm, 'ACC')
        calc_props(tha_mask, spm_gm, spm_wm, spm_cm, 'THA')
        calc_props(str_mask, spm_gm, spm_wm, spm_cm, 'STR')

        print '========================================================================================'

if __name__ == "__main__":
    calculate_voxel_statistics(test_subject, workspace_patients_a)