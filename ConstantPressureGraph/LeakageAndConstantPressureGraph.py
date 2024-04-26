import numpy as np
import matplotlib.pyplot as plt

class ConstantPressureGraph:
    def simulate_atmosphere_exportable_const_pressure(sealed_volume, leakage_coefficient, time_step, total_time, methane_inflow_rate, inert_gas_inflow_rate, inert_gas_purity, air_purity, average_pressure, max_pressure_change, pressure_period, pressure_time_offset, oxygen_depletion_rate, carbon_dioxide_inflow_rate, carbon_dioxide_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2):
        # Create a time array from 0 to total_time with time_step increments
        time = np.arange(0, total_time, time_step) / 3600  # Convert to hours
        leakage = []

        # Function to calculate barometric pressure (Pv) at a specific time
        def calculate_barometric_pressure(time):
            Pv = average_pressure
            return Pv

        # Calculate pressure within the sealed atmosphere using the provided equations for ingassing
        pressure_within = []
        partial_pressure_methane = initial_methane * calculate_barometric_pressure(0)  # Initial value
        partial_pressure_nitrogen = initial_nitrogen * calculate_barometric_pressure(0)  # Initial value
        partial_pressure_oxygen = initial_oxygen * calculate_barometric_pressure(0)  # Initial value
        partial_pressure_carbon_dioxide = initial_CO2 * calculate_barometric_pressure(0)  # Initial value
        total_pressure_within = partial_pressure_methane + partial_pressure_nitrogen + partial_pressure_oxygen + partial_pressure_carbon_dioxide
        T = 28 + 273.15  # Kelvin

        # Function for ingassing
        def ingassing(time):
            nonlocal partial_pressure_methane, partial_pressure_nitrogen, partial_pressure_oxygen, partial_pressure_carbon_dioxide, total_pressure_within
            Rho_m = 0.668  # density of methane (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_n = 1.2506  # density of nitrogen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_o = 1.429  # density of oxygen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_c = 1.977  # density of carbon dioxide (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            R_m = 518.47 # specific gas constant for methane (J/kg*K)
            R_n = 296.8 # specific gas constant for nitrogen (J/kg*K)
            R_o = 259.8 # specific gas constant for oxygen (J/kg*K)
            R_c = 188.9 # specific gas constant for carbon dioxide (J/kg*K)
            barometric_pressure = calculate_barometric_pressure(time)

            dPm_dt = (methane_inflow_rate * R_m * T * Rho_m) / (sealed_volume)  # Pa/s
            partial_pressure_methane += (dPm_dt * time_step)

            dPn_dt = ((inert_gas_purity * Rho_n * R_n * T * inert_gas_inflow_rate) / (sealed_volume)) + ((air_purity * Rho_n * R_n * T) / (sealed_volume)) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))  # Pa/s
            partial_pressure_nitrogen += (dPn_dt * time_step)

            dPo_dt = (((1-inert_gas_purity) * Rho_o * R_o * T * inert_gas_inflow_rate) / (sealed_volume)) + (((1-air_purity)* Rho_m * R_o * T)/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) - ((oxygen_depletion_rate * R_o * T)/(sealed_volume))  # Pa/s
            partial_pressure_oxygen += (dPo_dt * time_step)

            dPc_dt = (carbon_dioxide_inflow_rate * R_c * T * Rho_c/(sealed_volume)) + (carbon_dioxide_production_rate * R_c * T * partial_pressure_oxygen/(sealed_volume))  # Pa/s
            partial_pressure_carbon_dioxide += (dPc_dt * time_step)

            total_pressure_within = partial_pressure_methane + partial_pressure_nitrogen + partial_pressure_oxygen + partial_pressure_carbon_dioxide

        # Function for outgassing
        def outgassing(time):
            nonlocal partial_pressure_methane, partial_pressure_nitrogen, partial_pressure_oxygen, partial_pressure_carbon_dioxide, total_pressure_within
            Rho_m = 0.668  # density of methane (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_n = 1.2506  # density of nitrogen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_o = 1.429  # density of oxygen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            Rho_c = 1.977  # density of carbon dioxide (kg/m^3) at 28 degrees Celsius and 1 atm pressure
            R_m = 518.47 # specific gas constant for methane (J/kg*K)
            R_n = 296.8 # specific gas constant for nitrogen (J/kg*K)
            R_o = 259.8 # specific gas constant for oxygen (J/kg*K)
            R_c = 188.9 # specific gas constant for carbon dioxide (J/kg*K)
            barometric_pressure = calculate_barometric_pressure(time)

            dPm_dt = ((methane_inflow_rate * R_m * T * Rho_m) / (sealed_volume)) - ((partial_pressure_methane / sealed_volume) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure)))  # Pa/s
            partial_pressure_methane += (dPm_dt * time_step)

            dPn_dt = ((inert_gas_purity * Rho_n * R_n * T * inert_gas_inflow_rate) / (sealed_volume)) - (partial_pressure_nitrogen / (sealed_volume)) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))  # Pa/s
            partial_pressure_nitrogen += (dPn_dt * time_step)

            dPo_dt = (((1-inert_gas_purity) * Rho_o * R_o * T * inert_gas_inflow_rate) / (sealed_volume)) - (partial_pressure_oxygen/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) - oxygen_depletion_rate * R_o * T/(sealed_volume)  # Pa/s
            partial_pressure_oxygen += (dPo_dt * time_step)

            dPc_dt = (carbon_dioxide_inflow_rate * R_c * T * Rho_c/(sealed_volume)) + (carbon_dioxide_production_rate * R_c * T * partial_pressure_oxygen/(sealed_volume)) - ((partial_pressure_carbon_dioxide)/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) # Pa/s
            partial_pressure_carbon_dioxide += (dPc_dt * time_step)

            total_pressure_within = partial_pressure_methane + partial_pressure_nitrogen + partial_pressure_oxygen + partial_pressure_carbon_dioxide

        for t in time:
            barometric_pressure = calculate_barometric_pressure(t)
            if(total_pressure_within <= barometric_pressure):
                ingassing(t)
            else:
                outgassing(t)

            pressure_within.append(total_pressure_within/1e5)
            leakage_value = leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))
            leakage.append(leakage_value)

        # Create the figure and axis for the plot
        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Create a second Y-axis on the same X-axis
        ax2 = ax1.twinx()

        # Plot leakage on the first Y-axis
        ax1.plot(time, leakage, label='Leakage (m³/s)', color='b')
        ax1.set_xlabel('Time (hr)')
        ax1.set_ylabel('Leakage (m³/s) (in - or out +)', color='b')
        ax1.set_ylim(0, 1)  # Restrict the leakage y-axis
        ax1.set_yticks(np.arange(0, 1.1, 0.1))  # Show horizontal lines at increments of 0.1

        # Plot pressure within the sealed atmosphere and barometric pressure on the second Y-axis
        ax2.plot(time, pressure_within, label='Sealed Atmospheric Pressure (Pa)', color='r')
        constant_barometric_pressure = np.full_like(time, calculate_barometric_pressure(0) / 1e5)
        ax2.plot(time, constant_barometric_pressure, label='Barometric Pressure (Pa)', color='g')
        ax2.set_ylabel('Pressure (Pa)    x 100000', color='r')
        ax2.set_ylim(0.9, 1.1)  # Restrict the pressure y-axis

        # Manually set the x-axis ticks
        xticks = np.arange(0, total_time / 3600 + 1, 240)  # Generate ticks at 0, 240, 480, 720, ..., 1680
        xticks = np.append(xticks, total_time / 3600)  # Add 1680 as the last tick
        ax1.set_xticks(xticks)
        ax1.set_xlim(0, total_time / 3600)

        # Add legend for both plots
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines = lines1 + lines2
        labels = labels1 + labels2
        ax1.legend(lines, labels, loc='upper left')

        # Add a title and grid
        plt.title('Leakage, Sealed Atmospheric Pressure, and Barometric Pressure vs. Time')
        plt.grid(True)

        # Show the plot
        plt.show()