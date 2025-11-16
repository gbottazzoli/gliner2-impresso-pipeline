#!/bin/bash
# test-gliner2 - Script d'initialisation de l'environnement conda
# NER Zeroshot avec GLiNER2 sur Corpus SDN-Esperanto

set -e # Arrête le script si une commande échoue

# --- Configuration ---
PROJECT_NAME="test-gliner2"
ENV_FILE="environment.yml"
CONDA_ENV_NAME="test-gliner2"

echo "=========================================="
echo "  Initialisation test-gliner2"
echo "  NER Zeroshot GLiNER2 - Corpus Esperanto"
echo "=========================================="
echo ""

# --- Étape 1: Vérifier que conda est installé ---
if ! command -v conda &> /dev/null; then
    echo "❌ ERREUR: conda n'est pas installé ou n'est pas dans PATH."
    echo ""
    echo "Veuillez installer Anaconda ou Miniconda:"
    echo "  - Anaconda: https://www.anaconda.com/download"
    echo "  - Miniconda: https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    exit 1
fi

echo "✅ Conda détecté: $(conda --version)"
echo ""

# --- Étape 2: Vérifier que environment.yml existe ---
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ ERREUR: Fichier '$ENV_FILE' introuvable."
    echo "   Assurez-vous d'être dans le répertoire racine du projet."
    exit 1
fi

echo "✅ Fichier $ENV_FILE trouvé"
echo ""

# --- Étape 3: Créer l'environnement conda ---
echo "📦 Création de l'environnement conda '$CONDA_ENV_NAME'..."
echo "   (Cela peut prendre plusieurs minutes...)"
echo ""

if conda env list | grep -q "^${CONDA_ENV_NAME} "; then
    echo "⚠️  L'environnement '$CONDA_ENV_NAME' existe déjà."
    read -p "   Voulez-vous le recréer ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Suppression de l'environnement existant..."
        conda env remove -n $CONDA_ENV_NAME -y
        echo "📦 Création du nouvel environnement..."
        conda env create -f $ENV_FILE
    else
        echo "⏭️  Mise à jour de l'environnement existant..."
        conda env update -f $ENV_FILE --prune
    fi
else
    conda env create -f $ENV_FILE
fi

echo ""
echo "✅ Environnement conda créé avec succès"
echo ""

# --- Étape 4: Instructions pour activation ---
echo "=========================================="
echo "  Prochaines étapes"
echo "=========================================="
echo ""
echo "1. Activez l'environnement:"
echo "   conda activate $CONDA_ENV_NAME"
echo ""
echo "2. Téléchargez le modèle GLiNER2:"
echo "   ./scripts/download_models.sh"
echo ""
echo "3. Placez vos données dans:"
echo "   data/raw/"
echo ""
echo "4. Consultez la documentation:"
echo "   cat README.md"
echo "   cat docs/AGENTS_GUIDE.md"
echo ""
echo "=========================================="
echo "✅ Setup complet! Bon travail de recherche!"
echo "=========================================="
