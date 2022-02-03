# Improved-uGMRT-polarization-pipeline

# Pipeline originally developed by Russ Taylor in 2011
# Modified by Ishwara Chandra in 2018 
# This is an improved version of the polarization pipeline by Silpa Sasikumar
# Major improvements in flagging and self-calibration 
# Kindly refer to the paper: Ishwara-Chandra et al 2020  
# NOT tested for uGMRT band-2 (150 MHz) 
# Queries: jbaghel@ncra.tifr.res.in
# Initial phase only calibration added by Silpa Sasikumar in 2019-2020
# Polarization steps added by Silpa Sasikumar in 2019-2020, which involve:
# (1) Flagging of polarized and unpolarized calibrators
# (2) Polarization calibration (cross-hand delays; leakage terms; R-L polarization angle)
# (3) Stokes 'Q' and 'U' imaging
# The current version of the pipeline also flags all the four correlations (RR, LL, RL, LR). 
# 
# Pipeline modifications by Janhavi Baghel in 2020-2021, changes made:
# (1)refantmode = 'strict' and only one reference antenna to be specified.
# (2)datacoulmn = 'corrected' in the flagging of target field before splitting
# (3)datacoulmn = 'data' in tclean during creation of dirty image. Split target file has no datacolumn 'corrected'.
# (4)datacoulmn = 'RESIDUAL_DATA' when flagging residuals in self-calibration cycles
# (5)Initial flagging of known bad antenna from observer log.
# (6)Polarization modelling included within the pipeline for 3C286,3C48,3C138 with the pol_*.txt files.
# TEST.FITS is the output of gvfits, which coverts GMRT LTA format to multi-source FITS
# 
# Please CHANGE channels and source fields as per your data.
# Also change clip parameters if you have much stronger calibrator and/or target
#
#
# The parameters below are typical for 550 MHz, 2048 channels at Band-4 (550-750 MHz)
# Please change as required for your data.
# In BAND-4, recommended channels corresponding to ~ 560 MHz to ~ 810 MHz. The sensitivity drops sharply after 810 MHz.
# In any case DO NOT use beyond 820 MHz.
# It is highly recommended not to use OQ208 (unpolarized calibrator) to calculate the instrumental leakage for uGMRT since it is a very faint source (~few Jy); therefore a single short scan does not provide sufficient SNR to accurately determine the instrumental polarization.
# Also, we do not recommend the use of 3C138 (polarized calibrator) for leakage calibration.
# We recommend 3C286 (polarized calibrator) or 3C84 (unpolarized calibrator) for leakage calibration.

