"""
Chaque vue a une seule responsabilité : parler HTTP (lire la requête,
rediriger, choisir un template). Validation, tarification et persistance
sont délégués à RendezVousForm et RendezVousService (SRP, chapitre 2).
"""
from django.contrib import messages
from django.shortcuts import redirect, render

from patients.models import Patient

from .forms import RendezVousForm
from .models import TypeConsultation
from .services import RendezVousService

_service = RendezVousService()


def prendre_rendez_vous(request):
    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if not form.is_valid():
            for erreurs in form.errors.values():
                for erreur in erreurs:
                    messages.error(request, erreur)
            return redirect("rendezvous:prendre")

        rendez_vous = _service.creer_rendez_vous(
            patient=form.cleaned_data["patient"],
            type_consultation=form.cleaned_data["type_consultation"],
            date_rdv=form.cleaned_data["date"],
            notes=form.cleaned_data["notes"],
        )

        messages.success(request, f"Rendez-vous confirmé - {rendez_vous.prix} FCFA")
        return redirect("rendezvous:prendre")

    patients = Patient.objects.all()
    return render(
        request,
        "rendezvous/formulaire.html",
        {"patients": patients, "types": TypeConsultation.choices},
    )


def facture_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    total = _service.facturer_patient(patient)
    return render(request, "rendezvous/facture.html", {"patient": patient, "total": total})
