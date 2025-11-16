# Post-traitement PERSON - Documentation

## Vue d'ensemble

Ce document décrit le pipeline de nettoyage des entités **PERSON** extraites par GLiNER2 du corpus Esperanto de la Société des Nations.

## Résultats finaux

| Métrique | Valeur |
|----------|--------|
| **Entités initiales** | 1923 |
| **Entités finales** | 832 |
| **Taux de réduction** | 56.7% |
| **Score NER moyen** | 0.833 |

### TOP 10 personnes

1. **Privat** (49 occurrences)
2. **Gilbert Murray** (36 occ)
3. **Inazo Nitobe** (29 occ)
4. **G. Reynald** (28 occ)
5. **Louis Lazarus Zamenhof** (25 occ)
6. **Dave Hennen Morris** (22 occ)
7. **Mrs Coombe-tennant** (20 occ)
8. **Willo. Forchhammer** (19 occ)
9. **Bonnevie** (18 occ)
10. **S. Segfried Auerbach** (16 occ)

## Pipeline de nettoyage

### Script : `postprocess_person_FINAL.py`

Le script final applique les étapes suivantes :

### 1. **Normalisation**
- Correction des tirets de césure (`Pri-vat` → `Privat`)
- Correction des typos espéranto (`dro.` → `dr.`, `sro.` → `sr.`, `sioro` → `sinjoro`)
- Correction des typos anglais (`profrssor` → `professor`, `coolbe` → `coombe`)
- Suppression des espaces multiples
- Suppression de la ponctuation de fin

### 2. **Filtrage initial**
Suppression de :
- Acronymes courts (≤ 2 caractères en majuscules : `J`, `A.`, `T.`)
- Pronoms (erreurs NER : `I`, `you`, `he`, `she`, `we`, `they`)
- Noms trop courts (< 3 caractères)
- Noms composés de chiffres/initiales seulement (`I. N.`, `T. S. V. P`)
- Entités génériques (`students`, `parents`, `scholars`, `members`, `teachers`, `children`, `colleagues`)

### 3. **Suppression des titres honorifiques**

Le pipeline supprime les titres dans **4 langues** (français, anglais, allemand, espéranto) :

**Français** :
- `Monsieur`, `Madame`, `Mademoiselle`, `Mlle`, `Melle` (typo)
- `Le Professeur`, `Le Docteur`, `Le Sénateur`, `Le Président`, `Le Ministre`, `Le Directeur`

**Anglais** :
- `Professor`, `Prof.`, `Doctor`, `Dr.`, `Mister`, `Mr.`, `Mrs.`, `Miss`, `Ms.`
- `President`, `Senator`, `Minister`, `Director`, `General`

**Allemand** :
- `Herr`, `Herrn`, `Frau`, `Fräulein`

**Espéranto** :
- `Sinjoro`, `Sioro` (typo), `Eminenta`, `Estimata`
- `Dro`, `D-ro` (variantes de Dr.)
- `Sro`, `S-ro` (variantes de Sr.)

**Exemples de transformations** :
- `Eminenta Sinjoro Dr. Inazo Nitobe` → `Inazo Nitobe`
- `Le Professeur Privat` → `Privat`
- `Melle Bonnevie` → `Bonnevie`
- `Sioro Inazo Nitobe` → `Inazo Nitobe` (typo "Sioro" géré)

### 4. **Clustering intelligent par similarité**

**Seuil de similarité** : 0.90 (90%)

**Critères de fusion** :
- **Même nom de famille** (dernier mot) → fusion automatique
  - Exemple : `Privat` + `Edmond Privat` → `Privat`
- **Similarité ≥ 0.90** + même nom de famille similaire (≥ 0.85)
  - Exemple : `Gilbert Murray` + `Professor Murray` → `Gilbert Murray`

**Exemples de fusions réussies** :
- `PRIVAT` + `Edmond Privat` → `Privat` (49 occ)
- `MURRAY` + `Professor MURRAY` → `Gilbert Murray` (36 occ)

**Ordre de priorité pour le nom canonique** :
1. Nom le plus long (forme complète privilégiée)
2. En cas d'égalité, nom avec le plus d'occurrences

### 5. **Normalisation de la casse**

Applique la convention : **Première lettre majuscule, reste en minuscules**

**Exemples** :
- `PRIVAT` → `Privat`
- `EDMOND PRIVAT` → `Edmond Privat`
- `GILBERT MURRAY` → `Gilbert Murray`

**Exception** : Conservation des initiales (`J.`, `A.`)

### 6. **Suppression des entités multiples**

Suppression des entrées contenant plusieurs personnes :
- `Privat and Mrs. Morris` (supprimé)
- Détection du mot `and` ou `et` entre deux noms propres

## Fichiers générés

