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

####################################################################################################################################

#Initializing steps and conversions ---- Janhavi Baghel
print ("Starting conversion of TEST.FITS to multi.ms")
importgmrt(fitsfile='TEST.FITS', vis='multi.ms')
#
ms='multi.ms'
#
print ("List observations")  #A listobs step necessary to initialize parameters ---- Janhavi Baghel
listobs(vis=ms)
#  
print ("Flagging bad antenna") #Flagging non-workin antenna as given in the observer log ---- Janhavi Baghel
default(flagdata)
flagdata(vis=ms, mode='manual', field ='', spw='', antenna='C03', timerange='', correlation='')
#

#These steps can be put in a separate init.py file and the output of listobs() then read to fill in initializing parameters
####################################################################################################################################

print "Initializing parameters" 

ms='multi.ms'
#
flagspw = ''   # 
gainspw = '0:255~1791 '   # central ~ 75% good channel range for calibration
splitspw = '' # split channel range
specave = 7              # number of channels to average; suggested post-average BW (approx)
                         # 1.5 MHz at band-5; 0.7 MHz at band-4; 0.4 MHz at band-3; 0.1 MHz at band-2
timeave = '0s'           # time averaging
gainspw2 = '0:36~256'   # central good channels after split for self-cal
#
bpassfield     = '3'     # field number of the bandpass calibratorar, add phasecal if strong enough
fluxfield      = '3'     # field number of the primary flux calibrator
secondaryfield = '2'     # field number of the phase calibrator
anofield       = '5'     # field number of another field in your ms file ------ Janhavi Baghel
gaincals       ='0,2,3,4'    # All calibrators
kcorrfield     = '3'     # field number of the antenna-based delay calibrator
target         = '1'     # If more than one target, use target='2,3,4...', 
                         # BUT modify the pipelines to name and split the targets correctly
                         # GO TO LINE 149 and 620 to edit the target field ------ Janhavi Baghel
refant='18'              # use only one option and refantmode 'strict' . 
			 #With uGMRT's antenna configuration, it is better to use one of the outer antennas for reference, 
			 #which provides longer baselines and more stable phase solutions.------ Janhavi Baghel
#
transferfield = '0,2,4,5'
polcalib1 = '3'           # field number of the polarized calibratorar 1
polcalib2 = '4'	   # field number of the polarized calibratorar 2
unpolcalib1  = '0'         # field number of the unpolarized calibratorar 1
#Can add more polarization calibrators to compare and verify the polarization calibration ----- Janhavi Baghel


# Change limits as required
clipfluxcal =[0.0,200.0] # atleast twice the expected flux; only to remove high points
clipphasecal =[0.0,100.0] # atleast twice the expected flux; only to remove high points
clippolcalib2 =[0.0,60.0] # atleast twice the expected flux; only to remove high points
clipunpolcalib1 =[0.0,100.0] # atleast twice the expected flux; only to remove high points
clipanofield = [0.0,150.0] # atleast twice the expected flux; only to remove high points ----- Janhavi Baghel
cliptarget =[0.0,200.0]   # atleast four times the expected flux; only to remove high points
clipresid=[0.0,10.0]     # 10 times the rms for single channel and single baseline
uvracal='>1.0klambda'    # uvrange for gain calibration in main calibration
uvrascal='>0.75klambda'   # uvrange for gain calibration in self calibration
#
# Filenames for initial round of calibration
kcorrfile0 = ms+'.kcal0'
bpassfile0 = ms+'.bcal0'
gainfilep0 =  ms+'.gcalp0'
gainfile0 =  ms+'.gcal0'
fluxfile0 =  ms+'.fluxscale0'
#
# Filenames for final round of calibration
kcorrfile= ms+'.kcal'
bpassfile= ms+'.bcal'
gainfilep =  ms+'.gcalp'
gainfile=  ms+'.gcal'
fluxfile=  ms+'.fluxscale'
#
#Filenames for polarization calibration
#Add as many polarization calibrators you have----- Janhavi Baghel
#For polarized calibrator 1
kcross1 =    ms+'.kcross1'
leakage1 =   ms+'.leakage1'
polang1 =    ms+'.polang1'
#For polarized calibrator 2
kcross2 =    ms+'.kcross2'
leakage2 =   ms+'.leakage2'
polang2 =    ms+'.polang2'
#
#Can also do leakage calibration with unpolarized calibrator----- Janhavi Baghel
unpolleakage1 = ms+'.unpolleakage1'
####################################################################################################################################
#Imaging parameters

pcycles=4              # number of phase-only self-calibration
apcycles=5             # number of amplitude and phase self-calibration
doflag=True            #
solint=16.0            # this transaltes to 8, 4, 2 and 1 min for each selfcal loop
apsolint=16.0          # this transaltes to  8, 4, 2 and 1 min for each selfcal loop
startthreshold=0.1     # start threshold to stop flux (mJy, will reduce by count subsequently)
startniter=2500        # start iterations (will double in each phase-selfcal and 4 times in each A&P loop)
imagesize=[6000,6000]  # should cover alteast up to null at lower part of the band
cellsize='0.8arcsec'   # should be atleast 3 pixels in minor axis
wproj=-1               # w projection, default autocalculate
eachQUV=False	       # Create Stokes Q and U images for each self-cal iteration. ----- Janhavi Baghel
dirtyQUV=True           # Create Stokes Q and U images for dirty image. ----- Janhavi Baghel
createV=False		 # Create Stokes V image ----- Janhavi Baghel
####################################################################################################################################
#For polarization calibration; ----- Janhavi Baghel
#
print "Making polarization calibration models" 
import numpy as np
from scipy.optimize import curve_fit

