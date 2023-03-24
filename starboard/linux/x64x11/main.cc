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

#include <time.h>

#include "starboard/configuration.h"
#include "starboard/shared/signal/crash_signals.h"
#include "starboard/shared/signal/debug_signals.h"
#include "starboard/shared/signal/suspend_signals.h"
#if SB_IS(EVERGREEN_COMPATIBLE)
#include "starboard/common/paths.h"
#include "starboard/shared/starboard/command_line.h"
#include "starboard/shared/starboard/starboard_switches.h"
#endif
#include "starboard/shared/starboard/link_receiver.h"
#include "starboard/shared/x11/application_x11.h"

#include "third_party/crashpad/wrapper/wrapper.h"

extern "C" SB_EXPORT_PLATFORM int main(int argc, char** argv) {
  tzset();
  starboard::shared::signal::InstallCrashSignalHandlers();
  starboard::shared::signal::InstallDebugSignalHandlers();
  starboard::shared::signal::InstallSuspendSignalHandlers();

#if SB_IS(EVERGREEN_COMPATIBLE)
  std::string ca_certificates_path = starboard::common::GetCACertificatesPath();
  if (ca_certificates_path.empty()) {
    SB_LOG(ERROR) << "Failed to get CA certificates path";
    return 1;
  }

  if (starboard::shared::starboard::CommandLine(argc, argv)
          .HasSwitch(starboard::shared::starboard::kStartHandlerAtLaunch) &&
      !starboard::shared::starboard::CommandLine(argc, argv)
           .HasSwitch(starboard::shared::starboard::kStartHandlerAtCrash)) {
    third_party::crashpad::wrapper::InstallCrashpadHandler(
        false, ca_certificates_path);
  } else {
    third_party::crashpad::wrapper::InstallCrashpadHandler(
        true, ca_certificates_path);
  }
#endif

#if SB_HAS_QUIRK(BACKTRACE_DLOPEN_BUG)
  // Call backtrace() once to work around potential
  // crash bugs in glibc, in dlopen()
  SbLogRawDumpStack(3);
#endif

  starboard::shared::x11::ApplicationX11 application;
  int result = 0;
  {
    starboard::shared::starboard::LinkReceiver receiver(&application);
    result = application.Run(argc, argv);
  }
  starboard::shared::signal::UninstallSuspendSignalHandlers();
  starboard::shared::signal::UninstallDebugSignalHandlers();
  starboard::shared::signal::UninstallCrashSignalHandlers();
  return result;
}
