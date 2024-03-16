FROM python:3.13.0a4-slim

LABEL maintainer="Arie Lev <levinsonarie@gmail.com>" \
      description="Python version bumper"

RUN apt-get update && \
    apt-get install -y git

WORKDIR package

COPY src src
COPY setup.py .
COPY LICENSE .
COPY README.rst .
COPY requirements.txt .
RUN python ./setup.py install

WORKDIR /

# clean package files
RUN rm -rf /package

# execute simle version test
RUN pybump --version
ENTRYPOINT ["pybump"]