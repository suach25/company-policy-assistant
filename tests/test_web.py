"""Offline checks for hosting and request handling; no Gemini calls."""
import unittest
from unittest.mock import patch
import app as website


class WebsiteTests(unittest.TestCase):
    def setUp(self):
        self.client = website.app.test_client()
        website.AI_REQUESTS.clear()

    def test_page_data_and_saved_review(self):
        with self.client.get('/') as response:
            self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.client.get('/api/policies').json), 98)
        self.assertEqual(len(self.client.get('/api/evaluation').json['results']), 42)

    def test_health_is_independent_of_gemini(self):
        with patch('app.answer') as mocked:
            self.assertEqual(self.client.get('/health').json, {'status': 'ok'})
            mocked.assert_not_called()

    def test_word_search(self):
        response = self.client.post('/api/answer', json={'question': 'How many days per week may I work remotely?', 'method': 'rules'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['relevant_policies'], ['Remote Work Policy'])

    def test_https_origin_at_hosting_proxy(self):
        response = self.client.post('/api/answer', base_url='http://policies.example', headers={'Origin':'https://policies.example'}, json={'question':'remote work','method':'rules'})
        self.assertEqual(response.status_code, 200)

    def test_cross_site_request_rejected(self):
        response = self.client.post('/api/answer', headers={'Origin':'https://other.example'}, json={'question':'remote work','method':'rules'})
        self.assertEqual(response.status_code, 403)

    def test_bad_input_never_calls_gemini(self):
        with patch('app.answer') as mocked:
            for data in [None, [], {'question':'','method':'rules'}, {'question':'x'*2001,'method':'rag'}, {'question':1,'method':'rag'}, {'question':'hello','method':'invalid'}]:
                self.assertEqual(self.client.post('/api/answer', data=__import__('json').dumps(data), content_type='application/json').status_code, 400)
            self.assertEqual(self.client.post('/api/answer', data='{', content_type='application/json').status_code, 400)
            self.assertEqual(self.client.post('/api/answer', data='hello').status_code, 415)
            self.assertEqual(self.client.post('/api/answer', data='x'*10001, content_type='application/json').status_code, 413)
            mocked.assert_not_called()

    def test_private_files_not_served(self):
        for path in ['/.env','/policy_engine.py','/data/vector_index.json','/../.env']:
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_busy_and_rate_limit_do_not_call_gemini(self):
        with patch('app.answer') as mocked:
            website.AI_LOCK.acquire()
            try:
                self.assertEqual(self.client.post('/api/answer', json={'question':'hello','method':'rag'}).status_code, 429)
            finally:
                website.AI_LOCK.release()
            website.AI_REQUESTS.extend([__import__('time').monotonic()]*12)
            self.assertEqual(self.client.post('/api/answer', json={'question':'hello','method':'rag'}).status_code, 429)
            mocked.assert_not_called()

    def test_provider_failure_does_not_expose_internal_detail(self):
        with patch('app.answer', side_effect=RuntimeError('HTTP 403 project internal detail')):
            response=self.client.post('/api/answer', json={'question':'hello','method':'rag'})
        self.assertEqual(response.status_code, 502)
        self.assertNotIn('internal detail',response.get_data(as_text=True))
        self.assertTrue(website.AI_LOCK.acquire(blocking=False))
        website.AI_LOCK.release()

if __name__ == '__main__':
    unittest.main()
