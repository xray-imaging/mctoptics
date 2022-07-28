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
        
        if not isinstance(pv_files, list):
            pv_files = [pv_files]
        for pv_file in pv_files:
            self.read_pv_file(pv_file, macros)
        self.show_pvs()

        #Define PVs we will need from the sample x-y-z motors, which is on another IOC

        lens_sample_x_pv_name = self.control_pvs['LensSampleX'].pvname
        self.control_pvs['LensSampleXPosition']      = PV(lens_sample_x_pv_name + '.VAL')
        lens_sample_y_pv_name = self.control_pvs['LensSampleY'].pvname
        self.control_pvs['LensSampleYPosition']      = PV(lens_sample_y_pv_name + '.VAL')
        lens_sample_z_pv_name = self.control_pvs['LensSampleZ'].pvname
        self.control_pvs['LensSampleZPosition']      = PV(lens_sample_z_pv_name + '.VAL')

        camera0_rotation_pv_name = self.control_pvs['Camera0Rotation'].pvname
        self.control_pvs['Camera0RotationPosition']  = PV(camera0_rotation_pv_name + '.VAL')

        camera1_rotation_pv_name = self.control_pvs['Camera1Rotation'].pvname
        self.control_pvs['Camera1RotationPosition']  = PV(camera1_rotation_pv_name + '.VAL')

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

        ########################### VN
        # shall we run a sync() here?
        self.lens_cur = self.epics_pvs['LensSelect'].get()
        ########################### VN
        
        # print(self.epics_pvs)
        for epics_pv in ('LensSelect', 'CameraSelect', 'CrossSelect', 'Sync', 'Crop'):
            self.epics_pvs[epics_pv].add_callback(self.pv_callback)
        for epics_pv in ('Sync',):
            self.epics_pvs[epics_pv].put(0)

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
        elif (pvname.find('Sync') != -1) and (value == 1):
            thread = threading.Thread(target=self.sync, args=())
            thread.start()
        elif (pvname.find('Crop') != -1) and (value ==1):
            thread = threading.Thread(target=self.crop_detector, args=())
            thread.start()    

    def take_lens_offsets(self, lens):
        if lens == 0:
            return 0,0,0
        x = self.epics_pvs['Lens'+str(lens)+'XOffset'].get()
        y = self.epics_pvs['Lens'+str(lens)+'YOffset'].get()
        z = self.epics_pvs['Lens'+str(lens)+'ZOffset'].get()
        return x,y,z


    def take_camera_offsets(self, lens):

        cam = self.epics_pvs['CameraSelect'].get()
        return self.epics_pvs['Camera'+str(cam)+'Lens'+str(lens)+'Rotation'].get()


    def lens_select(self):
        """Moves the Optique Peter lens.
        """

        # take offsets of the current lens
        x_cur,y_cur,z_cur = self.take_lens_offsets(self.lens_cur)            
        # take new lens id, and its offsets
        lens_select = self.epics_pvs['LensSelect'].get()
        x_select,y_select,z_select = self.take_lens_offsets(lens_select)
        # take camera id and its rotation for the new lens
        cam = self.epics_pvs['CameraSelect'].get()
        camera_rotation = self.take_camera_offsets(lens_select)        
        # update current lens
        self.lens_cur = lens_select

        # move x,y,z motors to wrt relative offsets        
        x = self.epics_pvs['LensSampleXPosition'].get()
        y = self.epics_pvs['LensSampleYPosition'].get()
        z = self.epics_pvs['LensSampleZPosition'].get()
        x_new = x + x_select - x_cur
        y_new = y + y_select - y_cur
        z_new = z + z_select - z_cur
        log.info('move X from %f to %f', x, x_new)
        log.info('move Y from %f to %f', y, y_new)
        log.info('move Z from %f to %f', z, z_new)
        log.info('move camera %s rotation to %f' %(cam, camera_rotation))        
        self.epics_pvs['LensSampleXPosition'].put(x_new)
        self.epics_pvs['LensSampleYPosition'].put(y_new)
        self.epics_pvs['LensSampleZPosition'].put(z_new)
        self.epics_pvs['Camera'+str(cam)+'RotationPosition'].put(camera_rotation) # no wait, assuming the lens movement is the slowest part

        
        lens_pos0 = self.epics_pvs['LensPos0'].get()
        lens_pos1 = self.epics_pvs['LensPos1'].get()
        lens_pos2 = self.epics_pvs['LensPos2'].get()

        lens_select = self.epics_pvs['LensSelect'].get()
        lens_name = 'None'

        log.info('Changing Optique Peter lens')

        lens_positions = [lens_pos0, lens_pos1,lens_pos2]

        lens_index = self.epics_pvs['LensSelect'].get()
        lens_name  = self.epics_pvs['Lens' + str(lens_index) + 'Name'].get()
        self.epics_pvs['MCTStatus'].put('Moving to lens: ' + lens_name)
        self.epics_pvs['LensMotor'].put(lens_positions[lens_index], wait=True, timeout=120)

        message = 'Lens selected: ' + lens_name
        log.info(message)
        self.epics_pvs['MCTStatus'].put(message)

        lens_name = lens_name.upper().replace("X", "")
        with open(os.path.join(data_path, 'lens.json')) as json_file:
            lens_lookup = json.load(json_file)
        
        try:

            magnification          = str(lens_lookup[lens_name]['magnification'])
            tube_lens              = lens_lookup[lens_name]['tube_lens']

            # update tomoScan PVs
            self.epics_pvs['CameraObjective'].put(magnification)
            self.epics_pvs['CameraTubeLength'].put(tube_lens)

            detector_pixel_size    = self.epics_pvs['DetectorPixelSize'].get()
            image_pixel_size       = float(detector_pixel_size)/float(magnification)
            self.epics_pvs['ImagePixelSize'].put(image_pixel_size)
        except KeyError as e:
            log.error('Lens called %s is not defined. Please add it to the /data/lens.json file' % e)
            log.error('Failed to update: Camera objective')
            log.error('Failed to update: Camera tube length')
            log.error('Failed to update: Image pixel size')

        with open(os.path.join(data_path, 'scintillator.json')) as json_file:
            scintillator_lookup = json.load(json_file)

        try:           
            scintillator_type      = scintillator_lookup[str(lens_index)]['scintillator_type']
            scintillator_thickness = scintillator_lookup[str(lens_index)]['scintillator_thickness']
            self.epics_pvs['ScintillatorType'].put(scintillator_type)
            self.epics_pvs['ScintillatorThickness'].put(scintillator_thickness)
        except KeyError as e:
            log.error('Scintillator called %s is not defined. Please add it to the /data/scintillator.json file' % e)
            log.error('Failed to update: Scintillator type')
            log.error('Failed to update: Scintillator thickness')
        
    def camera_select(self):
        """Moves the Optique Peter camera.
        """
        
        camera_pos0 = self.epics_pvs['CameraPos0'].get()
        camera_pos1 = self.epics_pvs['CameraPos1'].get()

        camera_select = self.epics_pvs['CameraSelect'].get()
        camera_name = 'None'

        log.info('Changing Optique Peter camera')
        self.epics_pvs['MCTStatus'].put('Changing Optique Peter camera')

        if(self.epics_pvs['CameraSelect'].get() == 0):
            camera_name = self.epics_pvs['Camera0Name'].get()
            self.epics_pvs['MCTStatus'].put('Camera selected: 0')
            self.epics_pvs['CameraMotor'].put(camera_pos0, wait=True, timeout=120)
        elif(self.epics_pvs['CameraSelect'].get() == 1):
            camera_name = self.epics_pvs['Camera1Name'].get()
            self.epics_pvs['MCTStatus'].put('Camera selected: 1')
            self.epics_pvs['CameraMotor'].put(camera_pos1, wait=True, timeout=120)
        log.info('Camera: %s selected', camera_name)

        camera_name = camera_name.upper()
        with open(os.path.join(data_path, 'camera.json')) as json_file:
            camera_lookup = json.load(json_file)

        try:
            detector_pixel_size = camera_lookup[camera_name]['detector_pixel_size']
            # update tomoScan PVs
            self.epics_pvs['DetectorPixelSize'].put(detector_pixel_size)

            magnification = self.epics_pvs['CameraObjective'].get()
            magnification = magnification.upper().replace("X", "") # just in case there was a manual entry ...
            image_pixel_size = float(detector_pixel_size)/float(magnification)
            self.epics_pvs['ImagePixelSize'].put(image_pixel_size)
        except KeyError as e:
            log.error('Camera called %s is not defined. Please add it to the /data/camera.json file' % e)
            log.error('Failed to update: Detector pixel size')
            log.error('Failed to update: Image pixel size')

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

    def sync(self):
        """
        sync the optique peter selector with the actual motor positon
        """

        self.epics_pvs['MCTStatus'].put('Sync in progress')

        log.info('Sync camera')
        camera_pos0 = self.epics_pvs['CameraPos0'].get()
        camera_pos1 = self.epics_pvs['CameraPos1'].get()
        camera_motor_position = self.epics_pvs['CameraMotor'].get()

        is_camera_pos0 = np.isclose(camera_motor_position, camera_pos0, atol=1e-01)
        is_camera_pos1 = np.isclose(camera_motor_position, camera_pos1, atol=1e-01)

        log.info('Camera motor positon %s:',  camera_motor_position)
        log.info('Pos 0 %s: %s',  camera_pos0, is_camera_pos0)
        log.info('Pos 1 %s: %s',  camera_pos1, is_camera_pos1)

        if is_camera_pos0:
            camera_select_sync = 0
        elif is_camera_pos1:
            camera_select_sync = 1
        else:
            camera_select_sync = -1
            log.error('Sync camera failed: check camera select motor position')

        camera_select = self.epics_pvs['CameraSelect'].get()
        if camera_select != camera_select_sync:
            self.epics_pvs['CameraSelect'].put(camera_select_sync)
            log.warning('Sync camera: done')
        else:
            log.warning('Sync camera: not required, selector is already in the correct position')

        log.info('Sync lens')
        lens_pos0 = self.epics_pvs['LensPos0'].get()
        lens_pos1 = self.epics_pvs['LensPos1'].get()
        lens_pos2 = self.epics_pvs['LensPos2'].get()
        lens_motor_position = self.epics_pvs['LensMotor'].get()

        is_lens_pos0 = np.isclose(lens_motor_position, lens_pos0, atol=1e-01)
        is_lens_pos1 = np.isclose(lens_motor_position, lens_pos1, atol=1e-01)
        is_lens_pos2 = np.isclose(lens_motor_position, lens_pos2, atol=1e-01)

        log.info('Lens motor positon %s:',  lens_motor_position)
        log.info('Lens 0 %s: %s',  lens_pos0, is_lens_pos0)
        log.info('Lens 1 %s: %s',  lens_pos1, is_lens_pos1)
        log.info('Lens 2 %s: %s',  lens_pos2, is_lens_pos2)

        if is_lens_pos0:
            lens_select_sync = 0
        elif is_lens_pos1:
            lens_select_sync = 1
        elif is_lens_pos2:
            lens_select_sync = 2
        else:
            lens_select_sync = -1
            log.error('Sync lens failed: check lens select motor position')

        lens_select = self.epics_pvs['LensSelect'].get()
        if ((lens_select != lens_select_sync) and (lens_select_sync != -1)):
            self.epics_pvs['LensSelect'].put(lens_select_sync)
            log.warning('Sync lens: done')
        else:
            log.warning('Sync lens: not required, selector is already in the correct position')

        if((camera_select_sync == -1) or (lens_select_sync == -1)):
            self.epics_pvs['MCTStatus'].put('Sync error: check log for details')
        else:
            self.epics_pvs['MCTStatus'].put('Sync done!')
        self.epics_pvs['Sync'].put('Done')

    def crop_detector(self):
        """crop detector sizes"""
        state = self.epics_pvs['CamAcquire'].get()
        self.epics_pvs['CamAcquire'].put(0,wait=True)

        maxsizex = self.epics_pvs['CamMaxSizeXRBV'].get()
        self.epics_pvs['CamMinX'].put(0,wait=True)        
        
        maxsizey = self.epics_pvs['CamMaxSizeYRBV'].get()
        self.epics_pvs['CamMinY'].put(0,wait=True)        
        
        left = self.epics_pvs['CropLeft'].get()
        top = self.epics_pvs['CropTop'].get()
        
        right = self.epics_pvs['CropRight'].get()        
        self.epics_pvs['CamSizeX'].put(maxsizex-left-right,wait=True)
        sizex = self.epics_pvs['CamSizeXRBV'].get()
        right = maxsizex - left - sizex
        self.epics_pvs['CropRight'].put(right,wait=True)

        bottom = self.epics_pvs['CropBottom'].get()
        self.epics_pvs['CamSizeY'].put(maxsizey-top-bottom,wait=True)
        sizey = self.epics_pvs['CamSizeYRBV'].get()
        bottom = maxsizey - top - sizey
        self.epics_pvs['CropBottom'].put(bottom,wait=True)

        self.epics_pvs['CamMinX'].put(left,wait=True)        
        left = self.epics_pvs['CamMinXRBV'].get()
        self.epics_pvs['CropLeft'].put(left,wait=True)

        self.epics_pvs['CamMinY'].put(top,wait=True)        
        top = self.epics_pvs['CamMinYRBV'].get()
        self.epics_pvs['CropTop'].put(top,wait=True)                
    

        self.epics_pvs['CamAcquire'].put(state)  
        self.cross_select()      
        self.epics_pvs['Crop'].put(0,wait=True)  
