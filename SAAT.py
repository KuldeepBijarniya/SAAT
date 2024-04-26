import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import Label, Entry, Button, font, Toplevel, Text, END
from tkinter import ttk
from ConcentrationGraph.ConcVSTime import ConcentrationGraph
from ConstantPressureGraph.LeakageAndConstantPressureGraph import ConstantPressureGraph
from CyclicPressureGraph.LeakageandCyclicPresureGraph import CyclicPressureGraph
from ExplosibilityTriangle.CowardsTriangle import ExplosibilityTriangle
# from ExplosibilityTriangle.CowardsTrianglePoints import ExplosibilityTriangle

def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Define global variables to store simulation data (you can replace these with actual simulation results)
time_values = [0]
methane_concentration = [1]
nitrogen_concentration = [79]
oxygen_concentration = [20]
CO2_concentration = [0]
leakage_values = [0]
sealed_pressure_values = [101325]  # Placeholder for sealed pressure data
barometric_pressure_values = [101325]  # Placeholder for barometric pressure data
# Define other global variables
V = 0
LC = 0
Q_inert = 0
inert_gas_purity = 0
Q_CO2 = 0
CO2_production_rate = 0
O2_depletion_rate = 0
time_step = 0
total_time = 0
Qm = 0
air_purity = 0
initial_methane = 0
initial_nitrogen = 0
initial_oxygen = 0
initial_CO2 = 0
average_pressure = 0
max_pressure_change = 0
period = 0
time_offset = 0

