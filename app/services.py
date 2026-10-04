from .repository import TrademarkRepository
from .similarity import compare_marks

DISCLAIMER='Resultado computacional informativo; não constitui decisão do INPI nem parecer jurídico.'

class TrademarkService:
    def __init__(self, repo: TrademarkRepository): self.repo=repo

    def search(self, query: str, nice_classes: list[int], limit: int):
        candidates=self.repo.candidates(query,nice_classes,max(limit*5,50))
        rows=[]
        for tm in candidates:
            classes=sorted({c.nice_class for c in tm.classes})
            sim=compare_marks(query, tm.mark_name or '', nice_classes, classes)
            rows.append({
                'process_number':tm.process_number,'mark_name':tm.mark_name,
                'nice_classes':classes,'similarity':sim.to_dict(),
                'last_rpi_number':tm.last_rpi_number,
            })
        rows.sort(key=lambda x:x['similarity']['overall'], reverse=True)
        return {'query':query,'results':rows[:limit],'disclaimer':DISCLAIMER}

    def compare(self,left,right):
        sim=compare_marks(left.name,right.name,left.nice_classes,right.nice_classes)
        return {'similarity':sim.to_dict(),'legal_conclusion':None,'disclaimer':DISCLAIMER}
