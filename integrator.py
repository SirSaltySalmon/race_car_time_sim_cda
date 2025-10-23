"""
Numerical integration engine for solving the canister car dynamics.
x represents time in seconds.

The canister fires from t=0 to t=1.280275 seconds, then the car coasts with drag.

Process:
1. Get canister force as function of time: F_canister(t) [0 to 1.28s, then 0]
2. Get mass as function of time: m(t) [varies 0 to 1.28s, then constant]
3. Calculate canister acceleration: a_canister(t) = F_canister(t) / m(t)
4. Integrate to get velocity (without drag): v_nodrag(t) = ∫a_canister(t)dt
5. Calculate drag force using this velocity: F_drag(t) = f(v_nodrag(t))
6. Calculate resultant force: F_resultant(t) = F_canister(t) - F_drag(t)
7. Calculate actual acceleration: a(t) = F_resultant(t) / m(t)
8. Integrate to get actual velocity: v(t) = ∫a(t)dt
9. Integrate to get displacement: s(t) = ∫v(t)dt
10. Solve for t where s(t) = 20m
"""

import numpy as np
from scipy.integrate import cumulative_trapezoid
from constants import TARGET_DISPLACEMENT


class IntegrationResult:
    """Container for integration results."""
    
    def __init__(self, success, message, t=None, v=None, s=None, 
                 time_to_20m=None, top_speed=None, top_speed_time=None):
        self.success = success
        self.message = message
        self.t = t  # Time array
        self.v = v  # Velocity array
        self.s = s  # Displacement array
        self.time_to_20m = time_to_20m
        self.top_speed = top_speed
        self.top_speed_time = top_speed_time


def integrate_motion(cda, canister_force_func, mass_func, drag_force_func, max_time=10.0, accuracy=0.000001):
    """
    Args:
        cda: Drag coefficient times reference area
        canister_force_func: Function F_canister(t)
        mass_func: Function m(t)
        drag_force_func: Function F_drag(v, cda) - returns force for given velocity
        max_time: Maximum time to integrate (seconds)
    
    Returns:
        IntegrationResult object with solution data
    """
    # Create fine time array
    dt = accuracy  # Default time step is 1 microsecond for high accuracy
    t = np.arange(0, max_time + dt, dt)
    n = len(t)
    
    print(f"\n=== DEBUG: Starting integration ===")
    print(f"Time points: {n}, dt: {dt}, max_time: {max_time}")
    
    # PART 1: Calculate acceleration from canister force only (to get v for drag calculation)
    # Step 1: Get canister force at all times
    F_canister = canister_force_func(t)
    print(f"F_canister: min={np.min(F_canister):.6e}, max={np.max(F_canister):.6e}")
    print(f"F_canister at t=0: {F_canister[0]:.6e}")
    print(f"F_canister at t=0.1: {F_canister[int(0.1/dt)]:.6e}")
    
    # Step 2: Get mass at all times
    m = mass_func(t)
    print(f"Mass: min={np.min(m):.6e}, max={np.max(m):.6e}")
    print(f"Mass at t=0: {m[0]:.6e}")
    
    # Step 3: Calculate canister-only acceleration
    a_canister = np.zeros(n)
    nonzero_mass = m > 0
    a_canister[nonzero_mass] = F_canister[nonzero_mass] / m[nonzero_mass]
    print(f"a_canister: min={np.min(a_canister):.6e}, max={np.max(a_canister):.6e}")
    print(f"a_canister at t=0: {a_canister[0]:.6e}")
    
    # Check for NaN or Inf
    if np.any(np.isnan(a_canister)) or np.any(np.isinf(a_canister)):
        print("WARNING: NaN or Inf detected in acceleration!")
        a_canister = np.nan_to_num(a_canister, nan=0.0, posinf=1e6, neginf=-1e6)
    
    # Step 4: Integrate to get velocity (without drag) - this is v(x) from the formula
    v_nodrag = cumulative_trapezoid(a_canister, t, initial=0)
    print(f"v_nodrag: min={np.min(v_nodrag):.6e}, max={np.max(v_nodrag):.6e}")
    print(f"v_nodrag at t=0.1: {v_nodrag[int(0.1/dt)]:.6e}")
    print(f"v_nodrag at t=1: {v_nodrag[int(1.0/dt)]:.6e}")
    
    # PART 2: Now use this velocity to calculate drag, then get actual motion
    # Step 5: Calculate drag force using the no-drag velocity
    F_drag = drag_force_func(v_nodrag, cda)
    print(f"F_drag: min={np.min(F_drag):.6e}, max={np.max(F_drag):.6e}")
    
    # Step 6: Calculate resultant (net) force
    F_resultant = F_canister - F_drag
    print(f"F_resultant: min={np.min(F_resultant):.6e}, max={np.max(F_resultant):.6e}")
    
    # Step 7: Calculate actual acceleration with drag
    a_actual = np.zeros(n)
    a_actual[nonzero_mass] = F_resultant[nonzero_mass] / m[nonzero_mass]
    
    # Check for NaN or Inf
    if np.any(np.isnan(a_actual)) or np.any(np.isinf(a_actual)):
        print("WARNING: NaN or Inf detected in actual acceleration!")
        a_actual = np.nan_to_num(a_actual, nan=0.0, posinf=1e6, neginf=-1e6)
    
    print(f"a_actual: min={np.min(a_actual):.6e}, max={np.max(a_actual):.6e}")
    
    # Step 8: Integrate actual acceleration to get actual velocity
    v_actual = cumulative_trapezoid(a_actual, t, initial=0)
    print(f"v_actual: min={np.min(v_actual):.6e}, max={np.max(v_actual):.6e}")
    print(f"v_actual at t=0.1: {v_actual[int(0.1/dt)]:.6e}")
    print(f"v_actual at t=1: {v_actual[int(1.0/dt)]:.6e}")
    
    # Prevent negative velocity
    v_actual = np.maximum(v_actual, 0)
    
    # Step 9: Integrate velocity to get displacement
    s = cumulative_trapezoid(v_actual, t, initial=0)
    print(f"s: min={np.min(s):.6e}, max={np.max(s):.6e}")
    print(f"s at t=1: {s[int(1.0/dt)]:.6e}")
    print(f"s at t=5: {s[min(int(5.0/dt), len(s)-1)]:.6e}")
    print("=== DEBUG END ===\n")
    
    # Step 10: Find time to reach 20m
    time_to_20m = None
    idx_20m = np.where(s >= TARGET_DISPLACEMENT)[0]
    
    if len(idx_20m) > 0:
        i = idx_20m[0]
        if i > 0:
            # Linear interpolation for more accurate time
            t1, t2 = t[i-1], t[i]
            s1, s2 = s[i-1], s[i]
            if s2 > s1:  # Avoid division by zero
                time_to_20m = t1 + (TARGET_DISPLACEMENT - s1) * (t2 - t1) / (s2 - s1)
            else:
                time_to_20m = t1
        else:
            time_to_20m = t[0]
        
        message = f"Successfully reached 20m in {time_to_20m:.4f} seconds"
    else:
        message = f"Did not reach 20m (max displacement: {s[-1]:.2f}m)"
    
    # Find top speed
    if len(v_actual) > 0:
        max_v_idx = np.argmax(v_actual)
        top_speed = v_actual[max_v_idx]
        top_speed_time = t[max_v_idx]
    else:
        top_speed = None
        top_speed_time = None
    
    return IntegrationResult(
        success=True,
        message=message,
        t=t,
        v=v_actual,
        s=s,
        time_to_20m=time_to_20m,
        top_speed=top_speed,
        top_speed_time=top_speed_time
    )