# Function to run the simulation
def run_simulation():
    # Get user input from the GUI
    # Define simulation parameters based on user input
    global time_values, methane_concentration, nitrogen_concentration, oxygen_concentration, CO2_concentration
    global leakage_values, sealed_pressure_values, barometric_pressure_values
    global V, LC, Q_inert, inert_gas_purity, Q_CO2, CO2_production_rate, O2_depletion_rate
    global time_step, total_time, Qm, air_purity, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2
    global average_pressure, max_pressure_change, period, time_offset

    V = float(volume_entry.get()) * 1e3
    LC = float(leakage_coefficient_entry.get())
    Q_inert = float(inert_gas_inflow_entry.get())
    inert_gas_purity = float(inert_gas_purity_entry.get())
    Q_CO2 = float(CO2_inflow_entry.get())
    CO2_production_rate = float(CO2_production_rate_entry.get())
    O2_depletion_rate = float(O2_depletion_rate_entry.get())
    time_step = float(time_step_entry.get())
    total_time = float(total_time_entry.get()) * 3600
    Qm = float(methane_inflow_entry.get())
    air_purity = float(air_purity_entry.get())
    initial_methane = float(initial_methane_entry.get()) / 100
    initial_nitrogen = float(initial_nitrogen_entry.get()) / 100
    initial_oxygen = float(initial_oxygen_entry.get()) / 100
    initial_CO2 = float(initial_CO2_entry.get()) / 100
    average_pressure = float(average_pressure_entry.get())
    max_pressure_change = float(max_pressure_change_entry.get())
    period = float(period_entry.get()) * 3600
    time_offset = float(time_offset_entry.get()) * 3600

    # Arrays to store results over time
    time_values = [0]
    methane_concentration = [initial_methane]
    nitrogen_concentration = [initial_nitrogen]
    oxygen_concentration = [initial_oxygen]
    CO2_concentration = [initial_CO2]
    sealed_pressure = [average_pressure]

    # Arrays to store leakage and pressure data
    leakage_values = [0]
    barometric_pressure_values = [average_pressure * 1e5]  # Convert to Pa
    sealed_pressure_values = [average_pressure]

    # Simulation loop
    current_time = 0
    while current_time < total_time:
        # Calculate methane concentration change
        delta_methane = (Qm / V) * time_step

        # Calculate other gas concentration changes
        delta_nitrogen = -(Qm / V) * air_purity * time_step
        delta_oxygen = -(Qm / V) * (1 - air_purity) * time_step
        delta_CO2 = (CO2_production_rate / (initial_oxygen * average_pressure)) * time_step
        delta_CO2 -= (O2_depletion_rate / average_pressure) * time_step

        # Calculate pressure change based on leakage
        leakage = LC * (average_pressure - sealed_pressure[-1])
        delta_pressure = (Qm - leakage) * time_step

        # Update concentrations and sealed pressure
        methane_concentration.append(methane_concentration[-1] + delta_methane)
        nitrogen_concentration.append(nitrogen_concentration[-1] + delta_nitrogen)
        oxygen_concentration.append(oxygen_concentration[-1] + delta_oxygen)
        CO2_concentration.append(CO2_concentration[-1] + delta_CO2)
        sealed_pressure.append(sealed_pressure[-1] + delta_pressure)
        time_values.append(current_time)

        # Calculate barometric pressure (Pt(t))
        Pt = average_pressure + max_pressure_change * np.sin(2 * np.pi * current_time / period + time_offset)

        # Calculate leakage based on Pt and Pv
        Pv = Pt  # Assuming Pv is the same as Pt
        leakage = LC * np.sqrt(np.abs(Pt - Pv))
        leakage_values.append(-leakage)  # Negative sign for ingassing
        barometric_pressure_values.append(Pt * 1e5)  # Convert to Pa
        sealed_pressure_values.append(sealed_pressure[-1])

        current_time += time_step

    root.withdraw()

    options_window = Toplevel(root)
    options_window.title("Options")
    # Set the window size
    options_window.geometry("300x230")
    # Center the window on the screen
    center_window(options_window)

    def show_graphs():
        options_window.withdraw()
        create_graphs_window()
    
    def exp_triangle():
        options_window.withdraw()
        create_exp_triangle_window()

    def show_results():
        options_window.withdraw()
        create_results_window()

    def back_to_input():
        options_window.withdraw()
        root.deiconify()

    def exit_program():
        options_window.destroy()
        root.destroy()

    options_frame = ttk.Frame(options_window)
    options_frame.pack(padx=20, pady=20)

    show_graphs_button = ttk.Button(options_frame, text="Show Graphs", command=show_graphs)
    show_graphs_button.grid(row=0, column=0, padx=10, pady=10)

    show_results_button = ttk.Button(options_frame, text="Show Results", command=show_results)
    show_results_button.grid(row=0, column=1, padx=10, pady=10)

    exp_triangle_button = ttk.Button(options_frame, text="Explosibility Triangle", command=exp_triangle)
    exp_triangle_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    back_button = ttk.Button(options_frame, text="Back to Simulation Input", command=back_to_input)
    back_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    exit_button = ttk.Button(options_frame, text="Exit", command=exit_program)
    exit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

def create_graphs_window():
    graphs_window = Toplevel(root)
    graphs_window.title("Graphs")
    # Set the window size
    graphs_window.geometry("340x250")
    # Center the window on the screen
    center_window(graphs_window)

    def concentration_graph():
        ConcentrationGraph.simulate_atmosphere_exportable(V, LC, time_step, total_time, Qm, Q_inert, inert_gas_purity, air_purity, average_pressure, max_pressure_change, period, time_offset, O2_depletion_rate, Q_CO2, CO2_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2)

    def cyclic_leakage_pressure_graph():
        CyclicPressureGraph.simulate_atmosphere_exportable_cyclic_pressure(V, LC, time_step, total_time, Qm, Q_inert, inert_gas_purity, air_purity, average_pressure, max_pressure_change, period, time_offset, O2_depletion_rate, Q_CO2, CO2_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2)

    def constant_leakage_pressure_graph():
        ConstantPressureGraph.simulate_atmosphere_exportable_const_pressure(V, LC, time_step, total_time, Qm, Q_inert, inert_gas_purity, air_purity, average_pressure, max_pressure_change, period, time_offset, O2_depletion_rate, Q_CO2, CO2_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2)

    def back_to_input():
        graphs_window.destroy()  # Close the current window
        root.deiconify()  # Show the main window
        # Run the simulation again
        run_simulation()

    graphs_frame = ttk.Frame(graphs_window)
    graphs_frame.grid(row=0, column=0, padx=20, pady=20)

    concentration_button = ttk.Button(graphs_frame, text="Concentration Graph", command=concentration_graph)
    concentration_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    cyclic_leakage_pressure_button = ttk.Button(graphs_frame, text="Cyclic Leakage & Pressure Graph", command=cyclic_leakage_pressure_graph)
    cyclic_leakage_pressure_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    constant_leakage_pressure_button = ttk.Button(graphs_frame, text="Constant Leakage & Pressure Graph", command=constant_leakage_pressure_graph)
    constant_leakage_pressure_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')

    back_button = ttk.Button(graphs_frame, text="Back", command=back_to_input)
    back_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

