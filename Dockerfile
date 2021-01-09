FROM python:3.8.7-slim

LABEL maintainer="Arie Lev <levinsonarie@gmail.com>" \
      description="Python version bumper"

WORKDIR package

COPY pybump pybump
COPY setup.py .
COPY LICENSE .
COPY README.rst .
RUN python ./setup.py install

WORKDIR /

# clean package files
RUN rm -rf /package
ENTRYPOINT ["pybump"]