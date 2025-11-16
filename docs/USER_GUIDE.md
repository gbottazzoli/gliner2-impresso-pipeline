# Guide Utilisateur - Systeme NER GLiNER

## Vue d'ensemble

Ce projet implémente un système d'extraction d'entités nommées (NER - Named Entity Recognition) utilisant GLiNER v2.1 pour analyser des documents historiques de la Société des Nations.

### Objectifs

- Extraire automatiquement les entités nommées (personnes, organisations, lieux) depuis des documents OCR
- Évaluer la qualité des prédictions contre un gold standard annoté manuellement
- Produire des rapports détaillés avec métriques de performance

### Types d'entités

- **PERSON** : Personnes (noms propres, titres diplomatiques)
- **ORGANIZATION** : Organisations (institutions, commissions, sociétés)
- **GPE** (Geographic Political Entity) : Lieux (villes, pays, régions)

---

## Installation

### Prérequis

- Python 3.8+
- GPU recommandé (mais CPU supporté)
- 8GB RAM minimum

### Étapes d'installation

1. **Cloner le projet**
   ```bash
   cd /home/steeven/PycharmProjects/gliner2Tests/research-project-template
   ```

2. **Créer l'environnement virtuel**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Télécharger le modèle GLiNER**
   ```bash
   chmod +x scripts/download_models.sh
   ./scripts/download_models.sh
   ```

Le modèle sera téléchargé dans: `/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1`

---

## Structure du Projet

```
research-project-template/
├── data/
│   ├── annotated/
│   │   └── ocr_results/          # Documents OCR (entrée)
│   │       ├── R1048-13C-23516-23516/
│   │       ├── R1048-13C-24630-23516/
│   │       └── ...
│   └── gold_standard_annotations.txt  # Annotations manuelles (référence)
│
├── scripts/
│   ├── run_ner_pipeline.py       # Script principal (extraction + évaluation)
│   ├── evaluate_ner.py           # Script d'évaluation standalone
│   └── download_models.sh        # Téléchargement des modèles
│
├── outputs/
│   ├── ner_results_YYYYMMDD_HHMMSS.xlsx      # Résultats extraction
│   └── evaluation_report_YYYYMMDD_HHMMSS.txt # Rapport d'évaluation
│
└── docs/
    └── USER_GUIDE.md             # Ce guide
```

---

## Usage Basique

### 1. Extraction NER sur tout le corpus

Lance l'extraction sur tous les dossiers et génère un rapport d'évaluation:

```bash
python scripts/run_ner_pipeline.py
```

**Sortie:**
- `outputs/ner_results_YYYYMMDD_HHMMSS.xlsx` - Fichier Excel avec 3 sheets (PERSON, ORGANIZATION, GPE)
- `outputs/evaluation_report_YYYYMMDD_HHMMSS.txt` - Rapport d'évaluation détaillé

### 2. Extraction sur un dossier spécifique

```bash
python scripts/run_ner_pipeline.py --folder R1048-13C-23516-23516
```

### 3. Extraction uniquement sur les dossiers du gold standard

```bash
python scripts/run_ner_pipeline.py --gold-only
```

### 4. Extraction sans évaluation

```bash
python scripts/run_ner_pipeline.py --no-eval
```

### 5. Mode silencieux

```bash
python scripts/run_ner_pipeline.py --quiet
```

---

## Évaluation Standalone

Vous pouvez lancer l'évaluation indépendamment sur des résultats existants:

```bash
python scripts/evaluate_ner.py \
  --gold data/gold_standard_annotations.txt \
  --predictions outputs/ner_results_20251116_143000.xlsx \
  --output outputs/evaluation_report.txt
```

---

## Format du Fichier Excel de Sortie

Le fichier Excel contient 3 feuilles (sheets), une par type d'entité:

### Sheet "PERSON"

| Folder | Document | Entity | Type | Score |
|--------|----------|--------|------|-------|
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc02 | Madame Curie-Skłodowska | PERSON | 0.923 |
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc03 | Prof. Gilbert Murray | PERSON | 0.887 |

### Sheet "ORGANIZATION"

| Folder | Document | Entity | Type | Score |
|--------|----------|--------|------|-------|
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc01 | SOCIÉTÉ DES NATIONS | ORGANIZATION | 0.956 |
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc02 | Commission de Coopération Intellectuelle | ORGANIZATION | 0.912 |

### Sheet "GPE" (Locations)

