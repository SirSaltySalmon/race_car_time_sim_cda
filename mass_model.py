"""
Mass model for the canister car accounting for gas loss during operation.
"""

import numpy as np
from constants import MASS_BASE, MASS_COEFF_NUM, MASS_COEFF_DEN, MASS_CENTER, MASS_MAX_X


def mass(x):
    """
    Mass function accounting for compressed gas loss.
    
    x represents time in seconds.
    
    m(x) = 0.0694 + (0.008 * 40000^2 / 51211^2) * (x - 1.280275)^2
    
    Valid for: 0 ≤ x ≤ 1.280275 (while canister is firing)
    After x > 1.280275, mass remains constant at MASS_BASE (canister empty)
    
    Args:
        x: Time in seconds (scalar or array)
    
    Returns:
        Mass value(s) in kg
    """
    # Handle scalar input
    if np.isscalar(x):
        if x < 0:
            return MASS_BASE
        elif x <= MASS_MAX_X:
            coefficient = MASS_COEFF_NUM / MASS_COEFF_DEN
            return MASS_BASE + coefficient * (x - MASS_CENTER) ** 2
        else:
            # After canister is empty, mass remains constant at base value
            return MASS_BASE
    
    # Handle array input
    x = np.asarray(x)
    result = np.zeros_like(x, dtype=float)
    coefficient = MASS_COEFF_NUM / MASS_COEFF_DEN
    
    # Region 1: 0 ≤ x ≤ 1.280275 (gas is being expelled)
    mask_active = (x >= 0) & (x <= MASS_MAX_X)
    result[mask_active] = MASS_BASE + coefficient * (x[mask_active] - MASS_CENTER) ** 2
    
    # Region 2: x > 1.280275 (canister empty, constant mass)
    mask_empty = x > MASS_MAX_X
    result[mask_empty] = MASS_BASE
    
    # Region 3: x < 0 (shouldn't happen, but handle gracefully)
    mask_negative = x < 0
    result[mask_negative] = MASS_BASE
    
    return result


def mass_derivative(x):
    """
    Derivative of mass with respect to x.
    
    dm/dx = 2 * (0.008 * 40000^2 / 51211^2) * (x - 1.280275)
    
    Valid for: 0 ≤ x ≤ 1.280275
    After x > 1.280275, dm/dx = 0
    
    Args:
        x: Normalized position/time parameter (scalar or array)
    
    Returns:
        Mass derivative value(s)
    """
    # Handle scalar input
    if np.isscalar(x):
        if x < 0 or x > MASS_MAX_X:
            return 0.0
        else:
            coefficient = 2 * MASS_COEFF_NUM / MASS_COEFF_DEN
            return coefficient * (x - MASS_CENTER)
    
    # Handle array input
    x = np.asarray(x)
    result = np.zeros_like(x, dtype=float)
    
    # Only non-zero in active region
    mask_active = (x >= 0) & (x <= MASS_MAX_X)
    coefficient = 2 * MASS_COEFF_NUM / MASS_COEFF_DEN
    result[mask_active] = coefficient * (x[mask_active] - MASS_CENTER)
    
    return result


def get_final_mass():
    """
    Returns the final mass of the car after canister is empty.
    
    Returns:
        Final mass in kg
    """
    return MASS_BASE


def get_initial_mass():
    """
    Returns the initial mass of the car at x = 0.
    
    Returns:
        Initial mass in kg
    """
    return mass(0.0)