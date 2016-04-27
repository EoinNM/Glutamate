__author__ = 'kanaan' 'July 3 2015'

import os
import nipype.interfaces.spm as spm
import nipype.interfaces.fsl as fsl
import nibabel as nb
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
            out_seg_dir  = str(os.path.join(subject_dir, 'segmentation_spm'))

            # run SPM segmentation
            print '..... Starting matlab no splash to run segmentation'
            seg                      = spm.NewSegment()
            seg.inputs.channel_files = anatomical_file
            seg.inputs.channel_info  = (0.0001, 60, (True, True))
            seg.out_dir              = out_seg_dir
            seg.run()

            # rename output files
            print '..... Renaming outputs and dumping into SPM segmenation dir'

            shutil.move(str(os.path.join(anatomical_dir, 'c1ANATOMICAL.nii')),
                        str(os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c2ANATOMICAL.nii')),
                        str(os.path.join(out_seg_dir, 'TISSUE_CLASS_2_WM_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c3ANATOMICAL.nii')),
                        str(os.path.join(out_seg_dir, 'TISSUE_CLASS_3_CSF_prob.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c4ANATOMICAL.nii')),
                        str(os.path.join(out_seg_dir, '___Skull.nii')))

            shutil.move(str(os.path.join(anatomical_dir, 'c5ANATOMICAL.nii')),
                        str(os.path.join(out_seg_dir, '___SoftTissue.nii')))

            shutil.move((os.path.join(anatomical_dir, 'BiasField_ANATOMICAL.nii')),
                        (os.path.join(out_seg_dir, '___BiasFieldMap.nii')))

            shutil.move((os.path.join(anatomical_dir, 'mANATOMICAL.nii')),
                        (os.path.join(out_seg_dir, '___mFile.nii')))

            shutil.move((os.path.join(anatomical_dir, 'ANATOMICAL_seg8.mat')),
                        (os.path.join(out_seg_dir, '___seg8.mat')))

            '###########################################'
            # threshold and biniarize spm tissue masks
            print '..... Thresholding and binazing tissue probablity maps '
            out_seg_dir  = str(os.path.join(subject_dir, 'segmentation_spm'))
            gm_mask  = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_prob.nii'))
            wm_mask  = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_2_WM_prob.nii'))
            csf_mask = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_3_CSF_prob.nii'))

            thr_hbin_GM1                          = fsl.Threshold()
            thr_hbin_GM1.inputs.in_file           = gm_mask
            thr_hbin_GM1.inputs.thresh            = 0.5
            thr_hbin_GM1.inputs.args              = '-bin'
            thr_hbin_GM1.inputs.ignore_exception  = True
            thr_hbin_GM1.inputs.out_file          = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_BIN.nii.gz'))
            thr_hbin_GM1.run()

            thr_hbin_WM1                          = fsl.Threshold()
            thr_hbin_WM1.inputs.in_file           = wm_mask
            thr_hbin_WM1.inputs.thresh            = 0.5
            thr_hbin_WM1.inputs.args              = '-bin'
            thr_hbin_WM1.inputs.ignore_exception  = True
            thr_hbin_WM1.inputs.out_file          = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_2_WM_BIN.nii.gz'))
            thr_hbin_WM1.run()

            thr_hbin_CSF1                         = fsl.Threshold()
            thr_hbin_CSF1.inputs.in_file          = csf_mask
            thr_hbin_CSF1.inputs.thresh           = 0.5
            thr_hbin_CSF1.inputs.args             = '-bin'
            thr_hbin_CSF1.inputs.ignore_exception = True
            thr_hbin_CSF1.inputs.out_file         = str(os.path.join(out_seg_dir, 'TISSUE_CLASS_3_CSF_BIN.nii.gz'))
            thr_hbin_CSF1.run()

        '###########################################'


        out_seg_dir = os.path.join(subject_dir, 'segmentation_spm')
        if os.path.isfile(os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_OPTIMIZED.nii.gz')):
            print 'Optimized Tissue masks already created......... moving on'

        else:
            print '..... Segmentatiing Subcortex and creating optimized tissue masks'
            # create brain mask from GM, WM, CSF
            gm_bin = os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_BIN.nii.gz')
            wm_bin = os.path.join(out_seg_dir, 'TISSUE_CLASS_2_WM_BIN.nii.gz')
            cm_bin = os.path.join(out_seg_dir, 'TISSUE_CLASS_3_CSF_BIN.nii.gz')
            brain_mask = os.path.join(anatomical_dir, 'ANATOMICAL_brain_mask.nii.gz')
            os.system('fslmaths %s -add %s -add %s -fillh -dilM %s'%(gm_bin,wm_bin, cm_bin,brain_mask))

            # # deskull anatomical
            anatomical_deskull = os.path.join(anatomical_dir, 'ANATOMICAL_DESKULL.nii.gz')
            anatomical_deskull_rpi = os.path.join(anatomical_dir, 'ANATOMICAL_DESKULL_RPI.nii.gz')
            os.system('fslmaths %s -mul %s %s' %(anatomical_file, brain_mask, anatomical_deskull))
            os.system('fslswapdim %s RL PA IS %s'%(anatomical_deskull, anatomical_deskull_rpi))

            # run FLIRT and FIRST
            mkdir_path(os.path.join(out_seg_dir, 'FIRST_subcortical'))
            out_first_dir  = os.path.join(out_seg_dir, 'FIRST_subcortical')
            first_seg = os.path.join(out_first_dir, 'FIRST_all_fast_firstseg.nii.gz')

            if not os.path.isfile(first_seg):
            #if not os.path.isfile(os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_OPTIMIZED.nii.gz')):
                ref = '/usr/share/fsl/5.0/data/standard/MNI152_T1_1mm_brain.nii.gz'
                omat = os.path.join(anatomical_dir, 'ANATOMICAL_DESKULL_RPI_MNI.mat')
                anat2mni = os.path.join(anatomical_dir, 'ANATOMICAL_DESKULL_RPI_MNI.nii.gz')
                print 'running flirt'
                os.system('flirt -in %s -ref %s -out %s -omat %s -cost mutualinfo -dof 12'%(anatomical_deskull_rpi, ref, anat2mni, omat))
                print 'running first'
                os.system('run_first_all -v -i %s -a %s -o %s/FIRST'%(anatomical_deskull_rpi, omat, out_first_dir))

                # flip back to anatomical orientation
                first_seg = os.path.join(out_first_dir, 'FIRST_all_fast_firstseg.nii.gz')
                first_seg_ail = os.path.join(out_first_dir, 'FIRST_all_fast_firstseg_AIL.nii.gz')
                os.system('fslswapdim %s AP IS LR %s' %(first_seg, first_seg_ail))

                # create subcortically corrected tissue masks and flip them back to correct orientation
                first_seg_ail_bin = os.path.join(out_first_dir, 'FIRST_all_fast_firstseg_AIL_BIN.nii.gz')
                gm_combined = os.path.join(out_seg_dir, 'TISSUE_CLASS_1_GM_OPTIMIZED.nii.gz')
                wm_combined = os.path.join(out_seg_dir, 'TISSUE_CLASS_2_WM_OPTIMIZED.nii.gz')
                cm_combined = os.path.join(out_seg_dir, 'TISSUE_CLASS_3_CSF_OPTIMIZED.nii.gz')

                os.system('fslmaths %s -bin %s' %(first_seg_ail, first_seg_ail_bin))
                os.system('fslmaths %s -add %s -bin %s' %(first_seg_ail_bin, gm_bin, gm_combined))
                os.system('fslmaths %s -sub %s -bin %s' %(wm_bin, first_seg_ail_bin, wm_combined))
                os.system('fslmaths %s -sub %s -bin %s' %(cm_bin,first_seg_ail_bin, cm_combined))

            print 'done'

'======================================================================================================================================'
'======================================================================================================================================'

if __name__ == "__main__":
    # segment_spm(['GHAT'], workspace_controls_a)
    # segment_spm(controls_a, workspace_controls_a)
    # segment_spm(controls_b, workspace_controls_b)
    # segment_spm(patients_a, workspace_patients_a)
    # segment_spm(patients_b, workspace_patients_b)
    segment_spm(['CF1P'], workspace_patients_b)
