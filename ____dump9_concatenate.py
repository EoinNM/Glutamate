__author__ = 'kanaan' '28.07.2015'

import os
import numpy as np
from variables.subject_list import *
import pandas as pd
from utilities.utils import mkdir_path

'''
________________________________

Include in tables
    1. Subject name
    2. Age
    3. Gender
    4. Linewidth (Hz)
    5. SNR
    6. Datashift
    7. Phase
    8.  ' Cre'
    9.  ' Cre %SD'
    10. ' GPC+PCh'
    11. ' GPC+PCh'
    12. ' NAA+NAAG'
    13. ' NAA+NAAG %SD'
    14. ' mI'
    15. ' mI %SD'
    16. ' Glu'
    17. ' Glu %SD'
    18. ' Gln'
    19. ' Gln %SD'
    20. ' Glu+Gln'
    21. ' Glu+Gln %SD'
    22. ' GABA'
    23. ' GABA %SD'
    24. ' MM09'
    25. ' MM09 %SD
    26. ' MM20'
    27. ' MM20 %SD'
    28. ' MM09+Lip09'
    29. ' MM09+Lip09 %SD'
    30. ' MM20+Lip20'
    31. ' MM20+Lip20 %SD'
    32. 'Comment_1'
    33. 'Comment_2'
________________________________
'''
def make_tables_and_flag_rejects(population, workspace_dir):
    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    print '%s- Creating group tables and flagging bad data'


    def create_group_dataframe(voxel_name, analysis_type):

        count = 0
        dataframe_group= []
        subject_with_no_twix = []
        for subject in population:
            count +=1
            #print '%s- Creating single dataframe for subject %s_%s' %(count,subject, workspace_dir[-10:-9])

            # grab demographic data from an rda header
            rda_file = open(os.path.join(workspace_dir, subject, 'svs_rda', 'ACC', 'h2o', '%s%s_ACC_WATER.rda'%(subject, workspace_dir[-10:-9]))).read().splitlines()
            gender = [i[11:15] for i in rda_file if 'PatientSex' in i][0]
            age    = [i[13:15] for i in rda_file if 'PatientAge' in i][0]

            columns =  ['Age', 'Gender', 'Linewidth', 'SNR', 'GM', 'WM', 'CSF', 'AllTissue',
                        'Cre', 'Cre%', 'tCho', 'tCho%', 'tNAA', 'tNAA%', 'mIno', 'mIno%', 'Glu', 'Glu%', 'Gln', 'Gln%', 'Glx', 'Glx%',
                        'GABA', 'GABA%', 'MM9', 'MM9%', 'MM20', 'MM20%', 'MM9Lip9','MM9Lip9%', 'MM20Lip20', 'MM20Lip20%', 'BetterFWHM']

            ##########################
            # grab data quality info #
            ##########################

            if os.path.isfile(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name, 'table')):

                rda_table  = open(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'table')).read().splitlines()
                twx_table  =  open(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name, 'table')).read().splitlines()

                #LINEWIDTH
                rda_fwhm = float([i[9:14] for i in rda_table if 'FWHM' in i][0]) * 123.24
                twx_fwhm = float([i[9:14] for i in twx_table if 'FWHM' in i][0]) * 123.24

                #Signal-to-noise ratio
                rda_snr  = float([i[29:31] for i in rda_table if 'FWHM' in i][0])
                twx_snr  = float([i[29:31] for i in twx_table if 'FWHM' in i][0])

                #Data-shift and phase
                # shift = [i[15:18] for i in table if 'Data Shift' in i][0]
                # phase = [i[7:32] for i in table if 'Ph:' in i][0]

                fwhm_threshold = 9.0

                comment_fwhm_1 = ['RDA' if rda_fwhm < twx_fwhm else 'TWIX']
                #comment_fwhm_2 = ['TWIX FWHM passes threshold cutoffs' if twx_fwhm < fwhm_threshold else 'TWIX FWHM above Threshold' if twx_fwhm > rda_fwhm else 'RDA FWHM better' ]


                ###############################
                # Grab Tissue Proportion data #
                ###############################

                prop_gm, prop_wm, prop_csf, prop_all  = np.genfromtxt(os.path.join(workspace_dir,subject,'svs_voxel_stats', '%s_voxel_statistics_spm.txt'%voxel_name), delimiter = ',')

                #######################################
                # Create Pandas Dataframe for subject #
                #######################################

                # get lcmodel metabolites from spreadsheet csv
                csv = pd.read_csv(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type,voxel_name, 'spreadsheet.csv'))

                # create dataframe with subject demographics, frequency data and reliable metabolite concentrations


                if analysis_type is 'twix':
                    fwhm = twx_fwhm
                    snr  = twx_snr
                elif analysis_type is 'rda':
                    fwhm = rda_fwhm
                    snr  = rda_snr

                dataframe = pd.DataFrame(columns = columns, index = ['%s'%subject])
                dataframe.loc['%s'%subject] = pd.Series({'Age'         : age,
                                                         'Gender'      : gender,
                                                         'Linewidth'   : fwhm,
                                                         'SNR'         : snr,
                                                         'GM'          : prop_gm  * 100.,
                                                         'WM'          : prop_wm  * 100.,
                                                         'CSF'         : prop_csf * 100.,
                                                         'AllTissue'   : prop_all * 100.,
                                                         'Cre'         : float(csv[' Cre']),
                                                         'Cre%'        : float(csv[' Cre %SD']),
                                                         'tCho'        : float(csv[' GPC+PCh']),
                                                         'tCho%'       : float(csv[' GPC+PCh %SD']),
                                                         'tNAA'        : float(csv[' NAA+NAAG']),
                                                         'tNAA%'       : float(csv[' NAA+NAAG %SD']),
                                                         'mIno'        : float(csv[' mI']),
                                                         'mIno%'       : float(csv[' mI %SD']),
                                                         'Glu'         : float(csv[' Glu']),
                                                         'Glu%'        : float(csv[' Glu %SD']),
                                                         'Gln'         : float(csv[' Gln']),
                                                         'Gln%'        : float(csv[' Gln %SD']),
                                                         'Glx'         : float(csv[' Glu+Gln']),
                                                         'Glx%'        : float(csv[' Glu+Gln %SD']),
                                                         'GABA'        : float(csv[' GABA']),
                                                         'GABA%'       : float(csv[' GABA %SD']),
                                                         'MM9'         : float(csv[' MM09']),
                                                         'MM9%'        : float(csv[' MM09 %SD']),
                                                         'MM20'        : float(csv[' MM20']),
                                                         'MM20%'       : float(csv[' MM20 %SD']),
                                                         'MM9Lip9'     : float(csv[' MM09+Lip09']),
                                                         'MM9Lip9%'    : float(csv[' MM09+Lip09 %SD']),
                                                         'MM20Lip20'   : float(csv[' MM20+Lip20']),
                                                         'MM20Lip20%'  : float(csv[' MM20+Lip20 %SD']),
                                                         'BetterFWHM'    : comment_fwhm_1[0],
                                                         })
                # append subject data to list
                dataframe_group.append(dataframe)

            else:
                subject_with_no_twix.append(subject)

                if analysis_type == 'rda':

                    rda_table  = open(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'table')).read().splitlines()
                    rda_fwhm = float([i[9:14] for i in rda_table if 'FWHM' in i][0]) * 123.24
                    rda_snr  = float([i[29:31] for i in rda_table if 'FWHM' in i][0])
                    comment_fwhm_rda = ['NoTwixData']
                    prop_gm, prop_wm, prop_csf, prop_all  = np.genfromtxt(os.path.join(workspace_dir,subject,'svs_voxel_stats', '%s_voxel_statistics_spm.txt'%voxel_name), delimiter = ',')
                    csvx = pd.read_csv(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type,voxel_name, 'spreadsheet.csv'))

                    dataframex = pd.DataFrame(columns = columns, index = ['%s'%subject])
                    dataframex.loc['%s'%subject] = pd.Series({'Age'     : age,
                                                         'Gender'      : gender,
                                                         'Linewidth'   : rda_fwhm,
                                                         'SNR'         : rda_snr,
                                                         'GM'          : prop_gm  * 100.,
                                                         'WM'          : prop_wm  * 100.,
                                                         'CSF'         : prop_csf * 100.,
                                                         'AllTissue'   : prop_all * 100.,
                                                         'Cre'         : float(csvx[' Cre']),
                                                         'Cre%'        : float(csvx[' Cre %SD']),
                                                         'tCho'        : float(csvx[' GPC+PCh']),
                                                         'tCho%'       : float(csvx[' GPC+PCh %SD']),
                                                         'tNAA'        : float(csvx[' NAA+NAAG']),
                                                         'tNAA%'       : float(csvx[' NAA+NAAG %SD']),
                                                         'mIno'        : float(csvx[' mI']),
                                                         'mIno%'       : float(csvx[' mI %SD']),
                                                         'Glu'         : float(csvx[' Glu']),
                                                         'Glu%'        : float(csvx[' Glu %SD']),
                                                         'Gln'         : float(csvx[' Gln']),
                                                         'Gln%'        : float(csvx[' Gln %SD']),
                                                         'Glx'         : float(csvx[' Glu+Gln']),
                                                         'Glx%'        : float(csvx[' Glu+Gln %SD']),
                                                         'GABA'        : float(csvx[' GABA']),
                                                         'GABA%'       : float(csvx[' GABA %SD']),
                                                         'MM9'         : float(csvx[' MM09']),
                                                         'MM9%'        : float(csvx[' MM09 %SD']),
                                                         'MM20'        : float(csvx[' MM20']),
                                                         'MM20%'       : float(csvx[' MM20 %SD']),
                                                         'MM9Lip9'     : float(csvx[' MM09+Lip09']),
                                                         'MM9Lip9%'    : float(csvx[' MM09+Lip09 %SD']),
                                                         'MM20Lip20'   : float(csvx[' MM20+Lip20']),
                                                         'MM20Lip20%'  : float(csvx[' MM20+Lip20 %SD']),
                                                         'BetterFWHM'  : comment_fwhm_rda[0],
                                                         })

                    # append subject data to list
                    dataframe_group.append(dataframex)

            # Concatenating subject data into a group dataframe
            print dataframe_group
        #   group_dataframe = pd.concat(dataframe_group, ignore_index = False).sort(columns='Age')
        #
        #     # create results directory and save group dataframe
        #     mkdir_path(os.path.join(workspace_dir, 'group_tables'))
        #     results_dir = os.path.join(workspace_dir, 'group_tables')
        #     group_dataframe.to_csv(os.path.join(results_dir, 'lcmodel_%s_%s_%s_%s.csv'%(analysis_type, voxel_name, workspace_dir[-8:],workspace_dir[-10:-9])))
        # print subject_with_no_twix
        # print 'check results here: %s'%results_dir
        #

    #return group_dataframe

    # ACC
    # ACC_RDA = create_group_dataframe('ACC', 'rda')
    create_group_dataframe('ACC', 'rda')
    create_group_dataframe('ACC', 'twix')

    # # THA
    # create_group_dataframe('THA', 'rda')
    # create_group_dataframe('THA', 'twix')
    #
    # # sTR
    # create_group_dataframe('STR', 'rda')
    # create_group_dataframe('STR', 'twix')

if __name__ == "__main__":
    # make_tables_and_flag_rejects(test_control_a, workspace_controls_a)
    # make_tables_and_flag_rejects(controls_a, workspace_controls_a)
    # make_tables_and_flag_rejects(controls_b, workspace_controls_b)
    # make_tables_and_flag_rejects(patients_a, workspace_patients_a)
    make_tables_and_flag_rejects(patients_b, workspace_patients_b)
