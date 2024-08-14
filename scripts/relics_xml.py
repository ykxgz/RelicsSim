#!/usr/bin/python3
import os
import argparse
import json
import copy
from xml.dom.minidom import Document

import numpy as np

from arrangement import PMTArrangement, TankArrangement

parser = argparse.ArgumentParser(description='Automatically relics .xml geometry generator')

parser.add_argument('ipt',
                    action='store',
                    help='Input .json file, containing geometry parameters')
parser.add_argument('-o', dest='opt',
                    action='store', required=True,
                    help='Output .xml file name')
parser.add_argument('--run_number', dest='run_number',
                    action='store', default='0',
                    help='Run number in .xml file')
parser.add_argument('--gen', dest='generator',
                    choices=['muon', 'neutron', 'gamma', 'material'],
                    action='store', default='muon',
                    help='Generator used')
parser.add_argument('--cutlength', dest='cutlength', type=float,
                    action='store', default=0.1,  # in mm
                    help='Cut length used in simulation')
parser.add_argument('--enable_track', action='store_true',
                    help='Enable track of surface flux')
parser.add_argument('--force_sd', action='store_true',
                    help='Force all solid sensitive detector')
parser.add_argument('--check_overlap', action='store_true',
                    help='Whether check overlap of volumes')
parser.add_argument('--get_geo_mass', action='store_true',
                    help='Whether print geometry mass')
parser.add_argument('--save_txt', action='store_true',
                    help='Whether save .txt files of position')
parser.add_argument('--optical', action='store_true',
                    help='Whether do optical simulation')

args = parser.parse_args()

number = args.run_number
fipt = args.ipt
fopt = args.opt
gen = args.generator
cutlength = args.cutlength
enable_track = args.enable_track
force_sd = args.force_sd
check_overlap = args.check_overlap
get_geo_mass = args.get_geo_mass
save_txt = args.save_txt
optical = args.optical

with open(fipt) as f:
    params = json.load(f)

# Xenon detector radius
inn_lxe_r = params['inn_lxe_r']
assert inn_lxe_r >= 0
# Xenon detector height
inn_lxe_h = params['inn_lxe_h']
assert inn_lxe_h >= 0
# Xenon detector polygon edges
teflon_n = params['teflon_n']
assert teflon_n >= 0
# Inner gas xenon height
inn_gxe_h = params['inn_gxe_h']
assert inn_gxe_h >= 0
# PMT case to LXe veto
pmt_gxe_h = params['pmt_gxe_h']
assert pmt_gxe_h >= 0
# Xenon veto thickness
xe_veto_top = params['xe_veto_top']
assert xe_veto_top >= 0
xe_veto_side = params['xe_veto_side']
assert xe_veto_side >= 0
xe_veto_bot = params['xe_veto_bot']
assert xe_veto_bot >= 0
# Outer gas xenon height
out_gxe_h = params['out_gxe_h']
assert out_gxe_h >= 0
# Thickness of Teflon coating
teflon_coat = params['teflon_coat']
assert teflon_coat >= 0
# Width of shaping ring
copper_ring = params['copper_ring']
assert copper_ring >= 0
# Hole in bell top vessel
pmt_hole = params['pmt_hole']
assert pmt_hole >= 0
# Stainless steel thickness
ss_vessel = params['ss_vessel']
assert ss_vessel >= 0
# Vacuum thickness
vacuum = params['vacuum']
assert vacuum >= 0
# Copper shield thickness
copper = params['copper']
assert copper >= 0
# Inner PE shield thickness
inn_pe = params['inn_pe']
assert inn_pe >= 0
# Lead shield thickness
lead = params['lead']
assert lead >= 0
# Inner PE shield thickness
out_pe = params['out_pe']
assert out_pe >= 0
# Height of flange
flange_height = params['flange_height']
assert flange_height >= 0
# Width of flange
flange_width = params['flange_width']
assert flange_width >= 0
# Flange upper edge to welding of container lid and cylinder barrel
flange_to_welding = params['flange_to_welding']
assert flange_to_welding >= 0
# Bottom Screening to PMT window
bot_screen_to_window = params['bot_screen_to_window']
assert bot_screen_to_window >= 0
# Top Screening to PMT window
top_screen_to_window = params['top_screen_to_window']
assert top_screen_to_window >= 0
# Cathode to Bottom Screening
cathode_to_screen = params['cathode_to_screen']
assert cathode_to_screen >= 0
# Gate to liquid-gas surface
gate_to_surface = params['gate_to_surface']
assert gate_to_surface >= 0
# Anode to liquid-gas surface
anode_to_surface = params['anode_to_surface']
assert anode_to_surface >= 0
# Height of electrodes rings
ring_height = params['ring_height']
assert ring_height >= 0
# The thickness of the water tank’s iron
fe = params['fe']
assert fe >= 0
# The thickness of the water above the center of the detector
water_high = params['water_high']
assert water_high >= 0
# The thickness of the water below the center of the detector
water_low = params['water_low']
assert water_low >= 0
# The water thickness of the detector center facing the reactor
water_on = params['water_on']
assert water_on >= 0
# The detector center does not face the water thickness of the reactor
water_off = params['water_off']
assert water_off >= 0
# Bottom concrete thickness
concrete_high = params['concrete_high']
assert concrete_high >= 0
# Thickness of plastic
PE_th = params['PE_th']
assert PE_th >= 0

