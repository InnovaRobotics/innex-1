# Multi-arch (amd64 + arm64) ROS 2 Humble development image for INNEX-1.
# Base: official ros:humble (published for amd64 and arm64v8).
# Do NOT base on osrf/ros:humble-desktop*: those images are amd64-only.
FROM ros:humble-ros-base-jammy

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Reproducibility after Humble EOL (May 2027): pin the ROS apt source to a dated
# snapshot. Set ROS_SNAPSHOT to a date listed at http://snapshots.ros.org/humble/
# (for example 2026-09-01) to build against that snapshot. Empty = live repo.
ARG ROS_SNAPSHOT=""
RUN if [ -n "$ROS_SNAPSHOT" ]; then \
      echo "deb http://snapshots.ros.org/humble/${ROS_SNAPSHOT}/ubuntu jammy main" \
        > /etc/apt/sources.list.d/ros2-latest.list \
      && printf 'Package: *\nPin: origin snapshots.ros.org\nPin-Priority: 1001\n' \
        > /etc/apt/preferences.d/ros-snapshot; \
    fi

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash-completion \
    build-essential \
    clang-format \
    git \
    iproute2 \
    iputils-ping \
    jq \
    less \
    nano \
    net-tools \
    openssh-client \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    python3-vcstool \
    ros-humble-desktop \
    ros-humble-foxglove-bridge \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosbag2-storage-mcap \
    ros-humble-twist-mux \
    sudo \
    usbutils \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pre-commit ruff platformio

ARG USERNAME=rover
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid "$USER_GID" "$USERNAME" \
  && useradd --uid "$USER_UID" --gid "$USER_GID" -m -s /bin/bash "$USERNAME" \
  && usermod -aG dialout,plugdev,video "$USERNAME" \
  && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > "/etc/sudoers.d/$USERNAME" \
  && chmod 0440 "/etc/sudoers.d/$USERNAME"

RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then rosdep init; fi \
  && for attempt in 1 2 3; do \
    rosdep update --rosdistro humble && break; \
    if [ "$attempt" = 3 ]; then exit 1; fi; \
    sleep "$((attempt * 5))"; \
  done

# One RMW for every machine, including the Jetson. Mismatched RMWs do not talk.
ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
ENV ROS_DOMAIN_ID=27

USER $USERNAME
WORKDIR /workspace/innex-1

RUN echo "source /opt/ros/humble/setup.bash" >> "/home/$USERNAME/.bashrc" \
  && echo "if [ -f install/setup.bash ]; then source install/setup.bash; fi" >> "/home/$USERNAME/.bashrc"
