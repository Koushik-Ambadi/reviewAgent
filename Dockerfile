FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    clang-19 \
    libclang-19-dev \
    llvm-19 \
    cmake \
    ninja-build \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

ENV CC=/usr/bin/gcc
ENV CXX=/usr/bin/g++
ENV ASM=/usr/bin/gcc

ENV LIBCLANG_PATH=/usr/lib/x86_64-linux-gnu/libclang-19.so.19

COPY . /app

RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install --no-cache-dir clang==19.1.7

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]