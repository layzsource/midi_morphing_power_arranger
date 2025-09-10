#pragma once

#include <string>
#include "SonolumiPhysics.h"

class Simulator {
public:
    Simulator();

    // Set simulation parameters from Python
    void set_parameters(double frequency_hz, double pressure_atm, double radius_mm, const std::string& gas_type, const std::string& liquid_type);

    // Run one simulation step
    void step();

    // Get real-time simulation metrics
    double get_bubble_radius() const;
    double get_peak_temperature() const;
    double get_light_intensity() const;

private:
    SonolumiPhysics physics;
    // Current state variables
    double current_bubble_radius;
    double current_peak_temperature;
    double current_light_intensity;
};
