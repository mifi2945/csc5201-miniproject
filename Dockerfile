FROM python:3.14-slim

WORKDIR /build
COPY . /build

RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["python", "src/api.py"]