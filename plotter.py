"""
Visualization module for plotting canister car dynamics.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


class DynamicsPlotter:
    """Creates comprehensive plots of canister car dynamics."""
    
    def __init__(self, figsize=(12, 10)):
        """
        Initialize plotter.
        
        Args:
            figsize: Figure size as (width, height) tuple
        """
        self.figsize = figsize
    
    def create_plots(self, solver_result, time_history=None):
        """
        Create a comprehensive multi-panel plot of all dynamics.
        
        Args:
            solver_result: SolverResult object with all data
            time_history: Optional interpolated time history for smooth curves
        
        Returns:
            matplotlib Figure object
        """
        if not solver_result.success:
            return self._create_error_figure(solver_result.message)
        
        # Use time history if provided, otherwise use raw data
        if time_history is not None:
            data = time_history
        else:
            data = {
                't': solver_result.t,
                'v': solver_result.v,
                's': solver_result.s,
                'canister_force': solver_result.canister_force,
                'drag_force': solver_result.drag_force,
                'net_force': solver_result.net_force,
                'acceleration': solver_result.acceleration
            }
        
        # Create figure with subplots
        fig = Figure(figsize=self.figsize)
        
        # 2x2 grid of plots
        ax1 = fig.add_subplot(2, 2, 1)  # Forces
        ax2 = fig.add_subplot(2, 2, 2)  # Velocity
        ax3 = fig.add_subplot(2, 2, 3)  # Displacement
        ax4 = fig.add_subplot(2, 2, 4)  # Acceleration
        
        # Plot 1: Forces vs Time
        self._plot_forces(ax1, data, solver_result)
        
        # Plot 2: Velocity vs Time
        self._plot_velocity(ax2, data, solver_result)
        
        # Plot 3: Displacement vs Time
        self._plot_displacement(ax3, data, solver_result)
        
        # Plot 4: Acceleration vs Time
        self._plot_acceleration(ax4, data, solver_result)
        
        # Overall title
        title = f"Canister Car Dynamics (CdA = {solver_result.cda:.4f} m²)"
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        # Tight layout
        fig.tight_layout(rect=[0, 0.03, 1, 0.97])
        
        return fig
    
    def _plot_forces(self, ax, data, solver_result):
        """Plot forces vs time."""
        t = data['t']
        
        ax.plot(t, data['canister_force'], 'b-', label='Canister Force', linewidth=2)
        ax.plot(t, data['drag_force'], 'r-', label='Drag Force', linewidth=2)
        ax.plot(t, data['net_force'], 'g-', label='Net Force', linewidth=2, alpha=0.7)
        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Mark 20m time if available
        if solver_result.time_to_20m is not None:
            ax.axvline(x=solver_result.time_to_20m, color='orange', 
                      linestyle='--', linewidth=1, label=f'20m at {solver_result.time_to_20m:.3f}s')
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Force (N)')
        ax.set_title('Forces vs Time')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_velocity(self, ax, data, solver_result):
        """Plot velocity vs time."""
        t = data['t']
        v = data['v']
        
        ax.plot(t, v, 'b-', linewidth=2)
        
        # Mark top speed
        if solver_result.top_speed is not None:
            ax.axhline(y=solver_result.top_speed, color='r', linestyle='--', 
                      linewidth=1, alpha=0.7)
            ax.text(0.02, 0.98, f'Top Speed: {solver_result.top_speed:.2f} m/s\n({solver_result.top_speed*2.237:.2f} mph)',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                   fontsize=8)
        
        # Mark 20m time if available
        if solver_result.time_to_20m is not None:
            ax.axvline(x=solver_result.time_to_20m, color='orange', 
                      linestyle='--', linewidth=1)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Velocity (m/s)')
        ax.set_title('Velocity vs Time')
        ax.grid(True, alpha=0.3)
    
    def _plot_displacement(self, ax, data, solver_result):
        """Plot displacement vs time."""
        t = data['t']
        s = data['s']
        
        ax.plot(t, s, 'g-', linewidth=2)
        
        # Mark 20m line
        ax.axhline(y=20, color='r', linestyle='--', linewidth=1, alpha=0.7)
        
        # Mark 20m time if available
        if solver_result.time_to_20m is not None:
            ax.axvline(x=solver_result.time_to_20m, color='orange', 
                      linestyle='--', linewidth=1)
            ax.plot(solver_result.time_to_20m, 20, 'ro', markersize=8)
            ax.text(0.02, 0.98, f'Time to 20m: {solver_result.time_to_20m:.4f} s',
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
                   fontsize=8)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Displacement (m)')
        ax.set_title('Displacement vs Time')
        ax.grid(True, alpha=0.3)
    
    def _plot_acceleration(self, ax, data, solver_result):
        """Plot acceleration vs time."""
        t = data['t']
        a = data['acceleration']
        
        ax.plot(t, a, 'purple', linewidth=2)
        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
        
        # Mark 20m time if available
        if solver_result.time_to_20m is not None:
            ax.axvline(x=solver_result.time_to_20m, color='orange', 
                      linestyle='--', linewidth=1)
        
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Acceleration (m/s²)')
        ax.set_title('Acceleration vs Time')
        ax.grid(True, alpha=0.3)
    
    def _create_error_figure(self, error_message):
        """Create a figure showing error message."""
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(1, 1, 1)
        
        ax.text(0.5, 0.5, f'Error:\n{error_message}',
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax.transAxes,
               fontsize=12,
               color='red',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        return fig


def create_summary_figure(solver_result):
    """
    Create a single-panel summary plot showing key results.
    
    Args:
        solver_result: SolverResult object
    
    Returns:
        matplotlib Figure object
    """
    if not solver_result.success:
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(1, 1, 1)
        ax.text(0.5, 0.5, f'Error:\n{solver_result.message}',
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=12, color='red')
        ax.axis('off')
        return fig
    
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    
    # Plot velocity and displacement on same axes with different scales
    ax1 = ax
    ax2 = ax1.twinx()
    
    # Velocity on left axis
    line1 = ax1.plot(solver_result.t, solver_result.v, 'b-', linewidth=2, label='Velocity')
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Velocity (m/s)', color='b', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='b')
    
    # Displacement on right axis
    line2 = ax2.plot(solver_result.t, solver_result.s, 'g-', linewidth=2, label='Displacement')
    ax2.set_ylabel('Displacement (m)', color='g', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='g')
    ax2.axhline(y=20, color='r', linestyle='--', linewidth=1, alpha=0.7, label='20m Target')
    
    # Mark 20m time
    if solver_result.time_to_20m is not None:
        ax1.axvline(x=solver_result.time_to_20m, color='orange', 
                   linestyle='--', linewidth=2, alpha=0.7)
        ax2.plot(solver_result.time_to_20m, 20, 'ro', markersize=10)
    
    # Title and legend
    title = f"Canister Car Performance (CdA = {solver_result.cda:.4f} m²)"
    ax1.set_title(title, fontsize=14, fontweight='bold')
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    ax1.grid(True, alpha=0.3)
    
    fig.tight_layout()
    
    return fig