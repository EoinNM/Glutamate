__author__ = 'kanaan' 'July 3 2015'


import os
import subprocess
import shutil
from variables.subject_list import *
from utilities.utils import mkdir_path


def run_lcmodel_on_drift_corrected_data(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Running Frequency and Phase Drift Correction for  subject %s_%s' %(count,subject, workspace_dir[-10:-9])
        print '.'

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                       Running Frequency and Phase Drift Correction
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # inputs
        twix_dir = os.path.join(workspace_dir, subject, 'svs_twix')

        def run_lcmodel_raw(voxel_name, ppmst):

            print ''
            print 'PROCESSING SPECTRA WITH LCMODEL FOR %s PPMST = %s'%(voxel_name, ppmst)
            #
            #mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name,  'ppm_%s'%ppmst, 'met'))
            #mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix', voxel_name,  'ppm_%s'%ppmst, 'h2o'))
            #lcmodel_dir = os.path.join(workspace_dir, subject, 'lcmodel_twix',voxel_name,  'ppm_%s'%ppmst)

            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix_NMEACH', voxel_name,  'ppm_%s'%ppmst, 'met'))
            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_twix_NMEACH', voxel_name,  'ppm_%s'%ppmst, 'h2o'))
            lcmodel_dir = os.path.join(workspace_dir, subject, 'lcmodel_twix_NMEACH',voxel_name,  'ppm_%s'%ppmst)

            shutil.copy(os.path.join(twix_dir, '%s'%voxel_name, '%s'%voxel_name, '%s_lcm'%voxel_name),
                        os.path.join(lcmodel_dir, 'met', 'RAW'))

            shutil.copy(os.path.join(twix_dir, '%s'%voxel_name, '%s_w'%voxel_name, '%s_w_lcm'%voxel_name),
                        os.path.join(lcmodel_dir, 'h2o', 'RAW'))

            met = os.path.join(lcmodel_dir, 'met', 'RAW')
            h2o = os.path.join(lcmodel_dir, 'h2o', 'RAW')

            # read some data from the RDA header
            rda_info = []
            rda_header = open(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'ppm_%s'%ppmst, 'rda_header.txt'), 'r')
            for line in rda_header:
               rda_info.append(line)

            # define twix parameters
            nunfil = 2078
            hzpppm = 123.242398
            echot  = 30.0
            deltat = 0.000417


            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                              Building the control file
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            print '...building control file'
            file = open(os.path.join(lcmodel_dir, 'control'), "w")
            file.write(" $LCMODL\n")
            file.write(" title= 'TWIX - %s' \n" %rda_info[0])
            file.write(" srcraw= '%s' \n" %met)
            file.write(" srch2o= '%s' \n" %h2o)
            file.write(" savdir= '%s' \n" %lcmodel_dir)
            file.write(" ppmst= %s \n"%ppmst)
            file.write(" ppmend= 0.3\n")
            file.write(" nunfil= %s\n"%nunfil)
            file.write(" ltable= 7\n")
            file.write(" lps= 8\n")
            file.write(" lprint= 6\n")
            file.write(" lcsv= 11\n")
            file.write(" lcoraw= 10\n")
            file.write(" lcoord= 9\n")
            file.write(" hzpppm= %s\n"%hzpppm)
            file.write(" filtab= '%s/table'\n" %lcmodel_dir)
            file.write(" filraw= '%s/met/RAW'\n" %lcmodel_dir)
            file.write(" filps= '%s/ps'\n" %lcmodel_dir)
            file.write(" filpri= '%s/print'\n" %lcmodel_dir)
            file.write(" filh2o= '%s/h2o/RAW'\n" %lcmodel_dir)
            file.write(" filcsv= '%s/spreadsheet.csv'\n" %lcmodel_dir)
            file.write(" filcor= '%s/coraw'\n" %lcmodel_dir)
            file.write(" filcoo= '%s/coord'\n" %lcmodel_dir)
            file.write(" filbas= '/home/raid3/kanaan/.lcmodel/basis-sets/press_te30_3t_01a.basis'\n")
            file.write(" echot= %s \n" %echot)
            file.write(" dows= T \n")
            file.write(" NEACH= 999 \n") # export met fits
            #file.write(" DEGPPM =0 \n")
            file.write(" doecc= T\n")
            file.write(" deltat= %s\n"%deltat)
            file.write(" $END\n")
            file.close()

            if os.path.isfile(os.path.join(lcmodel_dir,  'spreadsheet.csv')):
                 print 'Spectrum already processed .................moving on'
            else:
                print '...running standardA4pdf execution-script '
                print ''
                lcm_command = ['/bin/sh','/home/raid3/kanaan/.lcmodel/execution-scripts/standardA4pdfv3','%s' %lcmodel_dir,'30','%s' %lcmodel_dir,'%s' %lcmodel_dir]
                print '... running execution script'
                print subprocess.list2cmdline(lcm_command)
                subprocess.call(lcm_command)

            reader = open(os.path.join(lcmodel_dir, 'table'), 'r')
            for line in reader:
                if 'FWHM' in line:
                    fwhm = float(line[9:14])
                    snrx  = line[29:31]
                if 'Data shift' in line:
                    shift = line[15:21]
                if 'Ph:' in line:
                    ph0 = line[6:10]
                    ph1 = line[19:24]
                    fwhm_hz = fwhm * 123.24

                    file = open(os.path.join(lcmodel_dir, 'snr.txt'), "w")
                    file.write('%s, %s, %s, %s, %s, %s' %(fwhm,fwhm_hz, snrx, shift, ph0, ph1))
                    file.close()
            print '###############################################################################'

        #ACC##########################################################################################
        run_lcmodel_raw(voxel_name = 'ACC', ppmst = 4.00)
        run_lcmodel_raw(voxel_name = 'ACC', ppmst = 3.67)

        #THA##########################################################################################
        run_lcmodel_raw(voxel_name = 'THA', ppmst = 4.00)
        run_lcmodel_raw(voxel_name = 'THA', ppmst = 3.67)

        #STR##########################################################################################
        run_lcmodel_raw(voxel_name = 'STR', ppmst = 4.00)
        run_lcmodel_raw(voxel_name = 'STR', ppmst = 3.67)
        ##########################################################################################

if __name__ == "__main__":
    run_lcmodel_on_drift_corrected_data(controls_a, workspace_controls_a)
    #run_lcmodel_on_drift_corrected_data(controls_b, workspace_controls_b)
    #run_lcmodel_on_drift_corrected_data(patients_a_twix, workspace_patients_a)
    #run_lcmodel_on_drift_corrected_data(patients_b_twix, workspace_patients_b)

