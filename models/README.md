# 🤖 models/

**Modèles et configurations pour NER**

Ce dossier contient les configurations GLiNER2 et les modèles téléchargés.

---

## Structure

```
models/
├── configs/         # Configurations NER (labels, paramètres)
└── checkpoints/     # Modèles téléchargés (git-ignored)
```

---

## 📁 Sous-dossiers

### `configs/`
**Contenu** : Fichiers de configuration pour GLiNER2

**Fichiers principaux** :
- `labels.yaml` - Définition des labels d'entités NER
- `extraction_params.yaml` - Paramètres d'extraction (threshold, batch size, etc.)

**Exemple `labels.yaml`** :
```yaml
# Labels pour extraction NER zeroshot avec GLiNER2
# Adapté au corpus SDN-Esperanto

labels:
  - PERSON          # Noms de personnes
  - ORGANIZATION    # Organisations, comités, institutions
  - LOCATION        # Lieux, pays, villes
  - EVENT           # Événements historiques, conférences
  - DATE            # Dates et périodes temporelles
```

**Exemple `extraction_params.yaml`** :
```yaml
# Paramètres GLiNER2
model_name: "urchade/gliner_multi-v2.1"
threshold: 0.5          # Seuil de confiance minimum
batch_size: 8           # Taille de batch pour traitement
max_length: 384         # Longueur max en tokens
device: "cuda"          # "cuda" ou "cpu"
```

### `checkpoints/`
**Contenu** : Modèles GLiNER2 téléchargés depuis Hugging Face

**Git-ignored** : OUI (trop volumineux, ~500MB)

**Téléchargement** :
```bash
./scripts/download_models.sh
```

**Structure attendue** :
```
checkpoints/
└── gliner_multi-v2.1/
    ├── config.json
    ├── pytorch_model.bin
    ├── tokenizer_config.json
    └── vocab.txt
```

---

## 🚀 Utilisation

### Définir les Labels NER

Créez `configs/labels.yaml` avec les types d'entités pertinents pour votre corpus :

```yaml
labels:
  - PERSON
  - ORGANIZATION
  - LOCATION
  # Ajoutez d'autres labels selon vos besoins
```

### Télécharger le Modèle

```bash
./scripts/download_models.sh
```

### Utiliser le Modèle

```python
from transformers import AutoTokenizer, AutoModelForTokenClassification

model_path = "models/checkpoints/gliner_multi-v2.1"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)
```

Ou via GLiNER (recommandé) :
```python
from gliner import GLiNER

model = GLiNER.from_pretrained("models/checkpoints/gliner_multi-v2.1")
entities = model.predict_entities(text, labels=["PERSON", "LOCATION"])
```

---

## 📝 TODO

- [ ] Créer `configs/labels.yaml` avec labels adaptés au corpus SDN
- [ ] Télécharger modèle GLiNER2 (`./scripts/download_models.sh`)
- [ ] Tester extraction sur exemples (`notebooks/02_ner/gliner_testing.ipynb`)
- [ ] Ajuster threshold selon F1-score obtenu

---

**Voir aussi** : `docs/METHODOLOGY.md` (section "Extraction NER")
