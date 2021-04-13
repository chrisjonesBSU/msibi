============
Installation
============

Install with pip
----------------
Coming soon!

Install from source
-------------------
::

    $ git clone https://github.com/cmelab/msibi
    $ cd msibi
    $ conda env create -f environment.yml
    $ conda activate msibi
    $ pip install -e .

Dependencies
------------
To use msibi, the following libraries and software will need to be installed.

    Linux, Mac OS X or Windows operating system
        We develop mainly on 64-bit OS X Yosemite and Windows 7 machines.

    `Python <http://python.org>`_ = 2.7 or 3.3+
        TravisCI currently tests on 2.7, 3.3 and 3.4.

    `MDTraj <http://mdtraj.org/>`_ >=1.0.0
        MDTraj is a Python library for reading, writing and analyizing
        molecular dynamics trajectories. mBuild uses MDTraj as an entry and
        exit point for several types of molecule data formats. See their
        installation instructions
        `here <http://mdtraj.org/latest/installation.html>`_.

To make your life easier, we recommend that you use a pre-packaged Python
distribution like `Continuum's Anaconda <https://store.continuum.io/>`_
in order to get all of the dependencies.

Testing your installation
-------------------------

mBuild uses `py.test` for unit testing. To run them simply type run the
following while in the base directory::

    $ pip install pytest
    $ py.test

We need a LOT more tests so any help here is especially welcome!
