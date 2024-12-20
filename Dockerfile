# Use Ubuntu 22.04 LTS as the base image
FROM ubuntu:bullseye-slim
# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    nvtop \
    htop \
    net-tools \   
    ffmpeg \
    libsm6 \
    libxext6 \
    alsa-utils \
    mpg123 \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    portaudio19 \
    systemd systemd-sysv dbus dbus-user-session \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Set Python 3.11 as the default Python version
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --set python3 /usr/bin/python3.11 \
    && ln -sf /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Azure OpenAI and Speech API keys will be passed as environment variables
CMD ["python", "app.py"]