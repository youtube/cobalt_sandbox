// Copyright 2018 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#ifndef NET_TEST_TEST_WITH_SCOPED_TASK_ENVIRONMENT_H_
#define NET_TEST_TEST_WITH_SCOPED_TASK_ENVIRONMENT_H_

#include "base/compiler_specific.h"
#include "base/macros.h"
#include "base/test/scoped_task_environment.h"
#include "base/time/time.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace base {
class TickClock;
}  // namespace base

namespace net {

// Inherit from this class if a ScopedTaskEnvironment is needed in a test.
// Use in class hierarchies where inheritance from ::testing::Test at the same
// time is not desirable or possible (for example, when inheriting from
// PlatformTest at the same time).
class WithScopedTaskEnvironment {
 protected:
  WithScopedTaskEnvironment()
      : scoped_task_environment_(
            base::test::ScopedTaskEnvironment::MainThreadType::IO) {}
  WithScopedTaskEnvironment(
      base::test::ScopedTaskEnvironment::MainThreadType type)
      : scoped_task_environment_(type) {}

  bool MainThreadHasPendingTask() const WARN_UNUSED_RESULT {
    return scoped_task_environment_.MainThreadHasPendingTask();
  }

  // Executes all tasks that have no remaining delay. Tasks with a remaining
  // delay greater than zero will remain enqueued, and no virtual time will
  // elapse.
  void RunUntilIdle() { scoped_task_environment_.RunUntilIdle(); }

  // Fast-forwards virtual time by |delta|, causing all tasks with a remaining
  // delay less than or equal to |delta| to be executed. |delta| must be
  // non-negative.
  void FastForwardBy(base::TimeDelta delta) {
    scoped_task_environment_.FastForwardBy(delta);
  }

  // Fast-forwards virtual time by |delta| but not causing any task execution.
  void AdvanceMockTickClock(base::TimeDelta delta) {
    scoped_task_environment_.AdvanceMockTickClock(delta);
  }

  // Fast-forwards virtual time just until all tasks are executed.
  void FastForwardUntilNoTasksRemain() {
    scoped_task_environment_.FastForwardUntilNoTasksRemain();
  }

  // Returns a TickClock that uses the virtual time ticks of |this| as its tick
  // source. The returned TickClock will hold a reference to |this|.
  const base::TickClock* GetMockTickClock() WARN_UNUSED_RESULT {
    return scoped_task_environment_.GetMockTickClock();
  }

  size_t GetPendingMainThreadTaskCount() const WARN_UNUSED_RESULT {
    return scoped_task_environment_.GetPendingMainThreadTaskCount();
  }

  base::TimeDelta NextMainThreadPendingTaskDelay() const WARN_UNUSED_RESULT {
    return scoped_task_environment_.NextMainThreadPendingTaskDelay();
  }

 private:
  base::test::ScopedTaskEnvironment scoped_task_environment_;

  DISALLOW_COPY_AND_ASSIGN(WithScopedTaskEnvironment);
};

// Inherit from this class instead of ::testing::Test directly if a
// ScopedTaskEnvironment is needed in a test.
class TestWithScopedTaskEnvironment : public ::testing::Test,
                                      public WithScopedTaskEnvironment {
 protected:
  TestWithScopedTaskEnvironment() = default;
  TestWithScopedTaskEnvironment(
      base::test::ScopedTaskEnvironment::MainThreadType type)
      : WithScopedTaskEnvironment(type) {}

  DISALLOW_COPY_AND_ASSIGN(TestWithScopedTaskEnvironment);
};

}  // namespace net

#endif  // NET_TEST_TEST_WITH_SCOPED_TASK_ENVIRONMENT_H_
