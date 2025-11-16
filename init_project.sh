#!/bin/bash
# Ce script met en place un environnement Python reproductible pour un projet de recherche.

set -e # Arrête le script si une commande échoue

# --- Configuration ---
PYTHON_VERSION="3.10"
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"

echo "--- Initialisation de l'environnement de recherche ---"

# --- Étape 1: Vérifier et configurer la version de Python ---
# Utilise pyenv si disponible pour garantir une version stable.
if command -v pyenv &> /dev/null; then
    echo "Pyenv détecté. Tentative de définir la version Python locale à ${PYTHON_VERSION}..."
    if ! pyenv local ${PYTHON_VERSION}; then
        echo "Version ${PYTHON_VERSION} non installée avec pyenv. Veuillez l'installer avec 'pyenv install ${PYTHON_VERSION}'."
        exit 1
    fi
    echo "Version Python locale définie sur $(python --version)."
else
    echo "Pyenv non trouvé. Utilisation de la version Python système. Assurez-vous qu'elle est compatible."
    # Vous pourriez ajouter un contrôle de version plus strict ici si nécessaire.
fi

# --- Étape 2: Créer l'environnement virtuel ---
if [ ! -d "$VENV_DIR" ]; then
    echo "Création de l'environnement virtuel dans '${VENV_DIR}'..."
    python -m venv $VENV_DIR
else
    echo "Environnement virtuel '${VENV_DIR}' déjà existant."
fi

# --- Étape 3: Activer l'environnement virtuel ---
source ${VENV_DIR}/bin/activate
echo "Environnement virtuel activé."

# --- Étape 4: Gérer le fichier de dépendances ---
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "Fichier '${REQUIREMENTS_FILE}' non trouvé. Création d'un fichier de base..."
    cat <<EOF > $REQUIREMENTS_FILE
# Dépendances de base pour les projets en Humanités Numériques (NER, OCR, Data Science)
# Utilisez 'pip freeze > requirements.txt' pour mettre à jour ce fichier avec les versions exactes.

# Data Manipulation
pandas

# NLP
spacy
# Pour le français : python -m spacy download fr_core_news_sm

# OCR
pytesseract
Pillow

# Outils de développement
pylint
pytest
EOF
fi

# --- Étape 5: Installer les dépendances ---
echo "Installation/Mise à jour des dépendances depuis '${REQUIREMENTS_FILE}'..."
pip install -r $REQUIREMENTS_FILE

# --- Étape 6: Vérifier les mises à jour disponibles ---
echo "Vérification des paquets obsolètes (sans les mettre à jour)..."
if pip list --outdated; then
    echo "Certains paquets peuvent être mis à jour. Analysez la liste ci-dessus avant de mettre à jour manuellement."
else
    echo "Toutes les dépendances sont à jour."
fi

# --- Fin ---
echo ""
echo "✅ Environnement prêt à l'emploi."
echo "Pour l'activer dans une nouvelle session, exécutez : source ${VENV_DIR}/bin/activate"
