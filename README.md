# Telegram Bot CV Collector #

The **Telegram Bot CV Collector** is designed to collect CVs from users in separate chats and send them to a group chat with HR representatives. If you’re interested in implementing this bot for your job process, follow the instructions below.

## Prerequisites ##
1. **Server or Local Machine:**
    * You’ll need a server or any machine that can run Docker containers. Make sure it stays operational for as long as possible since this directly affects whether your bot is running or not. For testing or initial setup, you can use your own PC.
2. **Telegram Bot Token:**
    * Register a bot with BotFather on Telegram to obtain a bot token.
3. **Create a Group:**
    * Create a group chat where you’ll receive CVs. Add HR representatives and your bot to this group.
4. **Find Out Chat ID:**
    * Determine the chat ID of the group where you want to collect CVs. You’ll need this ID to configure your bot.

## Setup Instructions
1. **Edit `bot.py`:**
    * Open the `bot.py` file and add your bot token and chat ID.
    * `TOKEN = os.environ.get('BOT_TOKEN', 'your_token')` >>  `TOKEN = 123434324` - same with chat ID.
    * Remove `import os` line from the code.
Customize the messages that the bot will send to users.
2. **Build the Docker Container:**
    * Navigate to the directory containing all the bot files.
Build the Docker container using the following command:

```docker build -t any_tag-name .```

3. **Run the Docker Container:**
    * Start the Docker container with the following command:
    
```docker run -d any_tag-name```

4. **Test the Bot:**
    * Start a direct message (DM) with your bot.
    * Use the `/start` command to initiate a conversation.
    * Follow the bot’s instructions as a user.
    * When a CV is submitted, it will appear in the group chat whose ID you added in the code.

## Note
* If you need to add the chat ID later (e.g., after the bot is already running), use the command `/my_id @your_bot_name` in the group chat.

Remember to keep your server or local machine running to ensure continuous bot functionality.

Feel free to reach out if you have any questions or need further assistance! 🤖📄
