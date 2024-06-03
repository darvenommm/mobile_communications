import asyncio
from django.test import TestCase
from channels.testing import WebsocketCommunicator

from subscribers.models import Subscriber
from calls.consumers.storages.call_rooms import CallRoomsStorage
from .main import CallRoomsConsumer
from .types import ActionType


class MyTests(TestCase):
    async def test_success(self):

        subscriber1 = Subscriber(username="test", first_name="name", last_name="surname")
        subscriber1.set_password("password")
        await subscriber1.asave()

        subscriber2 = Subscriber(username="test2", first_name="name", last_name="surname")
        subscriber2.set_password("password")
        await subscriber2.asave()

        room_id = await CallRoomsStorage().add(str(subscriber1.id), str(subscriber2.id))

        communicator1 = WebsocketCommunicator(
            CallRoomsConsumer.as_asgi(), f"/call-rooms/{room_id}/"
        )
        communicator2 = WebsocketCommunicator(
            CallRoomsConsumer.as_asgi(), f"/call-rooms/{room_id}/"
        )

        communicator1.scope["user"] = subscriber1
        communicator2.scope["user"] = subscriber2
        for communicator in (communicator1, communicator2):
            communicator.scope["url_route"] = {"kwargs": {"room_id": room_id}}

        async with asyncio.TaskGroup() as tg:
            connection_task1 = tg.create_task(communicator1.connect())
            connection_task2 = tg.create_task(communicator2.connect())

        connected1, _ = await connection_task1
        connected2, _ = await connection_task2

        assert connected1 and connected2

        await communicator1.send_json_to({"type": ActionType.offer, "data": {"offer": "pass"}})

        await communicator2.receive_json_from()
        await communicator2.send_json_to({"type": ActionType.answer, "data": {"answer": "pass"}})

        await communicator1.receive_json_from()

        CallRoomsStorage().set_start(room_id)

        await communicator1.disconnect()
        await communicator2.disconnect()