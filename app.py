"""Company policy comparison: Flask app served by Gunicorn when hosted."""
from collections import deque
import json
import os
import threading
import time
from urllib.parse import urlsplit

from flask import Flask, jsonify, request, send_file
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
from policy_engine import ROOT, answer, policies

app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 10000
AI_LOCK = threading.Lock()
RATE_LOCK = threading.Lock()
AI_REQUESTS = deque()


def allow_ai_request():
    """Single-worker, shared limit: at most 12 generation requests/minute."""
    now = time.monotonic()
    with RATE_LOCK:
        while AI_REQUESTS and AI_REQUESTS[0] <= now-60:
            AI_REQUESTS.popleft()
        if len(AI_REQUESTS) >= 12:
            return False
        AI_REQUESTS.append(now)
    return True


@app.after_request
def response_headers(response):
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response


@app.get('/')
def home():
    return send_file(ROOT/'web/index.html')


@app.get('/health')
def health():
    # Does not call Gemini or consume quota.
    return jsonify(status='ok')


@app.get('/api/policies')
def source_policies():
    return jsonify(policies())


@app.get('/api/evaluation')
def evaluation():
    return jsonify(json.loads((ROOT/'tests/evaluation_review.json').read_text()))


@app.post('/api/answer')
def policy_answer():
    if request.mimetype != 'application/json':
        return jsonify(error='A JSON request is required.'), 415
    origin = request.headers.get('Origin')
    if origin:
        parsed = urlsplit(origin)
        if parsed.scheme not in ('http', 'https') or parsed.netloc != request.host:
            return jsonify(error='This request must come from the policy website.'), 403
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            raise ValueError()
        question = data.get('question')
        method = data.get('method')
        if not isinstance(question, str) or not question.strip() or len(question) > 2000:
            raise ValueError()
        if method not in ('rules', 'full_context', 'rag'):
            raise ValueError()
        if method == 'rules':
            return jsonify(answer(question, method))
        if not AI_LOCK.acquire(blocking=False):
            return jsonify(error='Another AI answer is running. Please wait and try again.'), 429
        try:
            if not allow_ai_request():
                response = jsonify(error='The website has reached its request limit. Please wait one minute and try again.')
                response.headers['Retry-After'] = '60'
                return response, 429
            return jsonify(answer(question, method))
        finally:
            AI_LOCK.release()
    except RequestEntityTooLarge:
        raise
    except (ValueError, TypeError, BadRequest):
        return jsonify(error='Enter a question of 1–2,000 characters and a valid method.'), 400
    except RuntimeError as error:
        app.logger.warning('Policy service error: %s', error)
        if 'HTTP 429' in str(error):
            return jsonify(error='Gemini has reached its usage limit. Please wait and try again.'), 429
        return jsonify(error='The AI service could not complete this answer. Please try again later.'), 502
    except Exception:
        app.logger.exception('Unexpected policy request failure')
        return jsonify(error='The website could not complete this answer. Please try again.'), 500


@app.errorhandler(RequestEntityTooLarge)
def request_too_large(error):
    return jsonify(error='The question is too large.'), 413


@app.errorhandler(404)
def not_found(error):
    return jsonify(error='Page not found.'), 404


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', '8765')), debug=False)
