"""Call websocket urls."""

from django.urls import path

from .consumers import CallOffersConsumer, CallRoomsConsumer, SubscriberConsumer

websocket_urlpatterns = [
    path("subscribers/", SubscriberConsumer.as_asgi()),
    path("call-offers/", CallOffersConsumer.as_asgi()),
    path("call-rooms/<uuid:room_id>/", CallRoomsConsumer.as_asgi()),
]
