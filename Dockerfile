FROM python:3.8.2-slim
WORKDIR /code
COPY . .
RUN pip install --upgrade pip && pip install keyrings.alt && pip install --editable .
ENTRYPOINT [ "ghs" ]
