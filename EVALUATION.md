# Evaluation after instruction refinement

14 questions × 3 methods = 42 successful responses. Results are from one run with the same generation model and instructions for both AI methods. Five-second test pacing is outside measured response time.

Review performed by the coding assistant against source policy text and predefined expected behavior. Student review remains necessary. No independent human review is claimed.

| Method | Meets expected behavior | Mean seconds | Mean generation input tokens | Mean generation output tokens |
|---|---:|---:|---:|---:|
| rules | 7/14 | 0.002 | 0 | 0 |
| full_context | 14/14 | 1.266 | 3718.6 | 56.5 |
| rag | 13/14 | 1.393 | 348.6 | 60.6 |

No invented policy facts were observed in this run. This does not establish a zero hallucination rate. Word search returned the wrong policy once and incomplete answers six times. RAG included a real but irrelevant Work From Abroad policy in its answer to a leave question. No generative method should be treated as an approval authority.

The saved results in `tests/evaluation_results.jsonl` use the refined instructions. The website displays the reviewed summary in `tests/evaluation_review.json`. Earlier development attempts are excluded from this repository copy.

Embedding usage metadata was absent, so embedding token consumption is unknown. Index preparation is a separate one-time operation. Exact monetary cost has not been verified.

## Question-level review

- paraphrase_abroad / rules: Wrong policy. Returns Job Posting Policy instead of Work From Abroad Policy.
- expense_boundary / rules: Incomplete. Quotes threshold but does not explicitly address exactly $500.
- vacation_missing / rules: Incomplete. Quotes source but does not explicitly identify the missing rollover maximum.
- password_missing / rules: Incomplete. Quotes source but does not explicitly identify the missing minimum length.
- two_policies / rules: Incomplete. Returns VPN policy but misses working-abroad limit and approval.
- ambiguous / rules: Incomplete. Returns some leave policies, without clearly resolving ambiguity; vacation policy is absent.
- ambiguous / rag: Irrelevant addition. Correct leave policies are included, but Work From Abroad is also presented as a leave policy.
- vague_gifts / rules: Incomplete. Quotes guidelines but does not explicitly identify the missing monetary limit.
