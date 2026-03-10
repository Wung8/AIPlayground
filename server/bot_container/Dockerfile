FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

# create unprivileged user
RUN useradd -m sandbox

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY botwrapper.py .

# switch away from root
USER sandbox

ENTRYPOINT ["python", "-u", "botwrapper.py"]