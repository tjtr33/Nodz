#!/usr/bin/env python
# copy this to #PATH w/o .py extant

# 10oct chg name advance to GvHi   retract to GvLo
# 10oct idea: keep a; gap counting in here also, even add input for AtDest to allow SparkOut evaluation, while Arced out is just contiguous GvLo's, rqrs AdvLim LoGvLim inputs
# 10 oct exercising testing ArcOut so need to bias window for more GvLo signals   just chg the window thresholds 2& 4  to 3&5  or 4&6
# 10 oct added pins GvLoThreshold and GvHiThreshold to ease such chgs for testing , and a new Mcode M196
# 10oct DAMN the P & Q are ALWAYS floats ( descibed as 'numbers' in docs)
# 10 oct look for ways to have random 0 to 100
# easy   import random
# random.uniform(0.0, 100.)  

# a comp that generates GvHi and GvLo signals randomly, uniquely
# the random number is an int from 0 to 9

# i made this executable and put in in linuxcnc-dev/bin  WITHOUT .py EXTANT   i dont like that location, its not where other compms are but good for testing
import hal, time
#import random
#from random import randrange
from random import uniform

#    a fake edm gap value from 0 to 9 
#    is generated periodicly and is compared to 2 thresholds
#    like a typical edm window comparator
#    the 2 outputs GvHi and GvLo are set according to the comparison

rgv = hal.component("randomGV")
rgv.newpin("GvHi", hal.HAL_BIT, hal.HAL_OUT)
rgv.newpin("GvLo", hal.HAL_BIT, hal.HAL_OUT)
# 10oct new mcode will set these pins M196 P GvHiThreshold(1-9) Q GvLoThreshold (1-9)
# DAMN the pin has to be as screwed up as the rule that says P is ALWAYS a float   so all code everywhere has to convert to get an INT form P or Q
# 10 oct Buggerit  use random.uniform(lowfloat, highfloat)
rgv.newpin("GvHiThreshold", hal.HAL_FLOAT, hal.HAL_IN)
rgv.newpin("GvLoThreshold", hal.HAL_FLOAT, hal.HAL_IN)
rgv.ready()
try:
   # TODO the values rcvd on GvHiThreshold and GvLoThreshold need checking,  both between 1 and 8  nad GvHi > GvLo
    while 1:
        time.sleep(.1)
        # nugv = randrange(10)
	nugv = uniform(0.0,100.0)
        if nugv < rgv['GvLoThreshold']:
		rgv['GvHi'] = False
		rgv['GvLo'] = True
		#rets = rets + 1
	elif nugv > rgv['GvHiThreshold']:
		rgv['GvHi'] = True
		#advs = advs + 1
		rgv['GvLo'] = False
	else:
		rgv['GvHi'] = False
		rgv['GvLo'] = False

except KeyboardInterrupt:
    raise SystemExit
