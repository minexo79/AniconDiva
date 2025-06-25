FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN mv config_example.ini config.ini

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]