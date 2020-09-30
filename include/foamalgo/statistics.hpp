/**
 * Distributed under the terms of the BSD 3-Clause License.
 *
 * The full license is in the file BSD_LICENSE, distributed with this software.
 *
 * Author: Jun Zhu <jun.zhu@xfel.eu>
 * Copyright (C) European X-Ray Free-Electron Laser Facility GmbH.
 * All rights reserved.
 */
#ifndef FOAM_STATISTICS_HPP
#define FOAM_STATISTICS_HPP

#include <type_traits>

#include "xtensor/xview.hpp"
#include "xtensor/xmath.hpp"

#if defined(FOAM_USE_TBB)
#include "tbb/parallel_for.h"
#include "tbb/blocked_range2d.h"
#endif

#include "traits.hpp"


namespace foam
{

} // foam


#endif //FOAM_STATISTICS_HPP