| Folder | Document | Entity | Type | Score |
|--------|----------|--------|------|-------|
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc02 | Paris | GPE | 0.876 |
| R1048-13C-23516-23516 | R1048-13C-23516-23516_doc03 | Madrid | GPE | 0.901 |

**Colonnes:**
- **Folder**: Nom du dossier source
- **Document**: Nom du document (fichier .md)
- **Entity**: Texte de l'entité extraite
- **Type**: Type d'entité (PERSON, ORGANIZATION, GPE)
- **Score**: Score de confiance du modèle (0-1)

---

## Métriques d'Évaluation

### Métriques par Type

Le rapport d'évaluation calcule les métriques suivantes pour chaque type d'entité:

#### Précision (Precision)
```
Precision = TP / (TP + FP)
```
Proportion d'entités prédites qui sont correctes.
- **TP** (True Positives): Entités correctement identifiées
- **FP** (False Positives): Entités prédites à tort

#### Rappel (Recall)
```
Recall = TP / (TP + FN)
```
Proportion d'entités réelles qui ont été trouvées.
- **FN** (False Negatives): Entités manquées

#### F1-Score
```
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```
Moyenne harmonique entre précision et rappel (balance des deux métriques).

### Métriques Agrégées

#### Micro-Average
Agrège tous les TP, FP, FN de tous les types avant de calculer les métriques.
Donne plus de poids aux types fréquents.

#### Macro-Average
Calcule les métriques pour chaque type séparément, puis fait la moyenne.
Traite tous les types de manière égale.

### Exemple de Rapport

```
================================================================================
SUMMARY METRICS
================================================================================

Type            Precision     Recall         F1     TP     FP     FN
--------------------------------------------------------------------------------
PERSON              0.856      0.782      0.817     89     15     25
ORGANIZATION        0.923      0.845      0.882    156     13     29
LOCATION            0.789      0.721      0.753     98     26     38
--------------------------------------------------------------------------------
MICRO-AVG           0.874      0.795      0.833    343     54     92
MACRO-AVG           0.856      0.783      0.817
```

### Interprétation

- **F1 > 0.90**: Excellente performance
- **F1 entre 0.80-0.90**: Bonne performance
- **F1 entre 0.70-0.80**: Performance acceptable
- **F1 < 0.70**: Performance à améliorer

---

## Analyses Détaillées

### Faux Positifs (False Positives)

Entités prédites par le modèle mais absentes du gold standard:

```
False Positives (15):
  R1048-13C-23516-23516 | doc01 | 3rd Assembly
  R1048-13C-23516-23516 | doc02 | Secrétariat
```

**Causes possibles:**
- Sur-détection du modèle
- Annotations manquantes dans le gold standard
- Entités ambiguës

### Faux Négatifs (False Negatives)

Entités présentes dans le gold standard mais manquées par le modèle:

```
False Negatives (25):
  R1048-13C-23516-23516 | doc01 | M. Bergson
  R1048-13C-23516-23516 | doc03 | Mlle. Bonnevie
```

**Causes possibles:**
- Sous-détection du modèle
- Score de confiance trop bas
- Entités rares ou mal formées

---

## Configuration Avancée

### Ajuster les Seuils de Confiance

Éditez `scripts/run_ner_pipeline.py`:

```python
# Scores minimums pour filtrage
MIN_SCORE_PERSON = 0.60  # Par défaut: 0.60
MIN_SCORE_ORG = 0.70     # Par défaut: 0.70
MIN_SCORE_LOC = 0.65     # Par défaut: 0.65
```

**Impact:**
- Seuil plus **élevé** → Plus de précision, moins de rappel (moins de FP, plus de FN)
- Seuil plus **bas** → Plus de rappel, moins de précision (plus de FP, moins de FN)

### Ajuster le Chunking

Éditez `scripts/run_ner_pipeline.py`:

```python
chunks = smart_chunk(text_clean, max_length=400, overlap=50)
```

**Paramètres:**
- `max_length`: Taille maximum d'un chunk (en mots)
- `overlap`: Chevauchement entre chunks (en mots)

---

## Gold Standard

### Format

Le fichier `data/gold_standard_annotations.txt` contient les annotations manuelles au format:

