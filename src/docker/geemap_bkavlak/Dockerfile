FROM ubuntu:20.04
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Copying install_dependencies.sh & give permissions
COPY install_dependencies.sh /
RUN chmod +x /install_dependencies.sh

# install dependencies - making some changes here to test 
RUN ./install_dependencies.sh && \
    apt-get update && \
    /usr/bin/python3 -m pip install --upgrade pip

# install python package
COPY requirements.txt /
RUN pip3 --no-cache-dir install --upgrade setuptools && \
    pip3 --no-cache-dir install wheel && \
    pip3 --no-cache-dir install -r requirements.txt
	
# Making home & test folders
RUN mkdir geemap && \
    mkdir tests

# Copying tests
COPY /tests/test_geemap.py /tests
COPY /tests/run_tests.sh /tests

# Giving permission to tests to run
RUN chmod +x /tests/test_geemap.py && \
    chmod +x /tests/run_tests.sh

RUN apt-get install curl -y
RUN apt-get install apt-transport-https ca-certificates gnupg -y
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update && apt-get install google-cloud-cli -y

WORKDIR "geemap"
