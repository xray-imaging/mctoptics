import time
import numpy as np


def interpolate_energy_config_files(fname0, fname1, n, select):

    interp_energies_dict = {}

    pos_energy_start = read_energy_config(fname0)
    pos_energy_end   = read_energy_config(fname1)
    energies = merge(pos_energy_start, pos_energy_end)

    keys = list(energies.keys())
    interp_energies                 = np.linspace(float(keys[0]), float(keys[1]), n)
    interp_mirror_angle             = np.linspace(float(energies[keys[0]]['mirror-angle']),             float(energies[keys[1]]['mirror-angle']), n)
    interp_mirror_vertical_position = np.linspace(float(energies[keys[0]]['mirror-vertical-position']), float(energies[keys[1]]['mirror-vertical-position']), n)
    interp_dmm_usy_ob               = np.linspace(float(energies[keys[0]]['dmm-usy-ob']),               float(energies[keys[1]]['dmm-usy-ob']), n)
    interp_dmm_usy_ib               = np.linspace(float(energies[keys[0]]['dmm-usy-ib']),               float(energies[keys[1]]['dmm-usy-ib']), n)
    interp_dmm_dsy                  = np.linspace(float(energies[keys[0]]['dmm-dsy']),                  float(energies[keys[1]]['dmm-dsy']), n) 
    interp_dmm_us_arm               = np.linspace(float(energies[keys[0]]['dmm-us-arm']),               float(energies[keys[1]]['dmm-us-arm']), n)
    interp_dmm_ds_arm               = np.linspace(float(energies[keys[0]]['dmm-ds-arm']),               float(energies[keys[1]]['dmm-ds-arm']), n)
    interp_dmm_m2y                  = np.linspace(float(energies[keys[0]]['dmm-m2y']),                  float(energies[keys[1]]['dmm-m2y']), n)
    interp_dmm_usx                  = np.linspace(float(energies[keys[0]]['dmm-usx']),                  float(energies[keys[1]]['dmm-usx']), n)
    interp_dmm_dsx                  = np.linspace(float(energies[keys[0]]['dmm-dsx']),                  float(energies[keys[1]]['dmm-dsx']), n)
    interp_table_y                  = np.linspace(float(energies[keys[0]]['table-y']),                  float(energies[keys[1]]['table-y']), n)
    interp_flag                     = np.linspace(float(energies[keys[0]]['flag']),                     float(energies[keys[1]]['flag']), n) 
                 
    i = 0
    for energy in interp_energies:
        temp_dict = {}
        temp_dict['mirror-angle']             =  interp_mirror_angle[i]
        temp_dict['mirror-vertical-position'] =  interp_mirror_vertical_position[i]
        temp_dict['dmm-usy-ob']               =  interp_dmm_usy_ob[i]
        temp_dict['dmm-usy-ib']               =  interp_dmm_usy_ib[i]
        temp_dict['dmm-dsy']                  =  interp_dmm_dsy[i]
        temp_dict['dmm-us-arm']               =  interp_dmm_us_arm[i]
        temp_dict['dmm-ds-arm']               =  interp_dmm_ds_arm[i]
        temp_dict['dmm-m2y']                  =  interp_dmm_m2y[i]
        temp_dict['dmm-usx']                  =  interp_dmm_usx[i]
        temp_dict['dmm-dsx']                  =  interp_dmm_dsx[i]
        temp_dict['table-y']                  =  interp_table_y[i]
        temp_dict['flag']                     =  interp_flag[i]

        interp_energies_dict[str(energy)]     = temp_dict

        i += 1

    return interp_energies_dict

def save_energy_config(file_name, energy, pos_energy):   
    
    with open(file_name, 'w') as f:
        f.write('[general]\n')
        f.write('logs-home = /home/beams/USER2BMB/logs\n')
        f.write('verbose = False\n')
        f.write('testing = False\n')
        f.write('\n')
        f.write('[energy]\n')
        f.write('energy-value = %s\n' % energy)
        f.write('mode = Mono\n')
        f.write('\n')
        f.write('[mirror-vertical-positions]\n')
        f.write('mirror-angle = %s\n' % pos_energy['mirror-angle'])
        f.write('mirror-vertical-position = %s\n' % pos_energy['mirror-vertical-position'])
        f.write('\n')
        f.write('[dmm-motor-positions]\n')
        f.write('dmm-usy-ob = %s\n' % pos_energy['dmm-usy-ob'])
        f.write('dmm-usy-ib = %s\n' % pos_energy['dmm-usy-ib'])
        f.write('dmm-dsy = %s\n' % pos_energy['dmm-dsy'])
        f.write('dmm-us-arm = %s\n' % pos_energy['dmm-us-arm'])
        f.write('dmm-ds-arm = %s\n' % pos_energy['dmm-ds-arm'])
        f.write('dmm-m2y = %s\n' % pos_energy['dmm-m2y'])
        f.write('dmm-usx = %s\n' % pos_energy['dmm-usx'])
        f.write('dmm-dsx = %s\n' % pos_energy['dmm-dsx'])
        f.write('\n')
        f.write('[filter-selector]\n')
        f.write('filter = 4\n')
        f.write('\n')
        f.write('[tabley-flag]\n')
        f.write('table-y = %s\n' % pos_energy['table-y'])
        f.write('flag = %s\n' % pos_energy['flag'])
        f.write('\n')
        f.write('[energyioc]\n')
        f.write('energyioc-prefix = 2bm:MCTOptics:\n')

def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def read_energy_config(file_name):   
    
    energy_dict = {}
    energy      = {}

    with open(file_name) as f:
        for line in f:
            if line.find('=') != -1:
                words = line.split('=')
                if words[0].strip() == 'energy-value':
                    key = words[1].strip()
                else:    
                    energy[words[0].strip()] = words[1].strip()
        energy_dict[key] = energy
    
    return energy_dict

def tic():
    #Homemade version of matlab tic and toc functions
    global startTime_for_tictoc
    startTime_for_tictoc = time.time()

def toc():
    if 'startTime_for_tictoc' in globals():
       return time.time() - startTime_for_tictoc

type_dict = {
'uint8': 'ubyteValue',
'float32': 'floatValue',
'uint16' : 'ushortValue'
# add others
}

def positive_int(value):
    """Convert *value* to an integer and make sure it is positive."""
    result = int(value)
    if result < 0:
        raise argparse.ArgumentTypeError('Only positive integers are allowed')

    return result

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    value = "{0:4.2f}".format(array[idx])

    return value