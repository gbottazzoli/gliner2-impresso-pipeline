# 🐍 src/

**Code source Python du projet test-gliner2**

Ce dossier contient tous les modules Python pour preprocessing, NER, et analyse de réseau.

---

## Structure

```
src/
├── preprocessing/    # Nettoyage et normalisation de texte
├── ner/              # Extraction NER avec GLiNER2
├── network/          # Construction et analyse de graphes
└── utils/            # Fonctions utilitaires communes
```

---

## 📁 Modules

### `preprocessing/`
**Rôle** : Nettoyer et normaliser le corpus brut Esperanto

**Scripts principaux** :
- `clean_text.py` - Nettoyage texte (Unicode, caractères spéciaux)
- `normalize_esperanto.py` - Normalisation spécifique Esperanto (ĉ, ĝ, etc.)
- `segment_documents.py` - Segmentation en unités logiques

**Exemple d'utilisation** :
```bash
python src/preprocessing/clean_text.py \
  --input data/raw/ \
  --output data/processed/ \
  --log data/processed/processing_log.json
```

**Tests** : `tests/test_preprocessing/`

---

### `ner/`
**Rôle** : Extraction d'entités nommées avec GLiNER2

**Scripts principaux** :
- `gliner_extractor.py` - Extraction NER zeroshot avec GLiNER2
- `validate_ner.py` - Validation manuelle et calcul de métriques (F1, précision, rappel)
- `post_process.py` - Post-traitement (déduplication, normalisation variantes)

**Exemple d'utilisation** :
```bash
# Extraction NER
python src/ner/gliner_extractor.py \
  --input data/processed/ \
  --output data/annotated/ \
  --model models/checkpoints/gliner_multi-v2.1 \
  --config models/configs/labels.yaml \
  --threshold 0.5

# Validation
python src/ner/validate_ner.py \
  --input data/annotated/ \
  --sample 100 \
  --output outputs/reports/ner_quality_metrics.csv
```

**Configuration** : `models/configs/labels.yaml`
```yaml
labels:
  - PERSON
  - ORGANIZATION
  - LOCATION
  - EVENT
  - DATE
```

**Tests** : `tests/test_ner/`

---

### `network/`
**Rôle** : Construction et analyse de réseau d'entités

**Scripts principaux** :
- `build_network.py` - Construction du graphe de co-occurrences
- `analyze_network.py` - Calcul de métriques (centralité, communautés)
- `export_network.py` - Export GraphML, CSV pour visualisation

**Exemple d'utilisation** :
```bash
# Construction du réseau
python src/network/build_network.py \
  --input data/annotated/ \
  --output outputs/networks/entities_network.graphml \
  --min_weight 2

# Analyse
python src/network/analyze_network.py \
  --input outputs/networks/entities_network.graphml \
  --output outputs/reports/network_metrics.csv
```

**Tests** : `tests/test_network/`

---

### `utils/`
**Rôle** : Fonctions utilitaires réutilisables

**Modules** :
- `file_utils.py` - Lecture/écriture de fichiers (JSON, CSV, TXT)
- `text_utils.py` - Fonctions de traitement de texte (tokenisation, etc.)
- `logging_utils.py` - Configuration de logging standardisé
- `config.py` - Chargement de configurations (YAML, JSON)

**Exemple** :
```python
from src.utils.file_utils import load_json, save_csv
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)
data = load_json("data/annotated/doc1.json")
logger.info(f"Loaded {len(data['entities'])} entities")
```

---

## 🧪 Développement

### Standards de Code

**Style** : PEP 8 (appliqué avec `black` et `flake8`)

**Formatage** :
```bash
# Auto-formatage
black src/

# Vérification style
flake8 src/
```

**Docstrings** : Format Google (utilisez `@doc_technique`)
```python
def extract_entities(text: str, threshold: float = 0.5) -> List[Dict]:
    """
    Extrait les entités nommées d'un texte avec GLiNER2.

    Args:
        text: Texte à analyser
        threshold: Seuil de confiance minimum (0.0-1.0)

    Returns:
        Liste de dictionnaires avec clés 'text', 'label', 'start', 'end', 'confidence'

    Raises:
        ValueError: Si threshold n'est pas entre 0 et 1
    """
    ...
```

### Tests Unitaires

**Framework** : pytest

**Lancer les tests** :
```bash
# Tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests d'un module spécifique
pytest tests/test_ner/
```

**Créer des tests** : Utilisez `@testeur_code`
```bash
@testeur_code Crée des tests pour src/ner/gliner_extractor.py
```

---

## 📚 Documentation

**Générer documentation** :
```bash
@doc_technique Ajoute docstrings à tous les fichiers dans src/ner/
```

**README par module** :
Chaque sous-dossier peut avoir son propre README détaillé si nécessaire.

---

## 🔄 Pipeline Complet

**Workflow typique** :
```bash
# 1. Preprocessing
python src/preprocessing/clean_text.py --input data/raw/ --output data/processed/

# 2. NER
python src/ner/gliner_extractor.py --input data/processed/ --output data/annotated/

# 3. Validation
python src/ner/validate_ner.py --input data/annotated/ --sample 100

# 4. Réseau
python src/network/build_network.py --input data/annotated/ --output outputs/networks/
python src/network/analyze_network.py --input outputs/networks/entities_network.graphml
```

**Ou utiliser le pipeline automatique** :
```bash
./scripts/run_full_pipeline.sh
```

---

## 🤖 Agents Utiles

- `@doc_technique` - Documenter le code
- `@testeur_code` - Créer tests unitaires
- `@nettoyeur_projet` - Refactoring et qualité
- `@git_helper` - Messages de commit standardisés

---

## 📝 TODO

- [ ] Développer `src/preprocessing/clean_text.py`
- [ ] Développer `src/ner/gliner_extractor.py`
- [ ] Créer tests unitaires pour chaque module
- [ ] Documenter toutes les fonctions principales
- [ ] Optimiser performances pour corpus volumineux

---

**Voir aussi** : `docs/METHODOLOGY.md` pour justification des choix techniques
