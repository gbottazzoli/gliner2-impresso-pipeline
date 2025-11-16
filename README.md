# 🔬 test-gliner2

**NER Zeroshot avec GLiNER2 sur Corpus Société des Nations - Esperanto**

Projet de recherche en Humanités Numériques visant à extraire des entités nommées (NER) d'un corpus historique en Esperanto issu de la Société des Nations, pour analyse de réseau.

---

## 📋 Description

Ce projet utilise **GLiNER2**, un modèle de NER zeroshot, pour identifier automatiquement des entités (personnes, organisations, lieux, etc.) dans des textes en Esperanto de la Société des Nations. Les entités extraites seront ensuite utilisées pour construire et analyser un réseau de relations.

**Objectifs** :
- Nettoyer et normaliser le corpus textuel
- Extraire les entités nommées avec GLiNER2 (zeroshot)
- Construire un graphe de relations entre entités
- Analyser le réseau (centralité, communautés, etc.)
- Produire des visualisations et un dataset annoté

---

## 🚀 Démarrage Rapide

### 1. Initialiser l'environnement

```bash
# Créer l'environnement conda
./init_project.sh

# Activer l'environnement
conda activate test-gliner2

# Télécharger le modèle GLiNER2
./scripts/download_models.sh
```

### 2. Préparer les données

Placez vos textes bruts dans `data/raw/`:

```bash
cp /chemin/vers/corpus/*.txt data/raw/
```

### 3. Lancer le pipeline

```bash
# Option 1: Pipeline complet
./scripts/run_full_pipeline.sh

# Option 2: Étape par étape dans notebooks
jupyter lab
# Ouvrir: notebooks/01_exploration/, puis 02_ner/, puis 03_network/
```

---

## 📁 Structure du Projet

```
test-gliner2/
├── data/                    # Données (git-ignored)
│   ├── raw/                 # Corpus brut Esperanto
│   ├── processed/           # Textes nettoyés
│   ├── annotated/           # Résultats NER (JSON/CSV)
│   └── network/             # Listes d'entités pour graphes
│
├── src/                     # Code source Python
│   ├── preprocessing/       # Nettoyage texte
│   ├── ner/                 # Extraction NER avec GLiNER2
│   ├── network/             # Analyse de réseau
│   └── utils/               # Utilitaires communs
│
├── notebooks/               # Jupyter notebooks
│   ├── 01_exploration/      # EDA du corpus
│   ├── 02_ner/              # Tests GLiNER2
│   └── 03_network/          # Visualisation réseaux
│
├── models/
│   ├── configs/             # Configurations GLiNER2
│   └── checkpoints/         # Modèles (git-ignored)
│
├── outputs/                 # Résultats (git-ignored partiellement)
│   ├── ner_results/         # Entités extraites
│   ├── networks/            # Graphes (GraphML, etc.)
│   ├── visualizations/      # Figures
│   └── reports/             # Métriques qualité
│
├── tests/                   # Tests unitaires (pytest)
├── docs/                    # Documentation
└── scripts/                 # Scripts utilitaires
```

---

## 🤖 Utilisation des Agents Claude

Ce projet inclut **11 agents Claude Code** pour vous assister. Voir `docs/AGENTS_GUIDE.md` pour le guide complet.

**Agents principaux** :
- `@gardien_projet` - Suivi de l'état du projet entre sessions
- `@gestionnaire_contexte` - Gestion de la mémoire contextuelle
- `@validateur_donnees` - Métriques qualité NER (précision, rappel, F1)
- `@visualiseur_donnees` - Création de graphiques
- `@git_helper` - Messages de commit professionnels

**Exemple** :
```bash
# Demander l'état actuel
@gardien_projet Où en sommes-nous ?

# Valider les résultats NER
@validateur_donnees Évalue la qualité des extractions dans outputs/ner_results/

# Créer une visualisation
@visualiseur_donnees Crée un graphe de réseau à partir de data/network/entities.csv
```

---

## 🛠️ Technologies

**NER & NLP** :
- GLiNER (zeroshot NER)
- Transformers (Hugging Face)
- spaCy (optionnel, normalisation)

**Analyse de réseau** :
- NetworkX (construction de graphes)
- python-louvain (détection de communautés)

**Visualisation** :
- Matplotlib, Seaborn (graphiques)
- Plotly, Pyvis (réseaux interactifs)

**Environnement** :
- Conda (gestion dépendances)
- Pytest (tests unitaires)
- Jupyter (notebooks)

---

## 📊 Workflow Type

```
1. Nettoyage corpus       → src/preprocessing/clean_text.py
2. Extraction NER         → src/ner/gliner_extractor.py
3. Validation résultats   → @validateur_donnees
4. Construction graphe    → src/network/build_network.py
5. Analyse & visualisation→ notebooks/03_network/
6. Export final           → outputs/reports/
```

---

## 📖 Documentation

- `docs/PROJECT_STATE.md` - État actuel du projet (màj automatique par `@gardien_projet`)
- `docs/METHODOLOGY.md` - Méthodologie scientifique reproductible
- `docs/DATA_SOURCES.md` - Description du corpus SDN-Esperanto
- `docs/AGENTS_GUIDE.md` - Guide d'utilisation des 11 agents Claude

---

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=src --cov-report=html

# Tests spécifiques
pytest tests/test_ner/
```

---

## 📝 License

MIT License - Voir `LICENSE`

---

## 🙏 Remerciements

- **GLiNER** : Modèle NER zeroshot
- **Template** : Créé avec [research-project-template](https://github.com/gbottazzoli/research-project-template)
- **Corpus** : Société des Nations - Archives Esperanto

---

**Statut** : 🟢 Setup initial complet | Voir `docs/PROJECT_STATE.md` pour détails
