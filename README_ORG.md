# Post-traitement ORGANIZATION - Documentation

## Vue d'ensemble

Ce document décrit le pipeline de nettoyage des entités **ORGANIZATION** extraites par GLiNER2 du corpus Esperanto de la Société des Nations.

## Résultats finaux

| Métrique | Valeur |
|----------|--------|
| **Entités initiales** | 1663 |
| **Entités finales** | 600 |
| **Taux de réduction** | 63.9% |
| **Score NER moyen** | 0.829 |

### TOP 5 organisations

1. **Société des Nations** (330 occurrences, 246 documents)
2. **Commission de Coopération Intellectuelle** (93 occ, 77 docs)
3. **Chambre de Commerce de Paris** (33 occ, 33 docs)
4. **Chambre de Commerce Italienne pour la Suisse** (27 occ, 20 docs)
5. **Secrétariat de la Société des Nations** (16 occ, 16 docs)

## Pipeline de nettoyage

### Script : `postprocess_organization_FINAL.py`

Le script final applique les étapes suivantes :

### 1. **Normalisation**
- Correction des tirets de césure (`Coopé-Ration` → `Coopération`)
- Suppression des espaces multiples
- Suppression de la ponctuation de fin
- Suppression des articles définis (`Le`, `La`, `Les`, `L'`)

### 2. **Filtrage initial**
Suppression de :
- Acronymes courts (≤ 4 caractères en majuscules)
- Noms génériques seuls (`Secretariat`, `Commission`, `Committee`, etc.)
- Entités dans la liste de suppression explicite

### 3. **Traduction/Normalisation**
- Mapping manuel des variantes multilingues vers formes canoniques françaises
- Exemples :
  - `League of Nations` → `Société des Nations`
  - `Völkerbund` → `Société des Nations`
  - `Committee on Intellectual Co-operation` → `Commission de Coopération Intellectuelle`

### 4. **Clustering intelligent par similarité**

**Seuil de similarité** : 0.92 (92%)

**Contraintes géographiques** :
- Ne fusionne **PAS** si villes différentes
- Ne fusionne **PAS** si pays différents
- Ne fusionne **PAS** si nationalités différentes
- Ne fusionne **PAS** si scopes différents (international ≠ national)

**Exemples de fusions autorisées** :
- `Académie des Sciences` ← `Academie des Sciences` (typo accent)
- `British Esperanto Association` ← `The British Esperanto Association` (article)

**Exemples de fusions REFUSÉES** :
- `American Association` ≠ `Italian Association` (nationalités différentes)
- `Conseil International` ≠ `National Research Council` (scopes différents)
- `Chambre de Commerce de Paris` ≠ `Chambre de Commerce de Milan` (villes différentes)

### 5. **Suppression finale**
Suppression des :
- Concepts (ex: `Coopération Intellectuelle`)
- Groupes génériques (ex: `Esperantists`)
- Noms génériques sans contexte (ex: `League`, `Association`)

## Fichiers générés

| Fichier | Description |
|---------|-------------|
| `outputs/org_FINAL_CLEAN.xlsx` | **600 organisations nettoyées** |
| `outputs/evaluation_organization_report.txt` | Rapport d'évaluation avec statistiques |

## Format du fichier final

Colonnes dans `org_FINAL_CLEAN.xlsx` :

- `entity_normalized` : Nom canonique de l'organisation
- `aliases` : Variantes trouvées (séparées par `, `)
- `documents` : Documents où l'entité apparaît (séparés par `, `)
- `nb_occurrences` : Nombre total d'occurrences
- `nb_documents` : Nombre de documents uniques
- `score_moyen` : Score NER moyen
- `status` : `cleaned`

## Statistiques

### Distribution par fréquence

| Fréquence | Nombre d'entités | % |
|-----------|-----------------|---|
| 1 occurrence | 431 | 71.8% |
| 2 occurrences | 88 | 14.7% |
| 3-5 occurrences | 56 | 9.3% |
| 6-10 occurrences | 14 | 2.3% |
| 11-20 occurrences | 7 | 1.2% |
| 21-50 occurrences | 2 | 0.3% |
| 51-100 occurrences | 1 | 0.2% |
| > 100 occurrences | 1 | 0.2% |

