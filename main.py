"""
Canister Car Track Time Calculator
Main entry point for the application.

This program calculates the track time for a canister-powered car
based on the drag coefficient and reference area (CdA) input.

Usage:
    python main.py

The program will launch a GUI where you can:
1. Enter the CdA value (drag coefficient × reference area)
2. Calculate the time to reach 20 meters
3. View the top speed and complete dynamics visualization
"""

import sys
import traceback
from gui import run_gui


def main():
    """Main entry point for the application."""
    try:
        print("=" * 60)
        print("Canister Car Track Time Calculator")
        print("=" * 60)
        print("\nStarting GUI application...")
        print("Please enter CdA value and click 'Calculate' to begin.\n")
        
        # Run the GUI
        run_gui()
        
        print("\nApplication closed successfully.")
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR: Application crashed")
        print("=" * 60)
        print(f"\nError message: {str(e)}\n")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()