if optical:
    physics_name = 'RelicsOpticalPhysics'
    generator_name = 'ConfineGenerator'
    analysis_name = 'RelicsOpticalAnalysis'

    LXesd = False
    PMTsd = True
    opticalsd = True
    seed = int(number)

    # Input here the user specified material properties
    materialList = {'LXe_SCINTILLATIONYIELD' :  '3000000.'}  # per MeV

    analysisList = {'EnableEnergyDeposition' : 0,
                    'EnablePrimaryParticle' : 1,
                    'SaveNullEvents' : 1,
                    'OpticalSdName' : 'bR8520',
                    'UserSeed' : f'{seed}',
                    'GetGeoMass' : int(get_geo_mass)}

    pmt_opsurface = {
        'base_type' : 'dielectric_metal',  # should change to 'dielectric_dielectric' later?
        'casing_finish' : 'polished',
        'casing_type' : 'dielectric_metal',
        'window_partner' : 'parent',
        'window_finish' : 'polished',
        'window_order' : str(1),
        'photocathode_finish' : 'polished'
    }
    surface = True
else:
    physics_name = 'PandaXPhysics'
    if gen == 'muon':
        generator_name = 'MuonGenerator'
    elif gen == 'neutron' or gen == 'gamma':
        generator_name = 'SimpleGPSGenerator'
    elif gen == 'material':
        generator_name = 'ConfineGenerator'
    analysis_name = 'PandaXAnalysis'

    LXesd = True
    Plasticsd = True
    PMTsd = False
    opticalsd = False
    seed = 0

    materialList = dict()

    analysisList = {'EnableEnergyDeposition' : 1,
                    'EnableSurfaceFlux' : int(enable_track),
                    'EnablePrimaryParticle' : 1,
                    'SaveNullEvents' : 0,
                    'EnableDecayChainSplitting' : 1,
                    'ChainSplittingLifeTime' : '400*us',
                    'UserSeed' : f'{seed}',
                    'GetGeoMass' : int(get_geo_mass)}

    pmt_opsurface = dict()
    surface = False

inn_gxe_r = inn_lxe_r
out_lxe_r = inn_lxe_r + xe_veto_side
out_ptfe_r = out_lxe_r + teflon_coat
out_lxe_h = inn_lxe_h + inn_gxe_h + xe_veto_top + xe_veto_bot
out_gxe_r = out_lxe_r
inn_ss_r = out_ptfe_r + ss_vessel
inn_ss_h = out_lxe_h + out_gxe_h + 2 * ss_vessel
vacuum_r = inn_ss_r + vacuum
out_ss_r = vacuum_r + ss_vessel

doc = Document()
djson = dict()

root = doc.createElement('BambooMC')
doc.appendChild(root)

run = doc.createElement('run')
run.setAttribute('number', number)
root.appendChild(run)
djson['run'] = int(number)

geometry = doc.createElement('geometry')
root.appendChild(geometry)
djson['geometry'] = dict()

material = doc.createElement('material')
geometry.appendChild(material)
djson['geometry']['material'] = dict()
material.setAttribute('name', 'Material')
djson['geometry']['material'].update({'name': 'Material'})

if len(list(materialList.keys())) > 0:
    djson['geometry']['material'].update({'parameters': dict()})
for k in materialList.keys():
    parameter = doc.createElement('parameter')
    material.appendChild(parameter)
    parameter.setAttribute('name', k)
    parameter.setAttribute('value', f'{materialList[k]}')
    djson['geometry']['material']['parameters'].update({k: materialList[k]})

detector = doc.createElement('detector')
geometry.appendChild(detector)
djson['geometry']['detectors'] = []

