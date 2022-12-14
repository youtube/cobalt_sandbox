// Copyright (c) 2017 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include "net/third_party/quic/quartc/quartc_stream.h"

#include <memory>
#include <utility>

#include "net/third_party/quic/core/quic_ack_listener_interface.h"
#include "net/third_party/quic/core/quic_error_codes.h"
#include "net/third_party/quic/core/quic_stream_send_buffer.h"
#include "net/third_party/quic/core/quic_stream_sequencer.h"
#include "net/third_party/quic/core/quic_stream_sequencer_buffer.h"
#include "net/third_party/quic/core/quic_types.h"
#include "net/third_party/quic/platform/api/quic_ptr_util.h"
#include "net/third_party/quic/platform/api/quic_reference_counted.h"
#include "net/third_party/quic/platform/api/quic_string_piece.h"

namespace quic {

QuartcStream::QuartcStream(QuicStreamId id, QuicSession* session)
    : QuicStream(id, session, /*is_static=*/false, BIDIRECTIONAL) {
  sequencer()->set_level_triggered(true);
}

QuartcStream::QuartcStream(PendingStream pending)
    : QuicStream(std::move(pending), BIDIRECTIONAL) {
  sequencer()->set_level_triggered(true);
}

QuartcStream::~QuartcStream() {}

void QuartcStream::OnDataAvailable() {
  bool fin = sequencer()->ReadableBytes() + sequencer()->NumBytesConsumed() ==
             sequencer()->close_offset();

  // Upper bound on number of readable regions.  Each complete block's worth of
  // data crosses at most one region boundary.  The remainder may cross one more
  // boundary.  Number of regions is one more than the number of region
  // boundaries crossed.
  size_t iov_length = sequencer()->ReadableBytes() /
                          QuicStreamSequencerBuffer::kBlockSizeBytes +
                      2;
  std::unique_ptr<IOVEC[]> IOVECs = QuicMakeUnique<IOVEC[]>(iov_length);
  iov_length = sequencer()->GetReadableRegions(IOVECs.get(), iov_length);

  sequencer()->MarkConsumed(
      delegate_->OnReceived(this, IOVECs.get(), iov_length, fin));
  if (sequencer()->IsClosed()) {
    OnFinRead();
  }
}

void QuartcStream::OnClose() {
  QuicStream::OnClose();
  DCHECK(delegate_);
  delegate_->OnClose(this);
}

void QuartcStream::OnStreamDataConsumed(size_t bytes_consumed) {
  QuicStream::OnStreamDataConsumed(bytes_consumed);

  DCHECK(delegate_);
  delegate_->OnBufferChanged(this);
}

void QuartcStream::OnDataBuffered(
    QuicStreamOffset offset,
    QuicByteCount data_length,
    const QuicReferenceCountedPointer<QuicAckListenerInterface>& ack_listener) {
  DCHECK(delegate_);
  delegate_->OnBufferChanged(this);
}

bool QuartcStream::OnStreamFrameAcked(QuicStreamOffset offset,
                                      QuicByteCount data_length,
                                      bool fin_acked,
                                      QuicTime::Delta ack_delay_time,
                                      QuicByteCount* newly_acked_length) {
  // Previous losses of acked data are no longer relevant to the retransmission
  // count.  Once data is acked, it will never be retransmitted.
  lost_frame_counter_.RemoveInterval(
      QuicInterval<QuicStreamOffset>(offset, offset + data_length));

  return QuicStream::OnStreamFrameAcked(offset, data_length, fin_acked,
                                        ack_delay_time, newly_acked_length);
}

void QuartcStream::OnStreamFrameRetransmitted(QuicStreamOffset offset,
                                              QuicByteCount data_length,
                                              bool fin_retransmitted) {
  QuicStream::OnStreamFrameRetransmitted(offset, data_length,
                                         fin_retransmitted);

  DCHECK(delegate_);
  delegate_->OnBufferChanged(this);
}

void QuartcStream::OnStreamFrameLost(QuicStreamOffset offset,
                                     QuicByteCount data_length,
                                     bool fin_lost) {
  QuicStream::OnStreamFrameLost(offset, data_length, fin_lost);

  lost_frame_counter_.AddInterval(
      QuicInterval<QuicStreamOffset>(offset, offset + data_length));

  DCHECK(delegate_);
  delegate_->OnBufferChanged(this);
}

void QuartcStream::OnCanWrite() {
  if (lost_frame_counter_.MaxCount() >
          static_cast<size_t>(max_retransmission_count_) &&
      HasPendingRetransmission()) {
    Reset(QUIC_STREAM_CANCELLED);
    return;
  }
  QuicStream::OnCanWrite();
}

bool QuartcStream::cancel_on_loss() {
  return max_retransmission_count_ == 0;
}

void QuartcStream::set_cancel_on_loss(bool cancel_on_loss) {
  if (cancel_on_loss) {
    max_retransmission_count_ = 0;
  } else {
    max_retransmission_count_ = std::numeric_limits<int>::max();
  }
}

int QuartcStream::max_retransmission_count() const {
  return max_retransmission_count_;
}

void QuartcStream::set_max_retransmission_count(int max_retransmission_count) {
  max_retransmission_count_ = max_retransmission_count;
}

QuicByteCount QuartcStream::BytesPendingRetransmission() {
  if (lost_frame_counter_.MaxCount() >
      static_cast<size_t>(max_retransmission_count_)) {
    return 0;  // Lost bytes will never be retransmitted.
  }
  QuicByteCount bytes = 0;
  for (const auto& interval : send_buffer().pending_retransmissions()) {
    bytes += interval.Length();
  }
  return bytes;
}

QuicStreamOffset QuartcStream::ReadOffset() {
  return sequencer()->NumBytesConsumed();
}

void QuartcStream::FinishWriting() {
  WriteOrBufferData(QuicStringPiece(nullptr, 0), true, nullptr);
}

void QuartcStream::SetDelegate(Delegate* delegate) {
  if (delegate_) {
    LOG(WARNING) << "The delegate for Stream " << id()
                 << " has already been set.";
  }
  delegate_ = delegate;
  DCHECK(delegate_);
}

}  // namespace quic
