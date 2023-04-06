# Copyright 2021 The Cobalt Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

ARG BASE_OS
ARG BASE_OS_TAG
ARG NEEDS_GIT_UPDATE
FROM ${BASE_OS:-gcr.io/cloud-marketplace-containers/google/debian10}:${BASE_OS_TAG:-latest} as stage1

COPY base/clean-after-apt.sh /opt/clean-after-apt.sh

ENV PYTHONUNBUFFERED 1

# === Install common dependencies
RUN apt update -qqy \
    && apt install -qqy --no-install-recommends \
        python3-dev \
        python3-pip \
        python3-requests \
        python3-setuptools \
        python3-six \
        git ccache \
        curl xz-utils \
        software-properties-common \
    && /opt/clean-after-apt.sh

FROM stage1 as git-update-no
# Nothing to be done

FROM stage1 as git-update-yes
# Install git PPA and update
RUN apt update -qqy \
    && add-apt-repository -y ppa:git-core/ppa \
    && apt-get -y install git \
    && /opt/clean-after-apt.sh

FROM git-update-${NEEDS_GIT_UPDATE}
RUN echo "Blopx"
RUN git --version

RUN echo ${gitup}
CMD ["/usr/bin/python","--version"]
