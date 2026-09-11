// Pipeline Jenkins pour SunuSanté (chapitre 4).
//
// Chaque stage correspond à une étape du workflow vu en cours :
// Récupération du code -> Build -> Standard de code -> Tests -> Sécurité.
// Un stage rouge arrête le pipeline : c'est le "feedback" du serveur CI au
// dépôt, en quelques minutes plutôt qu'en semaines (cf. chapitre 4, partie 1).
//
// Portabilité (voir INSTALLATION_JENKINS.md) : avec l'agent Docker
// (recommandé), tous les stages tournent dans un conteneur Linux, quel
// que soit le système d'exploitation qui héberge Jenkins. Si vous utilisez
// `agent any` (agent Jenkins natif, sans Docker), runCmd() bascule
// automatiquement entre `sh` (Linux/macOS) et `bat` (Windows) : aucune
// autre ligne du pipeline n'a besoin de changer.

def runCmd(String commande) {
    if (isUnix()) {
        sh commande
    } else {
        bat commande
    }
}

pipeline {
        agent any

    stages {
        stage('Récupération du code') {
            steps {
                checkout scm
            }
        }

        stage('Installation des dépendances') {
            steps {
                runCmd 'python -m pip install --upgrade pip --break-system-packages'
                runCmd 'pip install -r requirements-dev.txt --break-system-packages'
            }
        }

        stage('Build') {
            // Python ne se compile pas comme Java, mais on peut quand
            // même vérifier que le projet est valide avant d'aller plus
            // loin : configuration Django cohérente, fichiers statiques
            // collectables sans erreur.
            steps {
                runCmd 'python manage.py check'
                runCmd 'python manage.py collectstatic --noinput --dry-run'
            }
        }

        stage('Standard de code (lint)') {
            // Prérequis d'une bonne CI, chapitre 4 partie 3 : le style est
            // vérifié par la machine, la revue de code se concentre sur le
            // fond.
            steps {
                runCmd 'flake8 .'
            }
        }

        stage('Tests') {
            // Unitaires, intégration et système (TP1-TP4) sont tous
            // exécutés ici par le même appel : manage.py les découvre
            // automatiquement.
            steps {
                runCmd 'python manage.py test'
            }
        }

        stage('Sécurité - SAST') {
            // cf. chapitre 3 et chapitre 4 partie 2 : "tests de sécurité,
            // cf. SAST/DAST/SCA au chapitre 3".
            steps {
                runCmd 'semgrep --config p/security-audit --config p/django --config p/python --error .'
            }
        }

        stage('Sécurité - SCA') {
            steps {
                runCmd 'pip-audit -r requirements.txt'
            }
        }
    }

    post {
        success {
            echo 'Pipeline vert : build, lint, tests et sécurité tous OK.'
        }
        failure {
            echo 'Pipeline rouge : consultez le premier stage en échec ci-dessus.'
        }
    }
}
