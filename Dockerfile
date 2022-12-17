FROM python:latest

WORKDIR /Data-Cent

COPY requirements.text ./
RUN pip install --no-cache-dir -r requirements.text
ENV PYTHONPATH="$PYTHONPATH:/Data-Cent"

COPY . .

CMD ["python3", "main/main.py"]