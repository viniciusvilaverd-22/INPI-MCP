from dataclasses import dataclass, asdict
from rapidfuzz import fuzz
from .normalization import normalize_mark, lexical_core, ptbr_phonetic

ENGINE_VERSION = 'sim-v0.1.0'

@dataclass(frozen=True)
class SimilarityResult:
    overall: float
    lexical: float
    phonetic: float
    token_structure: float
    semantic: float
    market_affinity: float
    reasons: list[str]
    engine_version: str = ENGINE_VERSION

    def to_dict(self):
        return asdict(self)

def _score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.ratio(a,b) / 100.0

def _token_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return fuzz.token_set_ratio(a,b) / 100.0

def class_affinity(left: set[int], right: set[int]) -> float:
    if not left or not right:
        return 0.20
    if left & right:
        return 1.0
    return 0.35

def compare_marks(left_name: str, right_name: str, left_classes=(), right_classes=()) -> SimilarityResult:
    l_norm, r_norm = normalize_mark(left_name), normalize_mark(right_name)
    l_core, r_core = lexical_core(left_name), lexical_core(right_name)
    lexical = max(_score(l_norm,r_norm), _score(l_core,r_core))
    phonetic = _score(ptbr_phonetic(left_name), ptbr_phonetic(right_name))
    token = _token_score(l_core, r_core)
    semantic = 0.0
    market = class_affinity(set(left_classes), set(right_classes))
    overall = (0.35*lexical + 0.30*phonetic + 0.20*token + 0.15*market)
    reasons=[]
    if lexical >= .85: reasons.append('alta proximidade gráfica/lexical')
    if phonetic >= .85: reasons.append('alta proximidade fonética computacional')
    if token >= .85: reasons.append('forte sobreposição de elementos nominativos')
    if market >= .95: reasons.append('mesma classe Nice informada')
    if not reasons: reasons.append('similaridade derivada da combinação de sinais fracos')
    return SimilarityResult(round(overall,4), round(lexical,4), round(phonetic,4), round(token,4), semantic, round(market,4), reasons)
