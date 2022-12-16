FROM python:latest

WORKDIR /Data-Cent

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./lib/app.py" ]