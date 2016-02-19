import os
import numpy as np
from utilities.utils import calc_dice_metric, mkdir_path, find_cut_coords
from variables.subject_list import controls_b
import nipype.interfaces.fsl as fsl
import nibabel as nb
import matplotlib
import seaborn as sns
import matplotlib.pyplot as plt

project_dir = '/SCR3/workspace/project_GLUTAMATE'


def calc_overlap(population, population_name):


    for subject in population:

        print 'Calculating DICE METRIC for subject', subject

        subdir_a = os.path.join(project_dir, 'study_a', population_name, subject)
        subdir_b = os.path.join(project_dir, 'study_b', population_name, subject)

        dice_dir = os.path.join(subdir_b, 'dice_metric')
        mkdir_path(dice_dir)
        os.chdir(dice_dir)

        anat_a = os.path.join(subdir_a, 'anatomical_original/ANATOMICAL.nii')
        anat_b = os.path.join(subdir_b, 'anatomical_original/ANATOMICAL.nii')

        acc_a = os.path.join(subdir_a, 'svs_voxel_mask/%sa_ACC_RDA_MASK.nii'%subject)
        tha_a = os.path.join(subdir_a, 'svs_voxel_mask/%sa_THA_RDA_MASK.nii'%subject)
        str_a = os.path.join(subdir_a, 'svs_voxel_mask/%sa_STR_RDA_MASK.nii'%subject)

        acc_b = os.path.join(subdir_b, 'svs_voxel_mask/%sb_ACC_RDA_MASK.nii'%subject)
        tha_b = os.path.join(subdir_b, 'svs_voxel_mask/%sb_THA_RDA_MASK.nii'%subject)
        str_b = os.path.join(subdir_b, 'svs_voxel_mask/%sb_STR_RDA_MASK.nii'%subject)

        print '....running anat registration'
        if not os.path.isfile('anat_a2b.mat'):
            os.system('flirt -in %s -ref %s -omat anat_a2b.mat -out anat_a2b.nii.gz '
                      '-dof 6 -cost mutualinfo -finesearch 18'
                      %(anat_a, anat_b))

        print '....applying transform to SVS'
        if not os.path.isfile('overlap_ACC_a2b.nii.gz'):
            os.system('flirt -in %s -ref %s -applyxfm -init anat_a2b.mat -out overlap_ACC_a2b.nii.gz' %(acc_a, anat_b))
            os.system('flirt -in %s -ref %s -applyxfm -init anat_a2b.mat -out overlap_THA_a2b.nii.gz' %(tha_a, anat_b))
            os.system('flirt -in %s -ref %s -applyxfm -init anat_a2b.mat -out overlap_STR_a2b.nii.gz' %(str_a, anat_b))

        print '....calculating dice'
        if not os.path.isfile('dice_metric_ACC.txt'):
            calc_dice_metric(acc_b, os.path.join(dice_dir, 'overlap_ACC_a2b.nii.gz'), 'ACC')
            calc_dice_metric(tha_b, os.path.join(dice_dir, 'overlap_THA_a2b.nii.gz'), 'THA')
            calc_dice_metric(str_b, os.path.join(dice_dir, 'overlap_STR_a2b.nii.gz'), 'STR')

        print '....plotting'

        def plot_svs(svs_a, svs_b, anatomical, fname):
            import os
            import numpy as np
            import nibabel as nb
            import matplotlib
            import matplotlib.pyplot as plt
            import seaborn as sns
            from matplotlib import colors

            #get data into matrix
            anat_load = nb.load(anatomical)
            anat_data = anat_load.get_data()

            svs_load_a  = nb.load(svs_a)
            svs_data_a  = svs_load_a.get_data().astype(float)

            svs_load_b  = nb.load(svs_b)
            svs_data_b  = svs_load_b.get_data().astype(float)

            # get svs cut coords
            coords = find_cut_coords(svs_load_b)

            # convert zeros to nans for visualization purposes
            svs_data_a[svs_data_a==0]=np.nan
            svs_data_b[svs_data_b==0]=np.nan

            svs_x = svs_data_a * svs_data_b

            # plot voxel on anat
            fig =plt.figure()
            fig.set_size_inches(15, 15)
            fig.subplots_adjust(wspace=0.005)


            red = colors.ListedColormap(['red'])
            blue = colors.ListedColormap(['blue'])
            mix = colors.ListedColormap(['purple'])


            #1
            ax1 = plt.subplot2grid((1,3), (0,0),  colspan = 1, rowspan =1)
            ax1.imshow(anat_data[coords[0],:,:], matplotlib.cm.bone_r)
            ax1.imshow(svs_data_b[coords[0],:,:] , red, alpha = 0.7)
            ax1.imshow(svs_data_a[coords[0],:,:] , blue, alpha = 0.7)
            ax1.imshow(svs_x[coords[0],:,:]      ,  mix , alpha = 1, interpolation='nearest')
            ax1.set_xlim(23, 157)
            ax1.set_ylim(101, 230)
            ax1.axes.get_yaxis().set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
            ax1.axes.get_xaxis().set_visible(False)
            #2
            ax2 = plt.subplot2grid((1,3), (0,1),  colspan = 1, rowspan =1)
            ax2.imshow(np.rot90(anat_data[:,:,coords[2]]), matplotlib.cm.bone_r )
            ax2.imshow(np.rot90(svs_data_b[:,:,coords[2]]) , red, alpha = 0.7 )
            ax2.imshow(np.rot90(svs_data_a[:,:,coords[2]]) , blue, alpha = 0.7 )
            ax2.imshow(np.rot90(svs_x[:,:,coords[2]]) , mix, alpha = 0.7 )

            ax2.set_xlim(230, 20)
            ax2.set_ylim(207, 4)
            ax2.axes.get_yaxis().set_visible(False)
            ax2.axes.get_xaxis().set_visible(False)
            #3
            ax3 = plt.subplot2grid((1,3), (0,2),  colspan = 1, rowspan =1)
            ax3.imshow(anat_data[:,coords[1],:], matplotlib.cm.bone_r, origin='lower')
            ax3.imshow(svs_data_b[:,coords[1],:] , red, alpha = 0.7, origin='lower')
            ax3.imshow(svs_data_a[:,coords[1],:] , blue, alpha = 0.7, origin='lower')
            ax3.imshow(svs_x[:,coords[1],:]      , mix, alpha = 0.7, origin='lower')

            ax3.set_xlim(37, 140)
            ax3.set_ylim(160, 61)
            ax3.axes.get_yaxis().set_visible(False)
            ax3.axes.get_xaxis().set_visible(False)

            for ax in [ax1, ax2, ax3]:
                for axis in ['top','bottom','left','right']:
                    ax.spines[axis].set_color('black')
                    ax.spines[axis].set_linewidth(3)
            fig.tight_layout()
            fig.savefig('plot_overlap_%s.png'%fname, dpi=200, bbox_inches='tight')

        plot_svs('overlap_ACC_a2b.nii.gz', acc_b, anat_b, 'ACC')
        plot_svs('overlap_THA_a2b.nii.gz', tha_b, anat_b, 'THA')
        plot_svs('overlap_STR_a2b.nii.gz', str_b, anat_b, 'STR')

#calc_overlap(['HR8T'], 'controls')
calc_overlap(controls_b, 'controls')