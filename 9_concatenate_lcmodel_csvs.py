
__author__ = 'kanaan' '28.07.2015'

import os
import numpy as np
from variables.subject_list import *
import pandas as pd
from utilities.utils import mkdir_path


def check_better_fwhm(subject, workspace_dir, voxel_name):

    rda_table  = open(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'table')).read().splitlines()
    twx_table  = open(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name, 'table')).read().splitlines()

    rda_fwhm = float([i[9:14] for i in rda_table if 'FWHM' in i][0]) * 123.24
    twx_fwhm = float([i[9:14] for i in twx_table if 'FWHM' in i][0]) * 123.24

    comment_fwhm = ['RDA' if rda_fwhm < twx_fwhm else 'TWIX']

    return comment_fwhm



def make_tables_and_flag_rejects(population, workspace_dir):
    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    def create_group_dataframe(voxel_name, analysis_type):

        df_group =[]
        for subject in population:
            header = open(os.path.join(workspace_dir, subject, 'svs_rda', 'ACC', 'h2o', '%s%s_ACC_WATER.rda'%(subject, workspace_dir[-10:-9]))).read().splitlines()
            gender = [i[11:15] for i in header if 'PatientSex' in i][0]
            age    = [i[13:15] for i in header if 'PatientAge' in i][0]

            analysis_file = os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type, voxel_name, 'table')

            if not os.path.isfile(analysis_file):
                print 'subject %s has not twix data for %s' %(subject,voxel_name)

            else:
                # grab data quality parameters
                table = open(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type, voxel_name, 'table')).read().splitlines()
                fwhm  = float([i[9:14] for i in table if 'FWHM' in i][0]) * 123.24
                snr  = float([i[29:31] for i in table if 'FWHM' in i][0])

                if os.path.isfile(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name, 'table')):
                    comment = check_better_fwhm(subject, workspace_dir, voxel_name)
                else:
                    comment= ['RDA_NoTwixData']

                # grab tissue proprotion data
                prop_gm, prop_wm, prop_csf, prop_all  = np.genfromtxt(os.path.join(workspace_dir,subject,'svs_voxel_stats', '%s_voxel_statistics_spm.txt'%voxel_name), delimiter = ',')

                # get lcmodel metabolites from spreadsheet csv
                csv = pd.read_csv(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type,voxel_name, 'spreadsheet.csv'))

                # create dataframe with subject demographics, frequency data and reliable metabolite concentrations

                columns =  ['Age', 'Gender', 'Linewidth', 'SNR', 'GM', 'WM', 'CSF', 'AllTissue',
                            'Cre', 'Cre%', 'tCho', 'tCho%', 'tNAA', 'tNAA%', 'mIno', 'mIno%', 'Glu', 'Glu%', 'Gln', 'Gln%', 'Glx', 'Glx%',
                            'GABA', 'GABA%', 'MM9', 'MM9%', 'MM20', 'MM20%', 'MM9Lip9','MM9Lip9%', 'MM20Lip20', 'MM20Lip20%', 'BetterFWHM']

                df_subject = pd.DataFrame(columns = columns, index = ['%s'%subject])
                df_subject.loc['%s'%subject] = pd.Series({'Age'         : age,
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
                                                         'BetterFWHM'    : comment[0],
                                                         })

                # append subject data to list
                df_group.append(df_subject)

        group_dataframe = pd.concat(df_group, ignore_index = False).sort(columns='Age')


        # create results directory and save group dataframe
        mkdir_path(os.path.join(workspace_dir, 'group_tables'))
        results_dir = os.path.join(workspace_dir, 'group_tables')
        group_dataframe.to_csv(os.path.join(results_dir, 'lcmodel_%s_%s_%s_%s.csv'%(analysis_type, voxel_name, workspace_dir[-8:],workspace_dir[-10:-9])))

        print '%s_%s Results here: %s'%( voxel_name,analysis_type, results_dir)

    # ACC
    create_group_dataframe('ACC', 'rda')
    create_group_dataframe('ACC', 'twix')


if __name__ == "__main__":

    make_tables_and_flag_rejects(controls_a, workspace_controls_a)
    make_tables_and_flag_rejects(controls_b, workspace_controls_b)
    make_tables_and_flag_rejects(patients_a, workspace_patients_a)
    make_tables_and_flag_rejects(patients_b, workspace_patients_b)
