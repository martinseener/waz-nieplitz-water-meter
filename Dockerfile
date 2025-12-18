ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN \
    apk add --no-cache \
        python3 \
        py3-pip

# Copy data for add-on
COPY run.py /
COPY run.sh /
COPY index.html /
COPY requirements.txt /tmp/

# Install Python packages
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Make scripts executable
RUN chmod a+x /run.py /run.sh

# Start script
CMD [ "/run.sh" ]