def create_exp_triangle_window():
    ExplosibilityTriangle.plot_cowards_triangle(V, LC, time_step, total_time, Qm, Q_inert, inert_gas_purity, air_purity, average_pressure, max_pressure_change, period, time_offset, O2_depletion_rate, Q_CO2, CO2_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2)
    # go back to the options window
    run_simulation()

def create_results_window():
    results_window = Toplevel(root)
    results_window.title("Results")
    # Set the window size
    results_window.geometry("350x300")
    # Center the window on the screen
    center_window(results_window)

    # Function to display Summary Results Table of input parameters
    def summary_results():
        # Create a new results window
        results_window = Toplevel()
        results_window.title("Summary Results")
        # Set the window size
        results_window.geometry("450x350")
        # Center the window on the screen
        center_window(results_window)

        # Create a Table widget to display summary results
        summary_table = ttk.Treeview(results_window)
        summary_table.grid(row=0, column=0, padx=20, pady=20)

        # Define columns for the table
        summary_table['columns'] = ('Parameter', 'Value')

        # Format columns
        summary_table.column('#0', width=0, stretch=tk.NO)
        summary_table.column('Parameter', anchor=tk.CENTER, width=200)
        summary_table.column('Value', anchor=tk.CENTER, width=200)

        # Create headings for the columns
        summary_table.heading('#0', text='', anchor=tk.CENTER)
        summary_table.heading('Parameter', text='Parameter', anchor=tk.CENTER)
        summary_table.heading('Value', text='Value', anchor=tk.CENTER)
        
        # Insert summary results (you can replace this with your actual results)
        summary_table.insert(parent='', index='end', iid=0, text='', values=('Sealed Volume (m^3)', 1000))
        summary_table.insert(parent='', index='end', iid=1, text='', values=('Leakage Coefficient (m^3/s/Pa^5)', 0.00625))
        summary_table.insert(parent='', index='end', iid=2, text='', values=('Inert Gas Inflow (m^3/s)', 0.25))
        summary_table.insert(parent='', index='end', iid=3, text='', values=('Inert Gas Purity', 0.95))
        summary_table.insert(parent='', index='end', iid=4, text='', values=('Carbon Dioxide Inflow (m^3/s)', 0.0))
        summary_table.insert(parent='', index='end', iid=5, text='', values=('Carbon Dioxide Production Rate (kg/s/PaO2)', 0.0))
        summary_table.insert(parent='', index='end', iid=6, text='', values=('Oxygen Depletion Rate (kg/s/PaO2)', 0.0))
        summary_table.insert(parent='', index='end', iid=7, text='', values=('Time Step (sec)', 3600))
        summary_table.insert(parent='', index='end', iid=8, text='', values=('Total Time (hr)', 24))
        summary_table.insert(parent='', index='end', iid=9, text='', values=('Methane Inflow (m^3/s)', 0.1))
        summary_table.insert(parent='', index='end', iid=10, text='', values=('Air Purity (Nitrogen Fraction)', 0.79))
        summary_table.insert(parent='', index='end', iid=11, text='', values=('Initial Methane Concentration (%)', 1))
        summary_table.insert(parent='', index='end', iid=12, text='', values=('Initial Nitrogen Concentration (%)', 79))
        summary_table.insert(parent='', index='end', iid=13, text='', values=('Initial Oxygen Concentration (%)', 20))
        summary_table.insert(parent='', index='end', iid=14, text='', values=('Initial Carbon Dioxide Concentration (%)', 0))
        summary_table.insert(parent='', index='end', iid=15, text='', values=('Average Pressure (Pa)', 101325))
        summary_table.insert(parent='', index='end', iid=16, text='', values=('Max Pressure Change (Pa)', 100))
        summary_table.insert(parent='', index='end', iid=17, text='', values=('Period (hr)', 24))
        summary_table.insert(parent='', index='end', iid=18, text='', values=('Time Offset (hr)', 0))

        # Add a "Back" button to return to the previous window
        back_button = Button(results_window, text="Back", command=results_window.destroy)
        back_button.grid(row=1, column=0, padx=10, pady=10)

    def concentration_results():
        # Create a new results window
        results_window = Toplevel()
        results_window.title("Concentration Results")
        # Set the window size
        results_window.geometry("550x350")
        # Center the window on the screen
        center_window(results_window)

        # Create a Table widget to display concentration results
        concentration_table = ttk.Treeview(results_window)
        concentration_table.grid(row=0, column=0, padx=10, pady=10)

        # Define columns for the table
        concentration_table['columns'] = ('Time (hr)', 'Methane (%)', 'Nitrogen (%)', 'Oxygen (%)', 'CO2 (%)')

        # Format columns
        concentration_table.column('#0', width=0, stretch=tk.NO)
        concentration_table.column('Time (hr)', anchor=tk.CENTER, width=100)
        concentration_table.column('Methane (%)', anchor=tk.CENTER, width=100)
        concentration_table.column('Nitrogen (%)', anchor=tk.CENTER, width=100)
        concentration_table.column('Oxygen (%)', anchor=tk.CENTER, width=100)
        concentration_table.column('CO2 (%)', anchor=tk.CENTER, width=100)

        # Create headings for the columns
        concentration_table.heading('#0', text='', anchor=tk.CENTER)
        concentration_table.heading('Time (hr)', text='Time (hr)', anchor=tk.CENTER)
        concentration_table.heading('Methane (%)', text='Methane (%)', anchor=tk.CENTER)
        concentration_table.heading('Nitrogen (%)', text='Nitrogen (%)', anchor=tk.CENTER)
        concentration_table.heading('Oxygen (%)', text='Oxygen (%)', anchor=tk.CENTER)
        concentration_table.heading('CO2 (%)', text='CO2 (%)', anchor=tk.CENTER)

        # Insert concentration results (you can replace this with your actual results)
        concentration_table.insert(parent='', index='end', iid=0, text='', values=(0, 1, 79, 20, 0))
        concentration_table.insert(parent='', index='end', iid=1, text='', values=(1, 0.9, 79.1, 20, 0))
        concentration_table.insert(parent='', index='end', iid=2, text='', values=(2, 0.8, 79.2, 20, 0))
        concentration_table.insert(parent='', index='end', iid=3, text='', values=(3, 0.7, 79.3, 20, 0))
        concentration_table.insert(parent='', index='end', iid=4, text='', values=(4, 0.6, 79.4, 20, 0))
        concentration_table.insert(parent='', index='end', iid=5, text='', values=(5, 0.5, 79.5, 20, 0))
        concentration_table.insert(parent='', index='end', iid=6, text='', values=(6, 0.4, 79.6, 20, 0))
        concentration_table.insert(parent='', index='end', iid=7, text='', values=(7, 0.3, 79.7, 20, 0))
        concentration_table.insert(parent='', index='end', iid=8, text='', values=(8, 0.2, 79.8, 20, 0))

        # Add a "Back" button to return to the previous window
        back_button = Button(results_window, text="Back", command=results_window.destroy)
        back_button.grid(row=1, column=0, padx=10, pady=10)

    def cyclic_leakage_pressure_results():
        # Create a new results window
        results_window = Toplevel()
        results_window.title("Cyclic Leakage & Pressure Results")
        # Set the window size
        results_window.geometry("450x350")
        # Center the window on the screen
        center_window(results_window)

        # Create a Text widget to display cyclic leakage & pressure results
        cyclic_leakage_pressure_text = Text(results_window, wrap=tk.WORD, width=40, height=10)
        cyclic_leakage_pressure_text.grid(row=0, column=0, padx=10, pady=10)

        # Insert cyclic leakage & pressure results (you can replace this with your actual results)
        cyclic_leakage_pressure_text.insert(END, "Placeholder for Cyclic Leakage & Pressure Results\n")
        cyclic_leakage_pressure_text.insert(END, "You can display cyclic leakage & pressure results here.")

        # Add a "Back" button to return to the previous window
        back_button = Button(results_window, text="Back", command=results_window.destroy)
        back_button.grid(row=1, column=0, padx=10, pady=10)

    def constant_leakage_pressure_results():
        # Create a new results window
        results_window = Toplevel()
        results_window.title("Constant Leakage & Pressure Results")
        # Set the window size
        results_window.geometry("450x350")
        # Center the window on the screen
        center_window(results_window)

        # Create a Text widget to display constant leakage & pressure results
        constant_leakage_pressure_text = Text(results_window, wrap=tk.WORD, width=40, height=10)
        constant_leakage_pressure_text.grid(row=0, column=0, padx=10, pady=10)

        # Insert constant leakage & pressure results (you can replace this with your actual results)
        constant_leakage_pressure_text.insert(END, "Placeholder for Constant Leakage & Pressure Results\n")
        constant_leakage_pressure_text.insert(END, "You can display constant leakage & pressure results here.")

        # Add a "Back" button to return to the previous window
        back_button = Button(results_window, text="Back", command=results_window.destroy)
        back_button.grid(row=1, column=0, padx=10, pady=10)

        results_frame = ttk.Frame(results_window)
        results_frame.pack(padx=20, pady=20)

        back_button = ttk.Button(results_frame, text="Back", command=run_simulation)
        back_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        concentration_button = ttk.Button(results_frame, text="Concentration Results", command=concentration_results)
        concentration_button.grid(row=1, column=0, padx=10, pady=10)

        cyclic_leakage_pressure_button = ttk.Button(results_frame, text="Cyclic Leakage & Pressure Results", command=cyclic_leakage_pressure_results)
        cyclic_leakage_pressure_button.grid(row=1, column=1, padx=10, pady=10)

        constant_leakage_pressure_button = ttk.Button(results_frame, text="Constant Leakage & Pressure Results", command=constant_leakage_pressure_results)
        constant_leakage_pressure_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
    
    def back_to_input():
        results_window.destroy()
        root.deiconify()
        run_simulation()

    results_frame = ttk.Frame(results_window)
    results_frame.grid(row=0, column=0, padx=20, pady=20)

    summary_results_button = ttk.Button(results_frame, text="Summary Results Table", command=summary_results)
    summary_results_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')

    concentration_button = ttk.Button(results_frame, text="Concentration Results", command=concentration_results)
    concentration_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')

    cyclic_leakage_pressure_button = ttk.Button(results_frame, text="Cyclic Leakage & Pressure Results", command=cyclic_leakage_pressure_results)
    cyclic_leakage_pressure_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')

    constant_leakage_pressure_button = ttk.Button(results_frame, text="Constant Leakage & Pressure Results", command=constant_leakage_pressure_results)
    constant_leakage_pressure_button.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    back_button = ttk.Button(results_frame, text="Back", command=back_to_input)
    back_button.grid(row=4, column=0, padx=10, pady=10, sticky='w')

