from simupy.block_diagram import BlockDiagram, DEFAULT_INTEGRATOR_OPTIONS
import aerospace_sim_classes
import pandas as pd, matplotlib.pyplot as plt
import numpy as np
import os

ft_per_m = 3.28084
slug_per_kg = 0.0685218

kg_per_slug = 14.5939

int_opts = DEFAULT_INTEGRATOR_OPTIONS.copy()
int_opts['max_step'] = 2**-4

kin_block = aerospace_sim_classes.KinematicsBlock(
    gravity=aerospace_sim_classes.earth_J2_gravity,
    winds=aerospace_sim_classes.get_constant_winds(wy=20/ft_per_m),
    density=aerospace_sim_classes.density_1976_atmosphere,
    speed_of_sound=aerospace_sim_classes.get_constant_speed_of_sound(),
    viscosity=aerospace_sim_classes.get_constant_viscosity(),
    a = aerospace_sim_classes.earth_equitorial_radius,
    omega_p=aerospace_sim_classes.earth_rotation_rate,
    f=aerospace_sim_classes.earth_f
)

print("I am defining wind from the west as + in eastward direction, is this how it is usually defined?")

Ixx = 3.6*kg_per_slug/(ft_per_m**2) #slug-ft2
Iyy = 3.6*kg_per_slug/(ft_per_m**2) #slug-ft2
Izz = 3.6*kg_per_slug/(ft_per_m**2) #slug-ft2
Ixy = 0.0*kg_per_slug/(ft_per_m**2) #slug-ft2
Iyz = 0.0*kg_per_slug/(ft_per_m**2) #slug-ft2
Izx = 0.0*kg_per_slug/(ft_per_m**2) #slug-ft2
m = 1.0*kg_per_slug #slug

x = 0.
y = 0.
z = 0.

S_A = 0.1963495/(ft_per_m**2)
b_l = 1.0
c_l = 1.0
a_l = b_l
dyn_block =  aerospace_sim_classes.DynamicsBlock(aerospace_sim_classes.get_constant_aero(CD_b=0.1), m, Ixx, Iyy, Izz, Ixy, Iyz, Izx, x,y,z, x,y,z, S_A=S_A, a_l=a_l, b_l=b_l, c_l=c_l, d_l=1.,)

BD = BlockDiagram(kin_block, dyn_block)
BD.connect(kin_block, dyn_block, inputs=np.arange(kin_block.dim_output))
BD.connect(dyn_block, kin_block, inputs=np.arange(dyn_block.dim_output))

lat_ic = 0.*np.pi/180
long_ic = 0.*np.pi/180
h_ic = 30_000/ft_per_m
V_N_ic = 0.
V_E_ic = 0.
V_D_ic = 0.
psi_ic = 0.*np.pi/180
theta_ic = 0.*np.pi/180
phi_ic = 0.*np.pi/180
omega_X_ic = 0.*np.pi/180
omega_Y_ic = 0.*np.pi/180
omega_Z_ic = 0.*np.pi/180

kin_block.initial_condition = kin_block.ic_from_geodetic(0, long_ic, lat_ic, h_ic, V_N_ic, V_E_ic, V_D_ic, psi_ic, theta_ic, phi_ic, omega_X_ic, omega_Y_ic, omega_Z_ic)
out_at_ic = kin_block.output_equation_function(0, kin_block.initial_condition)
dynamics_at_ic = dyn_block.dynamics_output_function(0, *out_at_ic, *np.zeros(6+9))
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
for fname in glob.glob(os.path.join('Atmospheric_checkcases', 'Atmos_07_DroppedSphereSteadyWind', 'Atmos_07_sim_*.csv'),):
    baseline_pds.append(pd.read_csv(fname, index_col=0))
plot_nesc_comparisons(res, baseline_pds)