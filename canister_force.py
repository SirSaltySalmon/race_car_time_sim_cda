"""
Canister force functions for the three regions of operation.
"""

import numpy as np
from constants import (
    F1_SCALE, F1_EXP_COEFF, F1_EXP_OFFSET, F1_OFFSET,
    F2_SCALE, F2_FREQ_COEFF, F2_PHASE, F2_EXP_COEFF, F2_EXP_PHASE, F2_OFFSET,
    F3_SLOPE, F3_INTERCEPT,
    X_RANGE_1_END, X_RANGE_2_END
)


def f1(x):
    """
    First canister force function.
    f1(x) = (1/250) * (cos((63.0896-100x)^(1/2))) * (e^((63.0896-100x)^(1/2))) + 1
    
    Valid for: 0 ≤ x < 0.1306115
    
    Args:
        x: Normalized position/time parameter (scalar or array)
    
    Returns:
        Force value(s)
    """
    arg = F1_EXP_COEFF * x + F1_EXP_OFFSET
    
    # Handle potential negative values under square root
    arg = np.maximum(arg, 0)
    
    sqrt_arg = np.sqrt(arg)
    cos_term = np.cos(sqrt_arg)
    exp_term = np.exp(sqrt_arg)
    
    return F1_SCALE * cos_term * exp_term + F1_OFFSET


def f2(x):
    """
    Second canister force function.
    f2(x) = (4.175/8) * sin(-π/1.035 * x + 172/207 * π) * e^(-π/1.035 * x + 172/207 * π) + 0.5
    
    Valid for: 0.1306115 ≤ x < 0.849993
    
    Args:
        x: Normalized position/time parameter (scalar or array)
    
    Returns:
        Force value(s)
    """
    sin_arg = F2_FREQ_COEFF * x + F2_PHASE
    exp_arg = F2_EXP_COEFF * x + F2_EXP_PHASE
    
    sin_term = np.sin(sin_arg)
    exp_term = np.exp(exp_arg)
    
    return F2_SCALE * sin_term * exp_term + F2_OFFSET


def f3(x):
    """
    Third canister force function.
    f3(x) = -1.2x + 1.53633
    
    Valid for: 0.849993 ≤ x ≤ 1.280275
    
    Args:
        x: Normalized position/time parameter (scalar or array)
    
    Returns:
        Force value(s)
    """
    return F3_SLOPE * x + F3_INTERCEPT


def canister_force(x):
    """
    Piecewise canister force function that selects the appropriate
    function based on x value (time in seconds).
    
    The canister empties at x = 1.280275 seconds.
    
    f(x) = {
        f1(x)  if 0 ≤ x < 0.1306115
        f2(x)  if 0.1306115 ≤ x < 0.849993
        f3(x)  if 0.849993 ≤ x ≤ 1.280275
        0      if x > 1.280275  (canister empty - coasting with drag only)
    }
    
    Args:
        x: Time in seconds (scalar or array)
    
    Returns:
        Force value(s) in Newtons
    """
    # Handle scalar input
    if np.isscalar(x):
        if x < 0:
            return 0.0
        elif x < X_RANGE_1_END:
            return f1(x)
        elif x < X_RANGE_2_END:
            return f2(x)
        elif x <= 1.280275:
            return f3(x)
        else:
            # Canister empty - no more thrust
            return 0.0
    
    # Handle array input
    x = np.asarray(x)
    result = np.zeros_like(x, dtype=float)
    
    # Region 1: 0 ≤ x < 0.1306115
    mask1 = (x >= 0) & (x < X_RANGE_1_END)
    result[mask1] = f1(x[mask1])
    
    # Region 2: 0.1306115 ≤ x < 0.849993
    mask2 = (x >= X_RANGE_1_END) & (x < X_RANGE_2_END)
    result[mask2] = f2(x[mask2])
    
    # Region 3: 0.849993 ≤ x ≤ 1.280275
    mask3 = (x >= X_RANGE_2_END) & (x <= 1.280275)
    result[mask3] = f3(x[mask3])
    
    # Region 4: x > 1.280275 (canister empty - coasting phase)
    # Already initialized to zero
    
    return result