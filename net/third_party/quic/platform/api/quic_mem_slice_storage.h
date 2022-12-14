// Copyright 2017 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef NET_THIRD_PARTY_QUIC_PLATFORM_API_QUIC_MEM_SLICE_STORAGE_H_
#define NET_THIRD_PARTY_QUIC_PLATFORM_API_QUIC_MEM_SLICE_STORAGE_H_

#include "net/third_party/quic/platform/api/quic_export.h"
#include "net/third_party/quic/platform/impl/quic_mem_slice_storage_impl.h"

namespace quic {

// QuicMemSliceStorage is a container class that store QuicMemSlices for further
// use cases such as turning into QuicMemSliceSpan.
class QUIC_EXPORT_PRIVATE QuicMemSliceStorage {
 public:
  QuicMemSliceStorage(const struct IOVEC* iov,
                      int iov_count,
                      QuicBufferAllocator* allocator,
                      const QuicByteCount max_slice_len)
      : impl_(iov, iov_count, allocator, max_slice_len) {}

  QuicMemSliceStorage(const QuicMemSliceStorage& other) = default;
  QuicMemSliceStorage& operator=(const QuicMemSliceStorage& other) = default;
  QuicMemSliceStorage(QuicMemSliceStorage&& other) = default;
  QuicMemSliceStorage& operator=(QuicMemSliceStorage&& other) = default;

  ~QuicMemSliceStorage() = default;

  // Return a QuicMemSliceSpan form of the storage.
  QuicMemSliceSpan ToSpan() { return impl_.ToSpan(); }

 private:
  QuicMemSliceStorageImpl impl_;
};

}  // namespace quic

#endif  // NET_THIRD_PARTY_QUIC_PLATFORM_API_QUIC_MEM_SLICE_STORAGE_H_
