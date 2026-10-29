"""Offline Slack formatting and duplicate-event checks; sends no messages."""
import unittest
from slack_bot import question_from_mention, response_text, first_delivery, SEEN


class SlackTests(unittest.TestCase):
    def test_remove_only_own_mention(self):
        self.assertEqual(question_from_mention('<@BOT> Can <@OTHER> work abroad?', 'BOT'), 'Can <@OTHER> work abroad?')

    def test_mention_without_question(self):
        self.assertEqual(question_from_mention('<@BOT> ', 'BOT'), '')

    def test_reply_contains_original_policy_evidence(self):
        result={'answer':'Up to 30 days with approval.','evidence':[{'title':'Work From Abroad Policy','policy_text':'Employees may work abroad for up to 30 days with approval.'}]}
        reply=response_text(result)
        self.assertIn(result['answer'],reply)
        self.assertIn('Work From Abroad Policy',reply)
        self.assertIn(result['evidence'][0]['policy_text'],reply)

    def test_unknown_answer_does_not_invent_source(self):
        reply=response_text({'answer':'Not specified.','evidence':[]})
        self.assertIn('No supporting policy identified',reply)

    def test_duplicate_delivery_is_ignored(self):
        SEEN.clear()
        self.assertTrue(first_delivery('event-test'))
        self.assertFalse(first_delivery('event-test'))
        self.assertTrue(first_delivery('event-other'))

if __name__ == '__main__':unittest.main()
