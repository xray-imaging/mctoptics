==============================
mctOpticsApp EPICS application
==============================

.. 
   toctree::
   :hidden:

   mctOptics.template
   mctOptics_settings.req
   mctOptics.substitutions


mctOptics includes a complete example EPICS application, including:

- A database file and corresponding autosave request file that contain the PVs required by the mctoptics.py base class.
- OPI screens for medm
- An example IOC application that can be used to run the above databases.
  The databases are loaded in the IOC with the example substitutions file, 
  :doc:`mctOptics.substitutions`.


Base class files
================
The following tables list all of the records in the mctOptics.template file.
These records are used by the mctoptics base class and so are required.

mctOptics.template
------------------

This is the database file that contains only the PVs required by the mctoptics.py base class
:doc:`mctOptics.template`.

TomoScan and Camera PV Prefixes
-------------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0PVPrefix
    - stringout
    - Contains the prefix for the detector 0, e.g. 2bmbSP1:
  * - $(P)$(R)Camera1PVPrefix
    - stringout
    - Contains the prefix for the detector 1, e.g. 2bmbSP2:
  * - $(P)$(R)OverlayPlugin0PVPrefix
    - stringout
    - Contains the prefix for OverlayPlugin 0, e.g. 2bmbSP1:Over1:
  * - $(P)$(R)OverlayPlugin0PVPrefix
    - stringout
    - Contains the prefix for OverlayPlugin 1, e.g. 2bmbSP2:Over1:
  * - $(P)$(R)OverlayPlugin1PVPrefix
    - stringout
    - Contains the prefix for FilePlugin 0, e.g. 2bmbSP1:HDF1:
  * - $(P)$(R)FilePlugin0PVPrefix
    - stringout
    - Contains the prefix for FilePlugin 1, e.g. 2bmbSP2:HDF1:

Lens Sample X-Y-Z PV Names
--------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)LensSampleXPVName
    - stringout
    - Contains the prefix for LensSampleX , e.g. 2bmS1:m2
  * - $(P)$(R)LensSampleYPVName
    - stringout
    - Contains the prefix for LensSampleY, e.g. 2bmb:25
  * - $(P)$(R)LensSampleZPVName
    - stringout
    - Contains the prefix for LensSampleZ, e.g. 2bmS1:m1

Lens Focus PV Names
-------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Lens0FocusPVName
    - stringout
    - Contains the prefix for Lens0Focus, e.g. 2bmb:m2
  * - $(P)$(R)Lens1FocusPVName
    - stringout
    - Contains the prefix for Lens1FocusPVName, e.g. 2bmb:m3
  * - $(P)$(R)Lens2FocusPVName
    - stringout
    - Contains the prefix for Lens2FocusPVName, e.g. 2bmb:m4

Camera rotation PV Names
------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0RotationPVName
    - stringout
    - Contains the prefix for Camera0Rotation , e.g. 2bmb:m7
  * - $(P)$(R)Camera1RotationPVName
    - stringout
    - Contains the prefix for Camera1Rotation , e.g. 2bmb:m8

Optique Peter camera selector
-----------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)CameraSelect
    - mbbo
    - Camera selector for Pos0 and Pos1 position
  * - $(P)$(R)CameraSelected
    - mbbo
    - Camera selector status for Camera0 and Camera1 position
  * - $(P)$(R)CameraPos0
    - a0
    - Motor position for the Camera0
  * - $(P)$(R)CameraPos1
    - a0
    - Motor position for the Camera1
  * - $(P)$(R)CameraName0
    - a0
    - Camera label for Pos0, e.g. Adimec
  * - $(P)$(R)CameraName1
    - a0
    - Camera label for Pos1, e.g. Flir
  * - $(P)$(R)CameraMotorPVName
    - stringout
    - Contains the camera motor PV name, e.g. 2bmb:m5


Optique Peter camera rotation
-----------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0Lens0Rotation
    - a0
    - PV storing Camera 0 Lens 0 rotation value
  * - (P)$(R)Camera0Lens1Rotation
    - a0
    - PV storing Camera 0 Lens 1 rotation value
  * - $(P)$(R)Camera0Lens2Rotation
    - a0
    - PV storing Camera 0 Lens 1 rotation value
  * - $(P)$(R)Camera1Lens0Rotation
    - a0
    - PV storing Camera 1 Lens 0 rotation value
  * - $(P)$(R)Camera1Lens1Rotation
    - a0
    - PV storing Camera 1 Lens 1 rotation value
  * - $(P)$(R)Camera1Lens2Rotation
    - a0
    - PV storing Camera 1 Lens 2 rotation value

Optique Peter lens focus
------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0Lens0Focus
    - a0
    - PV storing Camera 0 Lens 0 focus value
  * - $(P)$(R)Camera0Lens1Focus
    - a0
    - PV storing Camera 0 Lens 1 focus value
  * - $(P)$(R)Camera0Lens2Focus
    - a0
    - PV storing Camera 0 Lens 2 focus value
  * - $(P)$(R)Camera1Lens0Focus
    - a0
    - PV storing Camera 1 Lens 0 focus value
  * - $(P)$(R)Camera1Lens1Focus
    - a0
    - PV storing Camera 1 Lens 1 focus value
  * - $(P)$(R)Camera1Lens2Focus
    - a0
    - PV storing Camera 1 Lens 2 focus value

