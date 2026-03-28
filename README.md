# noBS_BotIntegrator
Telegram bot which helps with my minecraft server community automation.

## What it does
Parses telegram channel message and sends converted markdown to my server API.

## How it works
Bot listens for messages marked with announcement tag, formats them to markdown and sends it to FastAPI where front end reads it. Runs alongside the API via docker-compose.

## Tech stack
- Python
- pyTelegramBotAPI
- FastAPI
- requests
- Docker

## API repo link
https://github.com/Sl0wYx/noBS_ServerAPI/