```
## DOSSIER: R1048-13C-23516-23516

R1048-13C-23516-23516|doc01|ORGANIZATION|SOCIÉTÉ DES NATIONS
R1048-13C-23516-23516|doc01|ORGANIZATION|LEAGUE OF NATIONS
R1048-13C-23516-23516|doc02|PERSON|Madame Curie-Skłodowska
R1048-13C-23516-23516|doc02|LOCATION|Paris
```

**Structure:**
```
FOLDER|DOCUMENT|TYPE|ENTITY
```

- `FOLDER`: Nom du dossier
- `DOCUMENT`: Identifiant du document (doc01, doc02, etc.)
- `TYPE`: PERSON, ORGANIZATION, LOCATION
- `ENTITY`: Texte de l'entité

### Statistiques du Gold Standard

- **Total de dossiers annotés**: 9 (20% du corpus)
- **Documents par dossier**: 5
- **Total de documents annotés**: 45
- **Total d'annotations**: ~450 entités

---

## Dépannage

### Erreur: "Model not found"

Vérifiez que le modèle est téléchargé:
```bash
ls /home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1
```

Relancez le téléchargement si nécessaire:
```bash
./scripts/download_models.sh
```

### Erreur: "Out of memory"

Le modèle GLiNER nécessite beaucoup de mémoire. Solutions:

1. **Réduire la taille des chunks**:
   ```python
   chunks = smart_chunk(text_clean, max_length=200, overlap=30)
   ```

2. **Traiter moins de dossiers à la fois**:
   ```bash
   python scripts/run_ner_pipeline.py --folder R1048-13C-23516-23516
   ```

3. **Utiliser CPU au lieu de GPU** (plus lent):
   Le script détecte automatiquement le device disponible.

### Performances lentes

- **GPU**: L'extraction complète prend environ 5-10 minutes sur GPU
- **CPU**: L'extraction peut prendre 30-60 minutes sur CPU

Pour accélérer:
- Utilisez `--folder` pour traiter un seul dossier
- Utilisez `--gold-only` pour traiter uniquement les dossiers du gold standard

---

## Exemples de Commandes

### Workflow Complet

```bash
# 1. Extraction complète avec évaluation
python scripts/run_ner_pipeline.py

# 2. Consulter les résultats
libreoffice outputs/ner_results_20251116_143000.xlsx

# 3. Consulter le rapport d'évaluation
cat outputs/evaluation_report_20251116_143000.txt
```

### Tests sur un Petit Échantillon

```bash
# Test sur un seul dossier
python scripts/run_ner_pipeline.py --folder R1048-13C-23516-23516

# Test sur gold standard uniquement
python scripts/run_ner_pipeline.py --gold-only
```

### Re-évaluation

Si vous avez déjà des résultats et voulez juste re-évaluer:

```bash
python scripts/evaluate_ner.py \
  --gold data/gold_standard_annotations.txt \
  --predictions outputs/ner_results_20251116_143000.xlsx \
  --output outputs/new_evaluation.txt
```

---

## FAQ

### Q: Comment améliorer la précision ?

**R:** Augmentez les seuils de confiance:
```python
MIN_SCORE_PERSON = 0.70  # Au lieu de 0.60
MIN_SCORE_ORG = 0.80     # Au lieu de 0.70
MIN_SCORE_LOC = 0.75     # Au lieu de 0.65
```

### Q: Comment améliorer le rappel ?

**R:** Diminuez les seuils de confiance:
```python
MIN_SCORE_PERSON = 0.50
MIN_SCORE_ORG = 0.60
MIN_SCORE_LOC = 0.55
```

### Q: Pourquoi "GPE" au lieu de "LOCATION" ?

**R:** GPE (Geographic Political Entity) est le label standard pour les lieux dans les modèles NER. Dans le gold standard, nous utilisons "LOCATION" pour simplifier, mais le mapping est automatique lors de l'évaluation.

### Q: Comment ajouter de nouvelles annotations au gold standard ?

**R:** Éditez `data/gold_standard_annotations.txt` et ajoutez vos annotations au format:
```
FOLDER|DOCUMENT|TYPE|ENTITY
```

Respectez les types: PERSON, ORGANIZATION, LOCATION

---

## Contact et Support

Pour toute question ou problème:

- **Auteur**: Claude Code
- **Date de création**: 2025-11-16
- **Version**: 1.0

---

## Changelog

### Version 1.0 (2025-11-16)
- Première version du système NER
- Support pour PERSON, ORGANIZATION, GPE
- Gold standard de 45 documents (9 dossiers)
- Scripts d'extraction et d'évaluation
- Documentation complète
