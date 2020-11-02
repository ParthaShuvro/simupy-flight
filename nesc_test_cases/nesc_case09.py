from simupy.block_diagram import BlockDiagram
import simupy_flight
import pandas as pd
import numpy as np
import os
import glob
from nesc_testcase_helper import plot_nesc_comparisons, data_relative_path, int_opts, ft_per_m, kg_per_slug


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

lat_ic = 0.*np.pi/180
long_ic = 0.*np.pi/180
h_ic = 0./ft_per_m
V_N_ic = 000./ft_per_m
V_E_ic = 1000./ft_per_m
V_D_ic = -1000./ft_per_m
psi_ic = 90.*np.pi/180
theta_ic = 0.*np.pi/180
phi_ic = 0.*np.pi/180
omega_X_ic = 0.*np.pi/180
omega_Y_ic = -0.004178073*np.pi/180
omega_Z_ic = 0.*np.pi/180


planet = simupy_flight.Planet(
    gravity=simupy_flight.earth_J2_gravity,
    winds=simupy_flight.get_constant_winds(),
    atmosphere=simupy_flight.atmosphere_1976,
    planetodetics=simupy_flight.Planetodetic(a=simupy_flight.earth_equitorial_radius, omega_p=simupy_flight.earth_rotation_rate, f=simupy_flight.earth_f)
)


vehicle =  simupy_flight.Vehicle(base_aero_coeffs=simupy_flight.get_constant_aero(CD_b=0.1), m=m, I_xx=Ixx, I_yy=Iyy, I_zz=Izz, I_xy=Ixy, I_yz=Iyz, I_xz=Izx, x_com=x, y_com=y, z_com=z, x_mrc=x, y_mrc=y, z_mrc=z, S_A=S_A, a_l=a_l, b_l=b_l, c_l=c_l, d_l=0.,)

BD = BlockDiagram(planet, vehicle)
BD.connect(planet, vehicle, inputs=np.arange(planet.dim_output))
BD.connect(vehicle, planet, inputs=np.arange(vehicle.dim_output))



planet.initial_condition = planet.ic_from_planetodetic(long_ic, lat_ic, h_ic, V_N_ic, V_E_ic, V_D_ic, psi_ic, theta_ic, phi_ic)
planet.initial_condition[-3:] = omega_X_ic, omega_Y_ic, omega_Z_ic

res = BD.simulate(30, integrator_options=int_opts)

baseline_pds = []
for fname in glob.glob(os.path.join(data_relative_path, 'Atmospheric_checkcases', 'Atmos_09_EastwardCannonball', 'Atmos_09_sim_*.csv'),):
    baseline_pds.append(pd.read_csv(fname, index_col=0))
plot_nesc_comparisons(res, baseline_pds, '09')