import asyncio
import random

from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.types import Message, CallbackQuery
from pyrogram.raw.functions.phone import CreateGroupCall
from pytgcalls import PyTgCalls, StreamType
from pytgcalls.exceptions import NoActiveGroupCall, GroupCallNotFound
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import MediumQualityAudio, MediumQualityVideo

from dB import get_message
from triplesix.configs import config
from triplesix.functions import get_youtube_stream

user = Client(
	config.SESSION,
	config.API_ID,
	config.API_HASH
)

bot = Client(
	":memory:",
	config.API_ID,
	config.API_HASH,
	bot_token=config.BOT_TOKEN,
	plugins=dict(root="triplesix.handlers")
)


class Player:
	def __init__(self, pytgcalls: PyTgCalls):
		self.call = pytgcalls
		self._client = {}
		self._playlist: dict[int, list[dict[str, str]]] = {}

	async def _stream(self, query: str, message: Message, url: str, y):
		chat_id = message.chat.id
		playlist = self._playlist
		playlist[chat_id] = [{"query": query}]
		call = self.call
		await y.edit(get_message(chat_id, "stream").format(query))
		await call.join_group_call(
			chat_id,
			AudioVideoPiped(
				url,
				MediumQualityAudio(),
				MediumQualityVideo()
			),
			stream_type=StreamType().pulse_stream
		)
		self._client[chat_id] = call

	async def _start_stream(self, query, message: Message):
		chat_id = message.chat.id
		playlist = self._playlist
		if len(playlist) >= 1:
			try:
				playlist[chat_id].extend([{"query": query}])
				y = await message.reply("Queued")
				await asyncio.sleep(10)
				await y.delete()
				return
			except KeyError:
				await message.reply("restart the bot")
				playlist[chat_id].clear()
				return
		y = await message.reply(get_message(chat_id, "process"))
		url = await get_youtube_stream(query)
		try:
			await self._stream(query, message, url, y)
		except FloodWait as fw:
			await message.reply(f"Getting floodwait {fw.x} second, bot sleeping")
			await asyncio.sleep(fw.x)
			await self._stream(query, message, url, y)
		except NoActiveGroupCall:
			try:
				await user.send(CreateGroupCall(
					peer=await user.resolve_peer(chat_id),
					random_id=random.randint(10000, 999999999)
				))
				await self._stream(query, message, url, y)
			except Exception as ex:
				await y.edit(f"{type(ex).__name__}: {ex.with_traceback(ex.__traceback__)}")
				playlist[chat_id].clear()
		except Exception as ex:
			await y.edit(f"{type(ex).__name__}: {ex.with_traceback(ex.__traceback__)}")
			playlist[chat_id].clear()

	async def start_stream(self, query: str, message: Message):
		await self._start_stream(query, message)

	async def start_stream_via_callback(self, query: str, callback: CallbackQuery):
		message = callback.message
		await self._start_stream(query, message)

	async def end_stream(self, message: Message):
		chat_id = message.chat.id
		playlist = self._playlist
		client = self._client
		try:
			try:
				if client[chat_id].get_call(chat_id):
					await self.call.leave_group_call(chat_id)
					playlist[chat_id].clear()
					await message.reply("ended")
			except KeyError:
				await message.reply("you never streaming anything")
		except GroupCallNotFound:
			await message.reply("not streaming")


player = Player(PyTgCalls(user))
