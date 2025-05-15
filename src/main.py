from telethon.sync import TelegramClient, events
import os
from openai import OpenAI
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

client = OpenAI()

api_id = os.getenv('TELEGRAM_APP_API_ID')
api_hash = os.getenv('TELEGRAM_APP_API_HASH')

with TelegramClient('name', api_id, api_hash) as telegram_client:
   @telegram_client.on(events.NewMessage())
   async def handler(event):
      me = await telegram_client.get_me()
      
      logger.info(f"Received message from {event.sender_id} in chat {event.chat_id}")
      
      if event.sender_id == me.id:
         logger.debug(f"Ignoring message from non-self user {event.sender_id}")
         return
         
      chat_id = event.chat_id
      logger.info(f"Processing self message: {event.message.message[:50]}...")
      
      try:
         response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
               {
                  "role": "user",
                  "content": f"Reply to this message in gen alpha slang. Return ONLY the transformed text, nothing else: {event.message.message}"
               }
            ]
         )
         
         improved_message = response.choices[0].message.content
         logger.info(f"Generated improved message: {improved_message[:50]}...")
         
         await event.message.reply(improved_message)
         logger.info("Message edited successfully")
         
      except Exception as e:
         logger.error(f"Error processing message: {str(e)}", exc_info=True)
         await event.reply("Sorry, I encountered an error while processing your message.")

   logger.info("Bot started and running...")
   telegram_client.run_until_disconnected()
