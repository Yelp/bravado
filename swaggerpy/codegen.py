#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

"""Main entry point for codegen command line app.
"""

import sys

from optparse import OptionParser

USAGE = u"usage: %prog [options] template-dir output-dir"


def main(argv=None):
    """Main method, as invoked by setuptools launcher script.

    :param argv: Command line argument list.
    """
    if argv is None:
        argv = sys.argv

    parser = OptionParser(usage=USAGE)
    parser.add_option(u"-v", u"--verbose", action=u"store_true", dest=u"verbose",
                      default=False, help=u"Verbose output")

    (options, args) = parser.parse_args(argv)

    if len(args) < 3:
        parser.error(u"Missing arguments")
    elif len(args) > 3:
        parser.error(u"Too many arguments")


# And sometimes you just want to run the script...
if __name__ == u"__main__":
    sys.exit(main() or 0)
