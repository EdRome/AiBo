import Levenshtein
from collections import defaultdict, Counter

class CorrectorProvincias:
    def __init__(self, threshold=0.8):
        self.threshold = threshold
        self.canonicas = []

    def fit(self, X):
        grupos = []

        for prov in X:
            agregado = False
            for grupo in grupos:
                if any(Levenshtein.jaro(prov, miembro) >= self.threshold for miembro in grupo):
                    grupo.append(prov)
                    agregado = True
                    break
            if not agregado:
                grupos.append([prov])

        # Elegir forma canónica por grupo (más frecuente en el dataset)
        frecuencia = Counter(X)
        self.canonicas = [
            max(grupo, key=lambda x: frecuencia[x]) for grupo in grupos
        ]

        return self

    def predict(self, X):
        mejor_match = None
        mejor_score = 0.0
        for canonica in self.canonicas:
            score = Levenshtein.jaro(X, canonica)
            if score >= self.threshold and score > mejor_score:
                mejor_match = canonica
                mejor_score = score
        return mejor_match if mejor_match else X