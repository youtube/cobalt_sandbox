// Copyright 2024 The Cobalt Authors. All Rights Reserved.
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

#if defined(ADDRESS_SANITIZER)

char kLSanDefaultSuppressions[] =
    // b/312772759
    "leak:swrast_dri.so\n"

    // PLEASE READ ABOVE BEFORE ADDING NEW SUPPRESSIONS.

    // End of suppressions.
    ;  // NOLINT: Please keep this semicolon.

// The callbacks we define here will be called from the sanitizer runtime, but
// aren't referenced from the Chrome executable. We must ensure that those
// callbacks are not sanitizer-instrumented, and that they aren't stripped by
// the linker.
#define SANITIZER_HOOK_ATTRIBUTE                                               \
  extern "C"                                                                   \
      __attribute__((no_sanitize("address", "memory", "thread", "undefined"))) \
      __attribute__((visibility("default"))) __attribute__((used))

extern char kLSanDefaultSuppressions[];

SANITIZER_HOOK_ATTRIBUTE const char* __lsan_default_suppressions() {
  return kLSanDefaultSuppressions;
}

char kASanDefaultSuppressions[] =
    // b/312772759
    "interceptor_via_lib:swrast_dri.so\n";  // NOLINT -- keep the separate line

extern char kASanDefaultSuppressions[];

SANITIZER_HOOK_ATTRIBUTE const char* _asan_default_suppressions() {
  return kASanDefaultSuppressions;
}

// may consider -fsanitize-blacklist=/home/some/path/blacklist-sgen

#endif  // defined(ADDRESS_SANITIZER)