def refreq_function():
	msmd.open(ms)
        # get reference frequency
	reffreq0 = msmd.reffreq(0)
        # get list of field names in the ms
        fieldnames = msmd.fieldnames()
	msmd.done()
	v = (reffreq0['m0']['value'])
	u = (reffreq0['m0']['unit'])
	w = str(v)+u
	return v,u,w,fieldnames

reffreqfull = refreq_function()
reffreqval = reffreqfull[0]
reffrequnit = reffreqfull[1]
reffreq = reffreqfull[2]
fieldnames = reffreqfull[3]

#For polarization calibration; 
#

print "Making polarization calibration models" 
import numpy as np
from scipy.optimize import curve_fit

def refreq_function():
	msmd.open(ms)
	reffreq0 = msmd.reffreq(0)
	msmd.done()
	v = (reffreq0['m0']['value'])
	u = (reffreq0['m0']['unit'])
	w = str(v)+u
	return v,u,w

reffreqfull = refreq_function()
reffreqval = reffreqfull[0]
reffrequnit = reffreqfull[1]
reffreq = reffreqfull[2]

def pol_model(p): 
	myset=setjy(vis=ms, field = p, spw = '', scalebychan=True)
	i0 = (myset [p]['0']['fluxd'][0]) # Stokes I value from setjy
	name = (myset [p]['fieldName']) #Name of the polarized calibrator
	data = np.loadtxt("pol_"+name+".txt", skiprows=1) # data is stored in corresponding .txt file

	f=data[:,0] #Frequency
	pp=data[:,1] #Percent polarization
	pf = pp/100 #Fraction polarization
	pa=data[:,2] # Polarization angle
	an=data[:,3] # Coefficients for Polynomial Expressions for the Flux Densities (Perley and Butler, 2017)

	#Reference frequency in GHz
	if reffrequnit =="Hz":
		f0=reffreqval /(10**9)
	elif reffrequnit =="MHz":
		f0=reffreqval/(10**3)
	elif reffrequnit =="GHz":
		f0=reffreqval 

	# For polindices c0, c1 are the coefficients in the polynomial expansion of fractional polarization as function of frequency
	def PF(f, c0, c1, c2, c3):
		return c0 + c1*((f-f0)/f0)+ c2*((f-f0)/f0)**2 + c3*((f-f0)/f0)**3

	coeffs1, cov1 = curve_fit(PF,f,pf)
	polindices = (coeffs1)

	# For polangles d0, d1 are the coefficients in the polynomial expansion of polarization angle as function of frequency
	def PA(f, d0, d1, d2, d3):
       	 return d0 + d1*((f-f0)/f0) + d2*((f-f0)/f0)**2 + d3*((f-f0)/f0)**3

	coeffs2, cov2 = curve_fit(PA,f,pa)
	polangles = (coeffs2*pi/180)
	# For alphabeta, alpha is spectral index and beta is curvature
	def F(f, *an):
        	return an[0] + an[1]*np.log10(f) + an[2]*(np.log10(f))**2 + an[3]*(np.log10(f))**3

	S=10**(F(f,*an))
		
	def fr(i):
    		return 0.00128/(2**i)

	f3 = (f0-fr(np.arange(0,50))).tolist()+[f0]+(f0+fr(np.arange(0,50))).tolist()
	S3 = 10**(F(f3,*an))
	def Sa(f,Sa,alpha,beta):
       	 return Sa*(f/f0)**(alpha+beta*np.log10(f/f0))

	popt, pcov = curve_fit(Sa, f3, S3)
	alphabeta= (popt)
	
	return i0,name,polindices,polangles,alphabeta
#
#For polarized calibrator 1
polmodel_1 = pol_model(polcalib)
i0_1 = polmodel[0]
polindices_1 = polmodel[2]
polangles_1 = polmodel[3]
alphabeta_1 =polmodel[4][1:3]

#For polarized calibrator 2
polmodel2 = pol_model(polcalib2)
i0_2 = polmodel2[0]
polindices_2 = polmodel2[2]
polangles_2 = polmodel2[3]
alphabeta_2 = polmodel2[4][1:3]

###################################################################################################################################
print ("Measurement set contains :")
print ("Target : " + fieldnames[int(target)]) # If more than one target, use target1='1', target2 ='6', ... 
# target1 = '1'
# target2 = '6'
#print ("Target : " + fieldnames[int(target1)] + ', ' + fieldnames[int(target2)])
print ("\n")
print ("Reference frequency : " + reffreq)
print ("\n")

print ("Polarization Calibrator 1:" + fieldnames[int(polcalib1)])
print ("i0_1", i0_1)
print ("polindices_1", polindices_1)
print ("polangles_1", polangles_1)
print ("alphabeta_1", alphabeta_1)

print ("Polarization Calibrator 2:" + fieldnames[int(polcalib2)])
print ("i0_2", i0_2)
print ("polindices_2", polindices_2)
print ("polangles_2", polangles_2)
print ("alphabeta_2", alphabeta_2)

