__author__ = 'kanaan' 'July 3 2015'

import os
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess

def check_svs_spectra(population, afs_dir, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- CHECKING SVS SPECTRA for subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'

        subject_afs         = os.path.join(afs_dir, subject, 'SVS')
        subject_workspace   = os.path.join(workspace_dir, subject)

        print 'Locating and copying rda/twix files from afs dir to local workspace'
        def get_spectra(voxel_name, string1, string2, string3):

            rda_met = []
            rda_h2o = []
            twix_met= []
            twix_h2o= []

            for root, dirs, files, in os.walk(subject_afs, topdown= False):
                for name in files:
                    if 'SUPP' in name:
                        if string1 in name or string2 in name or string3 in name:
                            rda_met.append(os.path.join(root, name))

                    if 'HEAD' in name and 'REF' in name and 'SUPP' not in name and 'meas' not in name:
                        if string1 in name or string2 in name or string3 in name:
                            rda_h2o.append(os.path.join(root, name))

                    if 'meas' in name and 'rda' not in name:
                       if string1 in name or string2 in name or string3 in name:
                            if 'ref' not in name and 'head' not in name and 'body' not in name and 'HEAD' not in name:
                                twix_met.append(os.path.join(root, name))
                            elif 'ref' in name or 'REF' in name:
                                if 'body' not in name:
                                    twix_h2o.append(os.path.join(root, name))

            if rda_met is []:
                print 'RDA metabolite data does not exist for subject %s' %subject
            elif rda_h2o is []:
                print 'RDA water data does not exist for subject %s' %subject
            elif twix_met is []:
                print 'TWIX metabolite data does not exist for subject %s' %subject
            elif twix_h2o is []:
                print 'TWIX water data does not exist for subject %s' %subject

            mkdir_path(os.path.join(subject_workspace, 'svs_rda', voxel_name, 'met'))
            mkdir_path(os.path.join(subject_workspace, 'svs_rda', voxel_name, 'h2o'))
            mkdir_path(os.path.join(subject_workspace, 'svs_twix', voxel_name, voxel_name))
            mkdir_path(os.path.join(subject_workspace, 'svs_twix', voxel_name, '%s_w'%voxel_name))

            rda_met_dir = os.path.join(workspace_dir, subject, 'svs_rda', voxel_name, 'met')
            rda_h2o_dir = os.path.join(workspace_dir, subject, 'svs_rda', voxel_name, 'h2o')
            twx_met_dir = os.path.join(workspace_dir, subject, 'svs_twix', voxel_name, voxel_name)
            twx_h2o_dir = os.path.join(workspace_dir, subject, 'svs_twix', voxel_name, '%s_w'%voxel_name)

            shutil.copy(rda_met[0], os.path.join(rda_met_dir, '%s%s_%s_SUPPRESSED.rda' %(subject,  workspace_dir[-10:-9], voxel_name)))
            shutil.copy(rda_h2o[0], os.path.join(rda_h2o_dir, '%s%s_%s_WATER.rda' %(subject, workspace_dir[-10:-9], voxel_name)))
            shutil.copy(twix_met[0], os.path.join(twx_met_dir, '%s%s_%s_SUPPRESSED_TWIX.dat' %(subject,  workspace_dir[-10:-9], voxel_name)))
            shutil.copy(twix_h2o[0], os.path.join(twx_h2o_dir, '%s%s_%s_WATER_TWIX.dat' %(subject,workspace_dir[-10:-9], voxel_name)))

            print '.....done voxel %s'%voxel_name

        if os.path.isfile(os.path.join(subject_workspace, 'svs_twix', 'ACC', 'ACC', '%s%s_ACC_SUPPRESSED_TWIX.dat' %(subject, workspace_dir[-10:-9]))):
            print '.... ACC data already copied'
        else:
            get_spectra('ACC', 'ACC', 'acc', 'Acc')

        if os.path.isfile(os.path.join(subject_workspace, 'svs_twix', 'THA', 'THA', '%s%s_THA_SUPPRESSED_TWIX.dat' %(subject, workspace_dir[-10:-9]))):
            print '.... THA data already copied'
        else:
            get_spectra('THA', 'TH', 'Th', 'th')

        if os.path.isfile(os.path.join(subject_workspace, 'svs_twix', 'STR', 'STR', '%s%s_STR_SUPPRESSED_TWIX.dat' %(subject, workspace_dir[-10:-9]))):
            print '.... STR data already copied'
        else:
            get_spectra('STR', 'ST', 'ST', 'st')


if __name__ == "__main__":
    #check_svs_spectra(test_control_a, afs_controls_a, workspace_controls_a)
    check_svs_spectra(controls_a, afs_controls_a, workspace_controls_a)
    check_svs_spectra(controls_b, afs_controls_b, workspace_controls_b)
    check_svs_spectra(patients_a, afs_patients_a, workspace_patients_a)
    check_svs_spectra(patients_b, afs_patients_b, workspace_patients_b)
