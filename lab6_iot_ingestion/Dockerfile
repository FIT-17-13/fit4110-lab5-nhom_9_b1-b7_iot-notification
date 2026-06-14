# Sử dụng base image Python 3.11 bản rút gọn
FROM python:3.11-slim

# Thiết lập thư mục làm việc bên trong container
WORKDIR /app

# Copy file danh sách thư viện và cài đặt trước (để tận dụng Docker Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code và file CSV vào container
COPY . .

# Lệnh khởi chạy service
CMD ["python", "main.py"]