detector.setAttribute('type', 'World')
detector.setAttribute('name', 'World')
djson['geometry']['detectors'].append(dict())
djson['geometry']['detectors'][-1].update({'type': 'World'})
djson['geometry']['detectors'][-1].update({'name': 'World'})

Cuboid = 'Cuboid'
Cylinder = 'Cylinder'
Prism = 'Prism'
Polyhedra = 'Polyhedra'
HolesBoard = 'HolesBoard'
Array = 'Array'
PMTs = 'PMTsR8520'
LXe = 'LXe'
GXe = 'GXe'
Teflon = 'Teflon'
XenonVeto = 'XenonVeto'
XenonDetector = 'XenonDetector'
SS304LSteel = 'SS304LSteel'
concrete = 'concrete'
topPMTs = 'data/topPMTs.txt'
botPMTs = 'data/botPMTs.txt'
downtopVetoPMTs = 'data/downtopVetoPMTs.txt'
upbotVetoPMTs = 'data/upbotVetoPMTs.txt'
midtopVetoPMTs = 'data/midtopVetoPMTs.txt'
midbotVetoPMTs = 'data/midbotVetoPMTs.txt'
XeVetoInBell = 'data/XeVetoInBell.txt'
OuterContainerRZ = 'data/OuterContainerRZ.txt'
VacuumRZ = 'data/VacuumRZ.txt'
InnerContainerRZ = 'data/InnerContainerRZ.txt'
InnerTeflonRZ = 'data/InnerTeflonRZ.txt'
OuterGasXeRZ = 'data/OuterGasXeRZ.txt'
XenonVetoRZ = 'data/XenonVetoRZ.txt'
XeInTopPMTTeflon = 'data/XeInTopPMTTeflon.txt'
XeInBotPMTTeflon = 'data/XeInBotPMTTeflon.txt'

# PMT No. starts from 0
count_pmt = 0

top = PMTArrangement(inn_gxe_r, inn_gxe_h - 2 * pmt_gxe_h, top=True)
top.circular()
if save_txt:
    top.save(topPMTs, minN=count_pmt)
count_pmt += top.N
top_pmt_surface = top.z.min() - top.pmth / 2
top_teflon_offset = top_pmt_surface - teflon_coat / 2
top.z = np.zeros(top.N)
if save_txt:
    top.save(XeInTopPMTTeflon)

bot = PMTArrangement(inn_lxe_r, inn_lxe_h, top=False)
# bot.rectangular()
bot.circular()
if save_txt:
    bot.save(botPMTs, minN=count_pmt)
count_pmt += bot.N
bot_pmt_surface = bot.z.max() + bot.pmth / 2
bot_teflon_offset = bot_pmt_surface + teflon_coat / 2
bot.z = np.zeros(bot.N)
if save_txt:
    bot.save(XeInBotPMTTeflon)

# Top PMTs look down
downtopveto = PMTArrangement(out_lxe_r, out_lxe_h, top=True)
downtopveto.veto(rotY=False)
if save_txt:
    downtopveto.save(downtopVetoPMTs, minN=count_pmt)
count_pmt += downtopveto.N
downtopveto.z = np.zeros(downtopveto.N)
if save_txt:
    downtopveto.save(XeVetoInBell)

# Bottom PMTs look up
upbotveto = PMTArrangement(out_lxe_r, out_lxe_h, top=False)
upbotveto.veto(rotY=False)
if save_txt:
    upbotveto.save(upbotVetoPMTs, minN=count_pmt)
count_pmt += upbotveto.N

# Top PMTs look centripetally
midtopveto = PMTArrangement(out_lxe_r, out_lxe_h, top=True)
midtopveto.veto(rotY=True)
if save_txt:
    midtopveto.save(midtopVetoPMTs, minN=count_pmt)
count_pmt += midtopveto.N

# Bottom PMTs look centripetally
midbotveto = PMTArrangement(out_lxe_r, out_lxe_h, top=False)
midbotveto.veto(rotY=True)
if save_txt:
    midbotveto.save(midbotVetoPMTs, minN=count_pmt)
count_pmt += midbotveto.N

