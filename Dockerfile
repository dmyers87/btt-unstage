FROM --platform=linux/amd64 python:3.9

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x ./unstage-cloud-pr-site.py

RUN which python
RUN which python3


CMD ["python", "live.py"]