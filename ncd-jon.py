#!/usr/bin/env python

# ncd.py
# Normalized Compression Distance
# Jon Oberheide <jon@oberheide.org>
# http://jon.oberheide.org/ncd/

import sys, zlib, bz2, optparse, cPickle

class NCD(object):
    def __init__(self, compressor, level):
        self.data = {}
        self.level = int(level)

        if compressor == 'zlib':
            self.compress = zlib.compress
        elif compressor == 'bz2':
            self.compress = bz2.compress
        else:
            sys.stderr.write('invalid compressor\n')
            sys.exit(1)

    def ncd(self, a, b):
        (da, ca), (db, cb) = a, b
        return (float(len(self.compress(da + db))) - min(ca, cb)) / max(ca, cb)

    def process(self, files):
        self.files = files
        for file in self.files:
            data = open(file).read()
            clen = len(self.compress(data, self.level))
            self.data[file] = (data, clen)

        m = []
        for i in xrange(len(files)):
            m.append([])
            for j in xrange(i + 1, len(files)):
                m[i].append(self.ncd(self.data[files[i]], self.data[files[j]]))
        self.matrix = m

    def output(self, outfile, format):
        out = open(outfile, 'wb')
        if format == 'text':
            out.write('%s\n' % self.files)
            out.write('%s\n' % self.matrix)
        elif format == 'pickle':
            cPickle.dump(self.files, out)
            cPickle.dump(self.matrix, out)
        else:
            sys.stderr.write('invalid output format\n')
            sys.exit(1)
        out.close()

def main():
    opt = optparse.OptionParser("usage: %prog [OPTION] [FILE]...")
    opt.add_option('-c', dest='compressor', default='zlib', 
                   choices=('zlib', 'bz2'), 
                   help='compressor algorithm (zlib, bz2)')
    opt.add_option('-l', dest='level', default='9', 
                   choices=map(str, range(1,10)),
                   help='compression level (1-9)')
    opt.add_option('-f', dest='format', default='text',
                   choices=('text', 'pickle'), 
                   help='output format (text, pickle)')
    opt.add_option('-o', dest='output', default='ncd.output',
                   type='string', help='output filename')
    (options, files) = opt.parse_args()

    if len(files) <= 1:
        sys.stderr.write('multiple input files must be specified\n')
        sys.exit(1)

    ncd = NCD(options.compressor, options.level)
    ncd.process(files)
    ncd.output(options.output, options.format)

if __name__ == '__main__':
    main()
