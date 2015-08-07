__author__ = 'kanaan'

import os
import pandas as pd
from variables.subject_list import results_dir_a, results_dir_b, test_retest_dir
from variables.quality_list_a import  *
from variables.quality_list_b import  *
import numpy as np


def create_control_test_retest_dataframes(voxel_name, results_dir_a, results_dir_b, take_rda_a, take_rda_b, reject_a, reject_b):

    print '-----------------------------'
    print 'working on:', voxel_name

    if voxel_name is 'ACC':
        ppmst = 4.0
    else:
        ppmst = 3.67

    rda_a = pd.read_csv(os.path.join(results_dir_a, voxel_name, 'absolute_%s_rda_ppmst_%s_controls_a.csv'%(voxel_name, ppmst)), index_col = 0)
    rda_b = pd.read_csv(os.path.join(results_dir_b, voxel_name, 'absolute_%s_rda_ppmst_%s_controls_b.csv'%(voxel_name, ppmst)), index_col = 0)
    twx_a = pd.read_csv(os.path.join(results_dir_a, voxel_name, 'absolute_%s_twix_ppmst_%s_controls_a.csv'%(voxel_name, ppmst)), index_col = 0)
    twx_b = pd.read_csv(os.path.join(results_dir_b, voxel_name, 'absolute_%s_twix_ppmst_%s_controls_b.csv'%(voxel_name, ppmst)), index_col = 0)

    clean_a = twx_a
    clean_b = twx_b

    # Take RDA rows for subjects  with  rejected twix data
    for subject in take_rda_a:
        print 'Subject %sa has a better rda scan' %subject
        clean_a.loc[subject]  = rda_a.loc[subject]
    for subject in take_rda_b:
        print 'Subject %sb has a better rda scan' %subject
        clean_b.loc[subject]  = rda_b.loc[subject]

    #Drop rejected subjects
    for subject in reject_a:
        print 'Subject %sa is rejected... dropping'%subject
    clean_a = clean_a.drop(reject_a, axis = 0)

    for subject in reject_b:
        print 'Subject %sb is rejected... dropping'%subject
    clean_b = clean_b.drop(reject_b, axis = 0)


    # Replace High CRLB metabolites with NANs
    crlb_threshold = 50.0
    metabolites = ['Cre','tCho','tNAA', 'mIno','Glu', 'Gln','Glx','GABA', 'MM9','MM20','MM9Lip9','MM20Lip20']

    for metabolite in metabolites:
        clean_a.loc[clean_a['%s%%'%metabolite] > crlb_threshold, metabolite]= np.nan
        clean_b.loc[clean_b['%s%%'%metabolite] > crlb_threshold, metabolite]= np.nan

    clean_a.to_csv(os.path.join(test_retest_dir, 'trt_controls_%s_a.csv'%voxel_name))
    clean_b.to_csv(os.path.join(test_retest_dir, 'trt_controls_%s_b.csv'%voxel_name))
    print '-----------------------------'

    return clean_a, clean_b

if __name__ == "__main__":
    create_control_test_retest_dataframes('ACC', results_dir_a, results_dir_b,
                                          take_rda_a = CA_ACC_TAKE_RDA,
                                          take_rda_b = CB_ACC_TAKE_RDA,
                                          reject_a = CA_ACC_REJECT,
                                          reject_b = CB_ACC_REJECT)

    create_control_test_retest_dataframes('THA', results_dir_a, results_dir_b,
                                          take_rda_a = CA_THA_TAKE_RDA,
                                          take_rda_b = CB_THA_TAKE_RDA,
                                          reject_a = CA_THA_REJECT,
                                          reject_b = CB_THA_REJECT)

    create_control_test_retest_dataframes('STR', results_dir_a, results_dir_b,
                                          take_rda_a = CA_STR_TAKE_RDA,
                                          take_rda_b = CB_STR_TAKE_RDA,
                                          reject_a = CA_STR_REJECT,
                                          reject_b = CB_STR_REJECT)

