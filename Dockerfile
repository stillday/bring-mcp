FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./
RUN uv pip install --system --no-cache .

COPY src/ ./src/

ENV PORT=8000

CMD ["bring-mcp"]
