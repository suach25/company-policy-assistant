"""Local Slack policy bot using Socket Mode and the shared meaning-search method."""
from pathlib import Path
import html
import logging
import re
import ssl
import threading
import time

from policy_engine import ROOT, answer, settings

LOCK = threading.Lock()
SEEN = {}
SEEN_LOCK = threading.Lock()


def slack_settings():
    config = settings()
    file = ROOT / '.env.slack'
    if file.exists():
        for line in file.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key, value = line.split('=', 1)
                config.setdefault(key.strip(), value.strip().strip('\"\''))
    return config


def question_from_mention(text, bot_id):
    # Remove only this bot's mention; do not silently remove other message content.
    return text.replace(f'<@{bot_id}>', '').strip()


def response_text(result):
    parts = ['Answer', result['answer'], '', 'Relevant policies']
    if not result.get('evidence'):
        parts.append('No supporting policy identified in the supplied collection.')
    for policy in result.get('evidence', []):
        parts.extend([policy['title'], policy['policy_text'], ''])
    return '\n'.join(parts).strip()


def first_delivery(event_id):
    now = time.monotonic()
    with SEEN_LOCK:
        for key in list(SEEN):
            if SEEN[key] < now-600:
                del SEEN[key]
        if event_id in SEEN:
            return False
        SEEN[event_id] = now
        return True


def main():
    from slack_bolt import App
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    from slack_sdk import WebClient

    config = slack_settings()
    for name, prefix in [('SLACK_APP_TOKEN', 'xapp-'), ('SLACK_BOT_TOKEN', 'xoxb-')]:
        if not config.get(name, '').startswith(prefix):
            raise SystemExit(f'Please save a valid {name} in .env.slack before starting.')
    if not config.get('GEMINI_API_KEY'):
        raise SystemExit('The Gemini key is missing from the private .env file.')
    # Keep certificate verification enabled on macOS Python installations.
    certificate = '/etc/ssl/cert.pem'
    context = ssl.create_default_context(cafile=certificate if Path(certificate).exists() else None)
    client = WebClient(token=config['SLACK_BOT_TOKEN'], ssl=context)
    app = App(client=client)

    @app.event('app_mention')
    def handle_mention(event, body, say, context):
        if event.get('bot_id') or event.get('subtype'):
            return
        identifier = body.get('event_id') or event.get('ts')
        if not first_delivery(identifier):
            return
        question = question_from_mention(event.get('text', ''), context.bot_user_id)

        def reply(message):
            # Plain text prevents AI output from triggering Slack mentions or links.
            chunks = [message[i:i+2800] for i in range(0, len(message), 2800)]
            say(text=html.escape(message, quote=False),
                blocks=[{'type':'section','text':{'type':'plain_text','text':chunk}} for chunk in chunks[:10]],
                thread_ts=event.get('thread_ts'), unfurl_links=False, unfurl_media=False)

        if not question or len(question) > 2000:
            reply('Mention me with a company policy question of up to 2,000 characters. Example: @Policy Assistant How many days per week may I work remotely?')
            return
        if not LOCK.acquire(blocking=False):
            reply('I am answering another question. Please try again shortly.')
            return
        try:
            reply(response_text(answer(question, 'rag')))
        except RuntimeError:
            reply('I could not complete the policy search. Please try again later. If this continues, check the local bot settings or Gemini usage limits.')
        except Exception:
            # Do not print exception objects that might contain credentials.
            logging.error('A policy request or Slack reply failed; no secret values were logged.')
        finally:
            LOCK.release()

    print('Starting Policy Assistant. Keep this Terminal window open; press Control+C to stop.', flush=True)
    print('The bot responds when mentioned in a channel where it has been added.', flush=True)
    handler = SocketModeHandler(app, config['SLACK_APP_TOKEN'])
    handler.client.web_client.ssl = context
    try:
        handler.connect()
        print('Connected to Slack. Policy Assistant is ready for mentions.', flush=True)
        threading.Event().wait()
    except KeyboardInterrupt:
        print('Policy Assistant stopped.', flush=True)
    finally:
        handler.close()


if __name__ == '__main__':
    main()
