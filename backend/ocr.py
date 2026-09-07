"""Optional local Tesseract TSV adapter. No network or model fallback."""
import csv
import io
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

def executable():return os.getenv('TESSERACT_CMD') or shutil.which('tesseract')
def available():return bool(executable())
def recognize(content,rotation=0):
    from PIL import Image,ImageOps
    if not available():raise ValueError('Local OCR unavailable: install Tesseract or set TESSERACT_CMD.')
    im=Image.open(io.BytesIO(content)).convert('L');w,h=im.size
    im=ImageOps.autocontrast(im).rotate(rotation,expand=True)
    with tempfile.TemporaryDirectory(prefix='cg-ocr-') as temp:
        path=Path(temp)/'source.png';im.save(path)
        result=subprocess.run([executable(),str(path),'stdout','--psm','11','tsv'],capture_output=True,timeout=25,check=True)
    groups={}
    for token in csv.DictReader(io.StringIO(result.stdout.decode('utf-8',errors='replace')),delimiter='\t'):
        if not token.get('text','').strip() or float(token.get('conf','-1'))<0:continue
        key=tuple(token.get(k) for k in ['block_num','par_num','line_num']);groups.setdefault(key,[]).append(token)
    lines=[]
    for words in groups.values():
        x=min(int(t['left']) for t in words);y=min(int(t['top']) for t in words);x2=max(int(t['left'])+int(t['width']) for t in words);y2=max(int(t['top'])+int(t['height']) for t in words)
        if rotation==90:box=[w-y2,x,w-y,x2]
        elif rotation==180:box=[w-x2,h-y2,w-x,h-y]
        elif rotation==270:box=[y,h-x2,y2,h-x]
        else:box=[x,y,x2,y2]
        lines.append({'text':' '.join(t['text'] for t in words),'bbox':box,'confidence':min(.89,sum(float(t['conf']) for t in words)/len(words)/100),'method':'local_tesseract_ocr','rotation':rotation})
    return lines
