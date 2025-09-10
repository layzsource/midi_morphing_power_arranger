#include "SonolumiPhysics.h"
#include <cmath>
#include <iostream>

SonolumiPhysics::SonolumiPhysics() :
    m_frequency_hz(0.0),
    m_pressure_atm(0.0),
    m_ambient_radius_mm(0.0),
    m_time(0.0),
    m_current_radius(0.0),
    m_max_temperature(0.0),
    m_light_intensity(0.0) {
}

void SonolumiPhysics::set_frequency(double freq_hz) { m_frequency_hz = freq_hz; }
void SonolumiPhysics::set_pressure(double pressure_atm) { m_pressure_atm = pressure_atm; }
void SonolumiPhysics::set_ambient_radius(double radius_mm) {
    m_ambient_radius_mm = radius_mm;
    m_current_radius = radius_mm;
}
void SonolumiPhysics::set_gas_type(const std::string& type) { m_gas_type = type; }
void SonolumiPhysics::set_liquid_type(const std::string& type) { m_liquid_type = type; }

void SonolumiPhysics::simulate_step() {
    // This is a placeholder for a true numerical solver.
    // In a real simulator, this would involve solving the Rayleigh-Plesset equation
    // and a thermal model.
    m_time += 1.0 / 60.0; // Assume 60 FPS for now

    // Simple parametric model for demonstration
    double period = 1.0 / m_frequency_hz;
    double t_in_period = fmod(m_time, period);

    // Simulate bubble collapse behavior
    if (t_in_period < period * 0.9) {
        // Expansion phase
        m_current_radius = m_ambient_radius_mm * (1.0 + 1.0 * sin(t_in_period / period * M_PI));
        m_max_temperature = 0;
    } else {
        // Collapse phase (briefly)
        m_current_radius = m_ambient_radius_mm * (1.0 - 0.5 * sin((t_in_period - period * 0.9) / (period * 0.1) * M_PI));
        
        // Simulating extreme temperature and light flash
        if (m_current_radius < m_ambient_radius_mm * 0.5) {
            double compression_ratio = m_ambient_radius_mm * 0.5 / m_current_radius;
            m_max_temperature = 50000.0 * compression_ratio;
            m_light_intensity = model_thermal_emission(m_max_temperature);
        } else {
            m_max_temperature = 0;
            m_light_intensity = 0;
        }
    }
}

double SonolumiPhysics::get_radius() const { return m_current_radius; }
double SonolumiPhysics::get_max_temperature() const { return m_max_temperature; }
double SonolumiPhysics::get_emitted_light() const { return m_light_intensity; }

double SonolumiPhysics::model_thermal_emission(double temp) const {
    if (temp < 1000.0) return 0.0;
    // Simple exponential increase for demonstration
    return std::exp((temp - 1000.0) / 10000.0);
}
