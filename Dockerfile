FROM python:3.11-slim
ENV BOT_TOKEN=""
ENV GROUP_CHAT_ID=""
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x run.sh
CMD ["./run.sh"]
