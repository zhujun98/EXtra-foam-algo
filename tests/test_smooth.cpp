#include "gtest/gtest.h"
#include "gmock/gmock.h"

#include <xtensor/xio.hpp>

#include "foamalgo/smooth.hpp"

namespace foam::test
{

using ::testing::Each;
using ::testing::Eq;
using ::testing::ElementsAre;
using ::testing::FloatNear;

TEST(TestGetGaussianKernel, TestGeneral)
{
  EXPECT_THROW(getGaussianKernel<double>(2), std::invalid_argument);
  EXPECT_THAT(getGaussianKernel<double>(-1), ElementsAre(1.));
  EXPECT_THAT(getGaussianKernel<double>(1), ElementsAre(1.));
  EXPECT_THAT(getGaussianKernel<float>(3, 0.85),
              ElementsAre(FloatNear(0.25, 1e-3), FloatNear(0.50, 1e-3), FloatNear(0.25, 1e-3)));
}

TEST(TestGaussianBlur, TestGeneral)
{
  xt::xtensor<float, 2> src {xt::ones<float>({6, 8})};
  xt::xtensor<float, 2> dst {xt::ones<float>({6, 8})};

  gaussianBlur(src, dst, 5);
  ASSERT_THAT(dst, Each(Eq(1.f)));
}

} //foam::test