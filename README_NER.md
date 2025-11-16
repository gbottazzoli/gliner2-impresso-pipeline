# Systeme NER avec GLiNER - Guide Rapide

## Mise en Place Complete

Ce projet contient un systeme complet d'extraction d'entites nommees (NER) avec evaluation automatique sur gold standard.

---

## Quick Start

### 1. Installation

```bash
cd /home/steeven/PycharmProjects/gliner2Tests/research-project-template

# Installer dependances (si pas deja fait)
pip install -r requirements.txt

# Telecharger le modele GLiNER (si pas deja fait)
./scripts/download_models.sh
```

### 2. Lancer le Pipeline Complet

```bash
# Extraction NER + Evaluation sur les 9 dossiers du gold standard
python scripts/run_ner_pipeline.py --gold-only
```

**Sortie**:
- `outputs/ner_results_YYYYMMDD_HHMMSS.xlsx` - Fichier Excel avec 3 sheets (PERSON, ORGANIZATION, GPE)
- `outputs/evaluation_report_YYYYMMDD_HHMMSS.txt` - Rapport d'evaluation avec metriques

### 3. Consulter les Resultats

```bash
# Ouvrir l'Excel
libreoffice outputs/ner_results_20251116_151224.xlsx

# Lire le rapport d'evaluation
cat outputs/evaluation_report_fixed.txt
```

---

## Fichiers Importants

### Documentation

| Fichier | Description |
|---------|-------------|
| **docs/USER_GUIDE.md** | Guide utilisateur complet (installation, usage, metriques) |
| **outputs/RAPPORT_FINAL.md** | Rapport detaille de tous les travaux effectues |

### Scripts Principaux

| Script | Fonction |
|--------|----------|
| **scripts/run_ner_pipeline.py** | Pipeline principal (extraction + evaluation) |
| **scripts/evaluate_ner.py** | Evaluation standalone |

### Donnees

| Fichier | Description |
|---------|-------------|
| **data/gold_standard_annotations.txt** | 413 annotations manuelles sur 45 documents |
| **data/annotated/ocr_results/** | 9 dossiers avec documents OCR |

---

## Resultats Actuels (2025-11-16)

### Metriques d'Evaluation

```
Type             Precision     Recall         F1
------------------------------------------------
PERSON               0.136      0.504      0.215
ORGANIZATION         0.131      0.402      0.197
LOCATION             0.159      0.686      0.258
------------------------------------------------
MICRO-AVG            0.141      0.505      0.221
MACRO-AVG            0.142      0.531      0.223
```

### Extraction

- **Total entites extraites**: 1,460 (440 PERSON, 566 ORGANIZATION, 454 GPE)
- **Score de confiance moyen**: 0.84
- **Dossiers traites**: 9
- **Documents traites**: 182

---

## Commandes Utiles

### Extraction sur un dossier specifique

```bash
python scripts/run_ner_pipeline.py --folder R1048-13C-23516-23516
```

### Extraction sur tout le corpus (sans evaluation)

```bash
python scripts/run_ner_pipeline.py --no-eval
```

### Re-evaluation (sans re-extraction)

```bash
python scripts/evaluate_ner.py \
  --gold data/gold_standard_annotations.txt \
  --predictions outputs/ner_results_20251116_151224.xlsx \
  --output outputs/new_evaluation.txt
```

---

## Structure des Sorties

### Fichier Excel

3 sheets (un par type d'entite):

| Sheet | Colonnes | Description |
|-------|----------|-------------|
| **PERSON** | Folder, Document, Entity, Type, Score | Personnes extraites |
| **ORGANIZATION** | Folder, Document, Entity, Type, Score | Organisations extraites |
| **GPE** | Folder, Document, Entity, Type, Score | Lieux extraits |

### Rapport d'Evaluation

- Resume des metriques (Precision, Rappel, F1)
- Listes des faux positifs par type
- Listes des faux negatifs par type

---

## Pour Plus d'Informations

- **Guide complet**: Lire `docs/USER_GUIDE.md`
- **Rapport detaille**: Lire `outputs/RAPPORT_FINAL.md`
- **Exemples**: Voir scripts dans `tests/`

---

## Auteur

Claude Code - 2025-11-16
