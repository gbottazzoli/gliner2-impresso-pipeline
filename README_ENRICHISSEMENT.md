# Enrichissement contextuel des acteurs - Documentation

## Vue d'ensemble

Ce document décrit le pipeline d'enrichissement contextuel appliqué aux **832 personnes** extraites du corpus Esperanto de la Société des Nations. L'objectif est de générer un fichier Excel structuré compatible avec le format de la base de données des acteurs SDN.

## Format cible

### Colonnes du fichier final

| Colonne | Description | Exemple |
|---------|-------------|---------|
| **Nom** | Nom de famille | `Murray` |
| **Prénom** | Prénom(s) | `Gilbert` |
| **Identifiant** | Format `NomPrénom` | `MurrayGilbert` |
| **Variantes** | Aliases séparés par `, ` | `Prof. Murray, Professor Murray` |
| **Description** | Format structuré (voir ci-dessous) | `Titre: Professor \| Organisation: Committee on Intellectual Co-operation \| Lieu de travail/résidence: Oxford` |
| **Archives de correspondance** | Documents séparés par `;` | `R1048-13C-23516_doc03; R1048-13C-23516_doc11` |
| **Documents officiels** | (vide pour l'instant) | |
| **Presse** | (vide pour l'instant) | |
| **Nationalité** | Pays séparés par `;` | `Angleterre; France` |
| **Genre** | `Homme`, `Femme`, `Inconnu` | `Homme` |
| **Catégorie** | Catégorie d'acteur | `Personnalités externes` |

### Format de la Description

La description utilise un **format structuré lisible** avec 3 sections séparées par ` | ` :

```
Titre: [titres/fonctions] | Organisation: [organisations] | Lieu de travail/résidence: [lieux]
```

**Exemples** :
- `Titre: Dr., Professor | Organisation: Committee on Intellectual Co-operation | Lieu de travail/résidence: Oxford, Genève`
- `Titre: Secretary, Member | Organisation: Société des Nations | Lieu de travail/résidence: Genève`

## Pipeline d'enrichissement

### 1. Préparation (Phase 1)

**Script** : `scripts/enrich_all_persons.py`

**Chargement des données** :
- `person_FINAL_CLEAN.xlsx` : 832 personnes nettoyées
- `org_FINAL_CLEAN.xlsx` : 600 organisations
- `gpe_FINAL_CLEAN.xlsx` : 183 lieux (GPE)

**Construction des index** :
- Index ORG : 686 entrées (entités + aliases)
- Index GPE : 287 entrées (entités + aliases)

### 2. Extraction contextuelle (Phase 2)

Pour chaque personne :

#### A. Décomposition Nom/Prénom

**Règle** : Dernier mot = Nom, reste = Prénom

**Cas spéciaux** :
- Si nom incomplet (ex: `Privat` seul), recherche du prénom dans les aliases
- Nettoyage des titres dans le prénom extrait (`Dr.`, `M.`, `Prof.`, etc.)

**Exemples** :
- `Gilbert Murray` → Nom=`Murray`, Prénom=`Gilbert`
- `Privat` + alias `Edmond Privat` → Nom=`Privat`, Prénom=`EDMOND`

#### B. Extraction des contextes

**Méthode** : Recherche de toutes les occurrences de la personne dans les documents

**Fenêtre contextuelle** : ±100 mots (500 caractères) autour de chaque mention

**Variantes considérées** :
- Nom canonique : `Gilbert Murray`
- Tous les aliases : `Prof. Murray`, `Professor Murray`, `M. Murray`, etc.

**Exemple** :
- Personne : `Privat` (49 occurrences)
- Documents : 41 documents
- Contextes extraits : 497 fenêtres de ±100 mots

#### C. Matching hybride (Règles + LLM)

##### Phase 1 : Extraction par règles (rapide)

**1. Titres et fonctions** - Patterns regex :
```
- Anglais : Professor, Prof., Dr., Doctor, Director, Secretary, Member, President, etc.
- Français : Professeur, Directeur, Secrétaire, Membre, Président, etc.
- Espéranto : Patterns spéciaux détectés
```

**2. Organisations** - Matching avec index ORG :
```python
for org_alias, org_canonical in org_index.items():
    if org_alias in context.lower():
        organizations.append(org_canonical)
```

**3. Lieux** - Matching avec index GPE :
```python
for gpe_alias, gpe_canonical in gpe_index.items():
    if gpe_alias in context.lower():
        locations.append(gpe_canonical)
```

**4. Nationalités** - Patterns spécifiques :
- Pays directs : `France`, `Angleterre`, `Allemagne`, `Suisse`, `Japon`, etc.
- Adresses : `Oxford, Angleterre` → extrait `Angleterre`

**5. Genre** - Indices dans les titres :
- Masculin : `Mr.`, `Monsieur`, `M.`, `Herr`, `Herrn`
- Féminin : `Mrs.`, `Mme`, `Mlle`, `Miss`, `Madam`, `Frau`

##### Phase 2 : Extraction par LLM (intelligent)

**Déclenchement** :
- Score de confiance < 3 (fonctions + organisations + nationalités)
- OU nationalité vide/suspecte

**Modèle** : Ollama `llama3.1:8b`

**Prompt** :
```
Analyse ces extraits de documents de la Société des Nations concernant [personne].

CONTEXTES : [3 premiers contextes, max 1500 caractères]

Extraire au format JSON :
{
    "fonction": "...",
    "organisation": "...",
    "lieu_residence": "...",
    "nationalite": "...",
    "genre": "Homme|Femme|Inconnu"
}
```

**Gestion des erreurs** :
- Si LLM retourne format invalide → dict vide
- Si LLM retourne liste au lieu de dict → dict vide

#### D. Fusion des résultats

**1. Description** - Format structuré :

```python
# Titres (max 3, dédupliqués)
titres = "Dr., Professor, Member"
description.append(f"Titre: {titres}")

# Organisations (max 2, dédupliquées)
orgs = "Committee on Intellectual Co-operation, Société des Nations"
description.append(f"Organisation: {orgs}")

# Lieux (max 2, dédupliqués)
lieux = "Oxford, Genève"
description.append(f"Lieu de travail/résidence: {lieux}")

# Fusion finale
description = " | ".join(description_parts)
```

**2. Nationalité** - Filtrage et normalisation :

```python
# Filtrer stop words
stop_words = {'i', 'you', 'he', 'she', 'we', 'they', 'it', 'a', 'the', 'de', 'la', 'le', 'vous', 'je', 'tu', 'il', 'elle'}
nats_clean = [n for n in nats if len(n) > 2 and n.lower() not in stop_words]

# Normaliser pays similaires
country_mapping = {
    'england': 'Angleterre',
    'germany': 'Allemagne',
    'switzerland': 'Suisse',
    'japan': 'Japon',
    'usa': 'États-Unis',
}

# Top 3 pays par fréquence
nationalite = "; ".join(top_3_countries)
```

**3. Genre** - Majorité :
- Si indices multiples → prendre le plus fréquent
- Sinon LLM → utiliser résultat LLM
- Défaut → `Inconnu`

**4. Catégorie** - Règles sur description :

```python
if 'secretary' or 'secrétaire' or 'secretariat' in description.lower():
    catégorie = "Membres du secrétariat de la SDN"
elif 'délégué' or 'delegate' or 'gouvernement' in description.lower():
    catégorie = "Délégués des gouvernements"
else:
    catégorie = "Personnalités externes"
```

### 3. Parallélisation (Phase 3)

**Configuration** : 4 workers (multiprocessing)

**Avantages** :
- Traitement simultané de 4 personnes
- Vitesse : ~1-1.5 personne/seconde
- Temps total : 10-15 minutes pour 832 personnes

**Cache de documents** :
- Documents chargés une seule fois en mémoire
- Partagé entre tous les workers
- Réduit I/O disque

## Résultats

### Fichiers générés

| Fichier | Description |
|---------|-------------|
| `outputs/acteurs_SDN_enriched.xlsx` | **832 personnes enrichies** avec 11 colonnes |
| `outputs/enrichment_report.txt` | Rapport d'enrichissement avec statistiques |

### Statistiques attendues

| Métrique | Valeur estimée |
|----------|----------------|
| **Entités traitées** | 832 |
| **Temps total** | ~10-15 min |
| **Taux de complétude Description** | ~95% |
| **Taux de complétude Nationalité** | ~85-90% |
| **Taux de complétude Genre** | ~98% |
| **Utilisation LLM** | ~15-20% des cas |

## Exemples de résultats

### Edmond Privat

| Champ | Valeur |
|-------|--------|
| Nom | `Privat` |
| Prénom | `EDMOND` |
| Identifiant | `PrivatEDMOND` |
| Description | `Titre: Member, DR., Professor \| Organisation: Idist Union, Postal and Telegraphic Services \| Lieu de travail/résidence: Vienne, Angleterre` |
| Nationalité | `France; Suisse; Spain` |
| Genre | `Homme` |
| Catégorie | `Personnalités externes` |

### Gilbert Murray

| Champ | Valeur |
|-------|--------|
| Nom | `Murray` |
| Prénom | `Gilbert` |
| Identifiant | `MurrayGilbert` |
| Description | `Titre: Secretary, Prof., Professor \| Organisation: International Auxiliary Language, Finnish Government \| Lieu de travail/résidence: Vienne, Angleterre` |
| Nationalité | `France; Japon; Angleterre` |
| Genre | `Homme` |
| Catégorie | `Membres du secrétariat de la SDN` |

### Inazo Nitobe

| Champ | Valeur |
|-------|--------|
| Nom | `Nitobe` |
| Prénom | `Inazo` |
| Identifiant | `NitobeInazo` |
| Description | `Titre: Dr., Prof., General \| Organisation: Secretariat of the League, Economic Section \| Lieu de travail/résidence: Angleterre, Finlande` |
| Nationalité | `Suisse; États-Unis; Angleterre` |
| Genre | `Homme` |
| Catégorie | `Membres du secrétariat de la SDN` |

## Limites et considérations

### 1. Nationalités multiples

Les nationalités listées reflètent les **pays mentionnés dans les contextes**, pas nécessairement la nationalité réelle de la personne. Par exemple :
- Une personne peut être mentionnée dans des documents concernant plusieurs pays
- Cela ne signifie pas qu'elle a plusieurs nationalités

**Recommandation** : Interpréter comme "pays associés" plutôt que "nationalités confirmées"

### 2. Duplications dans le corpus

**IMPORTANT** : Les fréquences d'apparition peuvent être gonflées car le corpus peut contenir :
- Documents en double (projets vs versions finales)
- Traductions multiples (FR/EN/DE/EO)
- Versions révisées du même texte

**Impact** : Les statistiques de fréquence sont des **indicateurs relatifs** uniquement.

### 3. Extraction LLM

Le LLM (Ollama llama3.1:8b) est utilisé pour ~15-20% des cas complexes. Ses résultats peuvent être :
- Incomplets
- Parfois incorrects
- Dépendants de la qualité du contexte fourni

**Validation manuelle recommandée** pour les cas critiques.

## Utilisation

### Exécuter l'enrichissement complet

```bash
python scripts/enrich_all_persons.py
```

**Durée** : ~10-15 minutes

**Output** :
- `outputs/acteurs_SDN_enriched.xlsx`
- `outputs/enrichment_report.txt`

### Tester sur TOP 3 personnes

```bash
python scripts/enrich_persons_TEST.py
```

**Durée** : ~30 secondes

**Output** :
- `outputs/acteurs_SDN_TEST_TOP3.xlsx`

## Architecture technique

### Technologies utilisées

- **Python 3.13**
- **pandas** : Manipulation de données Excel
- **ollama** : LLM local pour extraction intelligente
- **tqdm** : Progress bar
- **multiprocessing** : Parallélisation

### Modèle LLM

- **Modèle** : `llama3.1:8b`
- **Provider** : Ollama (local)
- **Taille** : 4.9 GB
- **Utilisation** : Extraction structurée JSON

### Structure du code

```
scripts/
├── enrich_persons_TEST.py        # Test sur TOP 3 personnes
├── enrich_all_persons.py         # Enrichissement complet (832 personnes)
└── explore_data_structure.py     # Exploration initiale

outputs/
├── acteurs_SDN_enriched.xlsx     # Résultat final (832 personnes)
├── acteurs_SDN_TEST_TOP3.xlsx    # Résultat test (3 personnes)
├── enrichment_report.txt         # Rapport statistiques
├── person_FINAL_CLEAN.xlsx       # Input (832 personnes nettoyées)
├── org_FINAL_CLEAN.xlsx          # Input (600 organisations)
└── gpe_FINAL_CLEAN.xlsx          # Input (183 lieux)
```

## Développement itératif

Le pipeline a été développé en plusieurs étapes :

1. **v1** : Script de test sur 3 personnes
2. **v2** : Extraction contextuelle basique
3. **v3** : Ajout matching hybride (règles + LLM)
4. **v4** : Amélioration extraction prénom depuis aliases
5. **v5** : Filtrage nationalités bruitées
6. **v6** : Format Description structuré et lisible
7. **FINAL** : Parallélisation + gestion erreurs LLM

## Contact

Pour toute question sur le pipeline d'enrichissement :
- Code source : `scripts/enrich_all_persons.py`
- Documentation : `README_ENRICHISSEMENT.md`
- Rapport : `outputs/enrichment_report.txt`

---

**Auteur** : Claude Code
**Date** : 2025-11-16
**Corpus** : Esperanto Société des Nations
**Modèle NER** : GLiNER2
**Modèle LLM** : Ollama llama3.1:8b
