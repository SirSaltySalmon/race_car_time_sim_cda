"""
Drag force model for aerodynamic resistance.
"""

import numpy as np
from constants import AIR_DENSITY, MIN_CDA, MAX_CDA


def drag_force(velocity, cda):
    """
    Calculate aerodynamic drag force.
    
    F_d = 0.5 * ρ * v^2 * C_d * A
    
    where:
        ρ = air density (1.20473 kg/m^3)
        v = velocity (m/s)
        C_d = drag coefficient
        A = frontal reference area (m^2)
        C_d * A = CdA (combined parameter, input by user)
    
    Args:
        velocity: Vehicle velocity in m/s (scalar or array)
        cda: Drag coefficient times reference area (C_d * A)
    
    Returns:
        Drag force in Newtons (always positive, opposes motion)
    """
    # Handle negative velocities (shouldn't happen, but be safe)
    if np.isscalar(velocity):
        velocity = max(0, velocity)
    else:
        velocity = np.maximum(0, velocity)
    
    return 0.5 * AIR_DENSITY * velocity**2 * cda


def validate_cda(cda):
    """
    Validate that CdA value is physically reasonable.
    
    Args:
        cda: Drag coefficient times reference area
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if cda is None:
        return False, "CdA value cannot be None"
    
    try:
        cda_float = float(cda)
    except (ValueError, TypeError):
        return False, "CdA must be a number"
    
    if cda_float <= 0:
        return False, "CdA must be positive"
    
    if cda_float < MIN_CDA:
        return False, "CdA value too small (minimum ${MIN_CDA})"
    
    if cda_float > MAX_CDA:
        return False, "CdA value too large (maximum ${MAX_CDA})"
    
    return True, ""