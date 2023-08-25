FROM python:3.9

WORKDIR /app

RUN apt-get update

# camelot dependencies
RUN apt-get install libgl1 -y \
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

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

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

WORKDIR /app

COPY . /app

CMD [ "/bin/bash", "main.sh" ]