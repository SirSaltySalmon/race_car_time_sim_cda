"""
Physical constants and configuration parameters for the canister car calculator.
"""

# Air density (kg/m^3)
AIR_DENSITY = 1.20473

# Canister force function ranges
X_RANGE_1_START = 0.0
X_RANGE_1_END = 0.1306115
X_RANGE_2_START = 0.1306115
X_RANGE_2_END = 0.849993
X_RANGE_3_START = 0.849993
X_RANGE_3_END = 1.280275

# Mass function parameters
MASS_BASE = 0.0214
MASS_BASE_M = 0.048
MASS_COEFF_NUM = 0.008 * (40000)**2
MASS_COEFF_DEN = 51211**2
MASS_CENTER = 1.280275
MASS_MAX_X = 1.280275

# Target displacement for time calculation (meters)
TARGET_DISPLACEMENT = 20.0

# Integration tolerances
RTOL = 1e-9
ATOL = 1e-11

# Maximum integration time (seconds) - safety limit
MAX_TIME = 100.0

# Constants for canister force functions
import numpy as np

# f1 constants
F1_SCALE = 1.0 / 250.0
F1_EXP_COEFF = -100.0
F1_EXP_OFFSET = 63.0896
F1_OFFSET = 1.0

# f2 constants
F2_SCALE = 4.175 / 8.0
F2_FREQ_COEFF = -np.pi / 1.035
F2_PHASE = 172.0 / 207.0 * np.pi
F2_EXP_COEFF = -np.pi / 1.035
F2_EXP_PHASE = 172.0 / 207.0 * np.pi
F2_OFFSET = 0.5

# f3 constants
F3_SLOPE = -1.2
F3_INTERCEPT = 1.53633

# GUI default values
DEFAULT_CDA = 0.5
MIN_CDA = 0.0001
MAX_CDA = 1.0