def reset_simulation():
    initial_values = {
        "volume": 1000,
        "leakage_coefficient": 0.00625,
        "inert_gas_inflow": 0.0,
        "inert_gas_purity": 0.95,
        "CO2_inflow": 0.0,
        "CO2_production_rate": 0.0,
        "O2_depletion_rate": 0.0,
        "time_step": 200,
        "total_time": 1666.5,
        "methane_inflow": 0.25,
        "air_purity": 0.79,
        "initial_methane": 0,
        "initial_nitrogen": 79,
        "initial_oxygen": 21,
        "initial_CO2": 0,
        "average_pressure": 100765,
        "max_pressure_change": 3000,
        "period": 240,
        "time_offset": 120
    }
    volume_entry.delete(0, END)
    leakage_coefficient_entry.delete(0, END)
    inert_gas_inflow_entry.delete(0, END)
    inert_gas_purity_entry.delete(0, END)
    CO2_inflow_entry.delete(0, END)
    CO2_production_rate_entry.delete(0, END)
    O2_depletion_rate_entry.delete(0, END)
    time_step_entry.delete(0, END)
    total_time_entry.delete(0, END)
    methane_inflow_entry.delete(0, END)
    air_purity_entry.delete(0, END)
    initial_methane_entry.delete(0, END)
    initial_nitrogen_entry.delete(0, END)
    initial_oxygen_entry.delete(0, END)
    initial_CO2_entry.delete(0, END)
    average_pressure_entry.delete(0, END)
    max_pressure_change_entry.delete(0, END)
    period_entry.delete(0, END)
    time_offset_entry.delete(0, END)
    Measured_pressure_entry.delete(0, END)
    
    volume_entry.insert(0, initial_values["volume"])
    leakage_coefficient_entry.insert(0, initial_values["leakage_coefficient"])
    inert_gas_inflow_entry.insert(0, initial_values["inert_gas_inflow"])
    inert_gas_purity_entry.insert(0, initial_values["inert_gas_purity"])
    CO2_inflow_entry.insert(0, initial_values["CO2_inflow"])
    CO2_production_rate_entry.insert(0, initial_values["CO2_production_rate"])
    O2_depletion_rate_entry.insert(0, initial_values["O2_depletion_rate"])
    time_step_entry.insert(0, initial_values["time_step"])
    total_time_entry.insert(0, initial_values["total_time"])
    methane_inflow_entry.insert(0, initial_values["methane_inflow"])
    air_purity_entry.insert(0, initial_values["air_purity"])
    initial_methane_entry.insert(0, initial_values["initial_methane"])
    initial_nitrogen_entry.insert(0, initial_values["initial_nitrogen"])
    initial_oxygen_entry.insert(0, initial_values["initial_oxygen"])
    initial_CO2_entry.insert(0, initial_values["initial_CO2"])
    average_pressure_entry.insert(0, initial_values["average_pressure"])
    max_pressure_change_entry.insert(0, initial_values["max_pressure_change"])
    period_entry.insert(0, initial_values["period"])
    time_offset_entry.insert(0, initial_values["time_offset"])
    Measured_pressure_entry.insert(0, "")

    # Reset global variables (add any additional variables you need to reset)
    global time_values, methane_concentration, nitrogen_concentration, oxygen_concentration, CO2_concentration
    global leakage_values, sealed_pressure_values, barometric_pressure_values
    global V, LC, Q_inert, inert_gas_purity, Q_CO2, CO2_production_rate, O2_depletion_rate
    global time_step, total_time, Qm, air_purity, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2
    global average_pressure, max_pressure_change, period, time_offset

    time_values = [0]
    methane_concentration = [1]
    nitrogen_concentration = [79]
    oxygen_concentration = [20]
    CO2_concentration = [0]
    leakage_values = [0]
    sealed_pressure_values = [101325]
    barometric_pressure_values = [101325]

    # Reset any other global variables to their initial values
    V = 0
    LC = 0
    Q_inert = 0
    inert_gas_purity = 0
    Q_CO2 = 0
    CO2_production_rate = 0
    O2_depletion_rate = 0
    time_step = 0
    total_time = 0
    Qm = 0
    air_purity = 0
    initial_methane = 0
    initial_nitrogen = 0
    initial_oxygen = 0
    initial_CO2 = 0
    average_pressure = 0
    max_pressure_change = 0
    period = 0
    time_offset = 0

