FROM python:3.6

LABEL maintainer="Chu Junpeng <ermine.chu@gmail.com>"

ENV LC_ALL="C.UTF-8" \
  LANG="C.UTF-8"

WORKDIR /opt/app/

COPY Pipfile Pipfile.lock /opt/app/

RUN pip3 install pipenv && \
  pipenv install --deploy --system

COPY . /opt/app/

ENV PYTHONPATH=/opt/app/:${PYTHONPATH}

# django port
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
