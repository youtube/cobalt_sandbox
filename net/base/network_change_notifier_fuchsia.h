// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef NET_BASE_NETWORK_CHANGE_NOTIFIER_FUCHSIA_H_
#define NET_BASE_NETWORK_CHANGE_NOTIFIER_FUCHSIA_H_

#include <fuchsia/netstack/cpp/fidl.h>
#include <lib/fidl/cpp/binding.h>

#include "base/atomicops.h"
#include "base/containers/flat_set.h"
#include "base/gtest_prod_util.h"
#include "base/threading/thread_checker.h"
#include "net/base/net_export.h"
#include "net/base/network_change_notifier.h"
#include "net/base/network_interfaces.h"
#include "starboard/types.h"

namespace net {

class NET_EXPORT_PRIVATE NetworkChangeNotifierFuchsia
    : public NetworkChangeNotifier {
 public:
  // Blocks execution until an initial interface list is received from
  // |netstack_|.
  NetworkChangeNotifierFuchsia();
  ~NetworkChangeNotifierFuchsia() override;

 private:
  friend class NetworkChangeNotifierFuchsiaTest;
  FRIEND_TEST_ALL_PREFIXES(NetworkChangeNotifierFuchsiaTest, FoundWiFi);
  FRIEND_TEST_ALL_PREFIXES(NetworkChangeNotifierFuchsiaTest,
                           FoundWiFiNonDefault);

  // For testing purposes.
  explicit NetworkChangeNotifierFuchsia(
      fuchsia::netstack::NetstackPtr netstack);

  // Forwards the network interface list along with the result of
  // GetRouteTable() to OnRouteTableReceived().
  void ProcessInterfaceList(
      base::OnceClosure on_initialized_cb,
      fidl::VectorPtr<fuchsia::netstack::NetInterface> interfaces);

  // Computes network change notification state change from the list of
  // interfaces and routing table data, sending observer events if IP or
  // connection type changes are detected.
  // |on_initialized_cb| will be bound when the network state is populated for
  // the first time. In that case, change observer events will not be
  // published, and |on_initialized_cb| will be invoked once the function has
  // finished executing.
  void OnRouteTableReceived(
      base::OnceClosure on_initialized_cb,
      fidl::VectorPtr<fuchsia::netstack::NetInterface> interfaces,
      fidl::VectorPtr<fuchsia::netstack::RouteTableEntry> table);

  // NetworkChangeNotifier implementation.
  ConnectionType GetCurrentConnectionType() const override;

  // The ConnectionType of the default network interface, stored as an atomic
  // 32-bit int for safe concurrent access.
  base::subtle::Atomic32 cached_connection_type_ = CONNECTION_NONE;

  fuchsia::netstack::NetstackPtr netstack_;

  // Set of addresses from the previous query/update for the default interface.
  base::flat_set<IPAddress> cached_addresses_;

  THREAD_CHECKER(thread_checker_);

  DISALLOW_COPY_AND_ASSIGN(NetworkChangeNotifierFuchsia);
};

}  // namespace net

#endif  // NET_BASE_NETWORK_CHANGE_NOTIFIER_FUCHSIA_H_
