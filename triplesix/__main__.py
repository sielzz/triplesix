from os import path, mkdir
from pyrogram import idle
from triplesix.clients import bot, player
from triplesix import bot_username

if not path.exists("downloads"):
    mkdir("downloads")


async def get_username():
    global bot_username
    x = await bot.get_me()
    bot_username += x.username


player.call.start()
bot.start()
bot.run(get_username())
print(f"DON'T DELETE THIS, THIS IS FOR DEBUG \nBot username: {bot_username}")
print("=====Bot Running=====\n")

idle()
