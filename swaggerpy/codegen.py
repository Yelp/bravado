#!/usr/bin/env python

#
# Copyright (c) 2013, Digium, Inc.
#

import logging
import sys

LOG_FORMAT =
"%(asctime)s %(levelname)-8s %(message)-70s\t[ %(name)s:%(funcName)s ]"


def main():
    """Main method, as invoked by setuptools launcher script
    """
    logging.basicConfig(level=logging.INFO,
                        format=LOG_FORMAT,
                        stream=sys.stdout)
    log = logging.getLogger('swagger.py')

    print "Hello, swagger"

# And sometimes you just want to run the script...
if __name__ == "__main__":
    main()
