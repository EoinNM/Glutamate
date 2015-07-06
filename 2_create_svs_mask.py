__author__ = 'kanaan' 'July 3 2015'

import os
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess

def create_svs_mask_GTS_data(population, afs_dir, workspace_dir):

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

        subject_afs         = os.path.join(afs_dir, subject, 'SVS')
        subject_workspace   = os.path.join(workspace_dir, subject)

        rda_acc_met=[]
        rda_tha_met=[]
        rda_str_met=[]

        rda_acc_h2o=[]
        rda_tha_h2o=[]
        rda_str_h2o=[]

        twix_acc_met=[]
        twix_tha_met=[]
        twix_str_met=[]

        twix_acc_h2o=[]
        twix_tha_h2o=[]
        twix_str_h2o=[]


        '========================================================================================'
        '                              Copying SVS files to local dirs                           '
        '========================================================================================'

        print '1. Locating and copying rda files from afs dir to local workspace'

        for root, dirs, files, in os.walk(subject_afs, topdown= False):
            for name in files:

                if 'SUPP' in name:
                    if 'ACC' in name or 'acc' in name or 'Acc' in name:
                        rda_acc_met.append(os.path.join(root, name))
                    elif 'TH' in name or 'th' in name or 'Tha' in name:
                        rda_tha_met.append(os.path.join(root, name))
                    elif 'STR' in name or 'ST' in name or 'st' in name:
                        rda_str_met.append(os.path.join(root, name))

                if 'HEAD' in name and 'REF' in name and 'SUPP' not in name and 'meas' not in name:
                    if 'ACC' in name or 'acc' in name or 'Acc' in name:
                        rda_acc_h2o.append(os.path.join(root, name))
                    elif 'TH' in name or 'th' in name or 'Th' in name:
                        rda_tha_h2o.append(os.path.join(root,name))
                    elif 'STR' in name or 'ST' in name or 'st' in name:
                        rda_str_h2o.append(os.path.join(root, name))

                if 'meas' in name and 'rda' not in name:
                    if 'ACC' in name or 'acc' in name or 'Acc' in name:
                        if 'ref' not in name and 'head' not in name and 'body' not in name:
                            twix_acc_met.append(os.path.join(root, name))
                        elif 'ref' in name and 'body' not in name:
                            twix_acc_h2o.append(os.path.join(root, name))
                    elif 'TH' in name or 'th' in name or 'Tha' in name:
                        if 'ref' not in name and 'head' not in name and 'body' not in name:
                            twix_tha_met.append(os.path.join(root, name))
                        elif 'ref' in name and 'body' not in name:
                            twix_tha_h2o.append(os.path.join(root, name))
                    elif 'STR' in name or 'ST' in name or 'st' in name:
                        if 'ref' not in name and 'head' not in name and 'body' not in name:
                            twix_str_met.append(os.path.join(root, name))
                        elif 'ref' in name and 'body' not in name:
                            twix_str_h2o.append(os.path.join(root, name))

        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'ACC', 'met'))
        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'ACC', 'h2o'))
        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'THA', 'met'))
        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'THA', 'h2o'))
        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'STR', 'met'))
        mkdir_path(os.path.join(subject_workspace, 'svs_RDA', 'STR', 'h2o'))

        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'ACC', 'ACC'))
        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'ACC', 'ACC_w'))
        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'THA', 'THA'))
        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'THA', 'THA_w'))
        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'STR', 'STR'))
        mkdir_path(os.path.join(subject_workspace, 'svs_TWIX', 'STR', 'STR_w'))

        acc_met_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'ACC', 'met')
        acc_h2o_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'ACC', 'h2o')
        tha_met_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'THA', 'met')
        tha_h2o_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'THA', 'h2o')
        str_met_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'STR', 'met')
        str_h2o_rda_dir = os.path.join(workspace_dir, subject, 'svs_RDA', 'STR', 'h2o')

        acc_met_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'ACC', 'ACC')
        acc_h2o_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'ACC', 'ACC_w')
        tha_met_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'THA', 'THA')
        tha_h2o_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'THA', 'THA_w')
        str_met_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'STR', 'STR')
        str_h2o_twx_dir = os.path.join(workspace_dir, subject, 'svs_TWIX', 'STR', 'STR_w')


        shutil.copy(rda_acc_met[0], os.path.join(acc_met_rda_dir, '%s%s_ACC_SUPPRESSED.rda' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(rda_tha_met[0], os.path.join(tha_met_rda_dir, '%s%s_THA_SUPPRESSED.rda' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(rda_str_met[0], os.path.join(str_met_rda_dir, '%s%s_STR_SUPPRESSED.rda' %(subject,workspace_dir[-10:-9]) ))

        shutil.copy(rda_acc_h2o[0], os.path.join(acc_h2o_rda_dir, '%s%s_ACC_WATER.rda' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(rda_tha_h2o[0], os.path.join(tha_h2o_rda_dir, '%s%s_THA_WATER.rda' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(rda_str_h2o[0], os.path.join(str_h2o_rda_dir, '%s%s_STR_WATER.rda' %(subject,workspace_dir[-10:-9]) ))

        shutil.copy(twix_acc_met[0], os.path.join(acc_met_twx_dir, '%s%s_ACC_SUPPRESSED_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(twix_tha_met[0], os.path.join(tha_met_twx_dir, '%s%s_THA_SUPPRESSED_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(twix_str_met[0], os.path.join(str_met_twx_dir, '%s%s_STR_SUPPRESSED_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))

        shutil.copy(twix_acc_h2o[0], os.path.join(acc_h2o_twx_dir, '%s%s_ACC_WATER_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(twix_tha_h2o[0], os.path.join(tha_h2o_twx_dir, '%s%s_THA_WATER_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))
        shutil.copy(twix_str_h2o[0], os.path.join(str_h2o_twx_dir, '%s%s_STR_WATER_TWIX.dat' %(subject,workspace_dir[-10:-9]) ))

        '========================================================================================'
        '                               Creating mask for each voxel                             '
        '========================================================================================'

        print '2. Creating SVS masks'

        #matlab related defenitions.... check RDA2NII.m file

        T1Path          = os.path.join(subject_workspace, 'anatomical_original' + '/')
        T1Image         = 'ANATOMICAL.nii'

        ACC_path        = os.path.join(acc_met_rda_dir + '/')
        ACC_file        = '%s%s_ACC_SUPPRESSED.rda' %(subject ,workspace_dir[-10:-9])

        THA_path        = os.path.join(tha_met_rda_dir + '/')
        THA_file        = '%s%s_THA_SUPPRESSED.rda' %(subject,workspace_dir[-10:-9])

        STR_path        = os.path.join(str_met_rda_dir + '/')
        STR_file        = '%s%s_STR_SUPPRESSED.rda' %(subject,workspace_dir[-10:-9])

        print T1Path
        print T1Image

        print ACC_path
        print ACC_file

        #run matlab code to create registered mask from rda file

        anatomical_dir     = os.path.join(subject_workspace, 'anatomical_original')

        mkdir_path(os.path.join(subject_workspace, 'svs_voxel_mask'))
        mask_dir = os.path.join(subject_workspace, 'svs_voxel_mask')

        matlab_command_acc = ['matlab',  '--version', '8.2', '-nodesktop' ,'-nosplash'  ,'-nojvm' ,'-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                              %(T1Path, T1Image, ACC_path, ACC_file)]
        matlab_command_tha = ['matlab','--version', '8.2','-nodesktop' ,'-nosplash'  ,'-nojvm' ,'-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                              %(T1Path, T1Image, THA_path, THA_file)]
        matlab_command_str = ['matlab','--version', '8.2', '-nodesktop' ,'-nosplash'  ,'-nojvm' ,'-r "RDA_TO_NIFTI(\'%s\', \'%s\', \'%s\', \'%s\') ; quit;"'
                              %(T1Path, T1Image, STR_path, STR_file)]

                ####################
        if not os.path.isfile(os.path.join(mask_dir, '%s%s_ACC_RDA_MASK.nii' %(subject,workspace_dir[-10:-9]))):
            print '..... extracting geometry from creating mask for ACC'
            subprocess.call(matlab_command_acc)

            for file in os.listdir(anatomical_dir):
                        if 'rda' in file and 'ACC' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir,  '%s%s_ACC_RDA_MASK.nii' %(subject,workspace_dir[-10:-9])))
                        elif 'coord' in file and 'acc' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir, '%s%s_ACC_RDA_coord.txt' %(subject,workspace_dir[-10:-9])))
        else:
            print 'ACC SVS mask already created..... moving on'

        ####################
        if not os.path.isfile(os.path.join(mask_dir, '%s%s_THA_RDA_MASK.nii' %(subject,workspace_dir[-10:-9]))):
            print '..... extracting geometry from creating mask for THA'
            subprocess.call(matlab_command_tha)

            for file in os.listdir(anatomical_dir):
                        if 'rda' in file and 'THA' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir,  '%s%s_THA_RDA_MASK.nii' %(subject,workspace_dir[-10:-9])))
                        elif 'coord' in file and 'th' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir, '%s%s_THA_RDA_coord.txt' %(subject,workspace_dir[-10:-9])))
        else:
            print 'THA SVS mask already created..... moving on'

        ####################
        if not os.path.isfile(os.path.join(mask_dir, '%s%s_STR_RDA_MASK.nii' %(subject,workspace_dir[-10:-9]))):
            print '..... extracting geometry from creating mask for STR'
            subprocess.call(matlab_command_str)

            for file in os.listdir(anatomical_dir):
                        if 'rda' in file and 'STR' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir,  '%s%s_STR_RDA_MASK.nii' %(subject,workspace_dir[-10:-9])))
                        elif 'coord' in file and 'st' in file:
                            shutil.move(os.path.join(anatomical_dir, file),
                                        os.path.join(mask_dir, '%s%s_STR_RDA_coord.txt' %(subject,workspace_dir[-10:-9])))
        else:
            print 'STR SVS mask already created..... moving on'



        print '========================================================================================'




if __name__ == "__main__":
    create_svs_mask_GTS_data(test_subject, afs_patients_a, workspace_patients_a)