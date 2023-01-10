ARG BASE_IMAGE
FROM $BASE_IMAGE

WORKDIR /djapp
ENV PATH="${PATH}:/root/.local/bin"
ENV DEBUG=false

# install package managers and dependencies
RUN pip install --upgrade pip
RUN pip install --user poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --sync --only main

# now copy app files to avoid breaking build cache when dependencies were not changed
COPY . .

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8000", "-w", "8", "main.wsgi:application"]
