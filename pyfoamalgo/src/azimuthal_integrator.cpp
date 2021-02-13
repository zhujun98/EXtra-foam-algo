/**
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file BSD_LICENSE, distributed with this software.
 *
 * Author: Jun Zhu <jun.zhu@xfel.eu>
 * Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
 * All rights reserved.
 */
#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "foamalgo/azimuthal_integrator.hpp"
#include "pyconfig.hpp"

namespace py = pybind11;

template<typename T>
void declareAzimuthalIntegrator(py::module& m)
{
  using Integrator = foam::AzimuthalIntegrator<T>;

  std::string py_class_name = "AzimuthalIntegrator";
  py::class_<Integrator> cls(m, py_class_name.c_str());

  cls.def(py::init<T, T, T, T, T, T>(),
          py::arg("dist"), py::arg("poni1"), py::arg("poni2"),
          py::arg("pixel1"), py::arg("pixel2"), py::arg("wavelength"));

#define AZIMUTHAL_INTEGRATE1D(DTYPE)                                                                  \
  cls.def("integrate1d", (std::pair<foam::ReducedVectorType<xt::pytensor<DTYPE, 2>, T>,               \
                                    foam::ReducedVectorType<xt::pytensor<DTYPE, 2>, T>>               \
                          (Integrator::*)(const xt::pytensor<DTYPE, 2>&, size_t, size_t,              \
                                          foam::AzimuthalIntegrationMethod))                          \
     &Integrator::template integrate1d<const xt::pytensor<DTYPE, 2>&>,                                \
     py::arg("src").noconvert(), py::arg("npt"), py::arg("min_count")=1,                              \
     py::arg("method")=foam::AzimuthalIntegrationMethod::HISTOGRAM);

  // for image data type at XFEL
  AZIMUTHAL_INTEGRATE1D(float)
  AZIMUTHAL_INTEGRATE1D(uint16_t)
  AZIMUTHAL_INTEGRATE1D(int16_t)

#define AZIMUTHAL_INTEGRATE1D_PARA(DTYPE)                                                             \
  cls.def("integrate1d", (std::pair<foam::ReducedVectorType<xt::pytensor<DTYPE, 2>, T>,               \
                                    foam::ReducedImageType<xt::pytensor<DTYPE, 3>, T>>                \
                          (Integrator::*)(const xt::pytensor<DTYPE, 3>&, size_t, size_t,              \
                                          foam::AzimuthalIntegrationMethod))                          \
     &Integrator::template integrate1d<const xt::pytensor<DTYPE, 3>&>,                                \
     py::arg("src").noconvert(), py::arg("npt"), py::arg("min_count")=1,                              \
     py::arg("method")=foam::AzimuthalIntegrationMethod::HISTOGRAM);

  AZIMUTHAL_INTEGRATE1D_PARA(float)
  AZIMUTHAL_INTEGRATE1D_PARA(uint16_t)
  AZIMUTHAL_INTEGRATE1D_PARA(int16_t)
}

template<typename T>
void declareConcentricRingsFinder(py::module& m)
{
  using Finder = foam::ConcentricRingsFinder<T>;

  std::string py_class_name = "ConcentricRingsFinder";
  py::class_<Finder> cls(m, py_class_name.c_str());

  cls.def(py::init<T, T>(), py::arg("pixel_x"), py::arg("pixel_y"));

#define CONCENTRIC_RING_FINDER_SEARCH(DTYPE)                                                            \
  cls.def("search", (std::array<T, 2>                                                                   \
                     (Finder::*)(const xt::pytensor<DTYPE, 2>&, T, T, size_t) const)                    \
     &Finder::template search<const xt::pytensor<DTYPE, 2>&>,                                           \
     py::arg("src").noconvert(), py::arg("cx0"), py::arg("cy0"), py::arg("min_count") = 1);

  CONCENTRIC_RING_FINDER_SEARCH(float)
  CONCENTRIC_RING_FINDER_SEARCH(uint16_t)
  CONCENTRIC_RING_FINDER_SEARCH(int16_t)


#define CONCENTRIC_RING_FINDER_INTEGRATE(DTYPE)                                                         \
  cls.def("integrate", (std::pair<foam::ReducedVectorType<xt::pytensor<DTYPE, 2>, T>,                   \
                                  foam::ReducedVectorType<xt::pytensor<DTYPE, 2>, T>>                   \
                        (Finder::*)(const xt::pytensor<DTYPE, 2>&, T, T, size_t) const)                 \
     &Finder::template integrate<const xt::pytensor<DTYPE, 2>&>,                                        \
     py::arg("src").noconvert(), py::arg("cx0"), py::arg("cy0"), py::arg("min_count") = 1);

  CONCENTRIC_RING_FINDER_INTEGRATE(float)
  CONCENTRIC_RING_FINDER_INTEGRATE(uint16_t)
  CONCENTRIC_RING_FINDER_INTEGRATE(int16_t)
}


PYBIND11_MODULE(azimuthal_integrator, m)
{
  m.doc() = "Azimuthal integration.";

  xt::import_numpy();

  py::enum_<foam::AzimuthalIntegrationMethod>(m, "AzimuthalIntegrationMethod", py::arithmetic())
    .value("Histogram", foam::AzimuthalIntegrationMethod::HISTOGRAM);

  declareAzimuthalIntegrator<float>(m);

  declareConcentricRingsFinder<float>(m);
}