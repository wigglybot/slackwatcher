"""
Forward events received via the Slack api to event store
"""

from settings import *
import os
import requests
import uuid
from flask import Flask
from slackeventsapi import SlackEventAdapter

application = Flask(__name__)

slack_events_adapter = SlackEventAdapter(
    EVENTS_API_TOKEN,
    INCOMING_ENDPOINT_URL,
    server=application
)

@slack_events_adapter.on("app_mention")
def app_mention(event):
    log.debug("app_mention() enter")
    headers = {
        "ES-EventType": "app_mention",
        "ES-EventId": str(uuid.uuid1())
    }
    log.debug("app_mention() posting to stream")
    requests.post(
            "http://%s:%s/streams/dialogue" % (EVENT_STORE_URL, EVENT_STORE_HTTP_PORT),
            headers=headers,
            json=event
    )
    log.debug("app_mention() stream updated")


@application.route('/test')
def test():
    log.debug("test() enter")
    headers = {
        "ES-EventType": "test",
        "ES-EventId": str(uuid.uuid1())
    }
    log.debug("test() posting to stream")
    requests.post(
            "http://%s:%s/streams/test" % (EVENT_STORE_URL, EVENT_STORE_HTTP_PORT),
            headers=headers,
            json={"incoming": "test event"}
    )
    log.debug("test() stream updated")
    return "Test event sent to eventstore."
