# Pull official base image
FROM python:3.11-slim-buster

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

# Application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]