from simupy.block_diagram import BlockDiagram, DEFAULT_INTEGRATOR_OPTIONS
import aerospace_sim_classes
import pandas as pd, matplotlib.pyplot as plt
import numpy as np
import os

int_opts = DEFAULT_INTEGRATOR_OPTIONS.copy()
int_opts['max_step'] = 0.25

kin_block = aerospace_sim_classes.KinematicsBlock(
    gravity=aerospace_sim_classes.earth_J2_gravity,
    winds=aerospace_sim_classes.get_constant_winds(),
    density=aerospace_sim_classes.get_constant_density(0.),
    speed_of_sound=aerospace_sim_classes.get_constant_speed_of_sound(),
    viscosity=aerospace_sim_classes.get_constant_viscosity(),
    a = aerospace_sim_classes.earth_equitorial_radius,
    omega_p=aerospace_sim_classes.earth_rotation_rate,
    f=aerospace_sim_classes.earth_f
)

BD = BlockDiagram(kin_block)

ft_per_m = 3.28084

lat_ic = 0.*np.pi/180
long_ic = 0.*np.pi/180
h_ic = 30_000/ft_per_m
V_N_ic = 0.
V_E_ic = 0.
V_D_ic = 0.
psi_ic = 0.*np.pi/180
theta_ic = 0.*np.pi/180
phi_ic = 0.*np.pi/180
omega_X_ic = 0.
omega_Y_ic = 0.
omega_Z_ic = 0.

kin_block.initial_condition = kin_block.ic_from_geodetic(0, long_ic, lat_ic, h_ic, V_N_ic, V_E_ic, V_D_ic, psi_ic, theta_ic, phi_ic, omega_X_ic, omega_Y_ic, omega_Z_ic)
out_at_ic = kin_block.output_equation_function(0, kin_block.initial_condition)
check_pos = out_at_ic[13:16]
check_att = out_at_ic[16:19]
orig_pos = np.array([long_ic, lat_ic, h_ic])
orig_att = np.array([psi_ic, theta_ic, phi_ic])
print('position:', np.allclose(check_pos, orig_pos))
print('attitude:', np.allclose(check_att, orig_att))

res = BD.simulate(30, integrator_options=int_opts)
check_output = kin_block.output_equation_function(res.t[-1], res.x[-1,:])

long_lat_deg = res.y[:,13:15]*180/np.pi
alt_ft = res.y[:,15]*ft_per_m

psi_theta_phi_deg = res.y[:,16:19]*180/np.pi
##


import glob
baseline_pds = []
for fname in glob.glob(os.path.join('Atmospheric_checkcases', 'Atmos_01_DroppedSphere', 'Atmos_01_sim_*.csv'),):
    baseline_pds.append(pd.read_csv(fname, index_col=0))
    
plot_nesc_comparisons(res, baseline_pds)
