FROM public.ecr.aws/lambda/python:3.9

# PIP & Poetry
RUN pip install --upgrade pip
COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.2.2
RUN poetry config virtualenvs.create false
RUN poetry install --only main --no-interaction --no-ansi

ENV PYTHONUNBUFFERED True
ADD src/ src/

RUN pip freeze
# ENTRYPOINT uvicorn src.main:handler --host 0.0.0.0 --port 80
# ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# CMD [ "popo.handler" ]
CMD ["src.main.handler"]