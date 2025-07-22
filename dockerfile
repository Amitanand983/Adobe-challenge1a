FROM ubuntu:22.04

# Install required packages
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    libglib2.0-0 \
    libxrender1 \
    libxcursor1 \
    libxext6 \
    libsm6 \
    libxrandr2 \
    libice6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip3 install uv

# Install Python dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY src/ /app/src/
WORKDIR /app

CMD ["python3.10", "-O", "src/main.py"]
