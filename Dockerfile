# Stage 1: Сборка
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Финальный образ
FROM python:3.13-slim
WORKDIR /app

# Копируем зависимости из builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Настройка путей и окружения
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libdbus-1-3 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxrender1 \
    libxi6 \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Healthcheck: проверка, что процесс python запущен
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD pgrep -f "python main.py" || exit 1

CMD ["python", "main.py"]