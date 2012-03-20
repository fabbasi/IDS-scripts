#/bin/env python
import sys, os

from lib2to3 import refactor, main
from lib2to3.main import StdoutRefactoringTool

#fixes = refactor.get_fixers_from_package("lib2to3.fixes")    

import optparse
import logging
import shutil
import difflib


def diff_texts(a, b, filename):
    """Return a unified diff of two strings."""
    a = a.splitlines()
    b = b.splitlines()
    return difflib.unified_diff(a, b, filename, filename,
                                "(original)", "(refactored)",
                                lineterm="")
    
def warn(msg):
    print >> sys.stderr, "WARNING: %s" % (msg,)

class MyStdRefactoringTool(StdoutRefactoringTool):
    def write_file(self, new_text, filename, old_text, encoding):
        if not self.nobackups:
            # Make backup
            
            filename = getattr(self, "outputfilename", filename)
            
            if hasattr(self, "outputfilename"):
                self.nobackups = True
            backup = filename + ".bak"
            if os.path.lexists(backup):
                try:
                    os.remove(backup)
                except os.error, err:
                    self.log_message("Can't remove backup %s", backup)
            if os.path.exists(filename):
                try:
                    os.rename(filename, backup)
                except os.error, err:
                    self.log_message("Can't rename %s to %s", filename, backup)
        # Actually write the new file
        write = super(StdoutRefactoringTool, self).write_file
        write(new_text, filename, old_text, encoding)
        if not self.nobackups:
            try:
                shutil.copymode(backup, filename)
            except OSError, ex:
                pass
            
def main(fixer_pkg, args=None):
    """Main program.

    Args:
        fixer_pkg: the name of a package where the fixers are located.
        args: optional; a list of command line arguments. If omitted,
              sys.argv[1:] is used.

    Returns a suggested exit status (0, 1, 2).
    """
    # Set up option parser
    parser = optparse.OptionParser(usage="orange2to25 [options] file|dir ...")
    parser.add_option("-d", "--doctests_only", action="store_true",
                      help="Fix up doctests only")
    parser.add_option("-f", "--fix", action="append", default=[],
                      help="Each FIX specifies a transformation; default: all")
    parser.add_option("-j", "--processes", action="store", default=1,
                      type="int", help="Run orange2to25 concurrently")
    parser.add_option("-x", "--nofix", action="append", default=[],
                      help="Prevent a fixer from being run.")
    parser.add_option("-l", "--list-fixes", action="store_true",
                      help="List available transformations")
#    parser.add_option("-p", "--print-function", action="store_true",
#                      help="Modify the grammar so that print() is a function")
    parser.add_option("-v", "--verbose", action="store_true",
                      help="More verbose logging")
    parser.add_option("--no-diffs", action="store_true",
                      help="Don't show diffs of the refactoring")
    parser.add_option("-w", "--write", action="store_true",
                      help="Write back modified files")
    parser.add_option("-n", "--nobackups", action="store_true", default=False,
                      help="Don't write backups for modified files.")
    parser.add_option("-a", "--aggressive", action="store_true", default=False,
                      help="Aggressive name replace (without a module qualifier, e.g. replace ExampleTable with even if not preceded by orange.* )")
    parser.add_option("-o", "--outfile", default = "",
                      help="Output filename (if -w present and a single file on the command line)")

    # Parse command line arguments
    refactor_stdin = False
    flags = {}
    options, args = parser.parse_args(args)
    if not options.write and options.no_diffs:
        warn("not writing files and not printing diffs; that's not very useful")
    if not options.write and options.nobackups:
        parser.error("Can't use -n without -w")
    if options.list_fixes:
        print "Available transformations for the -f/--fix option:"
        for fixname in refactor.get_all_fix_names(fixer_pkg):
            print fixname
        if not args:
            return 0
    if not args:
        print >> sys.stderr, "At least one file or directory argument required."
        print >> sys.stderr, "Use --help to show usage."
        return 2
    if "-" in args:
        refactor_stdin = True
        if options.write:
            print >> sys.stderr, "Can't write to stdin."
            return 2
        
#    if options.print_function:
#        flags["print_function"] = True

    # Set up logging handler
    level = logging.DEBUG if options.verbose else logging.INFO
    logging.basicConfig(format='%(name)s: %(message)s', level=level)

    # Initialize the refactoring tool
    avail_fixes = set(refactor.get_fixers_from_package(fixer_pkg))
    # Remove aggressive fixes if not requested
    if not options.aggressive:
        avail_fixes = set([fix for fix in avail_fixes if not fix.endswith("_aggressive")])
        
    unwanted_fixes = set(fixer_pkg + ".fix_" + fix for fix in options.nofix)
    explicit = set()
    if options.fix:
        all_present = False
        for fix in options.fix:
            if fix == "all":
                all_present = True
            else:
                explicit.add(fixer_pkg + ".fix_" + fix)
        requested = avail_fixes.union(explicit) if all_present else explicit
    else:
        requested = avail_fixes.union(explicit)
    fixer_names = requested.difference(unwanted_fixes)
    rt = MyStdRefactoringTool(sorted(fixer_names), flags, sorted(explicit),
                               options.nobackups, not options.no_diffs)
    if options.outfile:
        if len(args) > 2:
            print >> sys.stderr, "-o, --outfile used but multiple script arguments"
        elif not os.path.isfile(args[-1]):
            print >> sys.stderr, "-o, --outfile used but argumnet is a directory"
        else:
            rt.outputfilename = options.outfile
        
    # Refactor all files and directories passed as arguments
    if not rt.errors:
        if refactor_stdin:
            rt.refactor_stdin()
        else:
            try:
                rt.refactor(args[1:], options.write, options.doctests_only,
                            options.processes)
            except refactor.MultiprocessingUnsupported:
                assert options.processes > 1
                print >> sys.stderr, "Sorry, -j isn't " \
                    "supported on this platform."
                return 1
        rt.summarize()

    # Return error status (0 if rt.errors is zero)
    return int(bool(rt.errors))

sys.exit(main("Orange.fixes", sys.argv))




