FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install dependencies:
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy files (copy api.py to main.py as the default api launcher):
COPY ./dmx/api.py /app/main.py
COPY ./dmx/modules /app/modules
COPY ./dmx/data_files /app/data_files

WORKDIR "/app"
