__author__ = 'kanaan' 'July 3 2015'

import os
import dicom as pydicom
import nipype.interfaces.spm.utils as spmu
from utilities.utils import mkdir_path
from variables.subject_list import *

def dicom_convert(population, data_dir, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT %s %s' %(data_dir[12:19], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count=0
    for subject in population:
        count +=1
        print '====================================================================='
        print '%s- DICOM CONVERSION for %s' %(count,subject)

        # define dicom directory for each subject
        dicom_dir  = os.path.join(data_dir, subject, 'DICOM')

        # define destination directory for NIFTI outputs
        mkdir_path(os.path.join(workspace_dir, subject, 'anatomical_original'))
        out_nifti_dir  = str(os.path.join(workspace_dir, subject, 'anatomical_original'))

        if not os.path.isfile(os.path.join(out_nifti_dir, 'ANATOMICAL.nii')):
            # create a list of all dicoms with absolute paths for each file
            dicom_list = []
            for dicom in os.listdir(dicom_dir):
                dicomstr = os.path.join(dicom_dir, dicom)
                dicom_list.append(dicomstr)

            # grab SeriesDescription and append T1 files to list
            T1_list = []
            print 'Reading dicom series descriptions'
            for dicom in dicom_list:
                try:
                    dcm_read = pydicom.read_file(dicom, force = True)
                    sequence = dcm_read.SeriesDescription
                except AttributeError:
                    continue

                if 'mp2rage_p3_602B_UNI_Images' in sequence:
                    T1_list.append(dicom)

            # convert T1 anatomical to NIFTI with SPM
            print 'Converting Dicom to Nifti for %s' %subject
            spm_dicom_convert                   = spmu.DicomImport()
            spm_dicom_convert.inputs.format     = 'nii'
            spm_dicom_convert.inputs.in_files   = T1_list
            spm_dicom_convert.inputs.output_dir = out_nifti_dir
            spm_dicom_convert.run()

            #rename output file
            for file in os.listdir(out_nifti_dir):
                if file.endswith('nii'):
                    os.rename(str(os.path.join(out_nifti_dir, file)),
                              str(os.path.join(out_nifti_dir, 'ANATOMICAL.nii')))
        else:
            print 'subject already processed.......moving on'

        print '====================================================================='
        print ''

'######################################################################################################################################'
'######################################################################################################################################'

if __name__ == "__main__":
    # dicom_convert(['KDET'], afs_controls_a, workspace_controls_a)
    # dicom_convert(controls_a, afs_controls_a, workspace_controls_a)
    # dicom_convert(controls_b, afs_controls_b, workspace_controls_b)
    # dicom_convert(patients_a, afs_patients_a, workspace_patients_a)
    # dicom_convert(patients_b, afs_patients_b, workspace_patients_b)
    dicom_convert(['CF1P'], afs_patients_b, workspace_patients_b)
