"""
Forward events received via the Slack api to event store
"""

import os
import requests
import uuid
from flask import Flask
from slackeventsapi import SlackEventAdapter
import logging
from configobj import ConfigObj

dir_path = os.path.dirname(os.path.realpath(__file__))
CONFIG = ConfigObj(os.path.join(dir_path, "config.ini"))
ENVIRON = os.getenv("ENVIRON", CONFIG["config"]["ENVIRON"])

EVENT_STORE_URL = os.getenv("EVENT_STORE_URL", CONFIG[ENVIRON]["EVENT_STORE_URL"])
EVENT_STORE_HTTP_PORT = os.getenv("EVENT_STORE_HTTP_PORT", int(CONFIG[ENVIRON]["EVENT_STORE_HTTP_PORT"]))
EVENT_STORE_USER = os.getenv("EVENT_STORE_USER", CONFIG[ENVIRON]["EVENT_STORE_USER"])
EVENT_STORE_PASS = os.getenv("EVENT_STORE_PASS", CONFIG[ENVIRON]["EVENT_STORE_PASS"])
LOGGER_LEVEL = os.getenv("LOGGER_LEVEL", int(CONFIG[ENVIRON]["LOGGER_LEVEL"]))
LOGGER_FORMAT = '%(asctime)s [%(name)s] %(message)s'
EVENTS_API_TOKEN = os.getenv("EVENTS_API_TOKEN", CONFIG[ENVIRON]["EVENTS_API_TOKEN"])  # todo: rename to clarify this is slack signing token
INCOMING_ENDPOINT_URL = os.getenv("ENDPOINT", CONFIG[ENVIRON]["INCOMING_ENDPOINT_URL"])  # todo: rename in docker-compose to match
V_MA = CONFIG["version"]["MAJOR"]
V_MI = CONFIG["version"]["MINOR"]
V_RE = CONFIG["version"]["REVISION"]
V_DATE = CONFIG["version"]["DATE"]
CODENAME = CONFIG["version"]["CODENAME"]

logging.basicConfig(format=LOGGER_FORMAT, datefmt='[%H:%M:%S]')
log = logging.getLogger("slackwatcher")

"""
CRITICAL 50
ERROR    40
WARNING  30
INFO     20
DEBUG    10
NOTSET    0
"""
log.setLevel(LOGGER_LEVEL)

application = Flask(__name__)

slack_events_adapter = SlackEventAdapter(
    EVENTS_API_TOKEN,
    INCOMING_ENDPOINT_URL,
    server=application
)


def version_fancy():
    return ''.join((
        "\n",
        " (  (                       (         (           )", "\n",
        " )\))(   ' (   (  (  (  (   )\ (    ( )\       ( /(", "\n",
        "((_)()\ )  )\  )\))( )\))( ((_))\ ) )((_)  (   )\())", "\n",
        "_(())\_)()((_)((_))\((_))\  _ (()/(((_)_   )\ (_))/", "\n",
        "\ \((_)/ / (_) (()(_)(()(_)| | )(_))| _ ) ((_)| |_ ",
        "         version: {0}".format("v%s.%s.%s" % (V_MA, V_MI, V_RE)), "\n",
        " \ \/\/ /  | |/ _` |/ _` | | || || || _ \/ _ \|  _|",
        "       code name: {0}".format(CODENAME), "\n",
        "  \_/\_/   |_|\__, |\__, | |_| \_, ||___/\___/ \__|",
        "    release date: {0}".format(V_DATE), "\n",
        "              |___/ |___/      |__/", "\n"
    ))


log.info(version_fancy())


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
