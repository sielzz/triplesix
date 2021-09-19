from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from youtube_search import YoutubeSearch

from triplesix.clients import player


@Client.on_callback_query(filters.regex(pattern=r"stream"))
async def play_callback(_, cb: CallbackQuery):
    callback = cb.data.split(" ")[1]
    x, query, user_id = callback.split("|")
    x = int(x)
    user_id = int(user_id)
    if cb.from_user.id != user_id:
        await cb.answer("this is not for u.", show_alert=True)
        return
    res = YoutubeSearch(query, 5).to_dict()
    title = res[x]["title"]
    await player.start_stream_via_callback(title, cb)
