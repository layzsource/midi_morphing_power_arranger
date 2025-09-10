#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "Simulator.h"

namespace py = pybind11;

PYBIND11_MODULE(sonolumi_physics, m) {
    m.doc() = "Pybind11 bindings for the sonoluminescence physics engine";

    py::class_<Simulator>(m, "Simulator")
        .def(py::init<>())
        .def("set_parameters", &Simulator::set_parameters)
        .def("step", &Simulator::step)
        .def("get_bubble_radius", &Simulator::get_bubble_radius)
        .def("get_peak_temperature", &Simulator::get_peak_temperature)
        .def("get_light_intensity", &Simulator::get_light_intensity);
}
