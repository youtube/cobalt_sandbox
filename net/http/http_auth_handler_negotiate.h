// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef NET_HTTP_HTTP_AUTH_HANDLER_NEGOTIATE_H_
#define NET_HTTP_HTTP_AUTH_HANDLER_NEGOTIATE_H_

#if !defined(STARBOARD)
// Cobalt does not support Kerberos yet.

#include <string>
#include <utility>

#include "build/build_config.h"
#include "net/base/address_list.h"
#include "net/base/completion_once_callback.h"
#include "net/base/net_export.h"
#include "net/dns/host_resolver.h"
#include "net/http/http_auth_handler.h"
#include "net/http/http_auth_handler_factory.h"

#if defined(OS_ANDROID)
#include "net/android/http_auth_negotiate_android.h"
#elif defined(OS_WIN)
#include "net/http/http_auth_sspi_win.h"
#elif defined(OS_POSIX)
#include "net/http/http_auth_gssapi_posix.h"
#elif defined(STARBOARD)
#include "net/http/http_auth_gssapi_starboard.h"
#endif

namespace net {

class HttpAuthPreferences;

// Handler for WWW-Authenticate: Negotiate protocol.
//
// See http://tools.ietf.org/html/rfc4178 and http://tools.ietf.org/html/rfc4559
// for more information about the protocol.

class NET_EXPORT_PRIVATE HttpAuthHandlerNegotiate : public HttpAuthHandler {
 public:
#if defined(OS_ANDROID)
  typedef net::android::HttpAuthNegotiateAndroid AuthSystem;
#elif defined(OS_WIN)
  typedef SSPILibrary AuthLibrary;
  typedef HttpAuthSSPI AuthSystem;
#elif defined(OS_POSIX) || defined(STARBOARD)
  typedef GSSAPILibrary AuthLibrary;
  typedef HttpAuthGSSAPI AuthSystem;
#endif

  class NET_EXPORT_PRIVATE Factory : public HttpAuthHandlerFactory {
   public:
    Factory();
    ~Factory() override;

    void set_host_resolver(HostResolver* host_resolver);

#if !defined(OS_ANDROID)
    // Sets the system library to use, thereby assuming ownership of
    // |auth_library|.
    void set_library(std::unique_ptr<AuthLibrary> auth_provider) {
      auth_library_ = std::move(auth_provider);
    }

#if defined(OS_POSIX)
    const std::string& GetLibraryNameForTesting() const;

    void set_allow_gssapi_library_load(bool allow_gssapi_library_load) {
      allow_gssapi_library_load_ = allow_gssapi_library_load;
    }
    bool allow_gssapi_library_load_for_testing() const {
      return allow_gssapi_library_load_;
    }
#endif  // defined(OS_POSIX)
#endif  // !defined(OS_ANDROID)

    // HttpAuthHandlerFactory overrides
    int CreateAuthHandler(HttpAuthChallengeTokenizer* challenge,
                          HttpAuth::Target target,
                          const SSLInfo& ssl_info,
                          const GURL& origin,
                          CreateReason reason,
                          int digest_nonce_count,
                          const NetLogWithSource& net_log,
                          std::unique_ptr<HttpAuthHandler>* handler) override;

   private:
    HostResolver* resolver_ = nullptr;
#if defined(OS_WIN)
    ULONG max_token_length_ = 0;
#endif
    bool is_unsupported_ = false;
#if !defined(OS_ANDROID)
    std::unique_ptr<AuthLibrary> auth_library_;
#if defined(OS_POSIX) || defined(STARBOARD)
    bool allow_gssapi_library_load_ = true;
#endif  // defined(OS_POSIX)
#endif  // !defined(OS_ANDROID)
  };

  HttpAuthHandlerNegotiate(
#if !defined(OS_ANDROID)
      AuthLibrary* auth_library,
#endif
#if defined(OS_WIN)
      ULONG max_token_length,
#endif
      const HttpAuthPreferences* prefs,
      HostResolver* host_resolver);

  ~HttpAuthHandlerNegotiate() override;

  // These are public for unit tests
  std::string CreateSPN(const AddressList& address_list, const GURL& orign);
  const std::string& spn() const { return spn_; }

  // HttpAuthHandler:
  HttpAuth::AuthorizationResult HandleAnotherChallenge(
      HttpAuthChallengeTokenizer* challenge) override;
  bool NeedsIdentity() override;
  bool AllowsDefaultCredentials() override;
  bool AllowsExplicitCredentials() override;

 protected:
  bool Init(HttpAuthChallengeTokenizer* challenge,
            const SSLInfo& ssl_info) override;

  int GenerateAuthTokenImpl(const AuthCredentials* credentials,
                            const HttpRequestInfo* request,
                            CompletionOnceCallback callback,
                            std::string* auth_token) override;

 private:
  enum State {
    STATE_RESOLVE_CANONICAL_NAME,
    STATE_RESOLVE_CANONICAL_NAME_COMPLETE,
    STATE_GENERATE_AUTH_TOKEN,
    STATE_GENERATE_AUTH_TOKEN_COMPLETE,
    STATE_NONE,
  };

  void OnIOComplete(int result);
  void DoCallback(int result);
  int DoLoop(int result);

  int DoResolveCanonicalName();
  int DoResolveCanonicalNameComplete(int rv);
  int DoGenerateAuthToken();
  int DoGenerateAuthTokenComplete(int rv);
  bool CanDelegate() const;

  AuthSystem auth_system_;
  HostResolver* const resolver_;

  // Members which are needed for DNS lookup + SPN.
  AddressList address_list_;
  std::unique_ptr<net::HostResolver::Request> request_;

  // Things which should be consistent after first call to GenerateAuthToken.
  bool already_called_;
  bool has_credentials_;
  AuthCredentials credentials_;
  std::string spn_;
  std::string channel_bindings_;

  // Things which vary each round.
  CompletionOnceCallback callback_;
  std::string* auth_token_;

  State next_state_;

  const HttpAuthPreferences* http_auth_preferences_;
};

}  // namespace net

#endif  // !defined(STARBOARD)

#endif  // NET_HTTP_HTTP_AUTH_HANDLER_NEGOTIATE_H_
