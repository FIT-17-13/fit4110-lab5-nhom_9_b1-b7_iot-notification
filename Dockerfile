# syntax=docker/dockerfile:1.7

FROM python:3.11-slim AS builder

# Không ghi bytecode và hiển thị stdout ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Tạo virtualenv riêng để giảm layer image
RUN python -m venv /opt/venv

COPY requirements.txt .

RUN /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# ==========================================
# BIẾN RUNTIME MẶC ĐỊNH (Dùng chung)
# ==========================================
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000
ENV AUTH_TOKEN=local-dev-token

# Đặt biến generic vì file này build cho cả IoT lẫn Notification
ENV SERVICE_NAME=fit4110-base-service
ENV SERVICE_VERSION=v0.1.0-team9
ENV APP_MODULE="src.iot_api.main:app"

WORKDIR /app

# Tạo user non-root để chạy app an toàn (Đáp ứng rubric điểm cao của lab)
RUN addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /app appuser

COPY --from=builder /opt/venv /opt/venv
COPY src/ ./src/

# Cấp quyền sở hữu thư mục /app cho non-root user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck mặc định (Sẽ bị Worker ghi đè trong docker-compose.yml)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" || exit 1

# Sử dụng biến APP_MODULE để file linh hoạt cho mọi API
CMD ["sh", "-c", "uvicorn ${APP_MODULE} --host ${APP_HOST} --port ${APP_PORT}"]