thickness = [0, teflon_coat, teflon_coat + ss_vessel, teflon_coat + ss_vessel + vacuum, teflon_coat + 2 * ss_vessel + vacuum]
tank = TankArrangement(out_lxe_r, out_lxe_h + out_gxe_h, thickness)
tank.getTankOutline()
flange_height
flange_width
flange_to_welding
if save_txt:
    tank.save(OuterContainerRZ, 4,
            flange_height=flange_height,
            flange_width=flange_width,
            flange_to_welding=flange_to_welding)
    tank.save(VacuumRZ, 3)
    tank.save(InnerContainerRZ, 2,
            flange_height=flange_height,
            flange_width=flange_width,
            flange_to_welding=flange_to_welding)
    tank.save(InnerTeflonRZ, 1)
    tank.save(OuterGasXeRZ, 0, shift_z=out_gxe_h/2, hight_cut=out_lxe_h/2, upward=True)
    tank.save(XenonVetoRZ, 0, shift_z=out_gxe_h/2, hight_cut=out_lxe_h/2, upward=False)

out_ss_h = tank.y.max()
air_x = (round((2 * out_ss_r) / 10) + 1) * 10
assert air_x > tank.x[4].max() + flange_width
assert flange_width < vacuum
air_z = (round((2 * out_ss_h) / 10) + 1) * 10

# water cuboid
water_x = water_on + water_off
water_y = 2 * water_off
water_z = water_high + water_low
water_shift_z = (water_low - water_high) / 2
water_shift_x = (water_off - water_on) / 2

# fe
fe_x = water_x + 2 * fe
fe_y = water_y + 2 * fe
fe_z = water_z + 2 * fe

# concrete
concrete_x = fe_x
concrete_y = fe_y
concrete_z = concrete_high
concrete_shift_z = - (fe_z + concrete_z) / 2

# plastic
plastic_x = 100 + 2 * PE_th
plastic_y = 100 + 2 * PE_th
plastic_z = 100 + 2 * PE_th

# water_in
water_in_x = 100
water_in_y = 100
water_in_z = 100

# copper_x = air_x + 2 * copper
# copper_z = air_z + 2 * copper
# inn_pe_x = copper_x + 2 * inn_pe
# inn_pe_z = copper_z + 2 * inn_pe
# lead_x = inn_pe_x + 2 * lead
# lead_z = inn_pe_z + 2 * lead
# out_pe_x = lead_x + 2 * out_pe
# out_pe_z = lead_z + 2 * out_pe
bell_ss_vessel = ss_vessel
teflon_panel_y = 2 * inn_lxe_r * np.tan(np.pi / teflon_n)

world_half_x = 500
# assert world_half_x >= out_pe_x / 2 * 1.5 and world_half_x >= out_pe_z / 2 * 1.5
djson['geometry']['detectors'][-1].update({'parameters': dict()})
for x in ['x', 'y', 'z']:
    parameter = doc.createElement('parameter')
    parameter.setAttribute('name', f'half_{x}')
    parameter.setAttribute('value', f'{world_half_x}*cm')
    detector.appendChild(parameter)
    djson['geometry']['detectors'][-1]['parameters'].update({f'half_{x}': f'{world_half_x}*cm'})

def dict_merger(dict_a, dict_b):
    dict_c = copy.deepcopy(dict_a)
    dict_c.update(dict_b)
    return dict_c

surface_shift_z = (inn_lxe_h - inn_gxe_h) / 2 + (xe_veto_bot - xe_veto_top) / 2
xenon_detector_shift_z = -inn_gxe_h / 2 + (xe_veto_bot - xe_veto_top) / 2
inner_gas_shift_z = inn_lxe_h / 2 + (xe_veto_bot - xe_veto_top) / 2