Optique Peter lens selector
---------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)LensSelect
    - mbbo
    - Lens selector for Pos0 and Pos1 position
  * - $(P)$(R)Camera0LensPos0
    - a0
    - Motor position for the first lens
  * - $(P)$(R)Camera0LensPos1
    - a0
    - Motor position for the second lens
  * - $(P)$(R)Camera0LensPos2
    - a0
    - Motor position for the third lens
  * - $(P)$(R)LensName0
    - a0
    - Lens label for Pos0, e.g. Lens0
  * - $(P)$(R)LensName1
    - a0
    - Lens label for Pos1, e.g. Lens1
  * - $(P)$(R)LensName2
    - a0
    - Lens label for Pos2, e.g. lens2
  * - $(P)$(R)LensMotorPVName
    - stringout
    - Contains the Lens motor PV name, e.g. 2bmb:m1

Detector image cross
--------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)CrossSelect
    - mbbo
    - 

Optique Peter lens 1 offsets
----------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0Lens1XOffset
    - ao
    - 
  * - $(P)$(R)Camera0Lens1YOffset
    - ao
    - 
  * - $(P)$(R)Camera0Lens1ZOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens1XOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens1YOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens1ZOffset
    - ao
    - 

Optique Peter lens 2 offsets
----------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0Lens2XOffset
    - ao
    - 
  * - $(P)$(R)Camera0Lens2YOffset
    - ao
    - 
  * - $(P)$(R)Camera0Lens2ZOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens2XOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens2YOffset
    - ao
    - 
  * - $(P)$(R)Camera1Lens2ZOffset
    - ao
    - 

MCT status via Channel Access
-----------------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)MCTStatus
    - waveform
    -
  * - $(P)$(R)Watchdog
    - calcout
    -
  * - $(P)$(R)ServerRunning
    - bi
    - 

Sync to motor
-------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Sync
    - busy
    - 

Optics information
------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)ScintillatorType
    - stringout
    - Contains the type of scintillator being used.
  * - $(P)$(R)ScintillatorThickness
    - ao
    - Contains the thickness of the scintillator in microns.
  * - $(P)$(R)ImagePixelSize
    - ao
    - Contains the pixel size on the sample in microns (i.e. includes objective magnification)
  * - $(P)$(R)DetectorPixelSize
    - ao
    - Contains the pixel size of the detector.
  * - $(P)$(R)CameraObjective
    - stringout
    - Description of the camera objective
  * - $(P)$(R)CameraTubeLength
    - stringout
    - Description of the camera objective

Lens name
---------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Lens0Name
    - stringout
    - Lens name for Lens0, e.g. 1.1x
  * - $(P)$(R)Lens1Name
    - stringout
    - Lens name for Lens1, e.g. 5x
  * - $(P)$(R)Lens2Name
    - stringout
    - Lens name for Lens2, e.g. 10x


Camera names
------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Camera0Name
    - stringout
    - 
  * - $(P)$(R)Camera1Name
    - stringout
    - 


Energy information
------------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)Energy
    - mbbo
    - Contains the energy of the beamline.
  * - $(P)$(R)EnergyMode
    - mbbo
    - Contains the energy mode of the beamline, e.g. 'Mono', 'Pink', 'White'.
  * - $(P)$(R)Filters
    - stringout
    - Contains the material and thickness of the filters manually set in the beam path, e.g. Al 1mm; Glass 5mm.
  * - $(P)$(R)EnergyArbitrarySet
    - busy
    - 
  * - $(P)$(R)EnergyBusy
    - busy
    - 
  * - $(P)$(R)EnergyUseCalibration
    - mbbo
    -
  * - $(P)$(R)EnergyCalibrationFileOne
    - stringout
    -
  * - $(P)$(R)EnergyCalibrationFileTwo
    - stringout
    -

Energy change
-------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)EnergyArbitrarySet
    - busy
    -
  * - $(P)$(R)EnergyBusy
    - busy
    -
  * - $(P)$(R)EnergyUseCalibration
    - mbbo
    -
  * - $(P)$(R)EnergyCalibrationFileOne
    - stringout
    -
  * - $(P)$(R)EnergyCalibrationFileTwo
    - stringout
    -

Detector cropping
-----------------

.. cssclass:: table-bordered table-striped table-hover
.. list-table::
  :header-rows: 1
  :widths: 5 5 90

  * - Record name
    - Record type
    - Description
  * - $(P)$(R)CutLeft
    - longout
    - 
  * - $(P)$(R)CutRight
    - longout
    - 
  * - $(P)$(R)CutTop
    - longout
    - 
  * - $(P)$(R)CutBottom
    - longout
    - 
  * - $(P)$(R)Cut
    - busy
    - 
  * - $(P)$(R)SuggestedAngles
    - ao
    - 
  * - $(P)$(R)SuggestedAngleStep
    - ao
    - 
    
medm files
----------

mctOptics.adl
^^^^^^^^^^^^^

The following is the MEDM screen :download:`mctOptics.adl <../../mctOpticsApp/op/adl/mctOptics.adl>` during a scan. 
The status information is updating.

.. image:: img/mctOptics.png
    :width: 75%
    :align: center

mctOpticsEPICS_PVs.adl
^^^^^^^^^^^^^^^^^^^^^^

The following is the MEDM screen :download:`mctOpticsEPICS_PVs.adl <../../mctOpticsApp/op/adl/mctOpticsEPICS_PVs.adl>`. 

If these PVs are changed tomoscan must be restarted.

.. image:: img/mctOpticsEPICS_PVs.png
    :width: 75%
    :align: center

