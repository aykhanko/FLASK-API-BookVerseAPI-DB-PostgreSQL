FROM python:3.12

WORKDIR /BookVerse-API

COPY . .

RUN pip install -r requirements.txt

ENV FLASK_APP=main
ENV FLASK_DEBUG=False
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["sh", "-c", "flask db upgrade && gunicorn -w 4 -b 0.0.0.0:5000 main:app"]

