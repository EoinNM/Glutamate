
__author__ = 'kanaan' '28.07.2015'

import os
import numpy as np
from variables.subject_list import *
import pandas as pd
from utilities.utils import mkdir_path


def concat_lcmodel_spreasheets(population, workspace_dir, results_dir):
    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    def create_group_dataframe(voxel_name, analysis_type, ppmst):

        df_group =[]
        for subject in population:
            print subject
            header = open(os.path.join(workspace_dir, subject, 'svs_rda', 'ACC', 'h2o', '%s%s_ACC_WATER.rda'%(subject, workspace_dir[-10:-9]))).read().splitlines()
            gender = [i[11:15] for i in header if 'PatientSex' in i][0]
            age    = [i[13:15] for i in header if 'PatientAge' in i][0]

            analysis_file = os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type, voxel_name, 'ppm_%s'%ppmst, 'table')

            if not os.path.isfile(analysis_file):
                print 'Subject %s has not %s data for %s' %(subject, analysis_type, voxel_name)

            else:
                print os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type ,  voxel_name, 'ppm_%s'%ppmst, 'snr.txt')
                quality = np.genfromtxt(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type ,  voxel_name, 'ppm_%s'%ppmst, 'snr.txt'), delimiter = ',')

                # grab tissue proprotion data
                prop_gm, prop_wm, prop_csf, prop_all  = np.genfromtxt(os.path.join(workspace_dir,subject,'svs_voxel_stats', '%s_voxel_statistics_spm.txt'%voxel_name), delimiter = ',')

                # get lcmodel metabolites from spreadsheet csv
                csv = pd.read_csv(os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type,voxel_name, 'ppm_%s'%ppmst, 'spreadsheet.csv'))

                # create dataframe with subject demographics, frequency data and reliable metabolite concentrations
                columns =  ['Age', 'Gender', 'FWHM', 'SNR', 'Shift', 'Ph0', 'Ph1', 'GM', 'WM', 'CSF', 'AllTissue',
                            'Cre', 'Cre%', 'tCho', 'tCho%', 'tNAA', 'tNAA%', 'mIno', 'mIno%', 'Glu', 'Glu%', 'Gln', 'Gln%', 'Glx', 'Glx%',
                            'Glu_Cre',  'Gln_Cre',  'Glx_Cre',
                            'GABA', 'GABA%', 'MM9', 'MM9%', 'MM20', 'MM20%', 'MM9Lip9','MM9Lip9%', 'MM20Lip20', 'MM20Lip20%']

                df_subject = pd.DataFrame(columns = columns, index = ['%s'%subject])
                df_subject.loc['%s'%subject] = pd.Series({'Age'         : age,
                                                         'Gender'      : gender,
                                                         'FWHM'   : quality[1],
                                                         'SNR'         : quality[2],
                                                         'Shift'   : quality[3],
                                                         'Ph0'         : quality[4],
                                                         'Ph1'         : quality[5],
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
                                                         'Glu_Cre'     : float(csv[' Glu/Cre']),
                                                         'Gln_Cre'     : float(csv[' Gln/Cre']),
                                                         'Glx_Cre'     : float(csv[' Glu+Gln/Cre']),
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
                                                         })

                # append subject data to list
                df_group.append(df_subject)

        group_dataframe = pd.concat(df_group, ignore_index = False).sort(columns='Age')


        # create results directory and save group dataframe
        mkdir_path(os.path.join(results_dir, voxel_name))
        group_dataframe.to_csv(os.path.join(results_dir, voxel_name, 'lcmodel_%s_%s_ppmst_%s_%s_%s.csv'%(voxel_name, analysis_type, ppmst, workspace_dir[-8:],workspace_dir[-10:-9])))

        print 'NMR-093%s_ %s %s_%s Results here: %s'%( workspace_dir[-10:-9],workspace_dir[-8:], voxel_name,analysis_type, results_dir)

    # ACC
    create_group_dataframe('ACC', 'rda', 4.00)
    create_group_dataframe('ACC', 'rda', 3.67)
    create_group_dataframe('ACC', 'twix', 4.0)
    create_group_dataframe('ACC', 'twix', 3.67)

    create_group_dataframe('THA', 'rda', 4.00)
    create_group_dataframe('THA', 'rda', 3.67)
    create_group_dataframe('THA', 'twix', 4.0)
    create_group_dataframe('THA', 'twix', 3.67)

    create_group_dataframe('STR', 'rda', 4.00)
    create_group_dataframe('STR', 'rda', 3.67)
    create_group_dataframe('STR', 'twix', 4.0)
    create_group_dataframe('STR', 'twix', 3.67)


if __name__ == "__main__":

    concat_lcmodel_spreasheets(controls_a, workspace_controls_a, results_dir_a)
    concat_lcmodel_spreasheets(patients_a, workspace_patients_a, results_dir_a)

    concat_lcmodel_spreasheets(controls_b, workspace_controls_b, results_dir_b)
    concat_lcmodel_spreasheets(patients_b, workspace_patients_b, results_dir_b)