# Create the main window
root = tk.Tk()
root.title("Composition Change Model (CCM) for Sealed Atmosphere in Coal Mines")
# Set the window size
root.geometry("950x450")
# Center the window on the screen
center_window(root)

bold_font = font.Font(weight="bold")

# Create and place the heading at the top
Label(root, text="Composition Change Model (CCM) for Sealed Atmosphere in Coal Mines", font=bold_font).grid(row=0, columnspan=4)

# Create and place inputs on the left side
left_frame = tk.Frame(root)
left_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')

# Sealed Volume and Leakage Coefficient
Label(left_frame, text="Sealed Volume*10^3:").grid(row=0, column=0, sticky='w')
volume_entry = Entry(left_frame)
volume_entry.grid(row=0, column=1)
volume_entry.insert(0, "1000")

Label(left_frame, text="Leakage Coefficient (m^3/s/Pa^0.5):").grid(row=1, column=0, sticky='w')
leakage_coefficient_entry = Entry(left_frame)
leakage_coefficient_entry.grid(row=1, column=1)
leakage_coefficient_entry.insert(0, "0.00625")

# Seal Inerting section
Label(left_frame, text="Seal Inerting", font=bold_font).grid(row=2, column=0, columnspan=2, sticky='w')

Label(left_frame, text="Inert gas inflow (m^3/s):").grid(row=3, column=0, sticky='w')
inert_gas_inflow_entry = Entry(left_frame)
inert_gas_inflow_entry.grid(row=3, column=1)
inert_gas_inflow_entry.insert(0, "0.25")

