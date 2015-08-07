__author__ = 'kanaan'

import os
import numpy as np
import pandas as pd
from variables.quality_list_a import *
from variables.quality_list_b import *
from variables.subject_list import results_dir_a, results_dir_b, df_metabolite_dir


def make_comparison_frames(population, study_id, voxel_name, results_dir, take_rda_list, reject_list):

    print '--------------------------------------------------------------------------------------------------------------------'
    print 'Working on: %s_%s_%s' %(population, study_id, voxel_name)
    print ''
    if voxel_name is 'ACC':
        ppmst = 4.0
    else:
        ppmst = 3.67

    rda_a = pd.read_csv(os.path.join(results_dir, voxel_name, 'absolute_%s_rda_ppmst_%s_%s_%s.csv' %(voxel_name, ppmst, population, study_id)), index_col = 0)
    twx_a = pd.read_csv(os.path.join(results_dir, voxel_name, 'absolute_%s_twix_ppmst_%s_%s_%s.csv' %(voxel_name, ppmst, population, study_id )), index_col = 0)

    clean = twx_a

    # Take RDA for subjects with rejected twix data
    print 'TAKE-RDA'
    if take_rda_list is not None:
        for subject in take_rda_list:
            print 'Subject %sa-%s has a better rda scan.... replacing.' %(subject, voxel_name)
            clean.loc[subject] = rda_a.loc[subject]

    # # Replace scan A Spectra with Scan B spectra in cases with incorrect localization
    # print ''
    # print 'TAKE-B'
    # if take_b_list is not None:
    #     for subject in take_b_list:
    #         print 'Subject %s-%s has better b scan, replacing.' %(subject, voxel_name)
    #         clean.loc[subject] = twx_b.loc[subject]

    # Replace High CRLB metabolites with NANs
    crlb_threshold = 50
    metabolites = ['Cre','tCho','tNAA', 'mIno','Glu', 'Gln','Glx','GABA',  'MM9','MM20','MM9Lip9','MM20Lip20']
    print ''

    print 'CRLB CUTOFF =', crlb_threshold
    for metabolite in metabolites:
        for subject in clean.index:
            if clean.loc[subject]['%s%%'%metabolite] > crlb_threshold:
                print 'HIGH CRLB METABOLITES'
                print 'Subject %s-%s-%s CRLB above cutoff..... replace metabolite with NAN' %(subject, voxel_name, metabolite)
        clean.loc[clean['%s%%'%metabolite] > crlb_threshold, metabolite] = np.nan

    # Drop Rejected Subjects
    print ''
    print 'REJECTED SPECTRA'
    if reject_list is not None:
        for subject in reject_list:
            print 'TWIX-%s data for Subject %s rejected... dropping.' %(voxel_name, subject)

    # Save dataframe
    clean = clean.drop(reject_list, axis =0 )
    df_name = os.path.join(df_metabolite_dir, 'dataframe_%s_%s_%s.csv'%(voxel_name, population, study_id ))
    clean.to_csv(df_name)

    print ''
    print 'DATAFRAME SAVED AS:',df_name
    print '--------------------------------------------------------------------------------------------------------------------'