# length unit is cm
detectorList = [{'type' : Cuboid, 
                 'name' : 'Fe',
                 'parent' : 'World',
                 'parameters' : {'width_x' : fe_x,
                                 'width_y' : fe_y,
                                 'width_z' : fe_z,
                                 'material' : SS304LSteel}},
                {'type' : Cuboid, 
                 'name' : 'Concrete',
                 'parent' : 'World',
                 'parameters' : {'width_x' : concrete_x,
                                 'width_y' : concrete_y,
                                 'width_z' : concrete_z,
                                 'material' : concrete,
                                 'shift_z' : concrete_shift_z}},
                {'type' : Cuboid, 
                 'name' : 'Water',
                 'parent' : 'Fe',
                 'parameters' : {'width_x' : water_x,
                                 'width_y' : water_y,
                                 'width_z' : water_z,
                                 'material' : 'G4_WATER'}},
                {'type' : Cuboid, 
                 'name' : 'Plastic',
                 'parent' : 'Water',
                 'parameters' : {'width_x' : plastic_x,
                                 'width_y' : plastic_y,
                                 'width_z' : plastic_z,
                                 'material' : 'G4_POLYETHYLENE',
                                 'shift_x' : water_shift_x,
                                 'shift_z' : water_shift_z},
                'sd' : Plasticsd},
                {'type' : Cuboid, 
                 'name' : 'Water_in',
                 'parent' : 'Plastic',
                 'parameters' : {'width_x' : water_in_x,
                                 'width_y' : water_in_y,
                                 'width_z' : water_in_z,
                                 'material' : 'G4_WATER'}},
                {'type' : Polyhedra, 
                 'name' : 'OuterContainer',
                 'parent' : 'Water_in',
                 'parameters' : {'source' : OuterContainerRZ,
                                 'material' : SS304LSteel}},
                {'type' : Polyhedra, 
                 'name' : 'Vacuum',
                 'parent' : 'OuterContainer',
                 'parameters' : {'source' : VacuumRZ,
                                 'material' : 'Vacuum'}},
                {'type' : Polyhedra, 
                 'name' : 'InnerContainer',
                 'parent' : 'Vacuum',
                 'parameters' : {'source' : InnerContainerRZ,
                                 'material' : SS304LSteel}},
                {'type' : Polyhedra, 
                 'name' : 'InnerTeflon',
                 'parent' : 'InnerContainer',
                 'parameters' : {'source' : InnerTeflonRZ,
                                 'material' : Teflon,
                                 'surface' : surface}},
                {'type' : Polyhedra, 
                 'name' : 'OuterGasXe',
                 'parent' : 'InnerTeflon',
                 'parameters' : {'source' : OuterGasXeRZ,
                                 'material' : GXe,
                                 'shift_z' : -out_gxe_h/2}},
                {'type' : Polyhedra, 
                 'name' : XenonVeto,
                 'parent' : 'InnerTeflon',
                 'parameters' : {'source' : XenonVetoRZ,
                                 'material' : LXe,
                                 'shift_z' : -out_gxe_h/2},
                 'sd' : LXesd},
                {'type' : HolesBoard, 
                 'name' : 'BellSS',
                 'parent' : XenonVeto,
                 'parameters' : {'radius' : out_lxe_r,
                                 'height' : bell_ss_vessel,
                                 'width_x' : pmt_hole,
                                 'sides': '0',
                                 'material' : SS304LSteel,
                                 'shift_z' : (out_lxe_h + bell_ss_vessel) / 2 - xe_veto_top + teflon_coat,
                                 'source' : XeVetoInBell,
                                 'surface' : surface,
                                 'type' : 'dielectric_metal'}},
                {'type' : HolesBoard, 
                 'name' : 'BellTeflonTopCoating',
                 'parent' : XenonVeto,
                 'parameters' : {'radius' : out_lxe_r,
                                 'height' : teflon_coat,
                                 'width_x' : pmt_hole,
                                 'sides': '0',
                                 'material' : Teflon,
                                 'shift_z' : (out_lxe_h + teflon_coat) / 2 - xe_veto_top,
                                 'source' : XeVetoInBell,
                                 'surface' : surface}},
                {'type' : HolesBoard, 
                 'name' : 'BellTeflonBotCoating',
                 'parent' : XenonVeto,
                 'parameters' : {'radius' : out_lxe_r,
                                 'height' : teflon_coat,
                                 'width_x' : pmt_hole,
                                 'sides': '0',
                                 'material' : Teflon,
                                 'shift_z' : out_lxe_h / 2 - xe_veto_top + bell_ss_vessel + 3 / 2 * teflon_coat,
                                 'source' : XeVetoInBell,
                                 'surface' : surface}},
                {'type' : Prism, 
                 'name' : 'InnerGasXe',
                 'parent' : XenonVeto,
                 'parameters' : {'outer_radius' : inn_gxe_r,
                                 'sides': str(teflon_n),
                                 'height' : inn_gxe_h,
                                 'material' : GXe,
                                 'shift_z' : inner_gas_shift_z}},
                {'type' : Prism, 
                 'name' : XenonDetector,
                 'parent' : XenonVeto,
                 'parameters' : {'outer_radius' : inn_lxe_r,
                                 'sides': str(teflon_n),
                                 'height' : inn_lxe_h,
                                 'material' : LXe,
                                 'shift_z' : xenon_detector_shift_z},
                 'sd' : LXesd},
                {'type' : Prism, 
                 'name' : 'BotTeflonCoating',
                 'parent' : XenonVeto,
                 'parameters' : {'outer_radius' : inn_lxe_r,
                                 'sides': str(teflon_n),
                                 'height' : teflon_coat,
                                 'material' : Teflon,
                                 'shift_z' : -(inn_lxe_h + inn_gxe_h + teflon_coat) / 2 + (xe_veto_bot - xe_veto_top) / 2,
                                 'surface' : surface}},
                {'type' : HolesBoard, 
                 'name' : 'TopPMTTeflon',
                 'parent' : 'InnerGasXe',
                 'parameters' : {'radius' : inn_lxe_r,
                                 'sides': str(teflon_n),
                                 'height' : teflon_coat,
                                 'width_x' : pmt_hole,
                                 'material' : Teflon,
                                 'shift_z' : top_teflon_offset,
                                 'source' : XeInTopPMTTeflon,
                                 'surface' : surface}},
                {'type' : HolesBoard, 
                 'name' : 'BotPMTTeflon',
                 'parent' : XenonDetector,
                 'parameters' : {'radius' : inn_lxe_r,
                                 'sides': str(teflon_n),
                                 'height' : teflon_coat,
                                 'width_x' : pmt_hole,
                                 'material' : Teflon,
                                 'shift_z' : bot_teflon_offset,
                                 'source' : XeInBotPMTTeflon,
                                 'surface' : surface}},
                {'type' : Array, 
                 'name' : 'tR8520',
                 'parent' : 'InnerGasXe',
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : topPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd},
                {'type' : Array, 
                 'name' : 'bR8520',
                 'parent' : XenonDetector,
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : botPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd},
                {'type' : Array, 
                 'name' : 'downtopvR8520',
                 'parent' : XenonVeto,
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : downtopVetoPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd},
                {'type' : Array, 
                 'name' : 'upbotvR8520',
                 'parent' : XenonVeto,
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : upbotVetoPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd},
                {'type' : Array, 
                 'name' : 'midtopvR8520',
                 'parent' : XenonVeto,
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : midtopVetoPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd},
                {'type' : Array, 
                 'name' : 'midbotvR8520',
                 'parent' : XenonVeto,
                 'parameters' : dict_merger({'objects' : PMTs,
                                            'physvol' : 'R8520',
                                            'source' : midbotVetoPMTs},
                                            pmt_opsurface),
                 'sd' : PMTsd,
                 'opticalsd' : opticalsd}]

