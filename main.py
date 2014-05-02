import RocketTrajectoryCalculator

# Make sure to set:
# - air pressure (100 psi)
# - air volume (m^3)
# - water volume (m^3)
# - structural mass (lb)
# - payload mass (lb)
# - frontal area (ft^2)
# - tankRadius
# - tankThickness
# - d_noz

## Defaults
# solver.airPressure = 12 * __psi_100_Pa
# solver.airVolume = 1.8 * __l_m3
# solver.waterVolume = 0.5 * __l_m3
# solver.structuralMass = 2.8 * __lb_kg
# solver.payloadMass = 0.5 * __lb_kg
# solver.frontalArea = 0.015 * __ft_2_m_2 # ~2.2in^2
#
# solver.tankRadius = 2.2 * __in_m
# solver.tankThickness = 1 * __in_m
#
# solver.d_noz = 0.5 * __in_m

## Conversion Numbers
__psi_100_Pa = 689475.729
__ft_2_m_2 = 0.092903
__lb_kg = 0.453592
__l_m3 = 0.001
__in_m = 0.0254
## End Conversions

solver = RocketTrajectoryCalculator.Solver()
###################
# Add Custom Values
###################
solver.airPressure = 12.1 * __psi_100_Pa
solver.airVolume = 1.6 * __l_m3
solver.waterVolume = 0.4 * __l_m3
solver.structuralMass = 2.8 * __lb_kg
solver.payloadMass = 0.5 * __lb_kg
solver.frontalArea = 0.017 * __ft_2_m_2 # ~2.2in^2

solver.tankRadius = 2.2 * __in_m
solver.tankThickness = 0.2 * __in_m

solver.d_noz = 1 * __in_m
###################
# End Custom Values
###################
solver.calculate()
height = solver.getMaxHeight()

