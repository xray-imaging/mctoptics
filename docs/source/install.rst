==================
Install directions
==================

Build EPICS base
----------------

.. warning:: Make sure the disk partition hosting ~/epics is not larger than 2 TB. See `tech talk <https://epics.anl.gov/tech-talk/2017/msg00046.php>`_ and  `Diamond Data Storage <https://epics.anl.gov/meetings/2012-10/program/1023-A3_Diamond_Data_Storage.pdf>`_ document.

::

    $ mkdir ~/epics
    $ cd epics
    

- Download EPICS base latest release, i.e. 7.0.3.1., from https://github.com/epics-base/epics-base::

    $ git clone https://github.com/epics-base/epics-base.git
    $ cd epics-base
    $ git submodule init
    $ git submodule update
    $ make distclean (do this in case there was an OS update)
    $ make -sj
    
.. warning:: if you get a *configure/os/CONFIG.rhel9-x86_64.Common: No such file or directory* error issue this in your csh termimal: $ **setenv EPICS_HOST_ARCH linux-x86_64** or bash terminal: $ **export EPICS_HOST_ARCH=linux-x86_64**


Build a minimal synApps
-----------------------

To build a minimal synApp::

    $ cd ~/epics

- Download in ~/epics `assemble_synApps <https://github.com/EPICS-synApps/assemble_synApps/blob/18fff37055bb78bc40a87d3818777adda83c69f9/assemble_synApps>`_.sh
- Edit the assemble_synApps.sh script to include only::
    
    $modules{'ASYN'} = 'R4-44-2';
    $modules{'AUTOSAVE'} = 'R5-11';
    $modules{'BUSY'} = 'R1-7-4';
    $modules{'XXX'} = 'R6-3';

You can comment out all of the other modules (ALLENBRADLEY, ALIVE, etc.)

- Run::

    $ cd ~/epics
    $ ./assemble_synApps --dir=synApps --base=/home/beams/FAST/epics/epics-base

.. warning:: replace /home/beams/FAST/ to the full path to your home directory

- This will create a synApps/support directory::

    $ cd synApps/support/

- Clone the mctoptics module into synApps/support::
    
    $ git clone https://github.com/xray-imaging/mctoptics.git

.. warning:: If you are a mctoptics developer you should clone your fork.

- Edit configure/RELEASE add this line to the end::
    
    MCTOPTICS=$(SUPPORT)/mctoptics

- Verify that synApps/support/mctoptics/configure/RELEASE::

    EPICS_BASE=/home/beams/FAST/epics/epics-base
    SUPPORT=/home/beams/FAST/epics/synApps/support

are set to the correct EPICS_BASE and SUPPORT directories and that::

    BUSY
    AUTOSAVE
    ASYN
    XXX

point to the version installed.

- Run the following commands::

    $ make release
    $ make -sj

Testing the installation
------------------------

- Start the epics ioc and associated medm screen with::

    $ cd ~/epics/synApps/support/mctoptics/iocBoot/iocMCTOptics
    $ start_IOC
    $ start_medm (in another terminal)


Python server
-------------

- create a dedicated conda environment::

    $ conda create --name mctoptics python=3.9
    $ conda activate mctoptics

and install all packages listed in the `requirements <https://github.com/xray-imaging/mctoptics/blob/main/envs/requirements.txt>`_.txt 

::

    conda install -c epics pvapy
    conda install -c epics pyepics

then 

::

    $ cd ~/epics/synApps/support/mctoptics
    $ pip install .
    $ cd ~/epics/synApps/support/mctoptics/iocBoot/iocMCTOptics/
    $ python -i start_mctoptics.py
