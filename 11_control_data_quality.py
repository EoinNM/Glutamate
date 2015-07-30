__author__ = 'kanaan'

import os
import numpy as np
import pandas as pd
from variables.subject_list import *


'''
Quality Control Protocol.

Start with TWIX Spectra from Study a.

    - If RDA FWHM < TWIX FHWM -------------------------> Take RDA.
    - If FWHM > 0.07-0.1 ppm (8.5-12Hz), --------------> Flag Subject spectrum for rejection
    - If Metabolite CRLB > 50% ------------------------> Flag Subject metabolite for rejection

Inspect remaining spectra and reject spectra with
    - Incorrect voxel localization
    - Unexplained features in residuals
    - Baseline issues
    - Asymmetric line-shapes
    - Phase issues

For Control vs. Patient Comparison.
    - If Controls_A data is rejected, use Controls_B data if its passes checkpoints.
'''


def create_composite_control_dataframes_for_patient_comparison(voxel_name):

    ###############################
    ####     Control Zone      ####
    ###############################

    ##########################################################################################################
    #                   Grab rda and twix absolute dataframes for study_a and study_b                        #
    ##########################################################################################################
    df_a_rda = pd.read_csv(os.path.join(workspace_controls_a, 'group_tables', 'absolute_rda_%s_controls_a.csv'%voxel_name), index_col = 0)
    df_a_twx = pd.read_csv(os.path.join(workspace_controls_a, 'group_tables', 'absolute_twix_%s_controls_a.csv'%voxel_name), index_col = 0)

    df_b_rda = pd.read_csv(os.path.join(workspace_controls_b, 'group_tables', 'absolute_rda_%s_controls_b.csv'%voxel_name), index_col = 0)
    df_b_twx = pd.read_csv(os.path.join(workspace_controls_b, 'group_tables', 'absolute_twix_%s_controls_b.csv'%voxel_name), index_col = 0)

    clean = df_a_twx

    ##########################################################################################################
    #                    get subjects with bad TWIX FWHM and replace with RDA data                           #
    ##########################################################################################################

    twix_bad_fwhm = [subject for subject in df_a_twx.index if df_a_twx.ix[subject]['BetterFWHM'] == 'RDA']
    for subject in twix_bad_fwhm:
        clean.loc[subject] = df_a_rda.loc[subject]

    ##########################################################################################################
    #         replace controls_a data with controls_b data for subjects with known localization errors       #
    ##########################################################################################################
    controls_a_bad_localization = ['HM1X', 'SJBT','NP4T', 'KDET', # Localization errors
                                   'SI5T', 'BM8X']                # Parameter changes

    #add new column to define where the data is coming from
    clean['DataFrom'] = pd.Series('A', index = clean.index)

    for subject in controls_a_bad_localization:
        if subject in set(list(df_a_twx.index)) & set(list(df_b_twx.index)):
            clean.ix[subject] =df_b_rda.loc[subject]
            # add changed StudyID to the DataFrom column
            clean.DataFrom.fillna('Study_B', inplace=True)

    ##########################################################################################################
    #              replace metabolite with Cramer-Rao Lower bounds above 50% with NAN                        #
    ##########################################################################################################

    crlb_threshold = 20.0
    metabolites = ['Cre','tCho','tNAA', 'mIno','Glu', 'Gln','Glx','GABA', 'MM9','MM20','MM9Lip9','MM20Lip20']
    for metabolite in metabolites:
        clean.loc[clean['%s%%'%metabolite] > crlb_threshold, metabolite] = np.nan

    #rename DataType column
    clean.rename(columns={'BetterFWHM':'DataType'}, inplace=True)

    #save dataframe
    clean.to_csv(os.path.join(statistics_dir, '%s_controls_clean.csv'%voxel_name))

'__________________________________________________________________________________________________________________________________________'
'__________________________________________________________________________________________________________________________________________'
'__________________________________________________________________________________________________________________________________________'


def create_control_dataframes_for_test_retest_reliability(voxel_name):

    #Grab rda and twix absolute dataframes for study_a and study_b###################################

    df_a_rda = pd.read_csv(os.path.join(workspace_controls_a, 'group_tables', 'absolute_rda_%s_controls_a.csv'%voxel_name), index_col = 0)
    df_a_twx = pd.read_csv(os.path.join(workspace_controls_a, 'group_tables', 'absolute_twix_%s_controls_a.csv'%voxel_name), index_col = 0)

    df_b_rda = pd.read_csv(os.path.join(workspace_controls_b, 'group_tables', 'absolute_rda_%s_controls_b.csv'%voxel_name), index_col = 0)
    df_b_twx = pd.read_csv(os.path.join(workspace_controls_b, 'group_tables', 'absolute_twix_%s_controls_b.csv'%voxel_name), index_col = 0)

    clean_a = df_a_twx
    clean_b = df_b_twx

    #do the same on on control a and b dataframes for group comparison
    twix_bad_fwhm_a = [subject for subject in df_a_twx.index if df_a_twx.ix[subject]['BetterFWHM'] == 'RDA']
    for subject in twix_bad_fwhm_a:
        clean_a.loc[subject] = df_a_rda.loc[subject]

    twix_bad_fwhm_b = [subject for subject in df_b_twx.index if df_b_twx.ix[subject]['BetterFWHM'] == 'RDA']
    for subject in twix_bad_fwhm_b:
        clean_b.loc[subject] = df_b_rda.loc[subject]

    # Drop subjects without a retest scan from df_a
    test_only_subjects = [subject for subject in clean_a.index if subject not in clean_b.index]
    print 'Study_A Subjects without retest scan:', test_only_subjects
    #print '...Dropping from dataframe_a'
    clean_a = clean_a.drop(test_only_subjects, axis=0)

    clean_a.rename(columns={'BetterFWHM':'DataType'}, inplace=True)
    clean_b.rename(columns={'BetterFWHM':'DataType'}, inplace=True)
    clean_a.to_csv((os.path.join(statistics_dir, '%s_controls_a.csv'%voxel_name)))
    clean_b.to_csv((os.path.join(statistics_dir, '%s_controls_b.csv'%voxel_name)))

    #return clean_a, clean_b

'__________________________________________________________________________________________________________________________________________'
'__________________________________________________________________________________________________________________________________________'
'__________________________________________________________________________________________________________________________________________'



if __name__ == "__main__":
    #test-retest realiability
    create_control_dataframes_for_test_retest_reliability('ACC')
    create_control_dataframes_for_test_retest_reliability('THA')
    create_control_dataframes_for_test_retest_reliability('STR')

    #create_composite_control_dataframes_for_patient_comparison('ACC')