Label(left_frame, text="Inert gas purity:").grid(row=4, column=0, sticky='w')
inert_gas_purity_entry = Entry(left_frame)
inert_gas_purity_entry.grid(row=4, column=1)
inert_gas_purity_entry.insert(0, "0.95")

Label(left_frame, text="Carbon dioxide inflow (m^3/s):").grid(row=5, column=0, sticky='w')
CO2_inflow_entry = Entry(left_frame)
CO2_inflow_entry.grid(row=5, column=1)
CO2_inflow_entry.insert(0, "0.0")

# Carbon oxidation section
Label(left_frame, text="Carbon Oxidation", font=bold_font).grid(row=6, column=0, columnspan=2, sticky='w')

Label(left_frame, text="Carbon dioxide production rate (kg/s/PaO2):").grid(row=7, column=0, sticky='w')
CO2_production_rate_entry = Entry(left_frame)
CO2_production_rate_entry.grid(row=7, column=1)
CO2_production_rate_entry.insert(0, "0.0")

Label(left_frame, text="Oxygen depletion rate (kg/s/PaO2):").grid(row=8, column=0, sticky='w')
O2_depletion_rate_entry = Entry(left_frame)
O2_depletion_rate_entry.grid(row=8, column=1)
O2_depletion_rate_entry.insert(0, "0.0")

