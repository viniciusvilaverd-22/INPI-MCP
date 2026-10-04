import re
from unidecode import unidecode

CORPORATE_SUFFIXES = {
    'LTDA','LIMITADA','ME','EPP','SA','S/A','EIRELI','SIMPLES','UNIPESSOAL'
}

def normalize_mark(value: str | None) -> str:
    if not value:
        return ''
    value = unidecode(value).upper()
    value = re.sub(r'[^A-Z0-9]+', ' ', value)
    return re.sub(r'\s+', ' ', value).strip()

def lexical_core(value: str | None) -> str:
    tokens = [t for t in normalize_mark(value).split() if t not in CORPORATE_SUFFIXES]
    return ' '.join(tokens)

def ptbr_phonetic(value: str | None) -> str:
    s = lexical_core(value)
    if not s:
        return ''
    repl = [
        ('PH','F'), ('Y','I'), ('W','V'), ('K','C'), ('Q','C'),
        ('CH','X'), ('LH','LI'), ('NH','NI'), ('GE','JE'), ('GI','JI'),
        ('SS','S'), ('SC','S'), ('Ç','S'), ('Z','S')
    ]
    for a,b in repl:
        s = s.replace(a,b)
    s = re.sub(r'([A-Z])\1+', r'\1', s)
    s = re.sub(r'[^A-Z0-9 ]+', '', s)
    return s
