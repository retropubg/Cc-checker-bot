import asyncio
from aiohttp import (
    ClientSession,
    ClientResponse,
    TCPConnector,
    ClientError,
    ClientResponseError,
)
from pyrogram import filters
from pyromod import Client
from pyrogram.types import Message
from utilsdf.db import Database
from utilsdf.vars import PREFIXES
from os import getenv
from sys import exit


headers = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
}



ID_OWNER = getenv("6699273462")


@Client.on_message(filters.command("broad", PREFIXES))
async def broad(client: Client, m: Message):
    with Database() as db:
        if not db.is_admin(m.from_user.id):
            return
        message_reply = m.reply_to_message
        msj = (
            m.reply_to_message.id
            if message_reply
            else m.text[len(m.command[0]) + 2 :].strip()
        )
        if not msj:
            return await m.reply("<b>No hay mensaje para enviar</b>")
        chats_ids = db.get_chats_ids()

        succesfulls = 0
        results = []
        async with ClientSession(
            headers=headers, connector=TCPConnector(verify_ssl=False)
        ) as client_http:
            for chat_id in chats_ids:
                if message_reply:
                    results.append(
                        forward_message(
                            chat_id,
                            from_chat_id=m.chat.id,
                            message_id=msj,
                            client=client_http,
                            bot_token=client.bot_token,
                        )
                    )
                    continue
                results.append(
                    send_message(
                        chat_id,
                        text=msj,
                        client=client_http,
                        bot_token=client.bot_token,
                    )
                )

            results = await asyncio.gather(*results)
            for result in results:
                if isinstance(result, ClientResponse):
                    succesfulls += 1
                else:
                    await asyncio.sleep(2)

        await m.reply(
            f"<b>Anuncios enviados exitosamente a <code>{succesfulls}</code> chats!</b>",
            quote=True,
        )


async def send_message(
    chat_id, text, client: ClientSession, bot_token
) -> bool | ClientResponse:
    url_base = f"https://api.telegram.org/bot{bot_token}/"
    url = url_base + "sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    tries = 0
    while tries <= 3:
        if tries == 3:
            return False
        try:
            response = await client.post(url, data=data)
            response_json = await response.json()

            if response.status == 429:
                await asyncio.sleep(int(response.headers.get("Retry-After", 5)))
                continue

            if response_json.get("ok", False):
                return response

            description_error = response_json.get("description", "").lower()

            if (
                "forbidden" in description_error
                or "blocked" in description_error
                or "bad request" in description_error
            ):
                return False

            tries += 1
            await asyncio.sleep(5)
        except:
            tries += 1
            await asyncio.sleep(5)


async def forward_message(
    chat_id, from_chat_id, message_id, client: ClientSession, bot_token
) -> bool | ClientResponse:
    url_base = f"https://api.telegram.org/bot{bot_token}/"
    url = url_base + "forwardMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id,
    }
    tries = 0
    while tries <= 3:
        if tries == 3:
            return False
        try:
            response = await client.post(url, data=data)
            response_json = await response.json()

            if response.status == 429:
                await asyncio.sleep(int(response.headers.get("Retry-After", 5)))
                continue

            if response_json.get("ok", False):
                return response

            description_error = response_json.get("description", "").lower()

            if (
                "forbidden" in description_error
                or "blocked" in description_error
                or "bad request" in description_error
            ):
                return False

            tries += 1
            await asyncio.sleep(5)
        except:
            tries += 1
            await asyncio.sleep(5)
