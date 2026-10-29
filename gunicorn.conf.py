"""Hosting settings; one worker keeps the shared request limit consistent."""
import os

bind = '0.0.0.0:' + os.environ.get('PORT', '10000')
workers = 1
worker_class = 'gthread'
threads = 4
timeout = 180
graceful_timeout = 30
accesslog = '-'
errorlog = '-'
