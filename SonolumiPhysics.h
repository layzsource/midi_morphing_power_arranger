#pragma once

#include <string>

// A simplified model of single-bubble sonoluminescence
class SonolumiPhysics {
public:
    SonolumiPhysics();

    void set_frequency(double freq_hz);
    void set_pressure(double pressure_atm);
    void set_ambient_radius(double radius_mm);
    void set_gas_type(const std::string& type);
    void set_liquid_type(const std::string& type);

    void simulate_step();

    double get_radius() const;
    double get_max_temperature() const;
    double get_emitted_light() const;

private:
    // Parameters
    double m_frequency_hz;
    double m_pressure_atm;
    double m_ambient_radius_mm;
    std::string m_gas_type;
    std::string m_liquid_type;

    // State variables
    double m_time;
    double m_current_radius;
    double m_max_temperature;
    double m_light_intensity;

    // Numerical solver for Rayleigh-Plesset equation
    void solve_rayleigh_plesset(double dt);
    // Model for thermal emission
    double model_thermal_emission(double temp) const;
};
