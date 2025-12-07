FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV APP_PORT=8000

RUN chmod +x start.sh

CMD ["./start.sh"]
