"""
GUI module for the canister car calculator.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from constants import DEFAULT_CDA, MIN_CDA, MAX_CDA
from solver import solve_canister_car, get_time_history
from plotter import DynamicsPlotter, create_summary_figure


class CanisterCarGUI:
    """Main GUI application for canister car track time calculator."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: tkinter root window
        """
        self.root = root
        self.root.title("Canister Car Track Time Calculator")
        self.root.geometry("1200x800")
        
        # Solver result storage
        self.current_result = None
        self.calculating = False
        
        # Create GUI components
        self._create_widgets()
        
    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Input section
        self._create_input_section(main_frame)
        
        # Results section
        self._create_results_section(main_frame)
        
        # Plot section
        self._create_plot_section(main_frame)
        
        # Status bar
        self._create_status_bar(main_frame)
    
    def _create_input_section(self, parent):
        """Create input controls section."""
        input_frame = ttk.LabelFrame(parent, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # CdA input
        ttk.Label(input_frame, text="CdA (Drag Coefficient × Area):").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        
        self.cda_var = tk.StringVar(value=str(DEFAULT_CDA))
        self.cda_entry = ttk.Entry(input_frame, textvariable=self.cda_var, width=15)
        self.cda_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        ttk.Label(input_frame, text="m²", foreground="gray").grid(
            row=0, column=2, sticky=tk.W, padx=(0, 20)
        )
        
        # Info label for CdA
        info_text = f"(Range: {MIN_CDA} - {MAX_CDA} m²)"
        ttk.Label(input_frame, text=info_text, foreground="gray", font=("", 9)).grid(
            row=0, column=3, sticky=tk.W
        )
        
        # Interpolation time input
        ttk.Label(input_frame, text="Max Interpolation Time:").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        
        self.interp_time_var = tk.StringVar(value="5.0")
        self.interp_time_entry = ttk.Entry(input_frame, textvariable=self.interp_time_var, width=15)
        self.interp_time_entry.grid(row=1, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        ttk.Label(input_frame, text="seconds", foreground="gray").grid(
            row=1, column=2, sticky=tk.W, padx=(0, 20), pady=(10, 0)
        )
        
        # Info label for interpolation time
        ttk.Label(input_frame, text="(Time limit for car to run)", 
                 foreground="gray", font=("", 9)).grid(
            row=1, column=3, sticky=tk.W, pady=(10, 0)
        )

        # Accuracy input
        ttk.Label(input_frame, text="Accuracy:").grid(
            row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0)
        )
        
        self.accuracy_var = tk.StringVar(value="0.000001")
        self.accuracy_entry = ttk.Entry(input_frame, textvariable=self.accuracy_var, width=15)
        self.accuracy_entry.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        ttk.Label(input_frame, text="seconds", foreground="gray").grid(
            row=2, column=2, sticky=tk.W, padx=(0, 20), pady=(10, 0)
        )
        
        # Info label for accuracy
        ttk.Label(input_frame, text="(Amount of time between points, smaller is more accurate)", 
                 foreground="gray", font=("", 9)).grid(
            row=2, column=3, sticky=tk.W, pady=(10, 0)
        )
        
        # Buttons
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=(10, 0))
        
        self.calculate_button = ttk.Button(
            button_frame, text="Calculate", command=self._on_calculate
        )
        self.calculate_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(
            button_frame, text="Clear", command=self._on_clear
        )
        self.clear_button.grid(row=0, column=1, padx=(0, 10))
        
        # Bind Enter key to calculate
        self.cda_entry.bind('<Return>', lambda e: self._on_calculate())
        self.interp_time_entry.bind('<Return>', lambda e: self._on_calculate())
        self.accuracy_entry.bind('<Return>', lambda e: self._on_calculate())

    def _create_results_section(self, parent):
        """Create results display section."""
        results_frame = ttk.LabelFrame(parent, text="Results", padding="10")
        results_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Results grid
        results_grid = ttk.Frame(results_frame)
        results_grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Time to 20m
        ttk.Label(results_grid, text="Time to 20m:", font=("", 10, "bold")).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.time_20m_var = tk.StringVar(value="---")
        ttk.Label(results_grid, textvariable=self.time_20m_var, font=("", 10)).grid(
            row=0, column=1, sticky=tk.W, pady=5
        )
        ttk.Label(results_grid, text="seconds", foreground="gray").grid(
            row=0, column=2, sticky=tk.W, padx=(5, 0), pady=5
        )
        
        # Top speed (m/s)
        ttk.Label(results_grid, text="Top Speed:", font=("", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.top_speed_var = tk.StringVar(value="---")
        ttk.Label(results_grid, textvariable=self.top_speed_var, font=("", 10)).grid(
            row=1, column=1, sticky=tk.W, pady=5
        )
        ttk.Label(results_grid, text="m/s", foreground="gray").grid(
            row=1, column=2, sticky=tk.W, padx=(5, 0), pady=5
        )
    
    def _create_plot_section(self, parent):
        """Create matplotlib plot section."""
        plot_frame = ttk.LabelFrame(parent, text="Dynamics Visualization", padding="10")
        plot_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weight for expansion
        plot_frame.columnconfigure(0, weight=1)
        plot_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 9))
        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial empty plot
        self._show_welcome_message()
    
    def _create_status_bar(self, parent):
        """Create status bar at bottom."""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=200)
        self.progress.grid(row=0, column=1, padx=(10, 0))
        
        status_frame.columnconfigure(0, weight=1)
    
    def _show_welcome_message(self):
        """Display welcome message on empty plot."""
        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        
        welcome_text = (
            "Canister Car Track Time Calculator\n\n"
            "Enter the CdA value (drag coefficient × reference area)\n"
            "and click 'Calculate' to begin simulation.\n\n"
            "The program will compute:\n"
            "• Time to reach 20 meters\n"
            "• Top speed of the vehicle\n"
            "• Complete dynamics visualization"
        )
        
        ax.text(0.5, 0.5, welcome_text,
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax.transAxes,
               fontsize=12,
               bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        self.canvas.draw()
    
    def _on_calculate(self):
        """Handle calculate button click."""
        if self.calculating:
            messagebox.showwarning("Calculation in Progress", 
                                  "Please wait for current calculation to complete.")
            return
        
        # Get CdA value
        try:
            cda = float(self.cda_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter a valid number for CdA.")
            return
        
        # Validate CdA range
        if cda < MIN_CDA or cda > MAX_CDA:
            messagebox.showerror("Invalid Input", 
                               f"CdA must be between {MIN_CDA} and {MAX_CDA} m².")
            return
        
        # Get interpolation time
        try:
            interp_time = float(self.interp_time_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter a valid number for interpolation time.")
            return
        
        # Validate interpolation time
        if interp_time <= 0:
            messagebox.showerror("Invalid Input", 
                               "Interpolation time must be positive.")
            return
        
        if interp_time > 100:
            messagebox.showwarning("Large Time Value", 
                                  "Large interpolation times may slow down plotting.")
        

        # Get accuracy
        try:
            accuracy = float(self.accuracy_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter a valid number for accuracy.")
            return
        
        # Validate accuracy
        if accuracy <= 0:
            messagebox.showerror("Invalid Input", 
                               "Accuracy must be positive.")
            return
        
        if accuracy < 0.00000001:
            messagebox.showwarning("Large Accuracy Value", 
                                "Large accuracy values may slow down calculation.")
        
        # Run calculation in separate thread
        self.calculating = True
        self.calculate_button.config(state='disabled')
        self.status_var.set(f"Calculating for CdA = {cda:.4f} m²...")
        self.progress.start(10)
        
        calc_thread = threading.Thread(target=self._run_calculation, args=(cda, interp_time, accuracy))
        calc_thread.daemon = True
        calc_thread.start()
    
    def _run_calculation(self, cda, interp_time, accuracy):
        """Run the calculation (called in separate thread)."""
        try:
            # Solve the dynamics (use interp_time as max_time for solver)
            result = solve_canister_car(cda, interp_time, accuracy)
            
            # Store interpolation time in result for later use
            result.interp_time = interp_time
            
            # Update GUI in main thread
            self.root.after(0, self._on_calculation_complete, result)
            
        except Exception as e:
            error_msg = f"Calculation error: {str(e)}"
            self.root.after(0, self._on_calculation_error, error_msg)
    
    def _on_calculation_complete(self, result):
        """Handle completion of calculation."""
        self.calculating = False
        self.calculate_button.config(state='normal')
        self.progress.stop()
        
        self.current_result = result
        
        if result.success:
            # Update results display
            if result.time_to_20m is not None:
                self.time_20m_var.set(f"{result.time_to_20m:.12f}")
                self.status_var.set(f"Success: Reached 20m in {result.time_to_20m:.4f} seconds")
            else:
                self.time_20m_var.set("Did not reach 20m")
                max_s = result.s[-1] if result.s is not None and len(result.s) > 0 else 0
                self.status_var.set(f"Warning: Did not reach 20m (max: {max_s:.4f}m)")
            
            if result.top_speed is not None:
                self.top_speed_var.set(f"{result.top_speed:.12f}")
            else:
                self.top_speed_var.set("---")
            # Generate plots
            self._update_plots(result)
            
        else:
            # Show error
            self.status_var.set(f"Error: {result.message}")
            messagebox.showerror("Calculation Error", result.message)
            self._clear_results()
    
    def _on_calculation_error(self, error_msg):
        """Handle calculation error."""
        self.calculating = False
        self.calculate_button.config(state='normal')
        self.progress.stop()
        self.status_var.set("Error occurred")
        messagebox.showerror("Calculation Error", error_msg)
    
    def _update_plots(self, result):
        """Update matplotlib plots with new results."""
        self.figure.clear()
        
        # Get smooth time history for plotting
        time_history = get_time_history(result, num_points=1000)
        
        # Create plots
        plotter = DynamicsPlotter(figsize=(12, 9))
        fig = plotter.create_plots(result, time_history)
        
        # Copy plots to canvas figure
        for i, ax_src in enumerate(fig.get_axes()):
            ax_dst = self.figure.add_subplot(2, 2, i+1)
            
            # Copy all lines
            for line in ax_src.get_lines():
                ax_dst.plot(line.get_xdata(), line.get_ydata(), 
                           linestyle=line.get_linestyle(),
                           color=line.get_color(),
                           linewidth=line.get_linewidth(),
                           label=line.get_label(),
                           alpha=line.get_alpha() if line.get_alpha() else 1.0)
            
            # Copy labels and title
            ax_dst.set_xlabel(ax_src.get_xlabel())
            ax_dst.set_ylabel(ax_src.get_ylabel())
            ax_dst.set_title(ax_src.get_title())
            
            # Copy legend if present
            if ax_src.get_legend():
                ax_dst.legend(loc='best', fontsize=8)
            
            # Copy grid
            ax_dst.grid(True, alpha=0.3)
        
        # Add overall title
        title = f"Canister Car Dynamics (CdA = {result.cda:.4f} m²)"
        self.figure.suptitle(title, fontsize=14, fontweight='bold')
        
        self.figure.tight_layout(rect=[0, 0.03, 1, 0.97])
        self.canvas.draw()
    
    def _on_clear(self):
        """Handle clear button click."""
        self.cda_var.set(str(DEFAULT_CDA))
        self.interp_time_var.set("10.0")
        self._clear_results()
        self._show_welcome_message()
        self.status_var.set("Ready")
        self.current_result = None
    
    def _clear_results(self):
        """Clear all result displays."""
        self.time_20m_var.set("---")
        self.top_speed_var.set("---")


def run_gui():
    """Main function to run the GUI application."""
    root = tk.Tk()
    app = CanisterCarGUI(root)
    root.mainloop()