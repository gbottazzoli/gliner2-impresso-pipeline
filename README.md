# GLiNER2 + Impresso Pipeline - Corpus SDN-Esperanto

🏁 **PROJET CLÔTURÉ** - 2025-11-20 - Tous les objectifs atteints ✅

---

## Vue d'Ensemble

Pipeline complet de **Named Entity Recognition (NER)** zeroshot utilisant **GLiNER v2.1** sur un corpus historique de la **Société des Nations (SDN)** en Esperanto, avec enrichissement contextuel Wikidata et intégration des archives presse historiques **Impresso**.

**Période couverte**: 3ème Assemblée de la SDN (août-octobre 1922)

---

## 🎯 Résultats Finaux

### Extraction NER
- **832 acteurs** extraits et enrichis (PERSON)
- **600 organisations** identifiées (ORGANIZATION)
- **183 lieux** géolocalisés (GPE)
- **666 documents** traités (43 dossiers)
- **Gold standard**: 413 annotations manuelles

### Enrichissement Contextuel
- **832 personnes enrichies** avec métadonnées Wikidata
- **Attributs**: Description, Nationalité, Genre, Catégorie (SDN/Sociétés membres)
- **Taux de complétude**: 88.5% avec métadonnées

### Intégration Impresso Archives Presse
- **311 articles uniques** trouvés (août-octobre 1922)
- **40 acteurs** recherchés avec 215 alias Wikidata (FR/EN/DE)
- **17 acteurs** avec mentions presse
- **Sélection intelligente**: 53 articles représentant tous les acteurs
- **Export prosopographique**: 40 personnes format modèle avec URLs cliquables

### Top 5 Acteurs Médiatiques
1. **Robert Cecil** (Q12702) - 105 articles
2. **Henri Bergson** (Q42156) - 62 articles
3. **Gilbert Murray** (Q538478) - 28 articles
4. **Eric Drummond** (Q335120) - 23 articles
5. **De Brouckere** - 20 articles

---

## 📂 Structure du Projet

```
research-project-template/
├── README.md                           # Ce fichier
├── README_NER.md                       # Documentation pipeline NER
├── README_IMPRESSO.md                  # Documentation intégration Impresso
├── USER_GUIDE.md                       # Guide utilisateur complet
├── PROJECT_STATE.md                    # État détaillé du projet
├── environment.yml                     # Environnement conda reproductible
│
├── scripts/                            # Scripts production
│   ├── run_ner_pipeline.py            # Pipeline NER complet
│   ├── evaluate_ner.py                # Évaluation automatique
│   ├── enrich_all_persons.py          # Enrichissement Wikidata 832 acteurs
│   ├── validate_ner_quality.py        # Validation statistique qualité
│   ├── impresso_1_wikidata_enrichment.py  # Extraction aliases Wikidata
│   ├── impresso_2_search_articles.py      # Recherche Impresso API
│   └── create_final_export.py             # Export prosopographique final
│
├── outputs/                            # Fichiers de sortie
│   ├── person_FINAL_CLEAN.xlsx        # 832 acteurs enrichis ⭐
│   ├── export_final_40_personnes.xlsx # Export prosopographique ⭐
│   ├── impresso_resultats_dedupliques.xlsx  # 311 articles presse ⭐
│   ├── impresso_selection_60_articles.xlsx  # Sélection 53 articles
│   ├── personnes_avec_aliases_wikidata.xlsx # 40 personnes + aliases
│   ├── RAPPORT_FINAL.md               # Rapport technique complet
│   ├── SELECTION_60_ARTICLES.md       # Méthodologie sélection
│   └── impresso_search_report.txt     # Statistiques Impresso
│
└── tests/                              # Tests unitaires
    └── test_ner_extraction.py         # Tests pipeline NER
```

---

## 🚀 Installation et Utilisation

