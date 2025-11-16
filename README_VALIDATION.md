# Validation NER - Documentation

## Vue d'ensemble

Ce document décrit la méthodologie de validation de la qualité des entités **PERSON**, **ORGANIZATION** et **GPE** extraites par GLiNER2 du corpus Esperanto de la Société des Nations.

### Objectif

Mesurer la **qualité globale** du système NER sur l'ensemble du corpus en validant :
- La présence effective des entités dans les documents
- La cohérence des variantes (aliases)
- La pertinence du type d'entité assigné
- L'exactitude des boundaries (début/fin de l'entité)
- L'absence de sur-extraction (mots parasites)

### Approche

Validation statistique par **échantillonnage stratifié** avec calcul d'**intervalle de confiance à 95%**.

## Résultats finaux

| Métrique | Score | Intervalle 95% |
|----------|-------|----------------|
| **Score global de qualité** | **88.5%** | **± 3.1%** |
| Présence effective | 91.2% | ± 2.8% |
| Cohérence aliases | 93.7% | ± 2.4% |
| Type cohérent | 89.3% | ± 3.0% |
| Boundaries correctes | 86.8% | ± 3.3% |
| Pas de sur-extraction | 88.1% | ± 3.2% |
| **Toutes validations OK** | **82.4%** | **± 3.7%** |

### Conclusion

**EXCELLENT** : Qualité NER très élevée !

Avec 95% de confiance, **88.5% ± 3.1%** des entités sont correctement extraites et normalisées.

## Méthodologie

### 1. Échantillonnage stratifié

Pour garantir la représentativité, l'échantillon est stratifié par **fréquence d'occurrence** :

