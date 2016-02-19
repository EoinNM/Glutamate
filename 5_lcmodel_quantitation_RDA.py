__author__ = 'kanaan' 'July 6 2015'

import os
from variables.subject_list import *
from utilities.utils import mkdir_path
import subprocess
import numpy as np


def run_lcmodel(population, workspace_dir):

    print '#############################################################################'
    print ''
    print '                 RUNNNING PROJECT NMR-093%s %s' %(workspace_dir[-10:-9], workspace_dir[-8:])
    print ''
    print '#############################################################################'

    count = 0
    for subject in population:
        count +=1
        print '========================================================================================'
        print '%s- Running lcmodel on subject %s' %(count,subject)
        print ''

        def run_lcmodel_on_voxel(voxel_name, ppmst):

            #define input and output directories
            svs_dir   = os.path.join(workspace_dir, subject, 'svs_rda')
            rda_met  = os.path.join(svs_dir, voxel_name, 'met', '%s%s_%s_SUPPRESSED.rda' %(subject, workspace_dir[-10:-9], voxel_name))
            rda_h2o  = os.path.join(svs_dir, voxel_name, 'h2o', '%s%s_%s_WATER.rda' %(subject, workspace_dir[-10:-9], voxel_name))
            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'ppm_%s'%ppmst, 'met'))
            mkdir_path(os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'ppm_%s'%ppmst, 'h2o'))
            lcmodel_dir = os.path.join(workspace_dir, subject, 'lcmodel_rda', voxel_name, 'ppm_%s'%ppmst)


            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                                RUN LCMODEL BIN2RAW
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

            if os.path.isfile(os.path.join(lcmodel_dir, 'met', 'RAW')) and  os.path.isfile(os.path.join(lcmodel_dir, 'h2o', 'RAW')):
                pass
                #print 'Bin2raw already run.........................moving on '
            else:
                print ' Generating RAW frequency files with BIN2RAW'
                met_bin2raw = ['/home/raid3/kanaan/.lcmodel/siemens/bin2raw', '%s'%rda_met, '%s/'%lcmodel_dir, 'met']
                h2o_bin2raw = ['/home/raid3/kanaan/.lcmodel/siemens/bin2raw', '%s'%rda_h2o, '%s/'%lcmodel_dir, 'h2o']

                subprocess.call(met_bin2raw)
                subprocess.call(h2o_bin2raw)

            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                              Read Scan parameters from RDA file
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            reader = open(rda_met, 'r')
            for line in reader:
                if 'SeriesDescription' in line:
                    Series = line[19:30]
                elif 'TR:' in line:
                    TR = line[4:8]
                elif 'TE:' in line:
                    TE = line[4:6]
                elif 'VectorSize' in line:
                    nfil = line[12:16]
                elif 'NumberOfAverages' in line:
                    NS = line[18:21]
                elif 'AcquisitionNumber' in line:#
                    ACQ = line[19:21]
                elif 'PatientSex' in line:
                    Sex = line[12:13]
                elif 'SeriesNumber' in line:
                    Seriesnum = line[14:16]
                elif 'PatientAge' in line:#
                    Age = line[12:15]
                elif 'PatientWeight' in line:
                    Weight = line[15:17]
                elif 'PixelSpacingRow' in line:
                    PSR = float(line[17:20])
                elif 'PixelSpacingCol' in line:
                    PSC = float(line[17:20])
                elif 'PixelSpacing3D:' in line:
                    PS3d = float(line[16:19])
                elif 'StudyDate' in line:
                    datex = line[0:19]

            volume = np.round(((PSR * PSC * PS3d) / 1000),2)

            header = open(os.path.join(lcmodel_dir, 'rda_header.txt'), 'w')
            header.write('%s(%s %s %skg); %s; %s %sx%sx%s=%s; TR/TE/NS=%s/%s/%s'
                          %(subject, Sex, Age, Weight, datex, voxel_name, PSR,PSC,PS3d,volume, TR,TE, NS))
            header.close()
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                              Building the control file
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
            if os.path.isfile(os.path.join(lcmodel_dir, 'control')):
                pass
                #print 'Control file already created................moving on'
            else:
                print 'Processing Spectra with LCMODEL'
                print '...building control file'

                file = open(os.path.join(lcmodel_dir, 'control'), "w")
                file.write(" $LCMODL\n")
                file.write(" title= 'RDA - %s(%s %s %skg), %s, %s %sx%sx%s, TR/TE/NS=%s/%s/%s' \n" %(subject, Sex, Age, Weight, datex, voxel_name, PSR,PSC,PS3d, TR,TE, NS ))
                file.write(" srcraw= '%s' \n" %rda_met)
                file.write(" srch2o= '%s' \n" %rda_h2o)
                file.write(" savdir= '%s' \n" %lcmodel_dir)
                file.write(" ppmst= %s \n"%ppmst)
                file.write(" ppmend= 0.3\n")
                file.write(" nunfil= %s\n"%nfil)
                file.write(" ltable= 7\n")
                file.write(" lps= 8\n")
                file.write(" lcsv= 11\n")
                file.write(" lcoraw= 10\n")
                file.write(" lcoord= 9\n")
                file.write(" hzpppm= 1.2328e+02\n")
                file.write(" filtab= '%s/table'\n" %lcmodel_dir)
                file.write(" filraw= '%s/met/RAW'\n" %lcmodel_dir)
                file.write(" filps= '%s/ps'\n" %lcmodel_dir)
                file.write(" filh2o= '%s/h2o/RAW'\n" %lcmodel_dir)
                file.write(" filcsv= '%s/spreadsheet.csv'\n" %lcmodel_dir)
                file.write(" filcor= '%s/coraw'\n" %lcmodel_dir)
                file.write(" filcoo= '%s/coord'\n" %lcmodel_dir)
                file.write(" filbas= '/home/raid3/kanaan/.lcmodel/basis-sets/press_te30_3t_01a.basis'\n")
                file.write(" echot= %s.00 \n" %TE)
                file.write(" dows= T \n")
                file.write(" doecc= T\n")
                file.write(" deltat= 8.330e-04\n")
                file.write(" $END\n")
                file.close()

            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
                          Execute quantitation.... run standardA4pdf
            '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

            if os.path.isfile(os.path.join(lcmodel_dir,  'spreadsheet.csv')):
                    print 'Spectrum already processed .................moving on'
            else:
                print '...running standardA4pdf execution-script '
                print ''
                lcmodel_command = ['/bin/sh','/home/raid3/kanaan/.lcmodel/execution-scripts/standardA4pdfv3',
                                   '%s' %lcmodel_dir,'19','%s' %lcmodel_dir, '%s' %lcmodel_dir]

                print subprocess.list2cmdline(lcmodel_command)
                print ''
                subprocess.call(lcmodel_command)

            reader = open(os.path.join(lcmodel_dir, 'table'), 'r')
            for line in reader:
                if 'FWHM' in line:
                    fwhm = float(line[9:14])
                    snrx  = line[29:31]
                    fwhm_hz = fwhm * 123.24
                if 'Data shift' in line:
                    shift = line[15:21]
                if 'Ph:' in line:
                    ph0 = line[6:10]
                    ph1 = line[19:24]

                    filex = open(os.path.join(lcmodel_dir, 'snr.txt'), "w")
                    filex.write('%s, %s, %s, %s, %s, %s' %(fwhm,fwhm_hz, snrx, shift, ph0, ph1))
                    filex.close()


        run_lcmodel_on_voxel(voxel_name = 'ACC', ppmst = 4.00)
        run_lcmodel_on_voxel(voxel_name = 'ACC', ppmst = 3.67)

        run_lcmodel_on_voxel(voxel_name = 'THA', ppmst = 4.00)
        run_lcmodel_on_voxel(voxel_name = 'THA', ppmst = 3.67)

        run_lcmodel_on_voxel(voxel_name = 'STR', ppmst = 4.00)
        run_lcmodel_on_voxel(voxel_name = 'STR', ppmst = 3.67)

if __name__ == "__main__":
    # run_lcmodel(['HM1X'] , workspace_controls_b)
    # run_lcmodel(controls_a , workspace_controls_a)
    # run_lcmodel(controls_b , workspace_controls_b)
    # run_lcmodel(patients_a , workspace_patients_a)
    # run_lcmodel(patients_b , workspace_patients_b)
    run_lcmodel(['NL2P'] , workspace_patients_b)
