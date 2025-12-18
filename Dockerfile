ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements for add-on
RUN \
    apk add --no-cache \
        python3 \
        py3-pip \
        py3-requests \
        py3-beautifulsoup4 \
        py3-lxml \
        py3-dateutil

# Copy data for add-on
COPY run.py /app/
COPY requirements.txt /tmp/

# Install Python packages
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Copy root filesystem
COPY rootfs /
