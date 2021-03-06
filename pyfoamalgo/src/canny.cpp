/**
 * Distributed under the terms of the GNU General Public License v3.0.
 *
 * The full license is in the file LICENSE, distributed with this software.
 *
 * Copyright (C) 2020, Jun Zhu. All rights reserved.
 */

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "foamalgo/canny.hpp"
#include "pyconfig.hpp"

namespace py = pybind11;


PYBIND11_MODULE(canny, m)
{
  m.doc() = "Canny edge detection implementation.";

  xt::import_numpy();

#define FOAM_CANNY_EDGE(INPUT_TYPE, RETURN_TYPE)                                                                              \
  m.def("cannyEdge",                                                                                             \
    (void (*)(const xt::pytensor<INPUT_TYPE, 2>& src, xt::pytensor<RETURN_TYPE, 2>& dst, double lb, double ub))  \
    &foam::cannyEdge<xt::pytensor<INPUT_TYPE, 2>, xt::pytensor<RETURN_TYPE, 2>>,                                 \
    py::arg("src").noconvert(), py::arg("dst").noconvert(),                                                      \
    py::arg("lb") = std::numeric_limits<double>::min(), py::arg("ub") = std::numeric_limits<double>::max());

  FOAM_CANNY_EDGE(double, double);
  FOAM_CANNY_EDGE(float, float);
  FOAM_CANNY_EDGE(double, uint8_t);
  FOAM_CANNY_EDGE(float, uint8_t);
}
