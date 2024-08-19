# Choice Python version
FROM python:3.10

# Uygulamanızın çalışacağı dizini belirleyin
WORKDIR /app

# Gereksinimlerinizi yükleyin
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyalayın
COPY . .

# Uvicorn sunucusunu başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
