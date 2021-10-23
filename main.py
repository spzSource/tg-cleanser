#!/usr/bin/python

import os
import asyncio
import argparse
from datetime import datetime, timedelta
from time import sleep
from typing import List
from pyrogram import Client
from pyrogram.errors import FloodWait
from pyrogram.raw.functions.messages import Search
from pyrogram.raw.types import InputPeerSelf, InputMessagesFilterEmpty


class MessagePage:
    def __init__(self, app, chat_id, messages):
        self.app = app
        self.chat_id = chat_id
        self.messages = messages

    async def remove(self, dry_run=False):
        ids = [x.id for x in self.messages]
        try:
            if not dry_run:
                await self.app.delete_messages(chat_id=self.chat_id,
                                               message_ids=ids)
            print(f'Following messages have been deleted:\n {ids}')

        except FloodWait as flood_exception:
            sleep(flood_exception.x)
            raise


class Group:
    def __init__(self, client, peer, chat_id, name) -> None:
        self.client = client
        self.name = name
        self.chat_id = chat_id
        self.peer = peer

    async def messages(self, page_size: int = 200):
        offset = 0

        q = await self.__search(offset, page_size)

        while len(q.messages) > 0:
            yield MessagePage(self.client, self.chat_id, q.messages)
            offset += page_size
            q = await self.__search(offset, page_size)

    async def __search(self, offset: int, number: int):
        print(f'Searching messages. Offset: {offset}')
        try:
            return await self.client.send(
                Search(peer=self.peer,
                       q='',
                       filter=InputMessagesFilterEmpty(),
                       min_date=0,
                       max_date=int(
                           (datetime.today() - timedelta(days=1)).timestamp()),
                       offset_id=0,
                       add_offset=offset,
                       limit=number,
                       max_id=0,
                       min_id=0,
                       hash=0,
                       from_id=InputPeerSelf()))
        except FloodWait as flood_exception:
            sleep(flood_exception.x)
            raise


class Telegram:
    def __init__(self, client: Client):
        self.client = client

    async def groups(self, group_ids: List[int]):
        for _, id in enumerate(group_ids):
            (chat, peer) = await asyncio.gather(self.client.get_chat(id), self.client.resolve_peer(id))
            yield Group(self.client, peer, chat.id, chat.title)


async def remove_messages(groups: list):
    client = Client(
        session_name=os.environ.get("TELEGRAM_SESSION"),
        api_id=os.environ.get("TELEGRAM_API_ID"),
        api_hash=os.environ.get("TELEGRAM_API_SECRET"))

    await client.start()
    try:
        telega = Telegram(client)
        async for group in telega.groups(group_ids=groups):
            print('-' * 100)
            print(
                f'Deleting messages in group "{group.name}" ({group.chat_id}).'
            )
            async for message_page in group.messages(page_size=100):
                print(f'Deleting messages. Batch size {len(message_page.messages)}.')
                await message_page.remove()
                print('-' * 50)
    finally:
        await client.stop()


async def list_groups():
    client = Client(
        session_name=os.environ.get("TELEGRAM_SESSION"),
        api_id=os.environ.get("TELEGRAM_API_ID"),
        api_hash=os.environ.get("TELEGRAM_API_SECRET"))

    await client.start()
    try:
        dialogs = await client.get_dialogs()
        groups = [
            dialog for dialog in dialogs
            if (dialog.chat.type == 'supergroup' or dialog.chat.type == 'group')
        ]
        for _, g in enumerate(groups):
            print(f'{g.chat.id} -> {g.chat.type} -> {g.chat.title}')
        print([g.chat.id for g in groups])
    finally:
        await client.stop()


class RemoveAction(argparse.Action):

    def __call__(self, parser, namespace, values: list, option_string=None):
        asyncio.get_event_loop().run_until_complete(
            remove_messages(values)
        )


class ListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        asyncio.get_event_loop().run_until_complete(
            list_groups()
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='commands')

    remove_parser = subparsers.add_parser('remove', help='Remove messages in groups')
    remove_parser.add_argument(
        '-g',
        '--groups',
        action=RemoveAction,
        nargs='+',
        type=int,
        help='List of groups to clean',
        required=True)

    list_parser = subparsers.add_parser('list', help='List all available groups')
    list_parser.add_argument('_', nargs=0, action=ListAction)
    parser.parse_args()
