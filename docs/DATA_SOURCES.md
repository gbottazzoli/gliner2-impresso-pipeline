# 📚 DATA SOURCES - test-gliner2

**Description des Sources de Données**

Documentation complète du corpus utilisé pour l'extraction NER et l'analyse de réseau.

---

## 🌍 Corpus Principal : Société des Nations - Esperanto

### Description Générale

**Source** : Archives de la Société des Nations (SDN) - Documents en Esperanto

**Période couverte** : [À COMPLÉTER selon votre corpus]
- Début : [ANNÉE]
- Fin : [ANNÉE]

**Contexte historique** :
La Société des Nations (1920-1946) a utilisé l'Esperanto comme langue auxiliaire pour certaines communications internationales. Ce corpus rassemble des documents administratifs, rapports, correspondances et publications officielles rédigés en Esperanto.

**Pertinence scientifique** :
- Témoignage unique d'usage institutionnel de l'Esperanto
- Réseau d'acteurs internationaux (diplomates, organisations, pays membres)
- Corpus multilingue rare pour recherche en Humanités Numériques

---

## 📊 Caractéristiques du Corpus

### Statistiques

**À COMPLÉTER après exploration initiale** (notebook `01_exploration/corpus_stats.ipynb`) :

| Métrique | Valeur |
|----------|--------|
| Nombre de documents | [À COMPLÉTER] |
| Nombre total de mots | [À COMPLÉTER] |
| Nombre moyen de mots/document | [À COMPLÉTER] |
| Vocabulaire unique | [À COMPLÉTER] |
| Période temporelle | [À COMPLÉTER] |

### Types de Documents

**Catégories présentes** (à affiner) :
- [ ] Rapports officiels
- [ ] Correspondances diplomatiques
- [ ] Comptes-rendus de réunions
- [ ] Publications périodiques
- [ ] Documents administratifs
- [ ] Autre : [Préciser]

---

## 🗂️ Organisation des Données

### Structure dans le Projet

```
data/
├── raw/                         # Corpus original (NON versionné Git)
│   ├── [fichiers sources]       # Formats : TXT, PDF, XML, etc.
│   └── metadata.csv             # Métadonnées (date, auteur, type doc)
│
├── processed/                   # Textes nettoyés (NON versionné Git)
│   ├── [textes UTF-8]
│   └── processing_log.json      # Traçabilité du preprocessing
│
├── annotated/                   # Résultats NER (NON versionné Git)
│   ├── entities_per_doc/        # JSON par document
│   └── entities_all.csv         # Table complète des entités
│
└── network/                     # Données pour graphes (NON versionné Git)
    ├── entities_list.csv        # Liste unique d'entités
    └── cooccurrences.csv        # Paires d'entités + poids
```

---

## 📥 Obtention du Corpus

### Source Officielle

**Lien** : [À COMPLÉTER - URL de l'archive ou du dépôt]

**Licence** : [À COMPLÉTER - Domaine public, CC-BY, etc.]

**Citation recommandée** :
```
[À COMPLÉTER selon la source]

Exemple:
Société des Nations (1920-1946). Archives en Esperanto.
Consulté le [DATE] depuis [URL].
```

### Instructions de Téléchargement

**Si corpus public** :
```bash
# [À COMPLÉTER avec commandes wget/curl ou instructions manuelles]

# Exemple:
wget [URL] -O data/raw/corpus_sdn_esperanto.zip
unzip data/raw/corpus_sdn_esperanto.zip -d data/raw/
```

**Si corpus privé/restreint** :
```
[INSTRUCTIONS pour accès autorisé]
- Demande d'accès auprès de [INSTITUTION]
- Justification académique requise
- Placement manuel dans data/raw/
```

---

## 🔍 Préparation et Nettoyage

### Format Initial

**Format d'origine** : [TXT / PDF / XML / Autre]

**Encodage** : [UTF-8 / Latin-1 / Autre]

**Particularités** :
- Caractères spéciaux Esperanto : ĉ, ĝ, ĥ, ĵ, ŝ, ŭ
- [Autres particularités à documenter]

### Transformations Appliquées

**Script** : `src/preprocessing/clean_text.py`

**Étapes** :
1. Conversion PDF → texte (si nécessaire, via pdfplumber ou OCR)
2. Normalisation Unicode (NFD → NFC pour Esperanto)
3. Suppression caractères non-textuels (headers, footers, numéros de page)
4. Segmentation en documents logiques
5. Vérification complétude et encodage

**Traçabilité** :
- Log des transformations : `data/processed/processing_log.json`
- Fichiers originaux conservés dans `data/raw/` (NON modifiés)

---

## 🏷️ Métadonnées

### Fichier `metadata.csv`

**Colonnes recommandées** :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| `doc_id` | Identifiant unique | `SDN_ESP_1925_042` |
| `title` | Titre du document | "Raporto pri internacia komerco" |
| `date` | Date de création | `1925-06-15` |
| `author` | Auteur/institution | "Sekretariato de SDN" |
| `type` | Type de document | "Raporto" |
| `language` | Langue (ici Esperanto) | `eo` |
| `pages` | Nombre de pages | `12` |
| `source_file` | Fichier source | `rapport_1925_06.pdf` |

**Création** :
- Extraction automatique (si métadonnées structurées)
- Annotation manuelle (si nécessaire)
- Enrichissement progressif

---

## ⚠️ Considérations Éthiques et Légales

### Licence et Droits

**Statut juridique** : [À VÉRIFIER]
- Domaine public (documents > 70 ans)
- Licence ouverte (CC-BY, CC0)
- Restrictions d'usage

**Citation obligatoire** : OUI / NON

### Données Sensibles

**Présence de données personnelles** : [À ÉVALUER]
- Noms de personnes (OK pour recherche historique)
- Informations confidentielles (à anonymiser si nécessaire)

**Conformité RGPD** :
- Données historiques (> 100 ans) : généralement exemptées
- À vérifier selon juridiction

---

## 📝 Notes de Curation

### Problèmes Identifiés

**À documenter au fil de l'analyse** :

- [ ] Problème d'encodage dans certains fichiers
- [ ] Documents incomplets ou fragmentaires
- [ ] Erreurs OCR (si applicable)
- [ ] Métadonnées manquantes pour certains docs
- [ ] Autre : [Préciser]

### Améliorations Futures

- [ ] Enrichissement métadonnées via Wikidata
- [ ] Liaison entités extraites → identifiants pérennes (VIAF, etc.)
- [ ] Alignement multilingue (si versions FR/EN disponibles)

---

## 🔗 Ressources Complémentaires

**Contexte Esperanto** :
- [Akademio de Esperanto](https://www.akademio-de-esperanto.org/)
- [Tekstaro de Esperanto](http://tekstaro.com/) (corpus de référence)

**Société des Nations** :
- [Archives de la SDN - ONU Genève](https://www.unog.ch/archives)

**Outils NLP pour Esperanto** :
- spaCy (support limité)
- GLiNER (multilingue, utilisé ici)

---

**Géré par** : Utilisateur + `@historien_computationnel` (documentation méthodologique)

**Dernière mise à jour** : 2025-11-16

---

## ✅ Checklist de Documentation

Compléter cette section au fur et à mesure :

- [ ] Source du corpus identifiée et documentée
- [ ] Licence vérifiée
- [ ] Statistiques de base calculées (nb docs, mots, etc.)
- [ ] Métadonnées extraites ou créées
- [ ] Problèmes de qualité identifiés et documentés
- [ ] Preprocessing documenté avec traçabilité
- [ ] Citation officielle rédigée
