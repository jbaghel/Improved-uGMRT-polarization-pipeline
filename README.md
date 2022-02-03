# Improved-uGMRT-polarization-pipeline

Pipeline originally developed by Russ Taylor in 2011 <br />
Modified by Ishwara Chandra in 2018 <br />
This is an improved version of the polarization pipeline by Silpa Sasikumar <br />
Major improvements in flagging and self-calibration <br />
Kindly refer to the paper: Ishwara-Chandra et al 2020  <br />
NOT tested for uGMRT band-2 (150 MHz) <br />
Queries: jbaghel@ncra.tifr.res.in <br />
Initial phase only calibration added by Silpa Sasikumar in 2019-2020 <br />
Polarization steps added by Silpa Sasikumar in 2019-2020, which involve: <br />
 (1) Flagging of polarized and unpolarized calibrators <br />
 (2) Polarization calibration (cross-hand delays; leakage terms; R-L polarization angle) <br />
 (3) Stokes 'Q' and 'U' imaging <br />
 The current version of the pipeline also flags all the four correlations (RR, LL, RL, LR). <br />
 
Pipeline modifications by Janhavi Baghel in 2020-2021, changes made: <br />
 (1)refantmode = 'strict' and only one reference antenna to be specified. <br />
 (2)datacoulmn = 'corrected' in the flagging of target field before splitting <br />
 (3)datacoulmn = 'data' in tclean during creation of dirty image. Split target file has no datacolumn 'corrected'. <br />
 (4)datacoulmn = 'RESIDUAL_DATA' when flagging residuals in self-calibration cycles <br />
 (5)Initial flagging of known bad antenna from observer log. <br />
 (6)Polarization modelling included within the pipeline for 3C286,3C48,3C138 with the pol_*.txt files. <br />

TEST.FITS is the output of gvfits, which coverts GMRT LTA format to multi-source FITS <br />
 
Please CHANGE channels and source fields as per your data. <br />
Also change clip parameters if you have much stronger calibrator and/or target <br />


The parameters below are typical for 550 MHz, 2048 channels at Band-4 (550-750 MHz) <br />
Please change as required for your data. <br />
In BAND-4, recommended channels corresponding to ~ 560 MHz to ~ 810 MHz. The sensitivity drops sharply after 810 MHz. <br />
In any case DO NOT use beyond 820 MHz. <br />
It is highly recommended not to use OQ208 (unpolarized calibrator) to calculate the instrumental leakage for uGMRT since it is a very faint source (~few Jy); therefore a single short scan does not provide sufficient SNR to accurately determine the instrumental polarization. <br />
Also, we do not recommend the use of 3C138 (polarized calibrator) for leakage calibration. <br />
We recommend 3C286 (polarized calibrator) or 3C84 (unpolarized calibrator) for leakage calibration. <br />
