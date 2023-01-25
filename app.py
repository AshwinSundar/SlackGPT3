import os
import re
import openai

openai.api_key = os.environ.get("OPENAI_KEY")
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# import logging
# logging.basicConfig(level=logging.DEBUG)

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


def queryModel(model, query, max_tokens, max_responses):
    return openai.Completion.create(
        engine=model,
        prompt=f"{query}",
        max_tokens=max_tokens,
        n=max_responses,
        stop=None,
    )


def plainResponseBlock(text):
    return {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": text,
            "emoji": False,
        },
    }


def modelDescrBlock():
    return {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "*Language Model*: OpenAI text-da-vinci-003",
            }
        ],
    }


def promptEchoBlock(text, author):
    return {
        "type": "context",
        "elements": [
            {"type": "mrkdwn", "text": f"*Prompt*: {text}\n*Author*: {author}"}
        ],
    }


def dividerBlockMsg():
    return {"type": "divider"}


def debugBlock(msg):
    return {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": f"{msg}",
        },
    }


# decorator goes BEFORE main function!!
@app.message(re.compile("(.*)"))
def reply(message, say):
    response = queryModel("text-davinci-003", message["text"], 1000, 1)
    say(
        blocks=[
            plainResponseBlock(response.choices[0]["text"]),
            modelDescrBlock(),
        ]
    )


# ack = acknowledge (required for commands)
# respond
# command - metadata sent to Slack
@app.command("/slackgpt")
def echo(ack, respond, command):
    ack()  # must acknowledge commands
    response = queryModel("text-davinci-003", command["text"], 1000, 1)
    respond(
        blocks=[
            dividerBlockMsg(),
            plainResponseBlock(response.choices[0]["text"]),
            dividerBlockMsg(),
            promptEchoBlock(command["text"], command["user_name"]),
            modelDescrBlock(),
            # debugBlock(command)
        ]
    )


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