if __name__ == "__main__":
    make_comparison_frames(population = 'controls', study_id = 'a', voxel_name= 'ACC', results_dir = results_dir_a,  take_rda_list = CA_ACC_TAKE_RDA, reject_list= CA_ACC_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'a', voxel_name= 'ACC', results_dir = results_dir_a,  take_rda_list = PA_ACC_TAKE_RDA, reject_list= PA_ACC_REJECT)
    make_comparison_frames(population = 'controls', study_id = 'b', voxel_name= 'ACC', results_dir = results_dir_b,  take_rda_list = CB_ACC_TAKE_RDA, reject_list= CB_ACC_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'b', voxel_name= 'ACC', results_dir = results_dir_b,  take_rda_list = PB_ACC_TAKE_RDA, reject_list= PB_ACC_REJECT)

    make_comparison_frames(population = 'controls', study_id = 'a', voxel_name= 'THA', results_dir = results_dir_a,  take_rda_list = CA_THA_TAKE_RDA, reject_list= CA_THA_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'a', voxel_name= 'THA', results_dir = results_dir_a,  take_rda_list = PA_THA_TAKE_RDA, reject_list= PA_THA_REJECT)
    make_comparison_frames(population = 'controls', study_id = 'b', voxel_name= 'THA', results_dir = results_dir_b,  take_rda_list = CB_THA_TAKE_RDA, reject_list= CB_THA_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'b', voxel_name= 'THA', results_dir = results_dir_b,  take_rda_list = PB_ACC_TAKE_RDA, reject_list= PB_THA_REJECT)

    make_comparison_frames(population = 'controls', study_id = 'a', voxel_name= 'STR', results_dir = results_dir_a,  take_rda_list = CA_STR_TAKE_RDA, reject_list= CA_STR_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'a', voxel_name= 'STR', results_dir = results_dir_a,  take_rda_list = PA_STR_TAKE_RDA, reject_list= PA_STR_REJECT)
    make_comparison_frames(population = 'controls', study_id = 'b', voxel_name= 'STR', results_dir = results_dir_b,  take_rda_list = CB_STR_TAKE_RDA, reject_list= CB_STR_REJECT)
    make_comparison_frames(population = 'patients', study_id = 'b', voxel_name= 'STR', results_dir = results_dir_b,  take_rda_list = PB_STR_TAKE_RDA, reject_list= PB_STR_REJECT)



def plt_spectra(workspace_dir, rejected_subjects, analysis_type, voxel_name, ppmst):
    import itertools
    for subject in rejected_subjects:

        #define location of lcmodel coordinate file
        coord = os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type, voxel_name, 'ppm_%'%ppmst, 'coord')

        # function to extract lcmodel datapoints from coordinate file
        def get_lcmodel_coords(coord_file, analysis_type):
            import itertools

            f = open(coord_file)

            ppm = []
            phased = []
            fit = []
            base = []

            if analysis_type is 'rda':
                xrange_list = [(47,125), (126,204), (205,283),(284,362) ]
            elif analysis_type is 'twix':
                xrange_list = [(47,127), (128,208), (209,289),(290,370) ]

            for i, line in enumerate(f):
                if i in xrange(xrange_list[0][0], xrange_list[0][1] ):
                    ppm.append(np.array(line.split()))
                elif i in xrange(xrange_list[1][0], xrange_list[1][1]):
                    phased.append(np.array(line.split()))
                elif i in xrange(xrange_list[2][0], xrange_list[2][1]):
                    fit.append(np.array(line.split()))
                elif i in xrange(xrange_list[3][0], xrange_list[3][1]):
                    base.append(np.array(line.split()))


            ppm  = np.array(map( float, np.asarray(list(itertools.chain.from_iterable(ppm)))))
            pha  = np.array(map( float, np.asarray(list(itertools.chain.from_iterable(phased)))))
            fit  = np.array(map( float, np.asarray(list(itertools.chain.from_iterable(fit)))))
            bsl  = np.array(map( float, np.asarray(list(itertools.chain.from_iterable(base)))))
            res  = pha -fit
            return ppm, fit, res, bsl

        ppm, fit, res, bsl = get_lcmodel_coords(coord, 'twix')

        fig = plt.figure()
        fig.subplots_adjust(wspace=0.05)
        fig.set_size_inches(12, 8)

        ax1 = plt.subplot2grid((3,2), (0,0),  colspan = 3, rowspan =2)
        #ax1.axes.get_yaxis().set_visible(False)
        #ax1.axes.get_xaxis().set_visible(False)
        ax1.set_color_cycle(['red', 'green', 'blue'])
        ax1.plot(ppm, fit, 'blue', linewidth=2.5)
        ax1.plot(ppm, bsl, 'black')
        ax1.plot(ppm, res, 'red')
        ax1.set_xlim([0.2, 4.4])
        textstr = '%s_%s'%(subject,voxel_name)
        #ax1.text(0.75, 2500000, textstr, fontsize=14)
        plt.gca().invert_xaxis()

