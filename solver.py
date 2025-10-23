"""
Main solver coordinating all physics components.
"""

import numpy as np
from canister_force import canister_force
from mass_model import mass
from drag_model import drag_force, validate_cda
from integrator import integrate_motion, IntegrationResult


class SolverResult:
    """Container for complete solver results with computed forces."""
    
    def __init__(self, integration_result, cda, forces=None):
        self.success = integration_result.success
        self.message = integration_result.message
        self.t = integration_result.t
        self.x = integration_result.t  # x is time
        self.v = integration_result.v
        self.s = integration_result.s
        self.time_to_20m = integration_result.time_to_20m
        self.top_speed = integration_result.top_speed
        self.top_speed_time = integration_result.top_speed_time
        self.cda = cda
        
        # Additional computed quantities
        if forces is not None:
            self.canister_force = forces['canister']
            self.drag_force = forces['drag']
            self.net_force = forces['net']
            self.acceleration = forces['acceleration']
            self.mass_values = forces['mass']
        else:
            self.canister_force = None
            self.drag_force = None
            self.net_force = None
            self.acceleration = None
            self.mass_values = None


def compute_forces(t, v, cda):
    """
    Compute all forces at each time step for visualization.
    
    Args:
        t: Time array (x = time)
        v: Velocity array
        cda: Drag coefficient times reference area
    
    Returns:
        Dictionary with force arrays
    """
    # Compute mass at each time point
    mass_values = mass(t)
    
    # Compute canister force at each time point
    canister_f = canister_force(t)
    
    # Compute drag force at each time point (depends on velocity)
    drag_f = drag_force(v, cda)
    
    # Net force (resultant force)
    net_f = canister_f - drag_f
    
    # Acceleration
    acceleration = np.zeros_like(net_f)
    nonzero_mass = mass_values > 0
    acceleration[nonzero_mass] = net_f[nonzero_mass] / mass_values[nonzero_mass]
    
    return {
        'canister': canister_f,
        'drag': drag_f,
        'net': net_f,
        'acceleration': acceleration,
        'mass': mass_values
    }


def solve_canister_car(cda, max_time=5.0, accuracy=0.000001):
    """
    Main solver function for canister car dynamics.
    
    This function:
    1. Validates input parameters
    2. Integrates the motion equations
    3. Computes forces for visualization
    4. Returns comprehensive results
    
    Process:
    - Canister force is F_canister(t) - function of time
    - Mass is m(t) - function of time
    - Drag force is F_drag(v) - function of velocity
    - Resultant force: F_net(t) = F_canister(t) - F_drag(v(t))
    - Acceleration: a(t) = F_net(t) / m(t)
    - Velocity: v(t) = ∫a(t)dt
    - Displacement: s(t) = ∫v(t)dt
    - Solve for t when s(t) = 20m
    
    Args:
        cda: Drag coefficient times reference area (m^2)
        max_time: Maximum integration time (seconds)
    
    Returns:
        SolverResult object with all computed data
    """
    # Validate CdA
    is_valid, error_msg = validate_cda(cda)
    if not is_valid:
        return SolverResult(
            integration_result=IntegrationResult(
                success=False,
                message=error_msg
            ),
            cda=cda
        )
    
    # Integrate the equations of motion
    integration_result = integrate_motion(
        cda=cda,
        canister_force_func=canister_force,
        mass_func=mass,
        drag_force_func=drag_force,
        max_time=max_time,
        accuracy=accuracy
    )
    
    if not integration_result.success:
        return SolverResult(integration_result, cda)
    
    # Compute forces for visualization
    forces = compute_forces(
        integration_result.t,
        integration_result.v,
        cda
    )
    
    return SolverResult(integration_result, cda, forces)


def get_time_history(solver_result, num_points=1000):
    """
    Generate evenly-spaced time history for smooth plotting.
    
    Args:
        solver_result: SolverResult object
        num_points: Number of points for interpolation
    
    Returns:
        Dictionary with interpolated arrays
    """
    if not solver_result.success or solver_result.t is None:
        return None
    
    # Create evenly spaced time array
    t_interp = np.linspace(solver_result.t[0], solver_result.t[-1], num_points)
    
    # Interpolate all quantities
    v_interp = np.interp(t_interp, solver_result.t, solver_result.v)
    s_interp = np.interp(t_interp, solver_result.t, solver_result.s)
    
    # Recompute forces at interpolated points
    forces_interp = compute_forces(t_interp, v_interp, solver_result.cda)
    
    return {
        't': t_interp,
        'x': t_interp,  # x is time
        'v': v_interp,
        's': s_interp,
        'canister_force': forces_interp['canister'],
        'drag_force': forces_interp['drag'],
        'net_force': forces_interp['net'],
        'acceleration': forces_interp['acceleration'],
        'mass': forces_interp['mass']
    }