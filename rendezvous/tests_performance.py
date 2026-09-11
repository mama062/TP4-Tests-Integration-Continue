"""
TP4, partie 2 — Test non fonctionnel de performance (chapitre 4).

"Est-ce que c'est rapide ?" On ne fait pas ici un vrai test de charge
(outils dédiés : Locust, k6 — hors scope de ce TP), mais un test de
performance minimal ("smoke test") qui échoue si une régression grossière
rend une page anormalement lente.

Seuil choisi (1 seconde) : très généreux pour une simple page de
formulaire sans requête coûteuse, mais assez bas pour attraper une vraie
régression (ex. une requête N+1 ajoutée par erreur) sans faire échouer le
pipeline CI sur une machine simplement chargée.
"""
import time

from django.test import TestCase

SEUIL_SECONDES = 1.0


class PerformanceFormulaireTest(TestCase):
    def test_formulaire_repond_rapidement(self):
        debut = time.perf_counter()
        reponse = self.client.get("/rendezvous/")
        duree = time.perf_counter() - debut

        self.assertEqual(reponse.status_code, 200)
        self.assertLess(
            duree,
            SEUIL_SECONDES,
            f"GET /rendezvous/ a mis {duree:.3f}s, attendu < {SEUIL_SECONDES}s",
        )
