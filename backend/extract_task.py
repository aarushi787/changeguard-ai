"""One bounded worker subprocess per extraction; no document contents in logs."""
import json
import sys
from backend.intelligence import DeterministicProvider

if __name__=='__main__':
    result=DeterministicProvider().extract(sys.stdin.buffer.read(20*1024*1024+1),sys.argv[1])
    sys.stdout.buffer.write(json.dumps(result,ensure_ascii=False).encode('utf-8'))
