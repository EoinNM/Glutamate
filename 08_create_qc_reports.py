__author__ = 'kanaan' 'July 6 2015'

import os
from variables.subject_list import *
from utilities.utils import mkdir_path, find_cut_coords
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm, inch, pica
import nibabel as nb
import subprocess

def create_mrs_qc(population, workspace_dir, analysis_type):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1

        print 'Creating MRS-%s Quality Control Reports for SUBJECT %s%s' %(analysis_type, subject,workspace_dir[-10:-9])

        # grab data
        subject_dir = os.path.join(workspace_dir, subject)
        anatomical  = os.path.join(subject_dir, 'anatomical_original', 'ANATOMICAL.nii')

        def create_voxel_plots(voxel_name, ppmst):
            print '...Working on %s %s ' %(analysis_type, ppmst)
            #create output QC directory
            mkdir_path(os.path.join(subject_dir, 'quality_control', analysis_type, voxel_name, 'ppm_%s' %ppmst, 'tmp'))
            qc_dir  = os.path.join(subject_dir, 'quality_control',  analysis_type,  voxel_name, 'ppm_%s' %ppmst)
            tmp_dir = os.path.join(qc_dir, 'tmp')

            #grab lcmodel plots
            svs_lcmodel = os.path.join(subject_dir, 'lcmodel_%s'%analysis_type, voxel_name, 'ppm_%s'%ppmst, 'ps.pdf')

            # create localization pngs
            make_png = ['convert', '-density', '300', '-trim', '%s'%svs_lcmodel,  '-quality', '300', '-sharpen', '0x1.0', '%s/%s_lcmodel.png'%(tmp_dir, voxel_name)]
            subprocess.call(make_png)
            lcm_plot = os.path.join(tmp_dir, '%s_lcmodel-0.png'%voxel_name)

            #grab snr/fwhm data
            svs_snr = np.genfromtxt(os.path.join(subject_dir, 'lcmodel_%s'%analysis_type, voxel_name, 'ppm_%s'%ppmst, 'snr.txt'), delimiter = ',')

            #grab voxel mask
            svs = os.path.join(subject_dir, 'svs_voxel_mask','%s%s_%s_RDA_MASK.nii'%(subject,workspace_dir[-10:-9], voxel_name))

            #get data into matrix
            anat_load = nb.load(anatomical)
            svs_load  = nb.load(svs)
            anat_data = anat_load.get_data()
            svs_data  = svs_load.get_data()

            # get svs cut coords
            coords = find_cut_coords(svs_load)

            # convert zeros to nans for visualization purposes
            svs_data[svs_data==0]=np.nan

            # plot voxel on anat
            fig =plt.figure()
            fig.set_size_inches(6.5, 6.5)
            fig.subplots_adjust(wspace=0.005)
            #1
            ax1 = plt.subplot2grid((1,3), (0,0),  colspan = 1, rowspan =1)
            ax1.imshow(anat_data[coords[0],:,:], matplotlib.cm.bone_r)
            ax1.imshow(svs_data[coords[0],:,:] , matplotlib.cm.rainbow_r, alpha = 0.7)
            ax1.set_xlim(23, 157)
            ax1.set_ylim(101, 230)
            ax1.axes.get_yaxis().set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
            #2
            ax2 = plt.subplot2grid((1,3), (0,1),  colspan = 1, rowspan =1)
            ax2.imshow(np.rot90(anat_data[:,:,coords[2]]), matplotlib.cm.bone_r )
            ax2.imshow(np.rot90(svs_data[:,:,coords[2]]) , matplotlib.cm.rainbow_r, alpha = 0.7 )
            ax2.set_xlim(230, 20)
            ax2.set_ylim(207, 4)
            ax2.axes.get_yaxis().set_visible(False)
            ax2.axes.get_xaxis().set_visible(False)
            #3
            ax3 = plt.subplot2grid((1,3), (0,2),  colspan = 1, rowspan =1)
            ax3.imshow(anat_data[:,coords[1],:], matplotlib.cm.bone_r, origin='lower')
            ax3.imshow(svs_data[:,coords[1],:] , matplotlib.cm.rainbow_r, alpha = 0.7, origin='lower')
            ax3.set_xlim(38, 140)
            ax3.set_ylim(160, 60)
            ax3.axes.get_yaxis().set_visible(False)
            ax3.axes.get_xaxis().set_visible(False)
            fig.tight_layout()
            fig.savefig('%s/localization_%s.png'%(qc_dir, voxel_name), dpi=200, bbox_inches='tight')

            # create qc report
            report = canvas.Canvas(os.path.join(qc_dir,'QC_REPORT_%s.pdf'%voxel_name), pagesize=(1280, 1556))
            report.setFont("Helvetica", 40)
            report.drawImage(os.path.join(qc_dir,'localization_%s.png'%voxel_name), 1, inch*13.5)
            report.drawImage(lcm_plot, 30, inch*1, width = 1200, height = 800)
            report.drawString(230, inch*20, ' %s%s, %s_%s , SNR=%s FWHM=%s ' %(subject,workspace_dir[-10:-9], voxel_name, analysis_type,  svs_snr[2],svs_snr[1]) )
            report.showPage()

            if analysis_type is 'twix':
                fig_f6 = os.path.join(subject_dir, 'svs_twix', voxel_name, 'f6_frequency_drift_correction.png')
                fig_f7 = os.path.join(subject_dir, 'svs_twix', voxel_name, 'f7_estimated_phase_phase_drift.png')
                fig_f8 = os.path.join(subject_dir, 'svs_twix', voxel_name, 'f8_estimated_frequency_drift.png')
                reader = open(os.path.join(subject_dir, 'svs_twix', voxel_name, voxel_name, 'readme.txt'), 'r')
                for line in reader:
                    if 'bad' in line:
                        badavn = line[34:38]
                report.drawImage(fig_f6, 1, inch*7.2)
                report.drawImage(fig_f7, 90, inch*1, width = 540, height = 450)
                report.drawImage(fig_f8, 590, inch*1, width = 540, height = 450)
                report.setFont("Helvetica", 40)
                report.drawString(350, inch*20, 'Number of Bad Averages =%s' %(badavn))
                report.save()
            else:
                report.save()


        def create_ppmst_quality_report(voxel_name):
            qc_dir  =  os.path.join(subject_dir, 'quality_control',  analysis_type,  voxel_name)
            ppmst_3 =  os.path.join(qc_dir, 'ppm_3.67', 'tmp',  '%s_lcmodel-0.png'%voxel_name)
            ppmst_4 =  os.path.join(qc_dir, 'ppm_4.0' , 'tmp',  '%s_lcmodel-0.png'%voxel_name)

            report = canvas.Canvas(os.path.join(qc_dir,'PPMST_REPORT_%s_%s.pdf'%(analysis_type, voxel_name)), pagesize=(1280, 1700))
            report.drawImage(ppmst_3, 30, inch*0.3 , width = 1200, height = 800)
            report.drawImage(ppmst_4, 30, inch*11.7, width = 1200, height = 800)
            report.save()


        # generate qc reports
        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'ACC', 'ppm_4.0', 'QC_REPORT_ACC.pdf')):
            print 'creating 4.0 QC-reports for ACC'
            create_voxel_plots('ACC', 4.0)
        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'ACC', 'ppm_3.67', 'QC_REPORT_ACC.pdf')):
            print 'creating 3.67 QC-reports for ACC'
            create_voxel_plots('ACC', 3.67)

        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'THA',  'ppm_4.0', 'QC_REPORT_THA.pdf')):
            print 'creating 4.0 QC-reports for THA'
            create_voxel_plots('THA', 4.0)
        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'THA',  'ppm_3.67', 'QC_REPORT_THA.pdf')):
            print 'creating 3.67 QC-reports for THA'
            create_voxel_plots('THA', 3.67)

        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'STR',  'ppm_4.0', 'QC_REPORT_STR.pdf')):
            print 'creating 4.0 QC-reports for STR'
            create_voxel_plots('STR', 4.0)
        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'STR',  'ppm_3.67', 'QC_REPORT_STR.pdf')):
            print 'creating 3.67 QC-reports for STR'
            create_voxel_plots('STR', 3.67)


        # generate PPMST reports
        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'ACC',  'PPMST_REPORT_%s_ACC.pdf'%analysis_type)):
            print 'creating ppmst report for ACC'
            create_ppmst_quality_report('ACC')

        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'THA',  'PPMST_REPORT_%s_THA.pdf'%analysis_type)):
            print 'creating ppmst report for THA'
            create_ppmst_quality_report('THA')

        if not os.path.isfile(os.path.join(subject_dir, 'quality_control',  analysis_type, 'STR',  'PPMST_REPORT_%s_STR.pdf'%analysis_type)):
            print 'creating ppmst report for STR'
            create_ppmst_quality_report('STR')


if __name__ == "__main__":
    create_mrs_qc(controls_a, workspace_controls_a, 'twix')
    #
    # create_mrs_qc(controls_b, workspace_controls_b, 'twix')
    # create_mrs_qc(controls_b, workspace_controls_b, 'rda')
    #
    # create_mrs_qc(patients_a, workspace_patients_a, 'rda')
    # create_mrs_qc(patients_a_twix, workspace_patients_a, 'twix')
    #
