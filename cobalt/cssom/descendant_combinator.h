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

#ifndef COBALT_CSSOM_DESCENDANT_COMBINATOR_H_
#define COBALT_CSSOM_DESCENDANT_COMBINATOR_H_

#include "base/basictypes.h"
#include "base/compiler_specific.h"
#include "cobalt/cssom/combinator.h"

namespace cobalt {
namespace cssom {

class CombinatorVisitor;

// Descendant combinator describes an element that is the descendant of another
// element in the document tree.
//   https://www.w3.org/TR/selectors4/#descendant-combinators
class DescendantCombinator : public Combinator {
 public:
  DescendantCombinator() {}
  ~DescendantCombinator() override {}

  // From Combinator.
  void Accept(CombinatorVisitor* visitor) override;
  CombinatorType GetCombinatorType() override { return kDescendantCombinator; }

 private:
  DISALLOW_COPY_AND_ASSIGN(DescendantCombinator);
};

}  // namespace cssom
}  // namespace cobalt

#endif  // COBALT_CSSOM_DESCENDANT_COMBINATOR_H_
