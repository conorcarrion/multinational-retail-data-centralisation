FROM python:latest

WORKDIR /Data-Cent

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.text

COPY . .

CMD [ "python", "./lib/app.py" ]