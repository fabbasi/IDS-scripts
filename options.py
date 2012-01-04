import sys
import os
import optparse

oparser = optparse.OptionParser(usage="usage: %prog [options] filename")
oparser.add_option("-s","--sigdir",
		   action="store",
		   dest = "sigdir",
		   default = False,
		   help = "path to signature directory")
oparser.add_option("-d","--datdir",
		   action="store",
		   dest = "datdir",
		   default = False,
		   help = "path to dataset directory")

(options, args) = oparser.parse_args()


#if len(args) != 1 :
#            oparser.error("wrong number of arguments")

print "arguments: ",args
print "options: ",options

#test = options[sigdir]
print "signaturedir is: ",options.sigdir
