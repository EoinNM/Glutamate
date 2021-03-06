__author__ = 'kanaan' 'July 3 2015'

import os
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess

def create_svs_mask_GTS_data(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- CREATING SVS mask for subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'

        subject_workspace   = os.path.join(workspace_dir, subject)


        def create_svs_masks(voxel_name):
            #matlab related defenitions.... check RDA2NII.m file
            anatomical_dir     = os.path.join(subject_workspace, 'anatomical_original')
            T1Path     = os.path.join(subject_workspace, 'anatomical_original' + '/')
            T1Image    = 'ANATOMICAL.nii'
            svs_path   = os.path.join(subject_workspace, 'svs_rda', voxel_name, 'met' + '/')
            svs_file   = '%s%s_%s_SUPPRESSED.rda' %(subject ,workspace_dir[-10:-9], voxel_name)

            #  output dir
            mkdir_path(os.path.join(subject_workspace, 'svs_voxel_mask'))
            mask_dir = os.path.join(subject_workspace, 'svs_voxel_mask')

            #run matlab code to create registered mask from rda file
            matlab_command = ['matlab',  '--version', '8.2', '-nodesktop' ,'-nosplash'  ,'-nojvm' ,'-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                               %(T1Path, T1Image, svs_path, svs_file)]

            if not os.path.isfile(os.path.join(mask_dir, '%s%s_%s_RDA_MASK.nii' %(subject,workspace_dir[-10:-9], voxel_name))):
                print '..... extracting geometry from RDA and creating mask for %s'%voxel_name
                subprocess.call(matlab_command)

            for file in os.listdir(anatomical_dir):
                        if 'rda' in file and '%s'%voxel_name in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir,  '%s%s_%s_RDA_MASK.nii' %(subject,workspace_dir[-10:-9], voxel_name)))
                        elif 'coord' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir, '%s%s_%s_RDA_coord.txt' %(subject,workspace_dir[-10:-9], voxel_name)))
            else:
                print '%s SVS mask already created..... moving on'%voxel_name

            print '========================================================================================'
        create_svs_masks('ACC')
        create_svs_masks('THA')
        create_svs_masks('STR')

        # def create_within_voxel_masks(voxel_name):
        #     mkdir_path(os.path.join(subject_workspace, 'svs_voxel_mask', 'within_voxel_tissue'))
        #     mask_dir_2= os.path.join(subject_workspace, 'svs_voxel_mask', 'within_voxel_tissue')
        #     svs_file = os.path.join(subject_workspace, 'svs_voxel_mask', '%s%s_%s_RDA_MASK.nii' %(subject,workspace_dir[-10:-9], voxel_name) )
        #
        #     gm = os.path.join(subject_workspace, 'segmentation_spm', 'TISSUE_CLASS_1_GM_OPTIMIZED.nii.gz')
        #     wm = os.path.join(subject_workspace, 'segmentation_spm', 'TISSUE_CLASS_2_WM_OPTIMIZED.nii.gz')
        #     cm = os.path.join(subject_workspace, 'segmentation_spm', 'TISSUE_CLASS_3_CSF_OPTIMIZED.nii.gz')
        #
        #     svs_gm = os.path.join(mask_dir_2, '%s%s_%s_RDA_MASK_GM.nii' %(subject,workspace_dir[-10:-9], voxel_name) )
        #     svs_wm = os.path.join(mask_dir_2, '%s%s_%s_RDA_MASK_WM.nii' %(subject,workspace_dir[-10:-9], voxel_name) )
        #     svs_cm = os.path.join(mask_dir_2, '%s%s_%s_RDA_MASK_CSF.nii' %(subject,workspace_dir[-10:-9], voxel_name) )
        #
        #     os.system('fslmaths %s -mul %s %s'%(svs_file, gm, svs_gm))
        #     os.system('fslmaths %s -mul %s %s'%(svs_file, wm, svs_wm))
        #     os.system('fslmaths %s -mul %s %s'%(svs_file, cm, svs_cm))
        # create_within_voxel_masks('ACC')
        # create_within_voxel_masks('THA')
        # create_within_voxel_masks('STR')

'======================================================================================================================================'
if __name__ == "__main__":
    create_svs_mask_GTS_data(controls_a,workspace_controls_a)
    # create_svs_mask_GTS_data(controls_b,workspace_controls_b)
    # create_svs_mask_GTS_data(patients_a,workspace_patients_a)
    # create_svs_mask_GTS_data(patients_b,workspace_patients_b)
