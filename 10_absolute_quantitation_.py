__author__ = 'kanaan'

import os
from variables.subject_list import *
import pandas as pd


def absolute_quantitation(workspace_dir, results_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'


    def calculate_asbolute_concentration(lcmodel, frac_gm, frac_wm, frac_csf):

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

    def make_absolute_dataframe(voxel_name, analysis_type, ppmst):

        #csv = os.path.join(results_dir, voxel_name, 'lcmodel_%s_%s_ppmst_%s_%s_%s.csv'%(voxel_name, analysis_type, ppmst, workspace_dir[-8:],workspace_dir[-10:-9]))
        csv = os.path.join(results_dir, voxel_name, 'v2_lcmodel_%s_%s_ppmst_%s_%s_%s.csv'%(voxel_name, analysis_type, ppmst, workspace_dir[-8:],workspace_dir[-10:-9]))
        df = pd.read_csv(csv, index_col = 0 )

        df.Cre       = calculate_asbolute_concentration(df.Cre, df.GM, df.WM, df.CSF)
        df.tCho      = calculate_asbolute_concentration(df.tCho, df.GM, df.WM, df.CSF)
        df.tNAA      = calculate_asbolute_concentration(df.tNAA, df.GM, df.WM, df.CSF)
        df.mIno      = calculate_asbolute_concentration(df.mIno, df.GM, df.WM, df.CSF)
        df.Glu       = calculate_asbolute_concentration(df.Glu, df.GM, df.WM, df.CSF)
        df.Glu_Cre   = calculate_asbolute_concentration(df.Glu_Cre, df.GM, df.WM, df.CSF)
        df.Gln       = calculate_asbolute_concentration(df.Gln, df.GM, df.WM, df.CSF)
        df.Gln_Cre   = calculate_asbolute_concentration(df.Gln_Cre, df.GM, df.WM, df.CSF)
        df.Glx       = calculate_asbolute_concentration(df.Glx, df.GM, df.WM, df.CSF)
        df.Glx_Cre   = calculate_asbolute_concentration(df.Glx_Cre, df.GM, df.WM, df.CSF)
        df.GABA      = calculate_asbolute_concentration(df.GABA, df.GM, df.WM, df.CSF)
        df.Asp       = calculate_asbolute_concentration(df.Asp, df.GM, df.WM, df.CSF)
        df.Tau       = calculate_asbolute_concentration(df.Tau, df.GM, df.WM, df.CSF)
        df.Lac       = calculate_asbolute_concentration(df.Lac, df.GM, df.WM, df.CSF)
        df.NAA       = calculate_asbolute_concentration(df.NAA, df.GM, df.WM, df.CSF)
        df.NAAG      = calculate_asbolute_concentration(df.NAAG, df.GM, df.WM, df.CSF)
        df.Ala       = calculate_asbolute_concentration(df.Ala, df.GM, df.WM, df.CSF)
        df.Glc       = calculate_asbolute_concentration(df.Glc, df.GM, df.WM, df.CSF)
        df.Scy       = calculate_asbolute_concentration(df.Scy, df.GM, df.WM, df.CSF)
        df.Gua       = calculate_asbolute_concentration(df.Gua, df.GM, df.WM, df.CSF)

        #df.to_csv(os.path.join(results_dir, voxel_name, 'absolute_%s_%s_ppmst_%s_%s_%s.csv'%(voxel_name, analysis_type, ppmst, workspace_dir[-8:],workspace_dir[-10:-9])))
        df.to_csv(os.path.join(results_dir, voxel_name, 'v2_absolute_%s_%s_ppmst_%s_%s_%s.csv'%(voxel_name, analysis_type, ppmst, workspace_dir[-8:],workspace_dir[-10:-9])))
        print 'check results here: %s'%results_dir

    make_absolute_dataframe('ACC', 'rda', 4.00)
    make_absolute_dataframe('ACC', 'rda', 3.67)
    make_absolute_dataframe('ACC', 'twix', 4.0)
    make_absolute_dataframe('ACC', 'twix', 3.67)

    make_absolute_dataframe('THA', 'rda', 4.00)
    make_absolute_dataframe('THA', 'rda', 3.67)
    make_absolute_dataframe('THA', 'twix', 4.0)
    make_absolute_dataframe('THA', 'twix', 3.67)

    make_absolute_dataframe('STR', 'rda', 4.00)
    make_absolute_dataframe('STR', 'rda', 3.67)
    make_absolute_dataframe('STR', 'twix', 4.0)
    make_absolute_dataframe('STR', 'twix', 3.67)

if __name__ == "__main__":
    #absolute_quantitation(workspace_controls_a, results_dir_a)
    #absolute_quantitation(workspace_patients_a, results_dir_a)
    #absolute_quantitation(workspace_controls_b, results_dir_b)
    absolute_quantitation(workspace_patients_b, results_dir_b)
