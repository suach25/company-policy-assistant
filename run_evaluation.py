"""Paced, resumable evaluation. Saves evidence, not automatic correctness scores."""
import hashlib
import json
import time
from datetime import datetime, timezone
from policy_engine import ROOT, answer

if __name__ == '__main__':
    engine_hash = hashlib.sha256((ROOT/'policy_engine.py').read_bytes()).hexdigest()
    target = ROOT/'tests/evaluation_results.jsonl'
    records = [json.loads(line) for line in target.read_text().splitlines()] if target.exists() else []
    done = {(r['test_id'],r['method']) for r in records if r.get('engine_sha256') == engine_hash and 'result' in r}
    questions = json.loads((ROOT/'tests/test_questions.json').read_text())
    for q in questions:
        for method in ['rules','full_context','rag']:
            if (q['id'],method) in done:
                continue
            if method != 'rules':
                time.sleep(5)  # Outside measured answer time; keep below 15 requests/minute.
            row = dict(test_id=q['id'], question=q['question'], method=method,
                       engine_sha256=engine_hash, timestamp=datetime.now(timezone.utc).isoformat())
            try:
                row['result'] = answer(q['question'],method)
                print(q['id'],method,row['result']['answer'],flush=True)
            except Exception as error:
                row['error'] = str(error)
                print(q['id'],method,str(error),flush=True)
            with target.open('a') as file:
                file.write(json.dumps(row)+'\n')
