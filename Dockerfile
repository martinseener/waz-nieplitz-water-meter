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
COPY run.py /
COPY requirements.txt /tmp/

# Install Python packages
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Make script executable
RUN chmod a+x /run.py

CMD [ "python3", "-u", "/run.py" ]
