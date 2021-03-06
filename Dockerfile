FROM python:3.7-alpine as base

FROM base as builder

RUN mkdir /install
ADD app /install
WORKDIR /install

RUN pip install --install-option="--prefix=/install" --ignore-installed -r requirements.txt

FROM base
COPY --from=builder /install /usr/local
COPY app /app

WORKDIR /app

EXPOSE 8000
CMD ["gunicorn", "-w 4", "--bind", "0.0.0.0:8000", "component.wsgi"]