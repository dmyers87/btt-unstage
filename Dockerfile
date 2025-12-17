FROM --platform=linux/amd64 python:3.13.11

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "live.py"]