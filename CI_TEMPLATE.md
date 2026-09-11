# Pipeline CI - SunuSanté

Nom / Groupe : Fatou Camara — MILIA, École Polytechnique de Thiès

## 1. Le workflow d'intégration continue (chapitre 4, partie 1)

| Étape du cours | Stage Jenkins correspondant |
|---|---|
| 1. Commit & push | *(action du développeur, hors pipeline)* - déclenche le stage **Récupération du code** (`checkout scm`), qui va chercher exactement ce qui vient d'être poussé. |
| 2. Notification (Jenkins est prévenu) | Aucun stage dédié : ce n'est pas une étape du `Jenkinsfile` mais un réglage du *job* Jenkins lui-même (polling SCM, webhook, ou déclenchement manuel). Dans ma configuration (voir question ci-dessous), c'est un déclenchement manuel. |
| 3. Build | **Build** (`python manage.py check` + `collectstatic --dry-run`) |
| 4. Feedback build | Aucun stage dédié : c'est le résultat (vert/rouge) du stage **Build** tel qu'affiché dans la Stage View de Jenkins, immédiatement après son exécution. |
| 5. Tests automatiques | **Tests** (`python manage.py test`) |
| 6. Feedback tests | Aucun stage dédié : résultat du stage **Tests** dans la Stage View, plus le bloc `post { success / failure }` du `Jenkinsfile` qui affiche un message récapitulatif à la toute fin du pipeline. |

**Comment Jenkins est-il informé qu'un nouveau commit existe ?** Dans ma
configuration : **déclenchement manuel** (bouton *Build Now*). Le job
pointe vers mon dépôt en local (`file:///...`) suivant les instructions de
`INSTALLATION_JENKINS.md`, qui ne met en place ni polling SCM planifié ni
webhook GitHub - c'est la méthode la plus simple pour ce TP, mais dans un
vrai projet en production, un webhook GitHub (Jenkins notifié à chaque
`push`, sans délai) serait préférable à un polling périodique.

## 2. Les prérequis d'une bonne CI (chapitre 4, partie 3)

| Prérequis | Statut sur SunuSanté | Détail |
|---|---|---|
| Dépôt avec versioning | Respecté | Git, avec un historique de commits lisible depuis le TP1 ; dépôt distant sur GitHub. |
| Standard de code vérifié | Respecté | `flake8` (config dans `.flake8` à la racine, `max-line-length = 100`), exécuté par le stage **Standard de code (lint)**. |
| Serveur d'intégration continue | Respecté | Jenkins, installé en local via Docker Desktop (image `jenkins/jenkins:lts-jdk17`). Le pipeline lui-même utilise `agent any` (Python installé directement dans le conteneur Jenkins) plutôt qu'un agent Docker dédié (`python:3.11-slim`), pour éviter la complexité du Docker-in-Docker sur cette machine - voir la note sur l'agent Python dans `INSTALLATION_JENKINS.md`. |

## 3. Pourquoi Jenkins, ici (chapitre 4, partie 4)

| Outil | Avantage principal | Inconvénient principal |
|---|---|---|
| GitLab CI/CD | Intégré nativement au dépôt (pas de serveur séparé à installer), configuration déclarative simple (`.gitlab-ci.yml`) | Lie fortement le projet à l'hébergement GitLab - peu pertinent si le code vit sur GitHub ou en local, comme ici. |
| Jenkins | Open source, s'installe n'importe où (local, on-premise), écosystème de plugins immense, totalement indépendant de l'hébergeur Git utilisé | Demande d'installer et de maintenir soi-même un serveur (mises à jour, plugins, sécurité) - plus de friction de mise en route qu'une solution hébergée. |
| GitHub Actions | Intégré directement à GitHub, aucun serveur à héberger, workflows YAML versionnés dans le dépôt | Dépendance forte à GitHub (verrouillage plateforme) ; minutes de calcul limitées/payantes au-delà d'un usage gratuit. |

**Justification du choix pour SunuSanté :** l'objectif de ce TP est
d'apprendre à installer et piloter un serveur CI soi-même (chapitre 4),
pas seulement à cocher une case sur une plateforme hébergée - Jenkins est
donc le bon choix pédagogique ici, en plus d'être indépendant de
l'endroit où le dépôt est hébergé (les TP précédents ont travaillé sur des
dépôts locaux avant d'être poussés sur GitHub). Pour une SunuSanté en
production réelle restant sur GitHub, GitHub Actions éviterait d'avoir un
serveur à maintenir ; Jenkins resterait pertinent si la clinique tient à
garder son infrastructure CI totalement indépendante d'un hébergeur
externe (contrainte de souveraineté sur des données de santé, voir
`DOSSIER_SDLC_TEMPLATE.md` du TP2).

## 4. CI, Continuous Delivery, déploiement continu

**Périmètre couvert :** Intégration continue (CI) uniquement. Le
`Jenkinsfile` récupère le code, le build (vérifications Django), vérifie
le style, exécute toute la pyramide de tests (unitaires, intégration,
système, performance) et scanne la sécurité (SAST, SCA) - à chaque
exécution. Il n'y a ni packaging d'un artefact déployable (pas d'image
Docker de l'application construite), ni release, ni déploiement d'aucune
sorte : aucun stage ne pousse quoi que ce soit vers un serveur de recette
ou de production.

**Ce qui manquerait pour aller plus loin :**
- **Continuous Delivery** : un stage qui construit un artefact déployable
  (image Docker de l'app SunuSanté, publiée dans un registre), suivi
  d'une étape de release **manuelle** - un humain déclenche explicitement
  le déploiement en recette une fois les stages qualité verts (typiquement
  une étape `input` dans le `Jenkinsfile`, qui met le pipeline en pause
  jusqu'à validation).
- **Déploiement continu** : automatiser entièrement la mise en
  production dès que le pipeline est vert, sans aucune intervention
  humaine. Cela suppose une confiance beaucoup plus élevée dans la suite
  de tests (y compris capacitaires et de compatibilité, actuellement hors
  scope - voir partie 5) et un mécanisme de rollback automatique en cas de
  problème détecté après coup.

## 5. Tests non fonctionnels hors scope

Les tests **capacitaires** (charge, montée en charge) et de
**compatibilité** (plusieurs navigateurs/OS) demandent une infrastructure
et des outils dédiés que ce TP n'a pas mis en place : Locust ou k6 pour
scripter et rejouer une charge réaliste, une grille de navigateurs
(Selenium Grid, BrowserStack) pour la compatibilité. À l'échelle de ce
TP, SunuSanté est un projet pédagogique pour une seule clinique, avec un
nombre d'utilisateurs très faible et connu : construire cette
infrastructure maintenant reviendrait à investir du temps dans une
capacité dont personne n'a besoin aujourd'hui - exactement ce que YAGNI
(chapitre 2) déconseille. Le smoke test de performance déjà écrit (partie
2) couvre le strict minimum («&nbsp;est-ce que ça reste rapide&nbsp;»)
sans le coût d'un vrai outil de charge.

**Si SunuSanté grandissait réellement**, il faudrait ajouter : un outil de
test de charge (Locust/k6) scriptant un scénario réaliste (plusieurs
secrétaires prenant des rendez-vous simultanément) avec des seuils précis
par endpoint, exécuté périodiquement plutôt qu'à chaque commit (trop
long pour rester dans la boucle de feedback rapide de la CI) ; et une
matrice de compatibilité couvrant au moins les navigateurs réellement
utilisés par le personnel, si l'interface devenait plus riche en
JavaScript.