print ("Polarization Calibrator 3 (unpolarized): " + fieldnames[int(unpolcalib1)])

####################################################################################################################################
print "First Round of Flagging" 

default(flagdata)
#Flag using 'clip' option to remove high points for calibrators
print "Flagging Step 1/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=fluxfield, clipminmax=clipfluxcal,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 2/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=secondaryfield, clipminmax=clipphasecal,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 3/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=anofield, clipminmax=clipanofield,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 4/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=polcalib2, clipminmax=clippolcalib2,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 5/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=unpolcalib1, clipminmax=clipunpolcalib1,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for calibrator tight flagging
print "Flagging Step 6/11" 
flagdata(vis=ms,mode="tfcrop", datacolumn="DATA", field=gaincals, ntime="scan",
        timecutoff=3.0, freqcutoff=3.0, timefit="line",freqfit="line",flagdimension="freqtime", 
        extendflags=False, timedevscale=4.0,freqdevscale=4.0, extendpols=False,growaround=False,
        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
print "Flagging Step 7/11" 
flagdata(vis=ms,mode="extend",spw=flagspw,field=gaincals,datacolumn="DATA",clipzeros=True,
         ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
         flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag for target - moderate flagging, more flagging in self-cal cycles
#Flag using 'clip' option to remove high points for target
print "Flagging Step 8/11" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=target, clipminmax=cliptarget,
        datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for target
print "Flagging Step 9/11" 
flagdata(vis=ms,mode="tfcrop", datacolumn="DATA", field=target, ntime="scan",
        timecutoff=4.0, freqcutoff=4.0, timefit="poly",freqfit="poly",flagdimension="freqtime", 
        extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
print "Flagging Step 10/11" 
flagdata(vis=ms,mode="extend",spw=flagspw,field=target,datacolumn="DATA",clipzeros=True,
         ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
         flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now summary
print "Flagging Step 11/11" 
flagdata(vis=ms,mode="summary",datacolumn="DATA", extendflags=True, 
         name=vis+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)

#####################################################################################################################################

print "Calibrating measurement set %s" % ms

print "stating initial flux density scaling"
setjy(vis=ms, field = fluxfield, spw = flagspw, scalebychan=True)

# Phase only calibration added - suggested and tested by Silpa Sasikumar
#
print " starting initial phase only gaincal -> %s" % gainfilep0
gaincal(vis=ms,caltable=gainfilep0,field=gaincals,spw=gainspw,intent="",
         selectdata=True,timerange="",uvrange="",antenna="",scan="",
         observation="",msselect="",solint="int",combine="",preavg=-1.0,
         refant=refant,refantmode="strict",minblperant=5,minsnr=1.0,solnorm=False,
         gaintype="G",smodel=[],calmode="p",append=False,splinetime=3600.0,
         npointaver=3,phasewrap=180.0,docallib=False,callib="",gaintable=[''],
         gainfield=[''],interp=[],spwmap=[],parang=True)


print " starting initial gaincal -> %s" % gainfile0
gaincal(vis=ms, caltable = kcorrfile0, field = kcorrfield, spw = flagspw, 
        refant = refant,  minblperant = 6, solnorm = True,  gaintype = 'K', 
        gaintable =[gainfilep0], gainfield=gaincals, solint = '10min', combine = 'scan', minsnr=1.0,
        parang = True, append = False)
  
print " starting bandpass -> %s" % bpassfile0
bandpass(vis=ms, caltable = bpassfile0, field = bpassfield, spw = flagspw, minsnr=1.0,
         refant = refant, minblperant = 6, solnorm = True,  solint = 'inf', 
         bandtype = 'B', fillgaps = 8, gaintable = [gainfilep0, kcorrfile0], gainfield=[gaincals,kcorrfield], 
         parang = True, append = False)
print " starting gaincal -> %s" % gainfile0
gaincal(vis=ms, caltable = gainfile0, field = gaincals, spw = gainspw, 
        refant = refant, solint = '1.0min', minblperant = 5, solnorm = False,  
        gaintype = 'G', combine = '', calmode = 'ap', minsnr=1.0, uvrange=uvracal,
        gaintable = [kcorrfile0,bpassfile0], gainfield = [kcorrfield,bpassfield],
        append = False, parang = True)

print " starting fluxscale -> %s" % fluxfile0 
fluxscale(vis=ms, caltable = gainfile0, reference = [fluxfield], 
          transfer = [transferfield], fluxtable = fluxfile0, 
          listfile = ms+'.fluxscale.txt0',
          append = False)               
          
#####################################################################################################################################

print " Applying Calibrations:"

print " applying calibrations: primary calibrator"
applycal(vis=ms, field = fluxfield, spw = flagspw, selectdata=False, calwt = False,
    gaintable = [kcorrfile0,bpassfile0, fluxfile0],
    gainfield = [kcorrfield,bpassfield,fluxfield],
    parang = True)

print " applying calibrations: secondary calibrators"
applycal(vis=ms, field = secondaryfield, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile0, bpassfile0, fluxfile0],
    gainfield = [kcorrfield, bpassfield,secondaryfield],
    parang= True)

print " applying calibrations: polarized calibrator 2"
applycal(vis=ms, field = polcalib, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile0, bpassfile0, fluxfile0],
    gainfield = [kcorrfield, bpassfield,polcalib2],
    parang= True)

print " applying calibrations: unpolarized calibrator 1"
applycal(vis=ms, field = unpolcalib, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile0, bpassfile0, fluxfile0],
    gainfield = [kcorrfield, bpassfield,unpolcalib1],
    parang= True)

print " applying calibrations: another field" 
applycal(vis=ms, field = anofield, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile0, bpassfile0, fluxfile0],
    gainfield = [kcorrfield, bpassfield, anofield],
    parang= True)

