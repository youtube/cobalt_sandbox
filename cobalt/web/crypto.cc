// Copyright 2015 The Cobalt Authors. All Rights Reserved.
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

#include "cobalt/web/crypto.h"

#include "cobalt/web/dom_exception.h"
#include "crypto/random.h"

namespace cobalt {
namespace web {

// https://www.w3.org/TR/WebCryptoAPI/#Crypto-attribute-subtle
scoped_refptr<subtlecrypto::SubtleCrypto> Crypto::subtle(
    script::EnvironmentSettings* settings) {
  if (!subtle_crypto_) {
    subtle_crypto_ = new subtlecrypto::SubtleCrypto(settings);
  }
  return subtle_crypto_;
}

// https://www.w3.org/TR/WebCryptoAPI/#dfn-Crypto-method-getRandomValues
// static
script::Handle<script::ArrayBufferView> Crypto::GetRandomValues(
    const script::Handle<script::ArrayBufferView>& array,
    script::ExceptionState* exception_state) {
  // If the length of the array in bytes exceeds the following constant,
  // getRandomValues() should raise QuotaExceedErr instead of filling the array
  // with random values.
  uint32 kMaxArrayLengthInBytes = 65536;
  if (array.IsEmpty()) {
    // TODO: Also throw exception if element type of the array is
    // not one of the integer types.
    web::DOMException::Raise(web::DOMException::kTypeMismatchErr,
                             exception_state);
    // Return value should be ignored.
    return script::Handle<script::ArrayBufferView>();
  }
  if (array->ByteLength() > kMaxArrayLengthInBytes) {
    web::DOMException::Raise(web::DOMException::kQuotaExceededErr,
                             exception_state);
    // Return value should be ignored.
    return script::Handle<script::ArrayBufferView>();
  }
  ::crypto::RandBytes(array->RawData(), array->ByteLength());
  return array;
}

}  // namespace web
}  // namespace cobalt
