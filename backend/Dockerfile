# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml /app/

# Project initialization:
RUN poetry config virtualenvs.create false \
&& poetry install --no-interaction --no-ansi

RUN python -m spacy download en_core_web_sm

# Copy project
COPY . /app/

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run", "--host=0.0.0.0"]