print " applying calibrations: target fields"
applycal(vis=ms, field = target, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile0, bpassfile0, fluxfile0],
    gainfield = [kcorrfield, bpassfield,secondaryfield],
    parang= True)

####################################################################################################################################

# Change clipmax as required

print "Second Round of Flagging" 

default(flagdata)
#Flag using 'clip' option to remove high points for calibrators
print "Flagging Step 1/12" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=fluxfield, clipminmax=clipfluxcal,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 2/12" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=secondaryfield, clipminmax=clipphasecal,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 3/12" #Flagging the pulsar 
flagdata(vis=ms,mode="clip", spw=flagspw,field=anofield, clipminmax=clipanofield,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 4/12" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=polcalib, clipminmax=clippolcalib,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
print "Flagging Step 5/12" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=unpolcalib, clipminmax=clipunpolcalib,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for calibrator tight flagging
print "Flagging Step 6/12" 
flagdata(vis=ms,mode="tfcrop", datacolumn="corrected", field=gaincals, ntime="scan",
        timecutoff=3.0, freqcutoff=3.0, timefit="line",freqfit="line",flagdimension="freqtime", 
        extendflags=False, timedevscale=4.0,freqdevscale=4.0, extendpols=False,growaround=False,
        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag using 'rflag' option for calibrator tight flagging
print "Flagging Step 7/12" 
flagdata(vis=ms,mode="rflag",datacolumn="corrected",field=gaincals, timecutoff=3.0, 
        freqcutoff=3.0,timefit="poly",freqfit="line",flagdimension="freqtime", extendflags=False,
        timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (70% more means full flag, change if required)
print "Flagging Step 8/12" 
flagdata(vis=ms,mode="extend",spw=flagspw,field=gaincals,datacolumn="corrected",clipzeros=True,
         ntime="scan", extendflags=False, extendpols=False,growtime=90.0, growfreq=90.0,growaround=False,
         flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag for target - moderate flagging, more flagging in self-cal cycles
#Flag using 'clip' option to remove high points for target
print "Flagging Step 9/12" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=target, clipminmax=cliptarget,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for target
print "Flagging Step 10/12" 
flagdata(vis=ms,mode="tfcrop", datacolumn="corrected", field=target, ntime="scan",
        timecutoff=4.0, freqcutoff=4.0, timefit="poly",freqfit="line",flagdimension="freqtime", 
        extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
        action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag using 'rflag' option for target
print "Flagging Step 11/12" 
flagdata(vis=ms,mode="rflag",datacolumn="corrected",field=target, timecutoff=4.0, 
        freqcutoff=4.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
        timedevscale=5.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now summary
print "Flagging Step 12/12" 
flagdata(vis=ms,mode="summary",datacolumn="corrected", extendflags=True, 
         name=vis+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)
#
####################################################################################################################################
#
print " Deleting existing model column"
clearcal(ms)

####################################################################################################################################
#
print "Calibrating measurement set %s" % ms

print " starting initial flux density scaling"
setjy(vis=ms, field = fluxfield, spw = flagspw, scalebychan=True)

print " starting initial phase only gaincal -> %s" % gainfilep
gaincal(vis=ms,caltable=gainfilep,field=gaincals,spw=gainspw,intent="",
         selectdata=True,timerange="",uvrange="",antenna="",scan="",
         observation="",msselect="",solint="int",combine="",preavg=-1.0,
         refant=refant,refantmode="strict",minblperant=5,minsnr=1.0,solnorm=False,
         gaintype="G",smodel=[],calmode="p",append=False,splinetime=3600.0,
         npointaver=3,phasewrap=180.0,docallib=False,callib="",gaintable=[''],
         gainfield=[''],interp=[],spwmap=[],parang=True)

print " starting initial gaincal -> %s" % kcorrfile
gaincal(vis=ms, caltable = kcorrfile, field = kcorrfield, spw = flagspw, 
        refant = refant,  minblperant = 6, solnorm = True,  gaintype = 'K', 
        gaintable =[gainfilep], gainfield=gaincals, solint = '10min', combine = 'scan', minsnr=1.0,
        parang = True, append = False)
  
print " starting bandpass -> %s" % bpassfile
bandpass(vis=ms, caltable = bpassfile, field = bpassfield, spw = flagspw, minsnr=1.0,
         refant = refant, minblperant = 6, solnorm = True,  solint = 'inf', 
         bandtype = 'B', fillgaps = 8, gaintable = [gainfilep, kcorrfile], gainfield=[gaincals, kcorrfield], 
         parang = True, append = False)
     
print " starting gaincal -> %s" % gainfile
gaincal(vis=ms, caltable = gainfile, field = gaincals, spw = gainspw, 
        refant = refant, solint = '1.0min', minblperant = 5, solnorm = False,  
        gaintype = 'G', combine = '', calmode = 'ap', minsnr=1.0, uvrange=uvracal,
        gaintable = [kcorrfile,bpassfile], gainfield = [kcorrfield,bpassfield],
        append = False, parang = True)
print " starting fluxscale -> %s" % fluxfile
fluxscale(vis=ms, caltable = gainfile, reference = [fluxfield], 
          transfer = [transferfield], fluxtable = fluxfile, 
          listfile = ms+'.fluxscale.txt2',
          append = False)               
####################################################################################################################################
print " starting Polarization calibration -> "
#
print " setting the polarization calibrator models"
setjy(vis=ms, field = polcalib1, spw = flagspw, scalebychan=True, standard='manual', 
      fluxdensity=[i0_1,0,0,0], spix=alphabeta_1, reffreq=reffreq, polindex=polindices_1, polangle=polangles_1)
setjy(vis=ms, field = polcalib2, spw = flagspw, scalebychan=True, standard='manual', 
      fluxdensity=[i0_2,0,0,0], spix=alphabeta_2, reffreq=reffreq, polindex=polindices_2, polangle=polangles_2)


print " starting cross-hand delay calibration -> %s" % kcross1
gaincal(vis=ms, caltable = kcross1, field = polcalib1, spw = flagspw, 
        refant = refant, solint = 'inf', gaintype = 'KCROSS', combine = 'scan',
        gaintable = [kcorrfile, bpassfile, gainfile], gainfield = [kcorrfield,bpassfield,polcalib1],
        parang = True) 
print " starting cross-hand delay calibration -> %s" % kcross2
gaincal(vis=ms, caltable = kcross2, field = polcalib2, spw = flagspw, 
        refant = refant, solint = 'inf', gaintype = 'KCROSS', combine = 'scan',
        gaintable = [kcorrfile, bpassfile, gainfile], gainfield = [kcorrfield,bpassfield,polcalib2],
        parang = True) 
####################################################################################################################################
#Analyse the various tables and choose the correct ones to apply

kcross = kcross1 #or kcross2
kcrosscalib = polcalib1 #or polcalib2
####################################################################################################################################

print " starting leakage calibration -> %s" % leakage1
polcal(vis=ms, caltable = leakage1, field = polcalib1, spw = flagspw, 
       refant = refant, solint = 'inf', poltype = 'Df+QU', combine = 'scan',
       gaintable = [kcorrfile, bpassfile, gainfile, kcross], gainfield = [kcorrfield, bpassfield, polcalib1, kcrosscalib])
print " starting leakage calibration -> %s" % leakage2
polcal(vis=ms, caltable = leakage2, field = polcalib2, spw = flagspw, 
       refant = refant, solint = 'inf', poltype = 'Df+QU', combine = 'scan',
       gaintable = [kcorrfile, bpassfile, gainfile, kcross], gainfield = [kcorrfield, bpassfield, polcalib2, kcrosscalib])

print " starting leakage calibration :unpolarized -> %s" % unpolleakage1
polcal(vis=ms, caltable = unpolleakage1, field = unpolcalib1, spw = flagspw, refant = refant, solint = 'inf', poltype = 'Df', combine = 'scan', gaintable = [kcorrfile, bpassfile, gainfile, kcross], gainfield = [kcorrfield,bpassfield,unpolcalib1,kcrosscalib])

####################################################################################################################################

leakage = leakage1 #or leakage2 or unpolleakage1
leakagecalib = polcalib1 #or polcalib2 or unpolcalib1

####################################################################################################################################

print " starting polarization angle calibration -> %s" % polang1
polcal(vis=ms, caltable = polang1, field = polcalib1, refant = refant, solint = 'inf', poltype = 'Xf',combine = 'scan', gaintable = [kcorrfile, bpassfile, gainfile, kcross, leakage], 
        gainfield = [kcorrfield,bpassfield,polcalib1,kcrosscalib,leakagecalib])
print " starting polarization angle calibration -> %s" % polang2
polcal(vis=ms, caltable = polang2, field = polcalib2, refant = refant, solint = 'inf', poltype = 'Xf',combine = 'scan', gaintable = [kcorrfile, bpassfile, gainfile, kcross, leakage], 
        gainfield = [kcorrfield,bpassfield,polcalib2,kcrosscalib,leakagecalib])

####################################################################################################################################
polang = polang1 #or polang2
polangcalib = polcalib1 #or polcalib2
####################################################################################################################################

#
print  " Applying Calibrations:" 

print " applying calibrations: primary calibrator"
applycal(vis=ms, field = fluxfield, spw = flagspw, selectdata=False, calwt = False,
    gaintable = [kcorrfile,bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield,bpassfield,fluxfield, kcrosscalib, leakagecalib, polangcalib],
    parang = True)

print " applying calibrations: secondary calibrators"
applycal(vis=ms, field = secondaryfield, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile, bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield, bpassfield,secondaryfield, kcrosscalib, leakagecalib, polangcalib],
    parang= True)

print " applying calibrations: polarized calibrator"
applycal(vis=ms, field = polcalib2, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile, bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield, bpassfield,polcalib2, kcrosscalib, leakagecalib, polangcalib],
    parang= True)

print " applying calibrations: unpolarized calibrator"
applycal(vis=ms, field = unpolcalib1, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile, bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield, bpassfield,unpolcalib1, kcrosscalib, leakagecalib, polangcalib],
    parang= True)

print " applying calibrations: target fields"
applycal(vis=ms, field = target, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile, bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield, bpassfield,secondaryfield, kcrosscalib, leakagecalib, polangcalib],
    parang= True)
    
print " applying calibrations: Another field"
applycal(vis=ms, field = anofield, spw = flagspw, selectdata = False, calwt = False,
    gaintable = [kcorrfile, bpassfile, fluxfile, kcross, leakage, polang],
    gainfield = [kcorrfield, bpassfield,anofield, kcrosscalib, leakagecalib, polangcalib],
    parang= True)

####################################################################################################################################

print "Flagging Target"
# Now flag for target - moderate flagging
print "Flagging Step 1/3" 
flagdata(vis=ms,mode="clip", spw=flagspw,field=target, clipminmax=cliptarget,
        datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# now flag using 'rflag' option 
print "Flagging Step 2/3"
flagdata(vis=ms,mode="rflag",datacolumn="corrected",field=target, timecutoff=4.0, 
        freqcutoff=4.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
        timedevscale=5.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
print "Flagging Step 3/3"
# Now summary
flagdata(vis=ms,mode="summary",datacolumn="corrected", extendflags=True, 
         name=vis+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)

####################################################################################################################################

print "Splitting target field"
split(vis=ms, outputvis = fieldnames[int(target)]+'.ms', datacolumn='corrected', 
          field = target, spw = splitspw, keepflags=False, width = specave)
#
# For more targets, add with target1, target2, ... 
#split(vis=ms, outputvis = fieldnames[int(target1)]+'.ms', datacolumn='corrected', 
#          field = target1, spw = splitspw, keepflags=False, width = specave)
#split(vis=ms, outputvis = fieldnames[int(target2)]+'.ms', datacolumn='corrected', 
#          field = target2, spw = splitspw, keepflags=False, width = specave)

####################################################################################################################################

print "\n Cleaning up. Starting imaging..."  

ms=fieldnames[int(target)]+'.ms'

def QUVimg():
	print "Creating Stokes Q image"

	tclean(vis=ms,selectdata=True,field="",spw="",timerange="",uvrange="", antenna="",scan="",observation="",intent="", datacolumn= dc , imagename=ms+'.'+scmode+str(count-1)+'_Q',imsize=imagesize,cell=cellsize,phasecenter="",
       stokes="Q",projection="SIN",startmodel="",specmode="mfs",reffreq="",
       nchan=-1,start="",width="",outframe="LSRK",veltype="radio",
       restfreq=[],interpolation="linear",perchanweightdensity=False,gridder="widefield",facets=1,
       psfphasecenter="",wprojplanes=wproj,vptable="",usepointing=False,
       mosweight=True,aterm=True,psterm=False,wbawp=True,conjbeams=False,
       cfcache="",computepastep=360.0,rotatepastep=360.0,pblimit=-1,normtype="flatnoise",
       deconvolver="mtmfs",scales=[],nterms=2,smallscalebias=0.6,restoration=True,
       restoringbeam=[],pbcor=False,outlierfile="",weighting="briggs",robust=0.0,
       noise="1.0Jy",npixels=0,uvtaper=[],niter=160000,gain=0.1,
       threshold="0.01mJy",nsigma=0.0,cycleniter=-1,cyclefactor=1.3,minpsffraction=0.05,
       maxpsffraction=0.8,interactive=False,usemask="auto-multithresh",mask="",pbmask=0.0,
       sidelobethreshold=2.0,noisethreshold=5.0,lownoisethreshold=1.5,negativethreshold=0.0,smoothfactor=1.0,
       minbeamfrac=0.3,cutthreshold=0.01,growiterations=75,dogrowprune=True,minpercentchange=-1.0,
       verbose=False,fastnoise=True,restart=True,savemodel="none",calcres=True,
       calcpsf=True,parallel=False)

	exportfits(imagename=ms+'.'+scmode+str(count-1)+'_Q'+'.image.tt0', fitsimage=ms+'.'+scmode+str(count-1)+'_Q'+'.fits', velocity=False,optical=False,bitpix=-32, minpix=0, maxpix=-1, overwrite=False, dropstokes=False, stokeslast=True, history=True, dropdeg=False)

	print "Creating Stokes U image"

	tclean(vis=ms,selectdata=True,field="",spw="",timerange="", uvrange="",antenna="",scan="",observation="",intent="",  datacolumn= dc , imagename=ms+'.'+scmode+str(count-1)+'_U',imsize=imagesize,cell=cellsize,phasecenter="",
       stokes="U",projection="SIN",startmodel="",specmode="mfs",reffreq="",
       nchan=-1,start="",width="",outframe="LSRK",veltype="radio",
       restfreq=[],interpolation="linear",perchanweightdensity=False,gridder="widefield",facets=1,
       psfphasecenter="",wprojplanes=wproj,vptable="",usepointing=False,
       mosweight=True,aterm=True,psterm=False,wbawp=True,conjbeams=False,
       cfcache="",computepastep=360.0,rotatepastep=360.0,pblimit=-1,normtype="flatnoise",
       deconvolver="mtmfs",scales=[],nterms=2,smallscalebias=0.6,restoration=True,
       restoringbeam=[],pbcor=False,outlierfile="",weighting="briggs",robust=0.0,
       noise="1.0Jy",npixels=0,uvtaper=[],niter=160000,gain=0.1,
       threshold="0.01mJy",nsigma=0.0,cycleniter=-1,cyclefactor=1.3,minpsffraction=0.05,
       maxpsffraction=0.8,interactive=False,usemask="auto-multithresh",mask="",pbmask=0.0,
       sidelobethreshold=2.0,noisethreshold=5.0,lownoisethreshold=1.5,negativethreshold=0.0,smoothfactor=1.0,
       minbeamfrac=0.3,cutthreshold=0.01,growiterations=75,dogrowprune=True,minpercentchange=-1.0,
       verbose=False,fastnoise=True,restart=True,savemodel="none",calcres=True,
       calcpsf=True,parallel=False)

	exportfits(imagename=ms+'.'+scmode+str(count-1)+'_U'+'.image.tt0' , fitsimage=ms+'.'+scmode+str(count-1)+'_U'+'.fits', velocity=False, optical=False, bitpix=-32, minpix=0, maxpix=-1, overwrite=False, dropstokes=False, stokeslast=True, history=True, dropdeg=False)
	
	if createV == True:
		print "Creating Stokes V image"

		tclean(vis=ms,selectdata=True,field="",spw="",timerange="",
		       uvrange="",antenna="",scan="",observation="",intent="",datacolumn="corrected",imagename=ms+'.'+scmode+str(count-1)+'_V',imsize=imagesize,cell=cellsize,phasecenter="",
		       stokes="V",projection="SIN",startmodel="",specmode="mfs",reffreq="",
		       nchan=-1,start="",width="",outframe="LSRK",veltype="radio",
		       restfreq=[],interpolation="linear",perchanweightdensity=False,gridder="widefield",facets=1,
		       psfphasecenter="",wprojplanes=wproj,vptable="",usepointing=False,
		       mosweight=True,aterm=True,psterm=False,wbawp=True,conjbeams=False,
		       cfcache="",computepastep=360.0,rotatepastep=360.0,pblimit=-1,normtype="flatnoise",
		       deconvolver="mtmfs",scales=[],nterms=2,smallscalebias=0.6,restoration=True,
		       restoringbeam=[],pbcor=False,outlierfile="",weighting="briggs",robust=0.0,
		       noise="1.0Jy",npixels=0,uvtaper=[],niter=160000,gain=0.1,
		       threshold="0.01mJy",nsigma=0.0,cycleniter=-1,cyclefactor=1.3,minpsffraction=0.05,
		      maxpsffraction=0.8,interactive=False,usemask="auto-multithresh",mask="",pbmask=0.0,
		       sidelobethreshold=2.0,noisethreshold=5.0,lownoisethreshold=1.5,negativethreshold=0.0,smoothfactor=1.0,
		       minbeamfrac=0.3,cutthreshold=0.01,growiterations=75,dogrowprune=True,minpercentchange=-1.0,
 		      verbose=False,fastnoise=True,restart=True,savemodel="none",calcres=True,
 		      calcpsf=True,parallel=False)

		exportfits(imagename=ms+'.'+scmode+str(count-1)+'_V'+'.image.tt0' , fitsimage=ms+'.'+scmode+str(count-1)+'_V'+'.fits',velocity=False,optical=False,bitpix=-32,
		           minpix=0,maxpix=-1,overwrite=False,dropstokes=False,stokeslast=True,
 		          history=True,dropdeg=False)	
	
print "\n Cleaning up. Starting imaging..."
#start self-calibration cycles    
count=1
scmode='p'
#

print "Prepaing dirty image"
tclean(vis=ms, imagename=ms+'.'+scmode+str(count-1),imsize=imagesize,cell=cellsize, selectdata=True, datacolumn="data", 
       phasecenter="",stokes="I",projection="SIN", specmode="mfs",nchan=-1,gridder="widefield",wprojplanes=wproj,
       aterm=True,pblimit=-1, deconvolver="mtmfs",nterms=2,smallscalebias=0.6,restoration=True,pbcor=False,
       weighting="briggs",robust=0.0,uvtaper=[],niter=int(0.5*startniter*2**count),gain=0.1,
       threshold=str(startthreshold/(count))+'mJy',cyclefactor=1.3,
       minpsffraction=0.05,maxpsffraction=0.8,usemask="auto-multithresh",pbmask=0.0,sidelobethreshold=2.0,
       growiterations=75,restart=True,savemodel="modelcolumn",calcres=True,calcpsf=True,parallel=False)

exportfits(imagename=ms+'.'+scmode+str(count-1)+'.image.tt0', fitsimage=ms+'.'+scmode+str(count-1)+'.fits')

print "Made : " +scmode+str(count-1)

if  dirtyQUV == True or eachQUV == True:
	dc="data"
	QUVimg()

#start self-calibration cycles  
print "Starting self-calibration, going to phase only calibration Cycle"
casalog.post("Staring self-calibration, going to phase only calibration Cycle")

for j in range(pcycles):  
  scmode='p'
  if(doflag==True and count>=1):
     print "Began flagging :"+scmode+str(count)
     flagdata(vis=ms,mode="clip", spw="",field='', clipminmax=clipresid,
              datacolumn="RESIDUAL_DATA",clipoutside=True, clipzeros=True, extendpols=False, 
              action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
     flagdata(vis=ms,mode="rflag",datacolumn="RESIDUAL_DATA",field='', timecutoff=5.0, 
              freqcutoff=5.0,timefit="line",freqfit="line",flagdimension="freqtime", extendflags=False,
              timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
              flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
     flagdata(vis=ms,mode="summary",datacolumn="RESIDUAL_DATA", extendflags=False, 
              name=ms+'temp.summary', action="apply", flagbackup=True,overwrite=True, writeflags=True)
#
  print "Began doing self-cal on :"+scmode+str(count)
  gaincal(vis=ms,caltable=ms+'.'+scmode+str(count),selectdata=False,solint=str(solint/2**count)+'min',refant=refant,refantmode="strict",
        minblperant=6, spw=gainspw2,minsnr=1.0,solnorm=True,gaintype="G",calmode=scmode,append=False, uvrange=uvrascal, parang=False)
# 
  print "Began processing :"+scmode+str(count)
  applycal(vis=ms, selectdata=False,gaintable=ms+'.'+scmode+str(count), parang=False,calwt=False,applymode="calflag",flagbackup=True)  
#
  tclean(vis=ms, imagename=ms+'.'+scmode+str(count),imsize=imagesize,cell=cellsize, selectdata=True, datacolumn="corrected", 
       phasecenter="",stokes="I",projection="SIN", specmode="mfs",nchan=-1,gridder="widefield",wprojplanes=wproj,
       aterm=True,pblimit=-1, deconvolver="mtmfs",nterms=2,smallscalebias=0.6,restoration=True,pbcor=False,
       weighting="briggs",robust=0.0,uvtaper=[],niter=int(startniter*2**count),gain=0.1,
       threshold=str(startthreshold/(count))+'mJy',cyclefactor=1.3,
       minpsffraction=0.05,maxpsffraction=0.8,usemask="auto-multithresh",pbmask=0.0,sidelobethreshold=2.0,
       growiterations=75,restart=True,savemodel="modelcolumn",calcres=True,calcpsf=True,parallel=False)
  exportfits(imagename=ms+'.'+scmode+str(count)+'.image.tt0', fitsimage=ms+'.'+scmode+str(count)+'.fits')
  print "Made : " +scmode+str(count)
  if eachQUV == True:
	dc="corrected"
  	QUVimg()
  count = count + 1
#
print "Completed phase only self-calibration, going to A&P calibration Cycle"
casalog.post("Completed phase only self-calibration, going to A&P calibration Cycle")
#
count=1
for j in range(apcycles):  
  scmode = 'ap'
  if count>= 4:
   sfactor=4
  else:
   sfactor=count
#
  if(doflag==True):
     print "Began flagging :"+scmode+str(count)
     flagdata(vis=ms,mode="clip", spw="",field='', clipminmax=clipresid,
              datacolumn="RESIDUAL_DATA",clipoutside=True, clipzeros=True, extendpols=False, 
              action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
     flagdata(vis=ms,mode="rflag",datacolumn="RESIDUAL_DATA",field='', timecutoff=5.0, 
              freqcutoff=5.0,timefit="line",freqfit="line",flagdimension="freqtime", extendflags=False,
              timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
              flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
     flagdata(vis=ms,mode="summary",datacolumn="RESIDUAL_DATA", extendflags=False, 
              name=ms+'temp.summary', action="apply", flagbackup=True,overwrite=True, writeflags=True)
#
  print "Began doing self-cal on :"+scmode+str(count)
  gaincal(vis=ms,caltable=ms+'.'+scmode+str(count),selectdata=False,solint=str(apsolint/2**sfactor)+'min',refant=refant,
        refantmode="strict",spw=gainspw2,minblperant=6, minsnr=1.0,solnorm=True,gaintype="G",calmode=scmode,append=False, parang=False)
#
  applycal(vis=ms, selectdata=False,gaintable=ms+'.'+scmode+str(count), parang=False,calwt=False,applymode="calflag",flagbackup=True)  
#
  print "Began processing :"+scmode+str(count)
  tclean(vis=ms, imagename=ms+'.'+scmode+str(count),imsize=imagesize,cell=cellsize, selectdata=True, datacolumn="corrected", 
       phasecenter="",stokes="I",projection="SIN", specmode="mfs",nchan=-1,gridder="widefield",wprojplanes=wproj,
       aterm=True,pblimit=-1, deconvolver="mtmfs",nterms=2,smallscalebias=0.6,restoration=True,pbcor=False,
       weighting="briggs",robust=0.0,uvtaper=[],niter=int(startniter*2*2**count),gain=0.1,
       threshold=str(startthreshold/(2*count))+'mJy',cyclefactor=1.3,
       minpsffraction=0.05,maxpsffraction=0.8,usemask="auto-multithresh",pbmask=0.0,sidelobethreshold=2.0,
       growiterations=75,restart=True,savemodel="modelcolumn",calcres=True,calcpsf=True,parallel=False)
  exportfits(imagename=ms+'.'+scmode+str(count)+'.image.tt0', fitsimage=ms+'.'+scmode+str(count)+'.fits')
  print "Made : " +scmode+str(count)
  if eachQUV == True:
	dc="corrected"
  	QUVimg()
  count = count + 1
#
print "Completed processing AP self-calibrations\n"
casalog.post("Completed processing A&P self-calibrations")

####################################################################################################################################
if eachQUV == False:
	dc="corrected"
	QUVimg()
####################################################################################################################################

print "Done"

