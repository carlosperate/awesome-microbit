FROM python:3.8-bullseye

LABEL "version"="0.2.0"
LABEL org.opencontainers.image.description="Docker image to run a Python action."
LABEL org.opencontainers.image.authors="Carlos Pereira Atencio <carlosperate@embeddedlog.com>"
LABEL org.opencontainers.image.source="https://github.com/carlosperate/awesome-microbit"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade --no-cache-dir pipenv==2022.9.*
COPY entrypoint.sh Pipfile* /
RUN cd / && pipenv install --dev --system --ignore-pipfile
ENTRYPOINT [ "/entrypoint.sh" ]
