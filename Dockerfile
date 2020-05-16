FROM python:3.7-slim
COPY . .
RUN python ./setup.py install
ENTRYPOINT ["pybump"]