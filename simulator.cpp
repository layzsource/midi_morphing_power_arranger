#include "Simulator.h"
#include <iostream>

Simulator::Simulator() :
    current_bubble_radius(0.0),
    current_peak_temperature(0.0),
    current_light_intensity(0.0) {
    // Initialize with default values or from a config file
    set_parameters(20000.0, 1.35, 0.005, "Argon", "Water");
}

void Simulator::set_parameters(double frequency_hz, double pressure_atm, double radius_mm, const std::string& gas_type, const std::string& liquid_type) {
    // Set parameters in the underlying physics engine
    physics.set_frequency(frequency_hz);
    physics.set_pressure(pressure_atm);
    physics.set_ambient_radius(radius_mm);
    physics.set_gas_type(gas_type);
    physics.set_liquid_type(liquid_type);
    // Reset simulation state
    current_bubble_radius = radius_mm;
    current_peak_temperature = 0.0;
    current_light_intensity = 0.0;
    std::cout << "C++: Simulation parameters updated." << std::endl;
}

void Simulator::step() {
    // Run one step of the physics simulation
    physics.simulate_step();

    // Update real-time state variables
    current_bubble_radius = physics.get_radius();
    current_peak_temperature = physics.get_max_temperature();
    current_light_intensity = physics.get_emitted_light();
}

double Simulator::get_bubble_radius() const {
    return current_bubble_radius;
}

double Simulator::get_peak_temperature() const {
    return current_peak_temperature;
}

double Simulator::get_light_intensity() const {
    return current_light_intensity;
}