electrodes = [
                {'name' : 'BottomScreening',
                 'parent' : XenonDetector,
                 'parameters' : {'shift_z': bot_pmt_surface + bot_screen_to_window,
                                 'wire_pitch': 1.0}},
                {'name' : 'Cathode',
                 'parent' : XenonDetector,
                 'parameters' : {'shift_z': bot_pmt_surface + bot_screen_to_window + cathode_to_screen}},
                {'name' : 'Gate',
                 'parent' : XenonDetector,
                 'parameters' : {'shift_z' : inn_lxe_h / 2 - gate_to_surface}},
                {'name' : 'Anode',
                 'parent' : 'InnerGasXe',
                 'parameters' : {'shift_z': -inn_gxe_h / 2 + anode_to_surface}},
                {'name' : 'TopScreening',
                 'parent' : 'InnerGasXe',
                 'parameters' : {'shift_z': top_pmt_surface - top_screen_to_window,
                                 'wire_pitch': 1.0}}]

for electrode in electrodes:
    electrode.update({'type' : 'MeshGrid'})
    electrode['parameters'].update({'radius' : inn_lxe_r,
                                    'sides': str(teflon_n),
                                    'material' : SS304LSteel,
                                    # 'ring_width': 2 * teflon_coat + copper_ring,
                                    # 'ring_height': ring_height,
                                    'type' : 'dielectric_metal',
                                    'surface' : surface})

detectorList += electrodes[:-1]  # no top screening

sideteflon_o = [
                {'name' : 'XeSideInnerTeflon',
                 'parameters' : {'outer_radius' : inn_lxe_r + teflon_coat,
                                 'inner_radius' : inn_lxe_r,
                                 'material' : Teflon}},
                {'name' : 'ShapingRings',
                 'parameters' : {'outer_radius' : inn_lxe_r + teflon_coat + copper_ring,
                                 'inner_radius' : inn_lxe_r + teflon_coat,
                                 'material' : 'Copper',
                                 'type' : 'dielectric_metal'}},
                {'name' : 'XeSideOuterTeflon',
                 'parameters' : {'outer_radius' : inn_lxe_r + 2 * teflon_coat + copper_ring,
                                 'inner_radius' : inn_lxe_r + teflon_coat + copper_ring,
                                 'material' : Teflon}}]

