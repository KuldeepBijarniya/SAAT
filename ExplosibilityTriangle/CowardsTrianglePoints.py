import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Cowards Triangle plot code
class ExplosibilityTriangle:
    def plot_cowards_triangle(sealed_volume, leakage_coefficient, time_step, total_time, methane_inflow_rate, inert_gas_inflow_rate, inert_gas_purity, air_purity, average_pressure, max_pressure_change, pressure_period, pressure_time_offset, oxygen_depletion_rate, carbon_dioxide_inflow_rate, carbon_dioxide_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2):
        # Define points
        points = {
            'A': (0, 20.93),
            'B': (5.4, 19.93),
            'C': (14.8, 17.93),
            'D': (103.103, 0),
            'E': (6.0, 12.5),
            'F': (14.8, 0),
            'O': (0, 0)
        }

        # Extract X and Y coordinates
        x = [point[0] for point in points.values()]
        y = [point[1] for point in points.values()]

        # Plot triangle
        plt.figure(figsize=(8, 6))

        # Plot individual triangles
        triangle_BCE = Polygon([points['B'], points['C'], points['E']], closed=True, edgecolor='r', facecolor='r', alpha=0.3)
        triangle_ACE = Polygon([points['A'], points['B'], points['E']], closed=True, edgecolor='b', facecolor='purple', alpha=0.3)
        triangle_DCEF = Polygon([points['D'], points['C'], points['E'], points['F']], closed=True, edgecolor='b', facecolor='purple', alpha=0.3)
        triangle_AEF = Polygon([points['A'], points['E'], points['F'], points['O']], closed=True, edgecolor='g', facecolor='green', alpha=0.3)

        plt.gca().add_patch(triangle_BCE)
        plt.gca().add_patch(triangle_ACE)
        plt.gca().add_patch(triangle_DCEF)
        plt.gca().add_patch(triangle_AEF)

        # Plot points
        plt.plot(x, y, 'ko')

        # Add labels
        for point, coord in points.items():
            plt.text(coord[0], coord[1], f'{point} ({coord[0]}, {coord[1]})')

        # Set axis limits and labels
        plt.xlim(0, 103.103)
        plt.ylim(0, 22)
        plt.xticks(range(0, 104, 10))
        plt.yticks(range(0, 23, 2))
        plt.xlabel('Combustible Gas Percentage')
        plt.ylabel('Oxygen Percentage')

        # Add text annotations
        plt.text(5.5, 18, 'Explosive', fontsize=8, color='red')
        plt.text(25, 6, 'Not Explosive (explosive if mixed more air)', fontsize=8, color='purple')
        plt.text(1, 8, 'Non-Explosive', fontsize=8, color='green')

        plt.title('Cowards Explosibility Triangle')

        # Simulation code

        class ConcentrationGraph:
            def simulate_atmosphere_exportable(sealed_volume, leakage_coefficient, time_step, total_time, methane_inflow_rate, inert_gas_inflow_rate, inert_gas_purity, air_purity, average_pressure, max_pressure_change, pressure_period, pressure_time_offset, oxygen_depletion_rate, carbon_dioxide_inflow_rate, carbon_dioxide_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2):
                # Create a time array from 0 to total_time with time_step increments
                time = np.arange(0, total_time, time_step) / 3600  # Convert to hours
                leakage = []
                methane_concentration = []
                nitrogen_concentration = []
                oxygen_concentration = []
                carbon_dioxide_concentration = []

                # Function to calculate barometric pressure (Pv) at a specific time
                def calculate_barometric_pressure(time):
                    Pv = average_pressure + (max_pressure_change) * np.sin(2 * np.pi * (time * 3600 - pressure_time_offset) / pressure_period)
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
                    Rho_m = 0.668  # density of methane (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_n = 1.2506  # density of nitrogen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_o = 1.429  # density of oxygen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_c = 1.977  # density of carbon dioxide (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    R_m = 518.47 # specific gas constant for methane (J/kg*K)
                    R_n = 296.8 # specific gas constant for nitrogen (J/kg*K)
                    R_o = 259.8 # specific gas constant for oxygen (J/kg*K)
                    R_c = 188.9 # specific gas constant for carbon dioxide (J/kg*K)
                    nonlocal partial_pressure_methane, partial_pressure_nitrogen, partial_pressure_oxygen, partial_pressure_carbon_dioxide, total_pressure_within
                    barometric_pressure = calculate_barometric_pressure(time)

                    dPm_dt = (methane_inflow_rate * R_m * T * Rho_m) / (sealed_volume)  # Pa/s
                    partial_pressure_methane += dPm_dt * time_step

                    dPn_dt = ((inert_gas_purity * Rho_n * R_n * T * inert_gas_inflow_rate) / (sealed_volume)) + ((air_purity * Rho_n * R_n * T) / (sealed_volume)) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))  # Pa/s
                    partial_pressure_nitrogen += dPn_dt * time_step

                    dPo_dt = (((1-inert_gas_purity) * Rho_o * R_o * T * inert_gas_inflow_rate) / (sealed_volume)) + (((1-air_purity)* Rho_m * R_o * T)/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) - ((oxygen_depletion_rate * R_o * T)/(sealed_volume))  # Pa/s
                    partial_pressure_oxygen += dPo_dt * time_step

                    dPc_dt = (carbon_dioxide_inflow_rate * R_c * T * Rho_c/(sealed_volume)) + (carbon_dioxide_production_rate * R_c * T * partial_pressure_oxygen/(sealed_volume))  # Pa/s
                    partial_pressure_carbon_dioxide += dPc_dt * time_step

                    total_pressure_within = partial_pressure_methane + partial_pressure_nitrogen + partial_pressure_oxygen + partial_pressure_carbon_dioxide

                    methane_percentage = (partial_pressure_methane / total_pressure_within) * 100
                    methane_concentration.append(methane_percentage)

                    nitrogen_percentage = (partial_pressure_nitrogen / total_pressure_within) * 100
                    nitrogen_concentration.append(nitrogen_percentage)

                    oxygen_percentage = (partial_pressure_oxygen / total_pressure_within) * 100
                    oxygen_concentration.append(oxygen_percentage)

                    carbon_dioxide_percentage = (partial_pressure_carbon_dioxide / total_pressure_within) * 100
                    carbon_dioxide_concentration.append(carbon_dioxide_percentage)

                # Function for outgassing
                def outgassing(time):
                    Rho_m = 0.668  # density of methane (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_n = 1.2506  # density of nitrogen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_o = 1.429  # density of oxygen (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    Rho_c = 1.977  # density of carbon dioxide (kg/m^3) at 28 degrees Celsius and 1 atm pressure
                    R_m = 518.47 # specific gas constant for methane (J/kg*K)
                    R_n = 296.8 # specific gas constant for nitrogen (J/kg*K)
                    R_o = 259.8 # specific gas constant for oxygen (J/kg*K)
                    R_c = 188.9 # specific gas constant for carbon dioxide (J/kg*K)
                    nonlocal partial_pressure_methane, partial_pressure_nitrogen, partial_pressure_oxygen, partial_pressure_carbon_dioxide, total_pressure_within
                    barometric_pressure = calculate_barometric_pressure(time)

                    dPm_dt = ((methane_inflow_rate * R_m * T * Rho_m) / (sealed_volume)) - ((partial_pressure_methane / sealed_volume) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure)))  # Pa/s
                    partial_pressure_methane += dPm_dt * time_step

                    dPn_dt = ((inert_gas_purity * Rho_n * R_n * T * inert_gas_inflow_rate) / (sealed_volume)) - (partial_pressure_nitrogen / (sealed_volume)) * leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))  # Pa/s
                    partial_pressure_nitrogen += dPn_dt * time_step

                    dPo_dt = (((1-inert_gas_purity) * Rho_o * R_o * T * inert_gas_inflow_rate) / (sealed_volume)) - (partial_pressure_oxygen/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) - oxygen_depletion_rate * R_o * T/(sealed_volume)  # Pa/s
                    partial_pressure_oxygen += dPo_dt * time_step

                    dPc_dt = (carbon_dioxide_inflow_rate * R_c * T * Rho_c/(sealed_volume)) + (carbon_dioxide_production_rate * R_c * T * partial_pressure_oxygen/(sealed_volume)) - ((partial_pressure_carbon_dioxide)/(sealed_volume))*(leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))) # Pa/s
                    partial_pressure_carbon_dioxide += dPc_dt * time_step

                    total_pressure_within = partial_pressure_methane + partial_pressure_nitrogen + partial_pressure_oxygen + partial_pressure_carbon_dioxide

                    methane_percentage = (partial_pressure_methane / total_pressure_within) * 100
                    methane_concentration.append(methane_percentage)

                    nitrogen_percentage = (partial_pressure_nitrogen / total_pressure_within) * 100
                    nitrogen_concentration.append(nitrogen_percentage)

                    oxygen_percentage = (partial_pressure_oxygen / total_pressure_within) * 100
                    oxygen_concentration.append(oxygen_percentage)

                    carbon_dioxide_percentage = (partial_pressure_carbon_dioxide / total_pressure_within) * 100
                    carbon_dioxide_concentration.append(carbon_dioxide_percentage)

                for t in time:
                    barometric_pressure = calculate_barometric_pressure(t)
                    if(total_pressure_within <= barometric_pressure):
                        ingassing(t)
                    else:
                        outgassing(t)

                    pressure_within.append(total_pressure_within/1e5)
                    leakage_value = leakage_coefficient * np.sqrt(abs(total_pressure_within - barometric_pressure))
                    leakage.append(leakage_value)
                return time, methane_concentration, oxygen_concentration

        # Run the simulation
        time, methane_concentration, oxygen_concentration = ConcentrationGraph.simulate_atmosphere_exportable(sealed_volume, leakage_coefficient, time_step, total_time, methane_inflow_rate, inert_gas_inflow_rate, inert_gas_purity, air_purity, average_pressure, max_pressure_change, pressure_period, pressure_time_offset, oxygen_depletion_rate, carbon_dioxide_inflow_rate, carbon_dioxide_production_rate, initial_methane, initial_nitrogen, initial_oxygen, initial_CO2)

        # Calculate coordinates in the Cowards Triangle
        methane_percentage = np.array(methane_concentration)
        oxygen_percentage = np.array(oxygen_concentration)
        x_triangle = methane_percentage
        y_triangle = oxygen_percentage

        # Plot trajectory in the Cowards Triangle
        plt.plot(x_triangle, y_triangle, marker='o', color='black')

        # Show plot
        plt.grid(True)
        plt.show()