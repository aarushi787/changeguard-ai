"""One bounded worker subprocess per extraction; no document contents in logs."""
import json
import sys
from contextlib import redirect_stdout

if __name__=='__main__':
    # Library diagnostics must never corrupt the machine-readable stdout channel.
    # The parent captures stderr privately and exposes only a generic failure reason.
    with redirect_stdout(sys.stderr):
        from backend.intelligence import DeterministicProvider
        result=DeterministicProvider().extract(sys.stdin.buffer.read(20*1024*1024+1),sys.argv[1])
    sys.stdout.buffer.write(json.dumps(result,ensure_ascii=False).encode('utf-8'))
