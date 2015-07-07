__author__ = 'kanaan' 'July 6 2015'

import os
from variables.subject_list import *
import shutil
from utilities.utils import mkdir_path
import subprocess


def create_mrs_qc(population, ):


    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