### Prérequis
- Python 3.11+
- Conda/Mamba
- Token API Impresso (https://impresso-project.ch/datalab/token)

### Installation
```bash
# Cloner le repo
git clone https://github.com/gbottazzoli/gliner2-impresso-pipeline.git
cd gliner2-impresso-pipeline

# Créer environnement conda
conda env create -f environment.yml
conda activate gliner2

# Télécharger modèle GLiNER
python scripts/download_models.py
```

### Workflows Principaux

#### 1. Pipeline NER Complet
```bash
python scripts/run_ner_pipeline.py
python scripts/evaluate_ner.py
```

#### 2. Enrichissement Wikidata
```bash
python scripts/enrich_all_persons.py
```

#### 3. Recherche Impresso
```bash
# Étape 1: Extraction aliases Wikidata
python scripts/impresso_1_wikidata_enrichment.py

# Étape 2: Recherche archives presse
python scripts/impresso_2_search_articles.py
```

#### 4. Export Prosopographique
```bash
python scripts/create_final_export.py
```

---

## 📊 Fichiers de Sortie Principaux

### 1. `person_FINAL_CLEAN.xlsx`
**832 acteurs enrichis** avec métadonnées contextuelles
- entity_normalized (nom + Wikidata ID)
- Description professionnelle
- Nationalité
- Genre
- Catégorie (SDN/Sociétés membres)
- Aliases originaux
- Documents sources

### 2. `export_final_40_personnes.xlsx`
**Export prosopographique** 40 premiers acteurs
- 11 colonnes: Nom, Prénom, Identifiant, Variantes, Description, Archives, Documents officiels, Presse, Nationalité, Genre, Catégorie
- **Variantes**: Aliases originaux + Wikidata (FR/EN/DE)
- **Presse**: Articles Impresso avec URLs cliquables
- **Format**: `article_id (url) | titre | date | journal`

### 3. `impresso_resultats_dedupliques.xlsx`
**311 articles presse uniques** (août-octobre 1922)
- Métadonnées: person_entity, article_id, title, date, newspaper, url
- Distribution: 88.7% FR, 11.3% DE
- Top journaux: JDG (73), Le Gaulois (34), GDL (30)

### 4. `impresso_selection_60_articles.xlsx`
**Sélection intelligente** 53 articles
- Méthodologie 3 phases: priorité thématique → diversité → proportionnalité
- Couvre 100% des 17 acteurs avec mentions

---

## 📖 Documentation Détaillée

- **[README_NER.md](README_NER.md)** - Pipeline NER, évaluation, métriques
- **[README_IMPRESSO.md](README_IMPRESSO.md)** - Intégration Impresso complète
- **[USER_GUIDE.md](USER_GUIDE.md)** - Guide utilisateur pas-à-pas
- **[PROJECT_STATE.md](PROJECT_STATE.md)** - Historique complet du projet
- **[RAPPORT_FINAL.md](outputs/RAPPORT_FINAL.md)** - Rapport technique détaillé

---

## 🔬 Méthodologie

### Pipeline NER
1. **Extraction**: GLiNER v2.1 zeroshot (PERSON, ORGANIZATION, GPE)
2. **Post-traitement**: Normalisation, déduplication, groupage
3. **Évaluation**: Comparaison gold standard (Precision/Rappel/F1)

### Enrichissement Contextuel
1. **Extraction Wikidata**: Recherche par nom → récupération métadonnées
2. **Extraction documentaire**: OCR → patterns regex → métadonnées
3. **Fusion**: Wikidata prioritaire, fallback documents OCR

### Intégration Impresso
1. **Enrichissement aliases**: Extraction Wikidata FR/EN/DE (215 alias)
2. **Recherche API**: 219 requêtes sur période août-oct 1922
3. **Déduplication**: 339 entrées → 311 articles uniques
4. **Sélection intelligente**: 3 phases pour réduire à ~60 articles

---

## 🔗 Références

- **GLiNER**: https://github.com/urchade/GLiNER
- **Impresso Project**: https://impresso-project.ch/
- **Wikidata**: https://www.wikidata.org/
- **Corpus SDN-Esperanto**: Archives Société des Nations Genève

---

## 📜 Licence

Projet de recherche académique - Usage non-commercial

---

## ✨ Crédits

Développé avec **Claude Code** (Anthropic)
Session #1-8 (2025-11-16 → 2025-11-20)

---

**Dernière mise à jour**: 2025-11-20
**Statut**: 🏁 Projet clôturé - Tous objectifs atteints
