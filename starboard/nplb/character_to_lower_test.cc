// Copyright 2016 The Cobalt Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// This test doesn't test that the appropriate output was produced, but ensures
// it compiles and runs without crashing.

#include "starboard/character.h"
#include "testing/gtest/include/gtest/gtest.h"

#if SB_API_VERSION < 13

namespace starboard {
namespace nplb {
namespace {

TEST(SbCharacterToLowerTest, SunnyDay) {
  const char kInputs[] =
      "1234567890"
      "`~!@#$%^&*()_+-=[]\\{}|;':\",./<>?"
      "abcdefghijklmnopqrstuvwxyz"
      "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const char kExpected[] =
      "1234567890"
      "`~!@#$%^&*()_+-=[]\\{}|;':\",./<>?"
      "abcdefghijklmnopqrstuvwxyz"
      "abcdefghijklmnopqrstuvwxyz";
  for (int i = 0; i < SB_ARRAY_SIZE_INT(kInputs); ++i) {
    EXPECT_EQ(kExpected[i], static_cast<char>(SbCharacterToLower(kInputs[i])));
  }
}

}  // namespace
}  // namespace nplb
}  // namespace starboard

#endif  // SB_API_VERSION < 13
