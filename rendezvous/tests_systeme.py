"""
TP4, partie 2 — Test système (chapitre 4).

Un test système exerce l'application ENTIÈRE, de bout en bout, comme le
ferait un utilisateur : formulaire -> soumission -> facture. Contrairement
aux tests unitaires (TP1/TP2) ou aux tests d'intégration vue par vue
(TP3), on ne teste pas ici un composant isolé, mais l'enchaînement complet
à travers plusieurs apps (patients + rendezvous).

Rappel de repère de dates (comme au TP1) : le 21/07/2026 est un mardi
(semaine, pas de majoration weekend).
"""
from django.test import TestCase

from patients.models import Patient


class ParcoursCompletRendezVousTest(TestCase):
    def test_parcours_complet_de_la_prise_de_rendez_vous_a_la_facture(self):
        # 1. Créer un patient
        patient = Patient.objects.create(
            nom="Ndiaye", prenom="Awa", email="awa@example.com", est_vip=False
        )

        # 2. Afficher le formulaire de prise de rendez-vous : le patient
        # doit y apparaître (app patients -> app rendezvous).
        reponse_formulaire = self.client.get("/rendezvous/")
        self.assertEqual(reponse_formulaire.status_code, 200)
        self.assertContains(reponse_formulaire, "Awa Ndiaye")

        # 3. Soumettre une prise de rendez-vous
        reponse_post = self.client.post("/rendezvous/", {
            "patient": patient.id,
            "type_consultation": "GENERALISTE",
            "date": "2026-07-21",
            "notes": "RAS",
        })
        self.assertEqual(reponse_post.status_code, 302)

        # 4. Consulter la facture : le total doit correspondre au tarif
        # attendu (5000 FCFA - généraliste, semaine, pas de VIP).
        reponse_facture = self.client.get(f"/rendezvous/facture/{patient.id}/")
        self.assertEqual(reponse_facture.status_code, 200)
        self.assertEqual(reponse_facture.context["total"], 5000)
