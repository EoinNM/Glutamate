__author__ = 'kanaan' 'July 6 2015'

from nilearn.plotting.find_cuts import find_cut_slices
import os
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess
import numpy as np
import nibabel as nb
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

        print 'Creating MRS Quality Control Report for SUBJECT %s' %subject

        # grab data
        subject_dir = os.path.join(workspace_dir, subject)
        anatomical  = os.path.join(subject_dir, 'anatomical_original', 'ANATOMICAL.nii')

        def create_voxel_plots(voxel_name):
            print 'creating report for %s voxel' %voxel_name
            #create output QC directory
            mkdir_path(os.path.join(subject_dir, 'quality_control', analysis_type, voxel_name, 'tmp'))
            tmp_dir = os.path.join(subject_dir, 'quality_control',  analysis_type, voxel_name, 'tmp')
            qc_dir  = os.path.join(subject_dir, 'quality_control',  analysis_type, voxel_name)


            #grab voxel mask
            svs = os.path.join(subject_dir, 'svs_voxel_mask','%s%s_%s_RDA_MASK.nii'%(subject,workspace_dir[-10:-9], voxel_name))

            #get data into matrix
            anat_load = nb.load(anatomical)
            svs_load  = nb.load(svs)
            anat_data = anat_load.get_data()
            svs_data  = svs_load.get_data()

            # convert zeros to nans for visualization purposes
            svs_data[svs_data==0]=np.nan

            #grab lcmodel plots
            svs_lcmodel = os.path.join(subject_dir, 'lcmodel_%s'%analysis_type, voxel_name, 'ps.pdf')

            # create localization pngs
            make_png = ['convert', '-density', '150', '-trim', '%s'%svs_lcmodel,  '-quality', '300', '-sharpen', '0x1.0', '%s/%s_lcmodel.png'%(tmp_dir, voxel_name)]

            subprocess.call(make_png)

            lcm_plot = os.path.join(tmp_dir, '%s_lcmodel-0.png'%voxel_name)

            #grab snr/fwhm data
            svs_snr = np.genfromtxt(os.path.join(subject_dir, 'lcmodel_%s'%analysis_type, '%s'%voxel_name, 'snr.txt'), delimiter = ',')

            # plot voxel localozation
            x = find_cut_slices(svs_load, direction='x', n_cuts=1)
            y = find_cut_slices(svs_load, direction='y', n_cuts=1)
            z = find_cut_slices(svs_load, direction='z', n_cuts=1)

            fig =plt.figure()
            fig.set_size_inches(6.5, 6.5)
            fig.subplots_adjust(wspace=0.005)
            #1
            ax1 = plt.subplot2grid((1,3), (0,0),  colspan = 1, rowspan =1)
            ax1.imshow(anat_data[-y[0],:,:], matplotlib.cm.bone_r )
            ax1.imshow(svs_data[-y[0],:,:] , matplotlib.cm.rainbow_r, alpha = 0.7)
            ax1.set_xlim(23, 157)
            ax1.set_ylim(101, 230)
            ax1.axes.get_yaxis().set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
            #2
            ax2 = plt.subplot2grid((1,3), (0,1),  colspan = 1, rowspan =1)
            ax2.imshow(np.rot90(anat_data[:,:,-x[0]]), matplotlib.cm.bone_r )
            ax2.imshow(np.rot90(svs_data[:,:,-x[0]]) , matplotlib.cm.rainbow_r, alpha = 0.7 )
            ax2.set_xlim(230, 20)
            ax2.set_ylim(207, 4)
            ax2.axes.get_yaxis().set_visible(False)
            ax2.axes.get_xaxis().set_visible(False)
            #3
            ax3 = plt.subplot2grid((1,3), (0,2),  colspan = 1, rowspan =1)
            ax3.imshow(anat_data[:,-z[0],:], matplotlib.cm.bone_r, origin='lower')
            ax3.imshow(svs_data[:,-z[0],:] , matplotlib.cm.rainbow_r, alpha = 0.7, origin='lower')
            ax3.set_xlim(38, 140)
            ax3.set_ylim(180, 80)
            ax3.axes.get_yaxis().set_visible(False)
            ax3.axes.get_xaxis().set_visible(False)
            fig.tight_layout()
            fig.savefig('%s/localization_%s.png'%(qc_dir, voxel_name), dpi=200, bbox_inches='tight')

            # create qc report
            report = canvas.Canvas(os.path.join(qc_dir,'QC_REPORT_%s.pdf'%voxel_name), pagesize=(1280, 1556))
            report.drawImage(os.path.join(qc_dir,'localization_%s.png'%voxel_name), 1, inch*13.5)
            report.setFont("Helvetica", 30)
            #c.drawString(inch*8, inch*11, 'SkullStripped' )
            report.drawImage(lcm_plot, 30, inch*1, width = 1200, height = 800)
            report.drawString(300, inch*20, ' %s%s, %s , SNR=%s FWHM=%s ' %(subject,workspace_dir[-10:-9], voxel_name, svs_snr[2],svs_snr[1]) )
            report.showPage()
            report.save()

        create_voxel_plots('ACC')
        create_voxel_plots('THA')
        create_voxel_plots('STR')

if __name__ == "__main__":
    create_mrs_qc(test_subject, workspace_patients_a, 'rda')
