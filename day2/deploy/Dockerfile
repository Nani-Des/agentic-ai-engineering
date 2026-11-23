# Build from the REPOSITORY ROOT so common/ is included:
#   docker build -f day2/deploy/Dockerfile -t bank-agent .
#   docker run -p 8000:8000 --env-file .env bank-agent
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

COPY common/ common/
COPY day2/deploy/app.py day2/deploy/app.py

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "day2.deploy.app:app", "--host", "0.0.0.0", "--port", "8000"]