# Create and place inputs on the right side
right_frame = tk.Frame(root)
right_frame.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# Time step and Total Time
Label(right_frame, text="Time step (sec):").grid(row=0, column=0, sticky='w')
time_step_entry = Entry(right_frame)
time_step_entry.grid(row=0, column=1)
time_step_entry.insert(0, "3600")

Label(right_frame, text="Total Time (hr):").grid(row=1, column=0, sticky='w')
total_time_entry = Entry(right_frame)
total_time_entry.grid(row=1, column=1)
total_time_entry.insert(0, "24")

# Methane inflow and Air purity
Label(right_frame, text="Methane inflow (m^3/s):").grid(row=2, column=0, sticky='w')
methane_inflow_entry = Entry(right_frame)
methane_inflow_entry.grid(row=2, column=1)
methane_inflow_entry.insert(0, "0.1")

Label(right_frame, text="Air purity (Nitrogen fraction):").grid(row=3, column=0, sticky='w')
air_purity_entry = Entry(right_frame)
air_purity_entry.grid(row=3, column=1)
air_purity_entry.insert(0, "0.79")

# Seal Atmosphere's initial concentration section
Label(right_frame, text="Seal Atmosphere's Initial Concentration", font=bold_font).grid(row=4, column=0, columnspan=2, sticky='w')

