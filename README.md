About
-----
Swagger.py is a Python library for using [Swagger][] defined API's.

Swagger itself is best described on the Swagger home page:

> Swagger is a specification and complete framework implementation for
> describing, producing, consuming, and visualizing RESTful web
> services.

* The [Swagger specification][] defines how API's may be described using
  Swagger.


Development
-----------

The code is documented using [Epydoc][], which allows [IntelliJ IDEA][]
to do a better job at inferring types for autocompletion.

To keep things isolated, I also recommend installing (and using)
[virtualenv][]. Some scripts are provided to help keep the
environments manageable

    $ sudo pip install virtualenv
    $ ./make-env.sh
    $ . activate-env.sh

[Setuptools][] is used for building.

    $ ./setup.py develop   # prep for development (install deps, launchers, etc.)
    $ ./setup.py nosetests # run unit tests
    $ ./setup.py bdist_egg # build distributable

[Nose][] is used for unit testing, with the [coverage][] plugin
installed to generated code coverage reports. Pass `--with-coverage`
to generate the code coverage report. HTML versions of the reports are
put in `cover/index.html`.


License
-------

Copyright (c) 2013, Digium, Inc.
All rights reserved.

Swagger.py is licensed with a [BSD 3-Clause License][BSD].

 [bsd]: http://opensource.org/licenses/BSD-3-Clause
 [coverage]: http://nedbatchelder.com/code/coverage/
 [epydoc]: http://epydoc.sourceforge.net/
 [intellij idea]: http://confluence.jetbrains.net/display/PYH/
 [nose]: http://nose.readthedocs.org/en/latest/
 [setuptools]: http://pypi.python.org/pypi/setuptools
 [swagger]: https://developers.helloreverb.com/swagger/
 [virtualenv]: http://www.virtualenv.org/
 [Swagger specification]: https://github.com/wordnik/swagger-core/wiki
