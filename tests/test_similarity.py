from app.normalization import normalize_mark
from app.similarity import compare_marks

def test_normalization():
    assert normalize_mark('Gêntill-Mob Serviços') == 'GENTILL MOB SERVICOS'

def test_similar_marks_score_high():
    r=compare_marks('GENTILL MOB','GENTIL MOB',[39],[39])
    assert r.overall > .80
    assert r.phonetic > .90
    assert 'mesma classe Nice informada' in r.reasons

def test_different_marks_score_lower():
    a=compare_marks('GENTILL MOB','GENTIL MOB',[39],[39]).overall
    b=compare_marks('GENTILL MOB','ALFA ALIMENTOS',[39],[30]).overall
    assert a > b
