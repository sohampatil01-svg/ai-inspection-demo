FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

EXPOSE 8501

ENV PORT=8501

CMD ["sh", "-c", "streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0"]
