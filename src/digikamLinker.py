#!/usr/bin/env python
# encoding: utf-8
'''
 -- walks a directory tree and sym-links all files matching a certian EXIF-tag to another directory while keeping directory structure

 is a script that reads in exif data from files in a directory structure and if they match a certain criteria sym-links them to another directory.

It defines classes_and_methods

@author:     Ian Hubbertz

@license:    AS-IS

@contact:    user_email                                                                                                                                                                   
@deffield    updated: Updated                                                                                                                                                             
'''                                                                                                                                                                                       
                                                                                                                                                                                          
import sys                                                                                                                                                                                
import os                                                                                                                                                                                 
                                                                                                                                                                                          
import pyexiv2                                                                                                                                                                            
                                                                                                                                                                                          
from optparse import OptionParser                                                                                                                                                         
from fileinput import filename                                                                                                                                                            
                                                                                                                                                                                          
__all__ = []                                                                                                                                                                              
__version__ = 0.1                                                                                                                                                                         
__date__ = '2014-01-02'                                                                                                                                                                   
__updated__ = '2017-07-18'      

vl = 1
                                                                                                                                                          
                                                                                                                                                                                          
def link_files(startpath, dstpath, min_rating):                                                                                                                                                       
    lastroot = ""                               
    print min_rating                                                                                                                                          
    for root, dirs, files in os.walk(startpath):                                                                                                                                          
        for f in files:                                                                                                                                                                   
            if ".jpg" not in f.lower(): continue ## Save some time                                                                                                                        
            filename = os.path.join(root,f)                                                                                                                                               
            metadata = pyexiv2.ImageMetadata(filename)                                                                                                                                    
            try:
                metadata.read()
                if vl>=3: print metadata.xmp_keys
                rating_tag = metadata['Xmp.xmp.Rating']
                rating = rating_tag.value
                if vl>=2: print "%s rated %d." (filename, rating) 
                if rating >= min_rating:
                    # optimize expensive join and dst-check
                    if not root == lastroot:
                        if vl>=2: print "New root: %s" % root
                        relpath = os.path.relpath(root, startpath)
                        dstdir = os.path.join(dstpath, relpath)
                        if vl>=2: print "New dest: %s and %s --> %s" % (dstpath, relpath, dstdir)
                        if not os.path.isdir(dstdir): os.makedirs(dstdir, 0755)
                        lastroot = root
                    dstname = os.path.join(dstdir, f)
                    if vl>=2: print "    %d: Symlinking %s to %s" % (rating, filename, dstname)
                    os.symlink(filename, dstname)
            except KeyError, e:
                print "File %s has no rating" % (filename)
                continue
            except IOError, e:
                print "Error [%s] reading file %s" % (e, filename)
                continue
            except OSError, e:
                if vl >= 1: print "Symlink %s already exists" % (filename)
                continue

def main(argv=None):
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    #program_usage = '''usage: spam two eggs''' # optional - will be autogenerated by optparse
    program_longdesc = '''''' # optional - give further explanation about what the program does
    program_license = "Created 2014-2017 Ian Hubbertz - use at your own risk."

    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-i", "--in", dest="inpath", help="set input path [default: %default]", metavar="FILE")
        parser.add_option("-o", "--out", dest="outfile", help="set output path [default: %default]", metavar="FILE")
        parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        parser.add_option("-r", "--rating", dest="rating", help="set minimum rating [default: %default]")

        # set defaults
        parser.set_defaults(outfile="./out", inpath="./in", rating=4)

        # process options
        (opts, args) = parser.parse_args(argv)

        if opts.verbose > 0:
            print("verbosity level = %d" % opts.verbose)
            vl = opts.verbose
        if opts.inpath:
            print("inpath = %s" % opts.inpath)
        if opts.outfile:
            print("outfile = %s" % opts.outfile)
            
        if opts.rating:
            print("rating = %s" % opts.rating)
        
            
        link_files(opts.inpath, opts.outfile, int(opts.rating))


        # MAIN BODY #

    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2


if __name__ == "__main__":
    sys.exit(main())
    