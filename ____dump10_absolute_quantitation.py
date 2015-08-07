__author__ = 'kanaan' 'July 6 2015'

import os
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess
import pandas as pd


def quantiation_correction(population, workspace_dir, analysis_type):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    # output dir
    mkdir_path(os.path.join(workspace_dir[:-8], 'group_statistics'))
    results_dir = os.path.join(workspace_dir[:-8], 'group_statistics')

    def save_reliable_concentrations(population, workspace_dir, voxel_name, analysis_type):

        csv_list = []
        for subject in population:
            # get metabolite data for each subject and append to a list
                csv   = os.path.join(workspace_dir, subject, 'lcmodel_%s'%analysis_type, voxel_name, 'spreadsheet.csv')
                if os.path.isfile(csv):
                    reader = pd.read_csv(csv)
                    reader.insert(0, 'Subject', subject)
                    csv_list.append(reader)

        # creat a dataframe and place reliable metabolite data for every subject
        df = pd.concat(csv_list, ignore_index = True)
        reliable = df.loc[:,['Subject'   ,
                             ' Cre',      ' Cre %SD',
                             ' GPC+PCh',  ' GPC+PCh %SD',
                             ' NAA+NAAG', ' NAA+NAAG %SD',
                             ' mI',       ' mI %SD',
                             ' Glu',      ' Glu %SD',
                             ' Gln',      ' Gln %SD',
                             ' Glu+Gln',  ' Glu+Gln %SD']]

        # sort subjects alphabetically and reset index....
        reliable.sort(columns='Subject', inplace=True)
        reliable.reset_index(drop = True, inplace=True)

        # save reliable dataframe
        reliable.to_csv(os.path.join(results_dir, 'lcmodel_%s_%s_%s_%s.csv'%(analysis_type, voxel_name, workspace_dir[-8:],workspace_dir[-10:-9])))

        return reliable

    print '1. Creating new dataframe with reliable LC-Model concentrations for ACC,THA,STR'
    acc_reliable = save_reliable_concentrations(population, workspace_dir, 'ACC', analysis_type)
    tha_reliable = save_reliable_concentrations(population, workspace_dir, 'THA', analysis_type)
    str_reliable = save_reliable_concentrations(population, workspace_dir, 'STR', analysis_type)

    def save_tissue_proportions(population, workspace_dir, voxel_name):
        list_spm =[]

        for subject in population:
            # grab tissue proportion data for all subjects and dump into list
             spm = pd.read_csv(os.path.join(workspace_dir, subject, 'svs_voxel_stats', '%s_voxel_statistics_spm.txt'%voxel_name), header = None)
             spm.insert(0, 'SUBJECT', subject)
             list_spm.append(spm)

        # create concatenated dataframe for all tissue data in list
        df_spm = pd.concat(list_spm, ignore_index=True)
        df_spm.columns = ['SUBJECT', '%s_GM'%voxel_name,'%s_WM'%voxel_name,'%s_CSF'%voxel_name,'%s_SUM'%voxel_name]

        df_spm.to_csv(os.path.join(results_dir, 'proportions_%s_%s_%s.csv'%(voxel_name, workspace_dir[-8:],workspace_dir[-10:-9])))
        return df_spm

    print '2. Creating new dataframe with SPM tissue proportions for ACC,THA,STR'
    acc_props = save_tissue_proportions(population, workspace_dir, 'ACC')
    tha_prpos = save_tissue_proportions(population, workspace_dir, 'THA')
    str_props = save_tissue_proportions(population, workspace_dir, 'STR')

    def calc_asbolute(lcmodel, frac_gm, frac_wm, frac_csf):

        import math

        #lcmodel correction factor
        factor =(55.55 / (35.88 * 0.7))

        # relative water content in tissue.. determined experimentally.
        alpha_gm  = 0.81      # 0.78
        alpha_wm  = 0.71      # 0.65
        alpha_csf = 1.0       # 1.0

        #attentuation factor for water
        R_H2O_GM  = (1.0-math.e**(-3000.0/1820.0)) * math.e**(-30.0/99.0)
        R_H2O_WM  = (1.0-math.e**(-3000.0/1084.0)) * math.e**(-30.0/69.0)
        R_H2O_CSF = (1.0-math.e**(-3000.0/4163.0)) * math.e**(-30.0/503.0)

        #########  Correction Equations  #######
        # tissel equation
        Cmet1 =  (lcmodel    *   (((frac_csf    * 1. * (1. - frac_csf)) + (frac_gm * 0.81 + frac_wm * 0.71))/ (1. - frac_csf )))

        # gusseuw equation
        Cmet2  =  (lcmodel)   *   ((( frac_gm    * alpha_gm    * R_H2O_GM  +
                                     frac_wm    * alpha_wm    * R_H2O_WM  +
                                     frac_csf   * alpha_csf   * R_H2O_CSF ) /
                                    (frac_gm    * 1.0    + frac_wm * 1.0))) * factor
        # gusseew csf equation
        Cmet3 = (lcmodel)   * (1/ (1-frac_csf) )

        return Cmet2

    def create_absolute_df(reliable, proportions, voxel_name):
        cre = calc_asbolute(reliable[' Cre'],     proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        cho = calc_asbolute(reliable[' GPC+PCh'], proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        naa = calc_asbolute(reliable[' NAA+NAAG'],proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        ino = calc_asbolute(reliable[' mI'],      proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        glu = calc_asbolute(reliable[' Glu'],     proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        gln = calc_asbolute(reliable[' Gln'],     proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )
        glx = calc_asbolute(reliable[' Glu+Gln'], proportions['%s_GM'%voxel_name], proportions['%s_WM'%voxel_name], proportions['%s_CSF'%voxel_name] )

        absolute = pd.DataFrame({'Subjects' :  reliable['Subject'],
                                 'Cre'                           :  cre          ,
                                 'GPC+PCh'                       :  cho          ,
                                 'NAA+NAAG'                      :  naa          ,
                                 'mI'                            :  ino          ,
                                 'Glu'                           :  glu          ,
                                 'Gln'                           :  gln          ,
                                 'Glu+Gln'                       :  glx          ,})

        column_order= ['Subjects' ,'Cre', 'GPC+PCh','NAA+NAAG','mI','Glu','Gln','Glu+Gln']
        absolute = absolute.reindex(columns=column_order)

        absolute.to_csv(os.path.join(results_dir, 'absolute_%s_%s_%s_%s.csv'%(analysis_type, voxel_name, workspace_dir[-8:],workspace_dir[-10:-9])))

    print '3. Creating new dataframe with Absolute Concentrations for ACC,THA,STR'
    create_absolute_df(acc_reliable, acc_props, 'ACC' )
    create_absolute_df(tha_reliable, tha_prpos, 'THA' )
    create_absolute_df(str_reliable, str_props, 'STR' )

if __name__ == "__main__":
    quantiation_correction(controls_a, workspace_controls_a, 'rda')
    quantiation_correction(controls_b, workspace_controls_b, 'rda')
    quantiation_correction(patients_a, workspace_patients_a, 'rda')
    quantiation_correction(patients_b, workspace_patients_b, 'rda')

