__author__ = 'kanaan'

import os
import numpy as np
import pandas as pd
import scipy.stats as stats
pd.options.display.max_columns = 50

statistics_dir = '/SCR3/workspace/project_GLUTAMATE/statistics/'

def run_statistics(voxel_name):
    # Load dataframes
    controls_a = pd.read_csv(os.path.join(statistics_dir, '%s_controls_a.csv'%voxel_name ), index_col = 0)
    controls_b = pd.read_csv(os.path.join(statistics_dir, '%s_controls_b.csv'%voxel_name ), index_col = 0)

    # Run an independent t-test on QUALITY PARAMETERS
    ttpaired_fwhm = stats.ttest_rel(controls_a['Linewidth'], controls_b['Linewidth'])
    ttpaired_snr  = stats.ttest_rel(controls_a['SNR'], controls_b['SNR'])



    print "FWHM: T-statistic is %.3f and the p-value is %.3f." % ttpaired_fwhm

    return controls_a, controls_b