This is a collection of my Python startup file and a set of useful utility
modules I commonly use. Unless otherwise noted, all of the code should
operate under Python 2.4 or better.

The ``tabhistory`` module is released under a separate project, currently
found at:

    http://code.google.com/p/tabhistory/

although that is likely to change in the future.

To have the startup file run automatically when you start the Python
interactive interpreter, set the environment variable PYTHONSTARTUP
to the path of the file. For example, on Linux using bash, I have:

    export PYTHONSTARTUP=/home/steve/python/utilities/startup.py

in my .bashrc file. To override that, you can temporarily clear the
environment variable at the bash command prompt:

    env -u PYTHONSTARTUP python

or for a more permanent setting, I add an alias in my .bashrc file:

    alias python2.3='env -u PYTHONSTARTUP python2.3'


