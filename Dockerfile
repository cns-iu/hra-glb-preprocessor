FROM ubuntu:24.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt -y update && apt install -y python-is-python3 python3 python3-pip python3-venv \
  build-essential cmake libssl-dev libboost-all-dev libgmp-dev libmpfr-dev libeigen3-dev \
  libassimp-dev libcpprest-dev gcc-10 g++-10 curl unzip \
  x11-common x11-utils libxkbcommon-tools
WORKDIR /usr/src/app
COPY . .
RUN ./scripts/00-setup-environment.sh

CMD [ "./scripts/10-build.sh" ]