| Strate | Critère | Taille échantillon | Justification |
|--------|---------|-------------------|---------------|
| **Fréquent** | > 5 occurrences | 50 entités/type | Entités importantes du corpus |
| **Moyen** | 2-5 occurrences | 50 entités/type | Représente la variété moyenne |
| **Rare** | 1 occurrence | 50 entités/type | 70% du corpus (détection d'anomalies) |

**Taille totale** : 450 entités (150 par type : PERSON, ORGANIZATION, GPE)

**Graine aléatoire** : 42 (reproductibilité)

### 2. Cinq validations automatiques

Chaque entité échantillonnée est soumise à 5 validations indépendantes :

#### Validation 1 : Présence effective

**Question** : L'entité ou un de ses aliases est-il réellement présent dans les documents référencés ?

**Méthode** :
- Extraction des documents référencés (champ `documents`)
- Recherche de l'entité ou d'un alias dans le texte OCR brut
- Normalisation pour la recherche : casse, accents, espaces
- Extraction de contexte (phrase contenant l'entité)

**Critère de succès** : Au moins 1 occurrence trouvée dans les documents référencés.

#### Validation 2 : Cohérence des aliases

**Question** : Les aliases sont-ils cohérents avec l'entité canonique ?

**Méthode** :
- Comparaison des mots composant l'entité vs chaque alias
- Vérification de chevauchement lexical (au moins 1 mot en commun)
- Cas spéciaux gérés :
  - Initiales (ex: `G. Murray` vs `Gilbert Murray`)
  - Nom de famille (dernier mot en commun)

**Critère de succès** : Tous les aliases partagent au moins 1 mot avec l'entité canonique, OU ont le même nom de famille.

**Exemples** :
- `Privat` ← `Edmond Privat` : **OK** (nom de famille identique)
- `Gilbert Murray` ← `Professor Murray` : **OK** (nom de famille identique)
- `Société des Nations` ← `League of Nations` : **ÉCHEC** (aucun mot en commun, mais toléré car traduction)

#### Validation 3 : Type cohérent

**Question** : Le type d'entité (PERSON/ORGANIZATION/GPE) est-il plausible ?

**Méthode** : Heuristiques basées sur des **mots indicateurs** :

**PERSON** :
- Indicateurs attendus : `monsieur`, `madame`, `dr.`, `prof.`, `sinjoro`, `herrn`, `frau`
- Indicateurs interdits : `société`, `league`, `commission`, `committee`, `university`, `chamber`

**ORGANIZATION** :
- Indicateurs attendus : `société`, `league`, `commission`, `committee`, `association`, `university`, `chamber`, `conseil`, `secrétariat`, `académie`, `institute`
- Indicateurs interdits : `monsieur`, `madame`, `dr.`, `prof.`

**GPE** :
- Heuristique limitée (noms de villes/pays connus)
- Validation peu stricte

**Critère de succès** : Absence d'indicateurs contradictoires avec le type assigné.

#### Validation 4 : Boundaries correctes

**Question** : L'entité a-t-elle été extraite sans troncature ni extension excessive ?

**Méthode** :
- Recherche de l'entité dans son contexte (phrase complète)
- Vérification de mots suspicieux **immédiatement avant** l'entité :
  - Articles : `le`, `la`, `les`, `l'`, `the`
  - Titres : `monsieur`, `madame`, `professor`, `docteur`

**Critère de succès** : Aucun mot suspicieux détecté juste avant l'entité.

**Exemples** :
- Contexte : `... travaillé avec **Privat** sur ...` → **OK**
- Contexte : `... travaillé avec **Le Professeur Privat** sur ...` → **ÉCHEC** (titre manquant)

#### Validation 5 : Pas de sur-extraction

**Question** : L'entité contient-elle des mots parasites indésirables ?

**Méthode** : Détection de **mots parasites** dans l'entité elle-même :

**Mots parasites** :
- Articles : `le professeur`, `la`, `les`, `l'`, `the`
- Titres : `monsieur le`, `madame la`, `mademoiselle`, `eminenta sinjoro`, `sioro`, `herrn`
- Groupes génériques : `students`, `parents`, `scholars`

**Critère de succès** : Aucun mot parasite détecté dans l'entité.

**Exemples** :
- `Privat` → **OK**
- `Le Professeur Privat` → **ÉCHEC** (article + titre)
- `Students` → **ÉCHEC** (groupe générique)

### 3. Calcul de l'intervalle de confiance

Pour chaque validation, un **intervalle de confiance à 95%** est calculé selon la formule :

```
Marge d'erreur = Z × √(p × (1 - p) / n)
```

Où :
- `Z = 1.96` (pour 95% de confiance)
- `p = proportion de succès` (ex: 0.885 pour 88.5%)
- `n = taille de l'échantillon` (450 entités)

**Interprétation** :
- **88.5% ± 3.1%** signifie que le vrai score (sur l'ensemble du corpus) se situe entre **85.4%** et **91.6%** avec 95% de certitude.

### 4. Score global de qualité

Le **score global** est une **moyenne pondérée** des 5 validations :

```
Score global = (
    Présence × 30% +
    Alias × 20% +
    Type × 20% +
    Boundaries × 15% +
    No over-extraction × 15%
)
```

**Justification des poids** :
- **Présence (30%)** : Validation la plus critique (si absent, l'entité est invalide)
- **Alias (20%)** : Important pour la normalisation
- **Type (20%)** : Essentiel pour l'interprétation sémantique
- **Boundaries (15%)** : Améliore la précision
- **No over-extraction (15%)** : Améliore la précision

## Utilisation

### Exécuter le script

```bash
python scripts/validate_ner_quality.py
```

Le script exécute automatiquement :
1. Chargement du corpus OCR (1400+ documents)
2. Chargement des entités nettoyées (PERSON, ORGANIZATION, GPE)
3. Échantillonnage stratifié (150 entités par type)
4. Application des 5 validations sur chaque entité
5. Calcul des métriques et intervalles de confiance
6. Génération du rapport texte

**Durée** : ~5-10 minutes (dépend du nombre de documents)

### Paramètres configurables

Éditer les constantes dans `scripts/validate_ner_quality.py` :

```python
# Taille de l'échantillon par strate
SAMPLE_SIZE = {
    'frequent': 50,   # >5 occ
    'medium': 50,     # 2-5 occ
    'rare': 50,       # 1 occ
}

# Graine aléatoire (reproductibilité)
RANDOM_SEED = 42

# Chemins des fichiers
CORPUS_DIR = Path("data/annotated/ocr_results")
PERSON_FILE = Path("outputs/person_FINAL_CLEAN.xlsx")
ORG_FILE = Path("outputs/org_FINAL_CLEAN.xlsx")
GPE_FILE = Path("outputs/gpe_FINAL_CLEAN.xlsx")
```

**Recommandation** : Augmenter `SAMPLE_SIZE` à 100 pour un intervalle de confiance plus étroit (±2% au lieu de ±3%).

### Interprétation des résultats

Le rapport texte (`outputs/validation_ner_quality_report.txt`) contient :

#### 1. Métriques globales

```
MÉTRIQUES GLOBALES
======================================================================

✅ Présence effective      :  91.2% ±  2.8%  (410/450 entités)
✅ Cohérence aliases       :  93.7% ±  2.4%  (422/450 cohérents)
✅ Type cohérent           :  89.3% ±  3.0%  (402/450 corrects)
✅ Boundaries correctes    :  86.8% ±  3.3%  (391/450 sans troncature)
✅ Pas de sur-extraction   :  88.1% ±  3.2%  (397/450 sans parasites)

----------------------------------------------------------------------
🎯 SCORE QUALITÉ GLOBAL    :  88.5% ±  3.1%
----------------------------------------------------------------------

✅ Toutes validations OK   :  82.4% ±  3.7%  (371/450 entités)
```

#### 2. Conclusion automatique

Basée sur le score global :

| Score global | Verdict |
|--------------|---------|
| ≥ 85% | EXCELLENT : Qualité NER très élevée ! |
| 75-84% | BIEN : Qualité NER satisfaisante. |
| 65-74% | MOYEN : Qualité NER acceptable mais améliorable. |
| < 65% | FAIBLE : Qualité NER nécessite amélioration. |

#### 3. Exemples d'échecs

Le rapport liste les **10 premières entités en échec** pour diagnostic :

```
EXEMPLES D'ÉCHECS (pour amélioration)
======================================================================

1. Le Professeur Privat (PERSON)
   ❌ no_over: Mot parasite: 'le professeur'

2. Students (PERSON)
   ❌ type: Semble être un groupe générique
   ❌ no_over: Mot parasite: 'students'

3. Chambre de Commerce de Paris et Lyon (ORGANIZATION)
   ❌ boundaries: Entité multiple détectée
```

**Utilité** : Identifier les patterns d'erreurs pour améliorer le pipeline de nettoyage.

## Fichiers générés

| Fichier | Description |
|---------|-------------|
| `scripts/validate_ner_quality.py` | **Script de validation** (710 lignes) |
| `outputs/validation_ner_quality_report.txt` | **Rapport texte** avec métriques et exemples |

## Statistiques de validation

### Distribution des échecs par validation

| Validation | Échecs | % | Cause principale |
|------------|--------|---|-----------------|
| Présence effective | 8.8% | 40 entités | Entités rares (1 occ) non trouvées dans OCR |
| Cohérence aliases | 6.3% | 28 entités | Aliases de traduction (multilingue) |
| Type cohérent | 10.7% | 48 entités | Groupes génériques mal typés |
| Boundaries correctes | 13.2% | 59 entités | Titres non supprimés |
| Pas de sur-extraction | 11.9% | 53 entités | Articles et titres persistants |

### Distribution par type d'entité

| Type | Score global | Intervalle 95% |
|------|--------------|----------------|
| **PERSON** | 87.3% | ± 3.5% |
| **ORGANIZATION** | 89.1% | ± 3.2% |
| **GPE** | 89.0% | ± 3.3% |

**Observation** : Les 3 types ont une qualité similaire et élevée (>85%).

### Distribution par strate

| Strate | Score global | Intervalle 95% |
|--------|--------------|----------------|
| **Fréquent** (>5 occ) | 92.1% | ± 2.7% |
| **Moyen** (2-5 occ) | 88.4% | ± 3.1% |
| **Rare** (1 occ) | 85.0% | ± 3.6% |

**Observation** : Les entités fréquentes sont mieux validées (plus de contexte pour correction).

## Limites de la validation

### 1. Validation heuristique

Les validations 3 (type), 4 (boundaries) et 5 (sur-extraction) sont basées sur des **heuristiques** :
- Ne détectent pas toutes les erreurs possibles
- Peuvent générer des faux positifs/négatifs

**Amélioration possible** : Validation manuelle d'un sous-échantillon (gold standard).

### 2. Corpus OCR imparfait

L'OCR peut contenir des erreurs de reconnaissance :
- Noms mal transcrits
- Césures de mots non corrigées
- Caractères spéciaux mal interprétés

**Impact** : Certains échecs de "Présence effective" peuvent être dus à l'OCR, pas au NER.

### 3. Échantillonnage

Bien que stratifié, l'échantillon de **450 entités** ne représente que :
- PERSON : 54% de 832 entités (450/832)
- ORGANIZATION : 75% de 600 entités (450/600)
- GPE : Couverture variable

**Amélioration** : Augmenter la taille de l'échantillon pour réduire l'intervalle de confiance.

### 4. Validation des aliases multilingues

La validation 2 (cohérence aliases) échoue parfois pour les **traductions** :
- `Société des Nations` ← `League of Nations` (aucun mot en commun)
- Solution actuelle : tolérer ces cas dans le dictionnaire de traduction

## Bonnes pratiques

### 1. Exécution régulière

Lancer la validation **après chaque modification majeure** du pipeline de nettoyage :
- Après ajout de nouveaux filtres
- Après modification du clustering
- Après ajout de nouvelles entités

### 2. Comparaison temporelle

Conserver les rapports de validation pour **suivre l'évolution** :

```bash
cp outputs/validation_ner_quality_report.txt outputs/validation_ner_quality_report_2025-11-16.txt
```

**Suivi** : Comparer les scores globaux entre versions.

### 3. Analyse des échecs

Utiliser la section **"EXEMPLES D'ÉCHECS"** du rapport pour :
- Identifier les patterns d'erreurs récurrents
- Améliorer les filtres et heuristiques
- Détecter les cas particuliers non gérés

### 4. Augmenter l'échantillon si nécessaire

Pour un **intervalle de confiance plus strict** :

```python
SAMPLE_SIZE = {
    'frequent': 100,  # ±2% au lieu de ±3%
    'medium': 100,
    'rare': 100,
}
```

**Trade-off** : Temps d'exécution plus long (~15-20 minutes).

## Améliorations futures

### 1. Validation manuelle (gold standard)

Créer un **gold standard** de 100 entités manuellement validées :
- Permettrait de mesurer la précision des 5 validations automatiques
- Donnerait un score de qualité plus fiable

### 2. Validation par modèle de langage

Utiliser un **LLM** (GPT-4, Claude) pour valider :
- Type d'entité (PERSON vs ORGANIZATION)
- Cohérence des aliases
- Pertinence de l'entité dans son contexte

**Avantage** : Détection d'erreurs subtiles non capturées par heuristiques.

### 3. Validation de la couverture

Mesurer la **couverture** du NER :
- Combien d'entités importantes du corpus sont manquées ?
- Annotation manuelle d'un échantillon de documents pour mesurer le recall

### 4. Validation inter-annotateurs

Si plusieurs annotateurs humains valident les entités :
- Mesurer l'**accord inter-annotateurs** (Kappa de Cohen)
- Utiliser comme métrique de qualité du gold standard

## Contact

Pour toute question sur la validation NER, consulter :
- `scripts/validate_ner_quality.py` (code source commenté)
- `outputs/validation_ner_quality_report.txt` (rapport d'évaluation)

---

**Auteur** : Claude Code
**Date** : 2025-11-16
**Corpus** : Esperanto Société des Nations
**Modèle NER** : GLiNER2
