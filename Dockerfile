FROM python:3.10-alpine

WORKDIR /app

RUN pip --no-cache-dir install gunicorn
ADD wt-server gunicorn.conf.py requirements.txt /app/
RUN pip install -r requirements.txt

CMD ["gunicorn", "wt-server:app"]