sideteflons_height = [inn_lxe_h / 2 + electrodes[0]['parameters']['shift_z'] - ring_height / 2,
                      electrodes[1]['parameters']['shift_z'] - electrodes[0]['parameters']['shift_z'] - ring_height,
                      electrodes[2]['parameters']['shift_z'] - electrodes[1]['parameters']['shift_z'] - ring_height,
                      gate_to_surface + anode_to_surface - ring_height,
                      inn_gxe_h / 2 - electrodes[3]['parameters']['shift_z'] - ring_height / 2]

sideteflons_shift_z = [sideteflons_height[0] / 2 - inn_lxe_h / 2 + xenon_detector_shift_z,
                       (electrodes[1]['parameters']['shift_z'] + electrodes[0]['parameters']['shift_z']) / 2 + xenon_detector_shift_z,
                       (electrodes[2]['parameters']['shift_z'] + electrodes[1]['parameters']['shift_z']) / 2 + xenon_detector_shift_z,
                       surface_shift_z,
                       -sideteflons_height[4] / 2 + inn_gxe_h / 2 + inner_gas_shift_z]

sideteflons = []
for i, (height_i, shift_z_i) in enumerate(zip(sideteflons_height, sideteflons_shift_z)):
    for j in range(len(sideteflon_o)):
        tr = copy.deepcopy(sideteflon_o[j])
        tr['type'] = Prism
        tr['parent'] = XenonVeto
        # if i == 3 and tr['name'] == 'XeSideInnerTeflon':
        #     tr['parameters']['partner'] = 'InnerGasXe'
        #     tr['parameters']['REFLECTIVITY'] = '0.0'
        tr['name'] = tr['name'] + str(i)

        tr['parameters']['sides'] = str(teflon_n)
        tr['parameters']['height'] = height_i
        tr['parameters']['shift_z'] = shift_z_i
        tr['parameters']['surface'] = surface
        sideteflons.append(copy.deepcopy(tr))

detectorList += sideteflons

ssring_o = [
                {'type' : Prism,
                 'name' : 'ElectrodeRing',
                 'parent' : XenonVeto,
                 'parameters' : {'outer_radius' : inn_lxe_r + 2 * teflon_coat + copper_ring,
                                 'inner_radius' : inn_lxe_r,
                                 'sides' : str(teflon_n),
                                 'material' : SS304LSteel,
                                 'surface' : surface}}]

ssrings = []
for i in range(len(sideteflons_height)-1):
    tr = copy.deepcopy(ssring_o[0])
    tr['name'] = tr['name'] + str(i)

    height_i = sideteflons_shift_z[i+1] - sideteflons_shift_z[i]
    height_i -= (sideteflons_height[i] + sideteflons_height[i+1]) / 2

    shift_z_i = sideteflons_shift_z[i] + sideteflons_height[i] / 2 + height_i / 2

    tr['parameters']['height'] = height_i
    tr['parameters']['shift_z'] = shift_z_i
    ssrings.append(copy.deepcopy(tr))

detectorList += ssrings

if force_sd:
    for d in detectorList:
        d.update({'sd' : True})

volume = {'soliname' : 'Solid',
          'logivol' : 'Log',
          'physvol' : ''}

