__author__ = 'kanaan' 'July 3 2015'

import os
from variables.subject_list import *
from utilities.utils import mkdir_path
import nibabel as nb
import numpy as np

def calculate_str_proportions(population, workspace_dir):

    for subject in population:
        print '__________________________________________________________________________'
        print subject
        # input files
        spm_dir       = os.path.join(workspace_dir, subject, 'segmentation_spm')
        stats_dir     = os.path.join(workspace_dir, subject, 'svs_voxel_stats')
        str_mask      = os.path.join(workspace_dir, subject, 'svs_voxel_mask', '%s%s_STR_RDA_MASK.nii'%(subject,workspace_dir[-10:-9]))
        spm_gm        = os.path.join(spm_dir, 'TISSUE_CLASS_1_GM_OPTIMIZED.nii.gz')

        # get bg
        first = os.path.join(spm_dir, 'FIRST_subcortical', 'FIRST_all_fast_firstseg_AIL.nii.gz')
        cau   = os.path.join(spm_dir, 'FIRST_subcortical', 'left_caudate.nii.gz')
        put   = os.path.join(spm_dir, 'FIRST_subcortical', 'left_putamen.nii.gz')
        pal   = os.path.join(spm_dir, 'FIRST_subcortical', 'left_pallidum.nii.gz')
        nac   = os.path.join(spm_dir, 'FIRST_subcortical', 'left_accumbens.nii.gz')

        os.system('fslmaths %s -thr 26 -uthr 26 -bin %s'%(first, nac))
        os.system('fslmaths %s -thr 11 -uthr 11 -bin %s'%(first, cau))
        os.system('fslmaths %s -thr 12 -uthr 12 -bin %s'%(first, put))
        os.system('fslmaths %s -thr 13 -uthr 13 -bin %s'%(first, pal))

        # Calculate nuclei proportions within voxel

        #1. grab data
        nac_data = nb.load(nac).get_data().squeeze()
        cau_data = nb.load(cau).get_data().squeeze()
        put_data = nb.load(put).get_data().squeeze()
        pal_data = nb.load(pal).get_data().squeeze()
        gm_data  = nb.load(spm_gm).get_data().squeeze()
        svs_data = nb.load(str_mask).get_data().squeeze()

        nac_svs = nac_data * svs_data
        cau_svs = cau_data * svs_data
        put_svs = put_data * svs_data
        pal_svs = pal_data * svs_data
        gm_svs = gm_data  * svs_data

        #2. multiply SVS ROI with BG segments
        vox_nac = np.sum(np.array(nac_data + gm_data, dtype=bool))
        vox_cau = np.sum(np.array(cau_data + gm_data, dtype=bool))
        vox_put = np.sum(np.array(put_data + gm_data, dtype=bool))
        vox_pal = np.sum(np.array(pal_data + gm_data, dtype=bool))
        vox_gm  = np.sum(gm_svs)
        vox_svs = np.sum(svs_data)

        #print vox_cau + vox_nac + vox_put + vox_pal
        #print vox_gm

        #3. calculate percentages
        percent_nac =np.round(float(vox_nac) / float(vox_svs), 3) * 100
        percent_cau =np.round(float(vox_cau) / float(vox_svs), 3) * 100
        percent_put =np.round(float(vox_put) / float(vox_svs), 3) * 100
        percent_pal =np.round(float(vox_pal) / float(vox_svs), 3) * 100
        percent_gm  =np.round(float(vox_gm) / float(vox_svs), 3) * 100

        print 'CAU = ', percent_cau
        print 'NAC = ', percent_nac
        print 'PUT = ', percent_put
        print 'PAL = ', percent_pal
        print 'ALL =', percent_pal + percent_put + percent_nac + percent_cau
        print 'GM  = ', percent_gm

        txt  = os.path.join(stats_dir, 'BG_STATISTICS.txt')
        write = open(txt, 'w')
        write.write('%s, %s, %s, %s' %(percent_cau, percent_nac, percent_put, percent_pal))
        write.close()

        print '__________________________________________________________________________'

if __name__ == "__main__":
     calculate_str_proportions(controls_a, workspace_controls_a)
     calculate_str_proportions(controls_b, workspace_controls_b)
     calculate_str_proportions(patients_a, workspace_patients_a)
     calculate_str_proportions(patients_b, workspace_patients_b)
