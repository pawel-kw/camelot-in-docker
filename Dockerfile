FROM python:3.9 AS builder

WORKDIR /app

RUN apt-get update

# camelot dependencies
RUN apt-get update \
    && apt-get -y install libgl1 \
    && apt-get -y install python3-tk \
    && apt-get -y install libconfig-dev \
    && apt-get -y install git \
    && apt-get -y install build-essential \
    && apt-get -y install g++ \
    && apt-get -y install python3-dev \
    && apt-get -y install autotools-dev \
    && apt-get -y install libicu-dev \
    && apt-get -y install libbz2-dev \
    && apt-get -y install libboost-all-dev \
    && apt-get -y install cmake protobuf-compiler \
    && apt-get -y install qtbase5-dev

RUN pip install poetry==1.6.1
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry export --without dev -f requirements.txt > requirements.txt
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -r requirements.txt

RUN git clone https://github.com/vinayak-mehta/pdftopng.git

RUN git clone https://gitlab.freedesktop.org/poppler/poppler.git pdftopng/lib/poppler
WORKDIR /app/pdftopng/lib/poppler
RUN git checkout fcdff7b
RUN mkdir build \
    && cd build \
    && cmake -DCMAKE_BUILD_TYPE=Release   \
    -DCMAKE_INSTALL_PREFIX=/usr .. \
    && make \
    && make install

RUN mv build/config.h .

WORKDIR /app/pdftopng
RUN python -m pip install .

FROM python:3.9 AS test

RUN apt-get update \
    && apt-get -y install libgl1 \
    && apt-get -y install python3-tk \
    && apt-get -y install libconfig-dev \
    && apt-get -y install autotools-dev \
    && apt-get -y install libicu-dev \
    && apt-get -y install libbz2-dev

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /usr/lib/aarch64-linux-gnu/libpoppler.so.111 /usr/lib/aarch64-linux-gnu/libpoppler.so.111 

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY src/* /app

CMD [ "python", "main.py" ]