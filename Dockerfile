# Use the official Python image from the Docker Hub
FROM python:3.11-slim

ARG BOT_TOKEN
ARG GROUP_CHAT_ID

ENV BOT_TOKEN=$BOT_TOKEN
ENV GROUP_CHAT_ID=$GROUP_CHAT_ID

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . .

# Make the run script executable
RUN chmod +x run.sh

# Command to run the bot
CMD ["./run.sh"]