Label(right_frame, text="Methane (%):").grid(row=5, column=0, sticky='w')
initial_methane_entry = Entry(right_frame)
initial_methane_entry.grid(row=5, column=1)
initial_methane_entry.insert(0, "1")

Label(right_frame, text="Nitrogen (%):").grid(row=6, column=0, sticky='w')
initial_nitrogen_entry = Entry(right_frame)
initial_nitrogen_entry.grid(row=6, column=1)
initial_nitrogen_entry.insert(0, "79")

Label(right_frame, text="Oxygen (%):").grid(row=7, column=0, sticky='w')
initial_oxygen_entry = Entry(right_frame)
initial_oxygen_entry.grid(row=7, column=1)
initial_oxygen_entry.insert(0, "20")

Label(right_frame, text="Carbon dioxide (%):").grid(row=8, column=0, sticky='w')
initial_CO2_entry = Entry(right_frame)
initial_CO2_entry.grid(row=8, column=1)
initial_CO2_entry.insert(0, "0")

# Barometric Pressure Model section
Label(left_frame, text="Barometric Pressure Model (Sine Function)", font=bold_font).grid(row=9, column=0, columnspan=2, sticky='w')

# Left side of the Barometric Pressure Model
left_barometric_frame = tk.Frame(left_frame)
left_barometric_frame.grid(row=10, column=0, padx=10, pady=10, sticky='w')

Label(left_barometric_frame, text="Average Pressure (Pa):").grid(row=0, column=0, sticky='w')
average_pressure_entry = Entry(left_barometric_frame)
average_pressure_entry.grid(row=0, column=1)
average_pressure_entry.insert(0, "101325")

Label(left_barometric_frame, text="Max Pressure Change (Pa):").grid(row=1, column=0, sticky='w')
max_pressure_change_entry = Entry(left_barometric_frame)
max_pressure_change_entry.grid(row=1, column=1)
max_pressure_change_entry.insert(0, "100")

# In the Right half of the Barometric Pressure Model
right_barometric_frame = tk.Frame(left_frame)
right_barometric_frame.grid(row=10, column=1, padx=10, pady=10, sticky='w')

Label(right_barometric_frame, text="Period (hr):").grid(row=0, column=0, sticky='w')
period_entry = Entry(right_barometric_frame)
period_entry.grid(row=0, column=1)
period_entry.insert(0, "24")

Label(right_barometric_frame, text="Time Offset (hr):").grid(row=1, column=0, sticky='w')
time_offset_entry = Entry(right_barometric_frame)
time_offset_entry.grid(row=1, column=1)
time_offset_entry.insert(0, "0")

# Measured pressure-time section
Label(right_frame, text="Measured pressure-time", font=bold_font).grid(row=11, column=0, columnspan=2, sticky='w')

Label(right_frame, text="(Optional input)").grid(row=12, column=0, columnspan=2, sticky='w')
Measured_pressure_entry = Entry(right_frame)
Measured_pressure_entry.grid(row=13, column=0, columnspan=2)

# Create and place the "Run Simulation" button below
run_button = Button(root, text="Run Simulation", command=run_simulation, font=bold_font, bg='green', fg='white', padx=10, pady=10, bd=5, relief=tk.RAISED, activebackground='green', activeforeground='white', cursor='hand2')
run_button.grid(row=2, column=0, columnspan=1, padx=10, pady=10)

# Create and place the "Reset Simulation" button below
reset_button = Button(root, text="Reset Simulation", command=reset_simulation, font=bold_font, bg='red', fg='white', padx=10, pady=10, bd=5, relief=tk.RAISED, activebackground='red', activeforeground='white', cursor='hand2')
reset_button.grid(row=2, column=1, columnspan=1, padx=10, pady=10)


style = ttk.Style()
style.configure('TButton', font=('Arial', 12))

# Start the GUI main loop
root.mainloop()
