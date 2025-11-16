#!/bin/bash
# test-gliner2 - Script de téléchargement du modèle GLiNER2
# Télécharge le modèle GLiNER multilingue depuis Hugging Face

set -e # Arrête le script si une commande échoue

# --- Configuration ---
MODEL_NAME="urchade/gliner_multi-v2.1"
MODEL_DIR="../models/checkpoints"
CONDA_ENV_NAME="test-gliner2"

echo "=========================================="
echo "  Téléchargement modèle GLiNER2"
echo "  Modèle: $MODEL_NAME"
echo "=========================================="
echo ""

# --- Étape 1: Vérifier que l'environnement conda est activé ---
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  ATTENTION: Aucun environnement conda activé."
    echo ""
    echo "Veuillez activer l'environnement avant de continuer:"
    echo "  conda activate $CONDA_ENV_NAME"
    echo ""
    read -p "Voulez-vous continuer sans activer l'environnement ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Annulé. Activez l'environnement et réessayez."
        exit 1
    fi
elif [ "$CONDA_DEFAULT_ENV" != "$CONDA_ENV_NAME" ]; then
    echo "⚠️  Environnement activé: '$CONDA_DEFAULT_ENV'"
    echo "   Attendu: '$CONDA_ENV_NAME'"
    echo ""
    read -p "Voulez-vous continuer avec cet environnement ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Annulé. Activez le bon environnement et réessayez."
        exit 1
    fi
else
    echo "✅ Environnement conda '$CONDA_ENV_NAME' activé"
fi
echo ""

# --- Étape 2: Vérifier que Python et transformers sont disponibles ---
if ! command -v python &> /dev/null; then
    echo "❌ ERREUR: Python n'est pas disponible dans PATH."
    exit 1
fi

echo "✅ Python détecté: $(python --version)"

# Vérifier que gliner est installé
if ! python -c "import gliner" 2>/dev/null; then
    echo "❌ ERREUR: Le package 'gliner' n'est pas installé."
    echo "   Installez-le avec: pip install gliner"
    exit 1
fi

echo "✅ Package 'gliner' détecté"
echo ""

# --- Étape 3: Créer le dossier de destination ---
mkdir -p $MODEL_DIR
echo "📁 Dossier de destination: $MODEL_DIR"
echo ""

# --- Étape 4: Télécharger le modèle ---
echo "📥 Téléchargement du modèle GLiNER2..."
echo "   Modèle: $MODEL_NAME"
echo "   (Taille: ~500MB, cela peut prendre plusieurs minutes selon votre connexion)"
echo ""

python - <<EOF
from gliner import GLiNER
import os

model_name = "$MODEL_NAME"
save_dir = "$MODEL_DIR/gliner_multi-v2.1"

print(f"📦 Téléchargement depuis Hugging Face Hub...")
print(f"   → {model_name}")
print()

try:
    # Télécharger le modèle GLiNER
    print("⚙️  Téléchargement du modèle GLiNER2 (cela peut prendre du temps)...")
    model = GLiNER.from_pretrained(model_name)

    # Sauvegarder le modèle localement
    print("⚙️  Sauvegarde du modèle...")
    model.save_pretrained(save_dir)
    print("   ✅ Modèle sauvegardé")

    print()
    print(f"✅ Modèle téléchargé avec succès dans:")
    print(f"   {os.path.abspath(save_dir)}")

except Exception as e:
    print(f"❌ ERREUR lors du téléchargement: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF

echo ""
echo "=========================================="
echo "  Téléchargement terminé!"
echo "=========================================="
echo ""
echo "Le modèle GLiNER2 est prêt à l'emploi."
echo ""
echo "Prochaines étapes:"
echo "  1. Placez vos données dans data/raw/"
echo "  2. Lancez l'exploration: jupyter lab notebooks/01_exploration/"
echo "  3. Configurez les labels NER dans models/configs/"
echo ""
echo "Consultez la documentation:"
echo "  cat docs/METHODOLOGY.md"
echo "  cat docs/AGENTS_GUIDE.md"
echo ""
