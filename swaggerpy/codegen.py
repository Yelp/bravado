#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Main entry point for codegen command line app.
"""

import sys

from optparse import OptionParser

USAGE = "usage: %prog [options] template-dir output-dir"


def main(argv=None):
    """Main method, as invoked by setuptools launcher script.

    :param argv: Command line argument list.
    """
    if argv is None:
        argv = sys.argv

    parser = OptionParser(usage=USAGE)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Verbose output")

    (options, args) = parser.parse_args(argv)

    if len(args) < 3:
        parser.error("Missing arguments")
    elif len(args) > 3:
        parser.error("Too many arguments")

    template_dir = args[1]
    output_dir = args[2]

# And sometimes you just want to run the script...
if __name__ == "__main__":
    sys.exit(main() or 0)
