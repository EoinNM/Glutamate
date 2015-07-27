__author__ = 'kanaan' 'July 3 2015'

import os
import nipype.interfaces.spm as spm
import nipype.interfaces.fsl as fsl
from utilities.utils import mkdir_path
from variables.subject_list import *
import shutil

def segment_spm(population, workspace_dir):
    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count= 0

    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Runnning SPM12 NewSegment on subject %s_%s' %(count, subject, workspace_dir[-10:-9])
        print ''

        # define subject directory and anatomical file path
        subject_dir     = os.path.join(workspace_dir ,  subject)
        anatomical_dir  = os.path.join(subject_dir   , 'anatomical_original')
        anatomical_file = os.path.join(anatomical_dir, 'ANATOMICAL.nii')

        # check if the file exists
        if os.path.isfile(os.path.join(workspace_dir, subject, 'segmentation_spm', 'TISSUE_CLASS_1_GM_prob.nii')):
            print 'Brain already segmented......... moving on'

        else:
            print '..... Segmenting Brain with SPM12-NewSegment'

            # define destination directory for spm segmentation outputs
            mkdir_path(os.path.join(subject_dir, 'segmentation_spm'))
            out_spm_dir  = str(os.path.join(subject_dir, 'segmentation_spm'))

            # run SPM segmentation
            print '..... Starting matlab no splash to run segmentation'
            seg                      = spm.NewSegment()
            seg.inputs.channel_files = anatomical_file
            seg.inputs.channel_info  = (0.0001, 60, (True, True))
            seg.out_dir              = out_spm_dir
            seg.run()

            # rename output files
            print '..... Renaming outputs and dumping into SPM segmenation dir'

            shutil.move(str(os.path.join(anatomical_dir, 'c1ANATOMICAL.nii')),
                        str(os.path.join(out_spm_dir, 'TISSUE_CLASS_1_GM_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c2ANATOMICAL.nii')),
                        str(os.path.join(out_spm_dir, 'TISSUE_CLASS_2_WM_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c3ANATOMICAL.nii')),
                        str(os.path.join(out_spm_dir, 'TISSUE_CLASS_3_CSF_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c4ANATOMICAL.nii')),
                        str(os.path.join(out_spm_dir, '___Skull.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c5ANATOMICAL.nii')),
                        str(os.path.join(out_spm_dir, '___SoftTissue.nii')))

            shutil.move((os.path.join(anatomical_dir, 'BiasField_ANATOMICAL.nii')),
                        (os.path.join(out_spm_dir, '___BiasFieldMap.nii')))

            shutil.move((os.path.join(anatomical_dir, 'mANATOMICAL.nii')),
                        (os.path.join(out_spm_dir, '___mFile.nii')))

            shutil.move((os.path.join(anatomical_dir, 'ANATOMICAL_seg8.mat')),
                        (os.path.join(out_spm_dir, '___seg8.mat')))

            '###########################################'
            # threshold and biniarize spm tissue masks
            print '..... Thresholding and binazing tissue probablity maps '
            out_spm_dir  = str(os.path.join(subject_dir, 'segmentation_spm'))
            gm_mask  = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_1_GM_prob.nii'))
            wm_mask  = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_2_WM_prob.nii'))
            csf_mask = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_3_CSF_prob.nii'))

            thr_hbin_GM1                          = fsl.Threshold()
            thr_hbin_GM1.inputs.in_file           = gm_mask
            thr_hbin_GM1.inputs.thresh            = 0.5
            thr_hbin_GM1.inputs.args              = '-bin'
            thr_hbin_GM1.inputs.ignore_exception  = True
            thr_hbin_GM1.inputs.out_file          = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_1_GM_BIN.nii.gz'))
            thr_hbin_GM1.run()

            thr_hbin_WM1                          = fsl.Threshold()
            thr_hbin_WM1.inputs.in_file           = wm_mask
            thr_hbin_WM1.inputs.thresh            = 0.5
            thr_hbin_WM1.inputs.args              = '-bin'
            thr_hbin_WM1.inputs.ignore_exception  = True
            thr_hbin_WM1.inputs.out_file          = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_2_WM_BIN.nii.gz'))
            thr_hbin_WM1.run()

            thr_hbin_CSF1                         = fsl.Threshold()
            thr_hbin_CSF1.inputs.in_file          = csf_mask
            thr_hbin_CSF1.inputs.thresh           = 0.5
            thr_hbin_CSF1.inputs.args             = '-bin'
            thr_hbin_CSF1.inputs.ignore_exception = True
            thr_hbin_CSF1.inputs.out_file         = str(os.path.join(out_spm_dir, 'TISSUE_CLASS_3_CSF_BIN.nii.gz'))
            thr_hbin_CSF1.run()

'======================================================================================================================================'
'======================================================================================================================================'

if __name__ == "__main__":
    #segment_spm(test_control_a, workspace_controls_a)
    segment_spm(controls_a, workspace_controls_a)
    # segment_spm(controls_b, workspace_controls_b)
    # segment_spm(patients_a, workspace_patients_a)
    # segment_spm(patients_b, workspace_patients_b)
