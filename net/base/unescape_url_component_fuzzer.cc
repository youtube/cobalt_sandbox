// Copyright 2015 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include <string>

#include "net/base/escape.h"
#include "starboard/types.h"

static const int kMaxUnescapeRule = 31;

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
  base::StringPiece path(reinterpret_cast<const char*>(data), size);
  for (int i = 0; i <= kMaxUnescapeRule; i++) {
    net::UnescapeURLComponent(path, static_cast<net::UnescapeRule::Type>(i));
  }

  return 0;
}
