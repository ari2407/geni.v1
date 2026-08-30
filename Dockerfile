FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 appuser && mkdir -p /app/data/runtime && chown -R appuser:appuser /app
USER appuser
ENTRYPOINT ["crypto-signals-scheduler"]
CMD ["--telegram", "--all-public", "--max-symbols", "100", "--timeframe", "H1", "--interval", "3600", "--cooldown", "1800", "--retries", "3"]