for d in detectorList:
    detector = doc.createElement('detector')
    geometry.appendChild(detector)
    detector.setAttribute('type', d['type'])
    detector.setAttribute('name', d['name'])
    detector.setAttribute('parent', d['parent'])
    djson['geometry']['detectors'].append(dict())
    djson['geometry']['detectors'][-1].update({'type': d['type']})
    djson['geometry']['detectors'][-1].update({'name': d['name']})
    djson['geometry']['detectors'][-1].update({'parent': d['parent']})
    djson['geometry']['detectors'][-1].update({'parameters': dict()})
    for k in volume.keys():
        parameter = doc.createElement('parameter')
        detector.appendChild(parameter)
        parameter.setAttribute('name', k)
        name = d['parameters'].get('physvol', d['name'])
        parameter.setAttribute('value', f'{name}{volume[k]}')
        djson['geometry']['detectors'][-1]['parameters'].update({k: f'{name}{volume[k]}'})
    for x in d['parameters'].keys():
        if x == 'physvol':
            continue
        is_surface = d['parameters'].get('surface', False)
        if not is_surface and (x in ['model', 'finish', 'type', 'alpha']):
            # No need to store optical surface information
            continue
        parameter = doc.createElement('parameter')
        detector.appendChild(parameter)
        parameter.setAttribute('name', f'{x}')
        if isinstance(d['parameters'][x], str):
            parameter.setAttribute('value', f"{d['parameters'][x]}")
            djson['geometry']['detectors'][-1]['parameters'].update({f'{x}': f"{d['parameters'][x]}"})
        elif isinstance(d['parameters'][x], bool):
            parameter.setAttribute('value', f"{int(d['parameters'][x])}")
            djson['geometry']['detectors'][-1]['parameters'].update({f'{x}': f"{int(d['parameters'][x])}"})
        else:
            parameter.setAttribute('value', f"{d['parameters'][x]}*cm")
            djson['geometry']['detectors'][-1]['parameters'].update({f'{x}': f"{d['parameters'][x]}*cm"})
    if d.pop('sd', None):
        parameter = doc.createElement('parameter')
        detector.appendChild(parameter)
        parameter.setAttribute('name', 'sendname')
        # name = d['parameters'].get('physvol', d['name'])
        name = d['name']
        parameter.setAttribute('value', f'{name}')
        djson['geometry']['detectors'][-1]['parameters'].update({'sendname': f'{name}'})
        if d.pop('opticalsd', False):
            parameter = doc.createElement('parameter')
            detector.appendChild(parameter)
            parameter.setAttribute('name', 'opticalsd')
            parameter.setAttribute('value', '1')
            djson['geometry']['detectors'][-1]['parameters'].update({'opticalsd': '1'})
        if enable_track:
            parameter = doc.createElement('parameter')
            detector.appendChild(parameter)
            parameter.setAttribute('name', 'entrack')
            parameter.setAttribute('value', '1')
            djson['geometry']['detectors'][-1]['parameters'].update({'entrack': '1'})
    if check_overlap:
        parameter = doc.createElement('parameter')
        detector.appendChild(parameter)
        parameter.setAttribute('name', 'check_overlap')
        parameter.setAttribute('value', '1')
        djson['geometry']['detectors'][-1]['parameters'].update({'check_overlap': '1'})

physics = doc.createElement('physics')
root.appendChild(physics)
djson['physics'] = dict()
physics.setAttribute('name', physics_name)
djson['physics'].update({'name': physics_name})

parameter = doc.createElement('parameter')
physics.appendChild(parameter)
djson['physics'].update({'parameters': dict()})
parameter.setAttribute('name', 'cutlength')
parameter.setAttribute('value', f'{cutlength}*mm')
djson['physics']['parameters'].update({'cutlength': f'{cutlength}*mm'})

generator = doc.createElement('generator')
root.appendChild(generator)
djson['generator'] = dict()
generator.setAttribute('name', generator_name)
djson['generator'].update({'name': generator_name})

djson['generator'].update({'parameters': dict()})
if gen == 'muon' and not optical:
    parameter = doc.createElement('parameter')
    generator.appendChild(parameter)
    parameter.setAttribute('name', 'shielding_x')
    parameter.setAttribute('value', f'{world_half_x * 2}*cm')
    djson['generator']['parameters'].update({'shielding_x': f'{world_half_x * 2}*cm'})

    parameter = doc.createElement('parameter')
    generator.appendChild(parameter)
    parameter.setAttribute('name', 'shielding_z')
    parameter.setAttribute('value', f'{world_half_x * 2}*cm')
    djson['generator']['parameters'].update({'shielding_z': f'{world_half_x * 2}*cm'})

    parameter = doc.createElement('parameter')
    generator.appendChild(parameter)
    parameter.setAttribute('name', 'E_low')
    parameter.setAttribute('value', '0.106*GeV')
    djson['generator']['parameters'].update({'E_low': '0.106*GeV'})

analysis = doc.createElement('analysis')
root.appendChild(analysis)
djson['analysis'] = dict()
analysis.setAttribute('name', analysis_name)
djson['analysis'].update({'name': analysis_name})

djson['analysis'].update({'parameters': dict()})
for k in analysisList.keys():
    parameter = doc.createElement('parameter')
    analysis.appendChild(parameter)
    parameter.setAttribute('name', k)
    parameter.setAttribute('value', f'{analysisList[k]}')
    djson['analysis']['parameters'].update({k: analysisList[k]})

fp = open(fopt, 'w')
doc.writexml(fp,
             indent='  ',
             addindent='  ',
             newl='\n',
             encoding="UTF-8")

with open(os.path.splitext(fopt)[0] + '.json', 'w') as fp:
    json.dump(djson, fp, indent='\t')