| Fichier | Description |
|---------|-------------|
| `outputs/person_FINAL_CLEAN.xlsx` | **832 personnes nettoyées** |
| `outputs/evaluation_person_report.txt` | Rapport d'évaluation avec statistiques |

## Format du fichier final

Colonnes dans `person_FINAL_CLEAN.xlsx` :

- `entity_normalized` : Nom canonique de la personne
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
| 1 occurrence | 567 | 68.1% |
| 2 occurrences | 143 | 17.2% |
| 3-5 occurrences | 77 | 9.3% |
| 6-10 occurrences | 29 | 3.5% |
| 11-20 occurrences | 10 | 1.2% |
| 21-50 occurrences | 6 | 0.7% |
| 51-100 occurrences | 0 | 0.0% |
| > 100 occurrences | 0 | 0.0% |

### Scores NER

| Métrique | Valeur |
|----------|--------|
| **Score moyen global** | 0.833 |
| **Score médian** | 0.856 |
| **Score min** | 0.601 |
| **Score max** | 0.989 |

## Utilisation

### Exécuter le pipeline complet

```bash
python scripts/postprocess_person_FINAL.py
```

**Paramètres optionnels** :
```bash
python scripts/postprocess_person_FINAL.py \
  --input outputs/person_RAW.xlsx \
  --output outputs/person_FINAL_CLEAN.xlsx
```

### Générer le rapport d'évaluation

```bash
python scripts/evaluate_person.py
```

**Paramètres optionnels** :
```bash
python scripts/evaluate_person.py \
  --input outputs/person_FINAL_CLEAN.xlsx \
  --output outputs/evaluation_person_report.txt
```

## Défis rencontrés

### 1. **Titres honorifiques multilingues**
- Corpus multilingue (français, anglais, allemand, espéranto)
- Titres espéranto : `Eminenta Sinjoro Dr.`, `Sioro` (typo de `Sinjoro`)
- **Solution** : Dictionnaire exhaustif de patterns regex + gestion des typos

### 2. **Variantes de noms**
- Forme complète vs nom de famille seul : `Edmond Privat` vs `Privat`
- Initiales vs nom complet : `G. Murray` vs `Gilbert Murray`
- **Solution** : Clustering par nom de famille + choix du nom le plus long comme canonique

### 3. **Normalisation de la casse**
- Données brutes en MAJUSCULES : `PRIVAT`, `MURRAY`
- Besoin de format standard : `Privat`, `Murray`
- **Solution** : Fonction `normalize_case()` avec préservation des initiales

### 4. **Entités avec 1 occurrence**
- 68% des entités n'apparaissent qu'une fois
- Difficile de valider automatiquement
- **Solution** : Clustering conservateur (seuil 0.90) + filtrage strict des titres

### 5. **Titres persistants dans le pipeline**
- Titres supprimés en Phase 1 mais réapparaissant via entity_canonical
- Exemple : `Le Professeur Privat` dans TOP 10
- **Solution** : Application de `remove_honorifics()` deux fois (Phase 1 + Phase 5)

### 6. **Typos espéranto**
- Variantes : `dro.` (dr.), `sro.` (sr.), `sioro` (sinjoro), `coolbe` (coombe)
- **Solution** : Dictionnaire `EXPLICIT_NAME_MAPPING` appliqué en Phase 1

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

## Différences avec ORGANIZATION

| Aspect | ORGANIZATION | PERSON |
|--------|--------------|--------|
| **Contraintes géographiques** | Oui (ville, pays, nationalité) | Non (personnes globales) |
| **Titres à supprimer** | Articles (`Le`, `La`) | Titres honorifiques multilingues |
| **Normalisation casse** | Capitalisation standard | Première lettre majuscule uniquement |
| **Clustering** | Seuil 0.92 (strict) | Seuil 0.90 + fusion auto par nom |
| **Entités multiples** | N/A | Suppression `X and Y` |

## Itérations du développement

Le pipeline a été développé de manière itérative :

1. **v1** : Normalisation de base (1923 → 1106 entités, 42.5%)
2. **v2-v4** : Ajout titres, amélioration clustering
3. **v5** : Normalisation casse + clustering par nom de famille (56.3%)
4. **v6** : Correction bug titres persistants + ajout `students/parents/scholars` (56.5%)
5. **v7** : Titres espéranto + suppression entités multiples (56.7%)
6. **FINAL** : Gestion typo `Sioro` → **832 entités (56.7%)**

## Contact

Pour toute question sur le pipeline PERSON, consulter :
- `scripts/postprocess_person_FINAL.py` (code source commenté)
- `outputs/evaluation_person_report.txt` (rapport d'évaluation)

---

**Auteur** : Claude Code
**Date** : 2025-11-16
**Corpus** : Esperanto Société des Nations
**Modèle NER** : GLiNER2
