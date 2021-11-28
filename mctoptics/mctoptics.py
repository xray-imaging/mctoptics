import os
import pvaccess as pva
import numpy as np
import queue
import time
import threading
import signal
import json

from pathlib import Path
from mctoptics import util
from mctoptics import log
from epics import PV

data_path = Path(__file__).parent / 'data'

class MCTOptics():
    """ Class for controlling TXM optics via EPICS

        Parameters
        ----------
        args : dict
            Dictionary of pv variables.
    """

    def __init__(self, pv_files, macros):

        # init pvs
        self.config_pvs = {}
        self.control_pvs = {}
        self.pv_prefixes = {}

        self.lens0_sample_x = None
        self.lens0_sample_y = None
        self.lens0_sample_z = None

        if not isinstance(pv_files, list):
            pv_files = [pv_files]
        for pv_file in pv_files:
            self.read_pv_file(pv_file, macros)
        self.show_pvs()

        #Define PVs we will need from the sample x-y-z motos, which is on another IOC
        lens_sample_x_pv_name = self.control_pvs['LensSampleX'].pvname
        self.control_pvs['LensSampleXPosition']      = PV(lens_sample_x_pv_name + '.VAL')
        lens_sample_y_pv_name = self.control_pvs['LensSampleY'].pvname
        self.control_pvs['LensSampleYPosition']      = PV(lens_sample_y_pv_name + '.VAL')
        lens_sample_z_pv_name = self.control_pvs['LensSampleX'].pvname
        self.control_pvs['LensSampleZPosition']      = PV(lens_sample_z_pv_name + '.VAL')


        prefix = self.pv_prefixes['TomoScan']
        self.control_pvs['TSScintillatorType']      = PV(prefix + 'ScintillatorType')
        self.control_pvs['TSScintillatorThickness'] = PV(prefix + 'ScintillatorThickness')
        self.control_pvs['TSCameraObjective']       = PV(prefix + 'CameraObjective')
        self.control_pvs['TSCameraTubeLength']      = PV(prefix + 'CameraTubeLength')
                 
        self.control_pvs['TSDetectorPixelSize']     = PV(prefix + 'DetectorPixelSize')
        self.control_pvs['TSImagePixelSize']        = PV(prefix + 'ImagePixelSize')
        self.control_pvs['TSExposureTime']          = PV(prefix + 'ExposureTime')

        #Define PVs from the camera IOC that we will need
        prefix = self.pv_prefixes['Camera']
        camera_prefix = prefix + 'cam1:'

        self.control_pvs['CamAcquireTime']          = PV(camera_prefix + 'AcquireTime')
        self.control_pvs['CamArraySizeXRBV']        = PV(camera_prefix + 'ArraySizeX_RBV')
        self.control_pvs['CamArraySizeYRBV']        = PV(camera_prefix + 'ArraySizeY_RBV')

        prefix = self.pv_prefixes['OverlayPlugin']
        self.control_pvs['OPEnableCallbacks'] = PV(prefix + 'EnableCallbacks')
        self.control_pvs['OP1Use']            = PV(prefix + '1:Use')        
        self.control_pvs['OP1CenterX']        = PV(prefix + '1:CenterX')        
        self.control_pvs['OP1CenterY']        = PV(prefix + '1:CenterY')        

        self.epics_pvs = {**self.config_pvs, **self.control_pvs}

        # print(self.epics_pvs)
        for epics_pv in ('LensSelect', 'CameraSelect', 'CrossSelect', 'Focus1Select', 'Focus2Select', 'ExposureTime'):
            self.epics_pvs[epics_pv].add_callback(self.pv_callback)

        # Start the watchdog timer thread
        thread = threading.Thread(target=self.reset_watchdog, args=(), daemon=True)
        thread.start()

        log.setup_custom_logger("./mctoptics.log")

    def reset_watchdog(self):
        """Sets the watchdog timer to 5 every 3 seconds"""
        while True:
            self.epics_pvs['Watchdog'].put(5)
            time.sleep(3)

        log.setup_custom_logger("./mctoptics.log")

    def read_pv_file(self, pv_file_name, macros):
        """Reads a file containing a list of EPICS PVs to be used by MCTOptics.


        Parameters
        ----------
        pv_file_name : str
          Name of the file to read
        macros: dict
          Dictionary of macro substitution to perform when reading the file
        """

        pv_file = open(pv_file_name)
        lines = pv_file.read()
        pv_file.close()
        lines = lines.splitlines()
        for line in lines:
            is_config_pv = True
            if line.find('#controlPV') != -1:
                line = line.replace('#controlPV', '')
                is_config_pv = False
            line = line.lstrip()
            # Skip lines starting with #
            if line.startswith('#'):
                continue
            # Skip blank lines
            if line == '':
                continue
            pvname = line
            # Do macro substitution on the pvName
            for key in macros:
                pvname = pvname.replace(key, macros[key])
            # Replace macros in dictionary key with nothing
            dictentry = line
            for key in macros:
                dictentry = dictentry.replace(key, '')

            epics_pv = PV(pvname)

            if is_config_pv:
                self.config_pvs[dictentry] = epics_pv
            else:
                self.control_pvs[dictentry] = epics_pv
            # if dictentry.find('PVAPName') != -1:
            #     pvname = epics_pv.value
            #     key = dictentry.replace('PVAPName', '')
            #     self.control_pvs[key] = PV(pvname)
            if dictentry.find('PVName') != -1:
                pvname = epics_pv.value
                key = dictentry.replace('PVName', '')
                self.control_pvs[key] = PV(pvname)
            if dictentry.find('PVPrefix') != -1:
                pvprefix = epics_pv.value
                key = dictentry.replace('PVPrefix', '')
                self.pv_prefixes[key] = pvprefix

    def show_pvs(self):
        """Prints the current values of all EPICS PVs in use.

        The values are printed in three sections:

        - config_pvs : The PVs that are part of the scan configuration and
          are saved by save_configuration()

        - control_pvs : The PVs that are used for EPICS control and status,
          but are not saved by save_configuration()

        - pv_prefixes : The prefixes for PVs that are used for the areaDetector camera,
          file plugin, etc.
        """

        print('configPVS:')
        for config_pv in self.config_pvs:
            print(config_pv, ':', self.config_pvs[config_pv].get(as_string=True))

        print('')
        print('controlPVS:')
        for control_pv in self.control_pvs:
            print(control_pv, ':', self.control_pvs[control_pv].get(as_string=True))

        print('')
        print('pv_prefixes:')
        for pv_prefix in self.pv_prefixes:
            print(pv_prefix, ':', self.pv_prefixes[pv_prefix])

    def pv_callback(self, pvname=None, value=None, char_value=None, **kw):
        """Callback function that is called by pyEpics when certain EPICS PVs are changed
        """

        log.debug('pv_callback pvName=%s, value=%s, char_value=%s', pvname, value, char_value)
        if (pvname.find('LensSelect') != -1) and ((value == 0) or (value == 1) or (value == 2)):
            thread = threading.Thread(target=self.lens_select, args=())
            thread.start()
        elif (pvname.find('CameraSelect') != -1) and ((value == 0) or (value == 1)):
            thread = threading.Thread(target=self.camera_select, args=())
            thread.start()
        elif (pvname.find('CrossSelect') != -1) and ((value == 0) or (value == 1)):
            thread = threading.Thread(target=self.cross_select, args=())
            thread.start()
        elif (pvname.find('Focus1Select') != -1) and ((value == 0) or (value == 1)):
            thread = threading.Thread(target=self.focus1_select, args=())
            thread.start()
        elif (pvname.find('Focus2Select') != -1) and ((value == 0) or (value == 1) or (value == 2)):
            thread = threading.Thread(target=self.focus2_select, args=())
            thread.start()
        elif (pvname.find('ExposureTime') != -1):
            thread = threading.Thread(target=self.exposure_time, args=())
            thread.start()

    def lens_select(self):
        """Moves the Optique Peter lens.
        """

        # TO BE completed
        # if((self.lens0_sample_x == None) and (self.epics_pvs['LensSelect'].get() == 0)):
        #     self.lens0_sample_x = self.control_pvs['LensSampleXPosition'].get()
        #     self.lens0_sample_y = self.control_pvs['LensSampleYPosition'].get()
        #     self.lens0_sample_z = self.control_pvs['LensSampleZPosition'].get()


        if (self.epics_pvs['LensLock'].get() == 1):
            lens_pos0 = self.epics_pvs['LensPos0'].get()
            lens_pos1 = self.epics_pvs['LensPos1'].get()
            lens_pos2 = self.epics_pvs['LensPos2'].get()

            lens_select = self.epics_pvs['LensSelect'].get()
            lens_name = 'None'

            log.info('Changing Optique Peter lens')
            if(self.epics_pvs['LensSelect'].get() == 0):
                lens_name = self.epics_pvs['LensName0'].get()
                self.epics_pvs['MCTStatus'].put('Moving to lens: ' + lens_name)
                self.epics_pvs['LensMotor'].put(lens_pos0, wait=True, timeout=120)
            elif(self.epics_pvs['LensSelect'].get() == 1):
                lens_name = self.epics_pvs['LensName1'].get()
                self.epics_pvs['MCTStatus'].put('Moving to lens: '+ lens_name)
                self.epics_pvs['LensMotor'].put(lens_pos1, wait=True, timeout=120)
            elif(self.epics_pvs['LensSelect'].get() == 2):
                lens_name = self.epics_pvs['LensName2'].get()
                self.epics_pvs['MCTStatus'].put('Moving to lens: '+ lens_name)
                self.epics_pvs['LensMotor'].put(lens_pos2, wait=True, timeout=120)
            # message = 'Lens selected: ' + str(self.epics_pvs['LensSelect'].get())
            message = 'Lens selected: ' + lens_name
            log.info(message)
            self.epics_pvs['MCTStatus'].put(message)

            lens_name = lens_name.upper().replace("X", "")
            with open(os.path.join(data_path, 'lens.json')) as json_file:
                lens_lookup = json.load(json_file)
            
            try:
                scintillator_type      = lens_lookup[lens_name]['scintillator_type']
                scintillator_thickness = lens_lookup[lens_name]['scintillator_thickness']
                magnification          = str(lens_lookup[lens_name]['magnification'])
                tube_lens              = lens_lookup[lens_name]['tube_lens']

                # update tomoScan PVs
                self.control_pvs['TSScintillatorType'].put(scintillator_type)
                self.control_pvs['TSScintillatorThickness'].put(scintillator_thickness)
                self.control_pvs['TSCameraObjective'].put(magnification)
                self.control_pvs['TSCameraTubeLength'].put(tube_lens)

                detector_pixel_size    = self.control_pvs['TSDetectorPixelSize'].get()
                image_pixel_size       = float(detector_pixel_size)/float(magnification)
                self.control_pvs['TSImagePixelSize'].put(image_pixel_size)
            except KeyError as e:
                log.error('Lens called %s is not defined. Please add it to the /data/lens.json file' % e)
                log.error('Failed to update: Scintillator type')
                log.error('Failed to update: Scintillator thickness')
                log.error('Failed to update: Camera objective')
                log.error('Failed to update: Camera tube length')
                log.error('Failed to update: Image pixel size')
        else:
            log.error('Changing Optique Peter lens: Locked')
            self.epics_pvs['MCTStatus'].put('Lens select is locked')

    def camera_select(self):
        """Moves the Optique Peter camera.
        """
        
        if (self.epics_pvs['CameraLock'].get() == 1):
            camera_pos0 = self.epics_pvs['CameraPos0'].get()
            camera_pos1 = self.epics_pvs['CameraPos1'].get()

            camera_select = self.epics_pvs['CameraSelect'].get()
            camera_name = 'None'

            log.info('Changing Optique Peter camera')
            self.epics_pvs['MCTStatus'].put('Changing Optique Peter camera')

            if(self.epics_pvs['CameraSelect'].get() == 0):
                camera_name = self.epics_pvs['CameraName0'].get()
                self.epics_pvs['MCTStatus'].put('Camera selected: 0')
                self.epics_pvs['CameraMotor'].put(camera_pos0, wait=True, timeout=120)
            elif(self.epics_pvs['CameraSelect'].get() == 1):
                camera_name = self.epics_pvs['CameraName1'].get()
                self.epics_pvs['MCTStatus'].put('Camera selected: 1')
                self.epics_pvs['CameraMotor'].put(camera_pos1, wait=True, timeout=120)
            log.info('Camera: %s selected', camera_name)

            camera_name = camera_name.upper()
            with open(os.path.join(data_path, 'camera.json')) as json_file:
                camera_lookup = json.load(json_file)

            try:
                detector_pixel_size = camera_lookup[camera_name]['detector_pixel_size']
                # update tomoScan PVs
                self.control_pvs['TSDetectorPixelSize'].put(detector_pixel_size)

                magnification = self.control_pvs['TSCameraObjective'].get()
                magnification = magnification.upper().replace("X", "") # just in case there was a manual entry ...
                image_pixel_size = float(detector_pixel_size)/float(magnification)
                self.control_pvs['TSImagePixelSize'].put(image_pixel_size)
            except KeyError as e:
                log.error('Camera called %s is not defined. Please add it to the /data/lens.json file' % e)
                log.error('Failed to update: Detector pixel size')
                log.error('Failed to update: Image pixel size')
        else:
            log.error('Changing Optique Peter camera: Locked')
            self.epics_pvs['MCTStatus'].put('Camera select is locked')

    def cross_select(self):
        """Plot the cross in imageJ.
        """
    

        if (self.epics_pvs['CrossSelect'].get() == 0):
            sizex = int(self.epics_pvs['CamArraySizeXRBV'].get())
            sizey = int(self.epics_pvs['CamArraySizeYRBV'].get())
            self.epics_pvs['OP1CenterX'].put(sizex//2)
            self.epics_pvs['OP1CenterY'].put(sizey//2)
            self.control_pvs['OP1Use'].put(1)
            log.info('Cross at %d %d is enable' % (sizex//2,sizey//2))
        else:
            self.control_pvs['OP1Use'].put(0)
            log.info('Cross is disabled')

    def focus1_select(self):
        """
        Moves the Optique Peter lens 1 focus position from focus location to 
        lens replacement poistion 
        """        
        if (self.epics_pvs['Focus1Lock'].get() == 1):
            focus1_pos0 = self.epics_pvs['Focus1Pos0'].get()
            focus1_pos1 = self.epics_pvs['Focus1Pos1'].get()

            focus1_select = self.epics_pvs['Focus1Select'].get()
            focus1_name = 'None'

            log.info('Changing Optique Peter lens 1 focus select')

            if(self.epics_pvs['Focus1Select'].get() == 0):
                focus1_name = self.epics_pvs['Focus1Name0'].get()
                self.epics_pvs['MCTStatus'].put('Lens 1 moving to the focus position')
                self.epics_pvs['Focus1Motor'].put(focus1_pos0, wait=True, timeout=120)
                self.epics_pvs['MCTStatus'].put('Lens 1 is the focus position')
            elif(self.epics_pvs['Focus1Select'].get() == 1):
                focus1_name = self.epics_pvs['Focus1Name1'].get()
                self.epics_pvs['MCTStatus'].put('Lens 1 moving to replacement position')
                self.epics_pvs['Focus1Motor'].put(focus1_pos1, wait=True, timeout=120)
                self.epics_pvs['Focus1Lock'].put(0, wait=True)
                self.epics_pvs['LensLock'].put(0, wait=True)
                self.epics_pvs['MCTStatus'].put('Lens 1 focus is locked: SET NEW LENS NAME')

            log.info('Focus1: %s selected', focus1_name)
        else:
            self.epics_pvs['MCTStatus'].put('Lens 1 focus is locked: SET NEW LENS NAME')
            self.epics_pvs['Focus1Select'].put(1)
            log.error('Changing Optique Peter focus1: Locked')

    def focus2_select(self):
        """
        Moves the Optique Peter focus 2 position from focus location to 
        lens replacement positions (focus 2 has 2 lens replacement positions for 20x and <10x)
        """

        if (self.epics_pvs['Focus2Lock'].get() == 1):
            focus2_pos0 = self.epics_pvs['Focus2Pos0'].get()
            focus2_pos1 = self.epics_pvs['Focus2Pos1'].get()
            focus2_pos2 = self.epics_pvs['Focus2Pos2'].get()

            focus2_select = self.epics_pvs['Focus2Select'].get()
            focus2_name = 'None'

            log.info('Changing Optique Peter focus2 2 focus select')

            if(self.epics_pvs['Focus2Select'].get() == 0):
                focus2_name = self.epics_pvs['Focus2Name0'].get()
                self.epics_pvs['MCTStatus'].put('Lens 2 moving to the focus position')
                self.epics_pvs['Focus2Motor'].put(focus2_pos0, wait=True, timeout=120)
                self.epics_pvs['MCTStatus'].put('Lens 2 is the focus position')
            elif(self.epics_pvs['Focus2Select'].get() == 1):
                focus2_name = self.epics_pvs['Focus2Name1'].get()
                self.epics_pvs['MCTStatus'].put('Lens 2 moving to replacement position 1')
                self.epics_pvs['Focus2Motor'].put(focus2_pos1, wait=True, timeout=120)
                self.epics_pvs['Focus2Lock'].put(0, wait=True)
                self.epics_pvs['LensLock'].put(0, wait=True)
                self.epics_pvs['MCTStatus'].put('Lens 2 focus is locked: SET NEW LENS NAME')
            elif(self.epics_pvs['Focus2Select'].get() == 2):
                focus2_name = self.epics_pvs['Focus2Name2'].get()
                self.epics_pvs['MCTStatus'].put('Lens 2 moving to replacement position 2')
                self.epics_pvs['Focus2Motor'].put(focus2_pos2, wait=True, timeout=120)
                self.epics_pvs['Focus2Lock'].put(0, wait=True)
                self.epics_pvs['LensLock'].put(0, wait=True)
                self.epics_pvs['MCTStatus'].put('Lens 2 focus is locked: SET NEW LENS NAME')

            log.info('Focus2: %s selected', focus2_name)
        else:
            self.epics_pvs['MCTStatus'].put('Lens 2 focus is locked: SET NEW LENS NAME')
            self.epics_pvs['Focus2Select'].put(2)
            log.error('Changing Optique Peter focus2: Locked')

    def exposure_time(self):
        """
        update exposure time values for both detector and tomoscan
        """
        exp_time = self.epics_pvs['ExposureTime'].get()
        self.epics_pvs['CamAcquireTime'].put(exp_time, wait=True)
        self.epics_pvs['TSExposureTime'].put(exp_time, wait=True)
