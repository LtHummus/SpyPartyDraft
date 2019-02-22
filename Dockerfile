FROM python:2.7

WORKDIR /usr/src/app

COPY ./ ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# gunicorn --worker-class eventlet SpyPartyDraft:app --log-file -
CMD [ "gunicorn", "--worker-class", "eventlet", "-b", "0.0.0.0:8000", "SpyPartyDraft:app", "--log-file", "-" ]