### Catégories d'organisations

| Catégorie | Occurrences | % |
|-----------|-------------|---|
| Société des Nations | 373 | 25.2% |
| Commissions/Comités | 160 | 10.8% |
| Chambres de Commerce | 144 | 9.7% |
| Associations Espéranto | 72 | 4.9% |
| Gouvernements/Ministères | 56 | 3.8% |
| Universités/Académies | 49 | 3.3% |
| Associations Scientifiques | 23 | 1.6% |
| Autres | 604 | 40.8% |

## Utilisation

### Exécuter le pipeline complet

```bash
python scripts/postprocess_organization_FINAL.py
```

### Générer le rapport d'évaluation

```bash
python scripts/evaluate_organization.py
```

## Défis rencontrés

### 1. **Variantes multilingues**
- Corpus multilingue (français, anglais, allemand, espéranto)
- Exemple : 34 variantes de "Société des Nations"
- **Solution** : Dictionnaire de traduction manuel exhaustif

### 2. **Tirets de césure**
- Fin de ligne avec césures : `Coopé-\nRation`
- **Solution** : Regex patterns multiples pour corriger toutes les formes

### 3. **Similarité trop large**
- Risque de fusionner des organisations distinctes
- **Solution** : Contraintes géographiques + scope words

### 4. **Entités avec 1 occurrence**
- 72% des entités n'apparaissent qu'une fois
- Difficile de valider automatiquement
- **Solution** : Clustering conservateur (seuil 0.92)

## LIMITATION IMPORTANTE : Duplications dans le corpus

**Fréquences d'apparition potentiellement gonflées**

Les statistiques de fréquence (nb_occurrences, nb_documents) doivent être interprétées avec prudence car :

- Le corpus peut contenir des **documents en double** :
  - Projets de protocole vs versions finales
  - Traductions multiples du même document (FR/EN/DE/EO)
  - Versions révisées d'un même texte

- **Impact sur les métriques** :
  - Une personne apparaissant 50 fois pourrait en réalité n'apparaître que dans 10 documents uniques
  - Les TOP personnes/organisations pourraient être biaisées vers les documents traduits/dupliqués
  - La distribution par fréquence n'est pas absolument fiable

- **Recommandations** :
  - Utiliser les fréquences comme **indicateur relatif** uniquement
  - Ne pas interpréter les chiffres absolus comme définitifs
  - Privilégier l'analyse qualitative des entités extraites
  - Si critique : effectuer une déduplication manuelle du corpus avant analyse

Cette limitation n'affecte **PAS** la qualité de l'extraction NER elle-même, mais uniquement les statistiques de fréquence.

## Bonnes pratiques pour PERSON (à venir)

Les techniques développées pour ORGANIZATION sont réutilisables pour PERSON :

1. **Normalisation robuste**
   - Correction tirets de césure
   - Suppression articles
   - Normalisation casse

2. **Dictionnaire de variantes**
   - Formes complètes du nom
   - Prénoms/noms/initiales
   - Variantes linguistiques

3. **Clustering intelligent**
   - Similarité + contraintes discriminantes
   - Pour PERSON : prénom/nom/initiales comme discriminants

4. **Filtrage progressif**
   - Phase 1 : Filtrage évident
   - Phase 2 : Traduction/normalisation
   - Phase 3 : Clustering
   - Phase 4 : Suppression finale

## Contact

Pour toute question sur le pipeline ORGANIZATION, consulter :
- `scripts/postprocess_organization_FINAL.py` (code source commenté)
- `outputs/evaluation_organization_report.txt` (rapport d'évaluation)

---

**Auteur** : Claude Code
**Date** : 2025-11-16
**Corpus** : Esperanto Société des Nations
**Modèle NER** : GLiNER2
