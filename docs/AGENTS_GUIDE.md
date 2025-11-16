# 🤖 AGENTS GUIDE - test-gliner2

**Guide d'utilisation des 11 Agents Claude Code**

Ce projet inclut 11 agents spécialisés dans `.claude/agents/` pour vous assister dans différentes tâches. Ce guide explique quand et comment les utiliser.

---

## 🎯 Vue d'Ensemble

Les agents sont invoqués avec la syntaxe `@nom_agent` dans Claude Code.

**Catégories** :
- ⭐ **Critiques** : À utiliser régulièrement
- 🔧 **Qualité du code** : Pour développement propre
- 🔬 **Scientifiques** : Pour recherche reproductible
- 🏗️ **Infrastructure** : Pour setup et environnement

---

## ⭐ Agents Critiques (À Utiliser Régulièrement)

### 1. `@gardien_projet` - Continuité Entre Sessions

**Rôle** : Maintient `PROJECT_STATE.md` à jour et assure la continuité entre sessions de travail.

**Quand l'utiliser** :
- Au début de chaque session : "Où en sommes-nous ?"
- Après avoir terminé une tâche majeure
- Avant de clôturer une session de travail

**Exemples** :
```
@gardien_projet Où en sommes-nous ?

@gardien_projet J'ai terminé le preprocessing du corpus, 1250 documents nettoyés

@gardien_projet Résume ce qui a été fait aujourd'hui et ce qui reste à faire

@gardien_projet Ajoute une note : problème d'encodage UTF-8 dans fichier SDN_1925_042.txt
```

**Fichier géré** : `docs/PROJECT_STATE.md`

---

### 2. `@gestionnaire_contexte` - Gestion de la Mémoire

**Rôle** : Surveille la mémoire contextuelle de Claude Code et vous alerte avant saturation.

**Quand l'utiliser** :
- Lors de sessions longues (> 1h)
- Si vous travaillez sur de gros fichiers ou beaucoup de code
- Quand Claude semble "oublier" des éléments de conversation

**Exemples** :
```
@gestionnaire_contexte État de la mémoire ?

@gestionnaire_contexte Optimise le contexte actuel

@gestionnaire_contexte Préviens-moi avant compaction
```

**Utilité** : Évite les pertes d'information en cours de session.

---

## 🔧 Agents Qualité du Code

### 3. `@git_helper` - Messages de Commit Professionnels

**Rôle** : Génère des messages de commit selon **Conventional Commits**.

**Quand l'utiliser** :
- À chaque commit Git
- Pour standardiser l'historique Git

**Exemples** :
```
@git_helper Crée un commit pour les changements actuels

@git_helper Message de commit pour l'ajout du script NER

git add src/ner/gliner_extractor.py
@git_helper Commit avec message approprié
```

**Format généré** :
```
feat(ner): add GLiNER2 extractor script

- Implement entity extraction with confidence threshold
- Add batch processing for large corpora
- Include logging for traceability
```

---

### 4. `@doc_technique` - Documentation Claire

**Rôle** : Génère et améliore la documentation (README, commentaires de code, docstrings).

**Quand l'utiliser** :
- Après avoir écrit un nouveau module Python
- Pour documenter une fonction complexe
- Pour créer des README dans sous-dossiers

**Exemples** :
```
@doc_technique Ajoute des docstrings au fichier src/ner/gliner_extractor.py

@doc_technique Crée un README pour le dossier notebooks/02_ner/

@doc_technique Explique comment utiliser la fonction build_network()
```

---

### 5. `@testeur_code` - Tests Unitaires avec Pytest

**Rôle** : Génère des tests unitaires et vérifie la fiabilité du code.

**Quand l'utiliser** :
- Après avoir écrit une fonction importante
- Avant de finaliser un module
- Pour s'assurer de la reproductibilité

**Exemples** :
```
@testeur_code Crée des tests pour src/preprocessing/clean_text.py

@testeur_code Lance tous les tests et affiche les résultats

@testeur_code Ajoute un test pour la fonction extract_entities()
```

**Tests générés dans** : `tests/`

---

### 6. `@nettoyeur_projet` - Refactoring et Qualité

**Rôle** : Améliore la qualité du code (refactoring, suppression de duplications, optimisation).

**Quand l'utiliser** :
- Quand le code devient complexe ou redondant
- Pour améliorer la lisibilité
- Avant une release/publication

**Exemples** :
```
@nettoyeur_projet Analyse et améliore le code dans src/

@nettoyeur_projet Refactorise src/ner/gliner_extractor.py (code dupliqué)

@nettoyeur_projet Applique black et flake8 sur tout le projet
```

---

## 🔬 Agents Scientifiques

### 7. `@validateur_donnees` - Métriques de Qualité NER

**Rôle** : Calcule et valide les métriques de qualité des données (CER, WER, F1, Kappa, précision, rappel).

**Quand l'utiliser** :
- Après extraction NER pour évaluer la qualité
- Pour comparer différentes configurations GLiNER2
- Pour générer des rapports de validation

**Exemples** :
```
@validateur_donnees Évalue la qualité NER sur data/annotated/

@validateur_donnees Compare les résultats entre seuil 0.5 et 0.7

@validateur_donnees Calcule F1-score, précision et rappel par type d'entité

@validateur_donnees Génère un rapport de qualité pour outputs/reports/
```

**Métriques pour NER** :
- Précision (% entités correctes)
- Rappel (% entités trouvées)
- F1-score (moyenne harmonique)
- Confusion matrix (erreurs par type)

---

### 8. `@visualiseur_donnees` - Graphiques et Data Storytelling

**Rôle** : Crée des visualisations (graphiques, réseaux, dashboards).

**Quand l'utiliser** :
- Pour explorer les résultats
- Pour créer des figures pour publication
- Pour visualiser le réseau d'entités

**Exemples** :
```
@visualiseur_donnees Crée un graphe de réseau à partir de outputs/networks/entities_network.graphml

@visualiseur_donnees Histogramme des types d'entités extraites

@visualiseur_donnees Visualisation interactive du réseau (Pyvis)

@visualiseur_donnees Heatmap des co-occurrences entre entités
```

**Outputs** : `outputs/visualizations/`

---

### 9. `@historien_computationnel` - Documentation Méthodologique

**Rôle** : Documente la méthodologie scientifique pour reproductibilité.

**Quand l'utiliser** :
- Lors de choix méthodologiques importants
- Pour documenter les paramètres d'expériences
- Pour préparer une publication

**Exemples** :
```
@historien_computationnel Documente le choix du seuil de confiance GLiNER2

@historien_computationnel Ajoute dans METHODOLOGY.md les paramètres de construction du réseau

@historien_computationnel Justifie pourquoi utiliser co-occurrences plutôt que dépendances syntaxiques
```

**Fichier géré** : `docs/METHODOLOGY.md`

---

## 🏗️ Agents Infrastructure

### 10. `@architecte_projet` - Structure de Projet

**Rôle** : Maintient une structure de projet standardisée et cohérente.

**Quand l'utiliser** :
- Pour ajouter un nouveau module ou dossier
- Pour réorganiser le projet
- Pour vérifier la conformité de la structure

**Exemples** :
```
@architecte_projet Vérifie que la structure est conforme

@architecte_projet Propose une organisation pour le dossier src/network/

@architecte_projet Où placer les configurations GLiNER2 ?
```

---

### 11. `@gestionnaire_environnement` - Docker et Dépendances

**Rôle** : Gère l'environnement conda, Docker, et assure la reproductibilité.

**Quand l'utiliser** :
- Pour ajouter une nouvelle dépendance Python
- Pour créer un Dockerfile (si nécessaire)
- Pour résoudre des conflits de versions

**Exemples** :
```
@gestionnaire_environnement Ajoute la bibliothèque spacy-lookups-data à environment.yml

@gestionnaire_environnement Crée un Dockerfile pour le projet

@gestionnaire_environnement Résous le conflit entre transformers et torch
```

**Fichier géré** : `environment.yml` (+ optionnel `Dockerfile`)

---

## 📋 Workflows Recommandés

### Début de Session

```bash
# 1. État du projet
@gardien_projet Où en sommes-nous ?

# 2. Vérifier la mémoire (si session longue prévue)
@gestionnaire_contexte État de la mémoire ?
```

---

### Développement d'un Nouveau Module

```bash
# 1. Développer le code (ex: src/ner/gliner_extractor.py)

# 2. Documenter
@doc_technique Ajoute docstrings à src/ner/gliner_extractor.py

# 3. Tester
@testeur_code Crée tests pour src/ner/gliner_extractor.py

# 4. Commit
git add src/ner/ tests/test_ner/
@git_helper Commit avec message approprié
```

---

### Validation des Résultats NER

```bash
# 1. Évaluer qualité
@validateur_donnees Calcule F1-score sur data/annotated/

# 2. Visualiser
@visualiseur_donnees Histogramme des types d'entités

# 3. Documenter méthode
@historien_computationnel Documente les résultats de validation dans METHODOLOGY.md

# 4. Mettre à jour état
@gardien_projet NER complétée, F1-score = 0.78
```

---

### Analyse de Réseau

```bash
# 1. Construire réseau (code)

# 2. Visualiser
@visualiseur_donnees Graphe interactif du réseau (Pyvis)

# 3. Valider métriques
@validateur_donnees Calcule métriques de réseau (densité, clustering)

# 4. Documenter
@historien_computationnel Ajoute paramètres de construction du réseau dans METHODOLOGY.md
```

---

### Fin de Session

```bash
# 1. Résumé des progrès
@gardien_projet Résume ce qui a été fait aujourd'hui

# 2. Commit final
@git_helper Commit de fin de session

# 3. Nettoyage (optionnel)
@nettoyeur_projet Vérifie la qualité du code ajouté aujourd'hui
```

---

## 💡 Bonnes Pratiques

**Régularité** :
- Utiliser `@gardien_projet` au début et fin de chaque session
- Invoquer `@validateur_donnees` après chaque étape majeure

**Documentation** :
- `@doc_technique` pour code
- `@historien_computationnel` pour méthodologie
- Les deux sont complémentaires !

**Qualité** :
- `@testeur_code` avant chaque commit important
- `@nettoyeur_projet` avant publication/partage

**Commits** :
- Toujours utiliser `@git_helper` pour messages standardisés
- Facilite la compréhension de l'historique Git

---

## 🆘 Aide et Support

**Lister les agents disponibles** :
```bash
ls .claude/agents/
```

**Voir la description d'un agent** :
```bash
cat .claude/agents/gardien_projet.md
```

**Documentation Claude Code** :
- [Documentation officielle](https://code.claude.com/docs)

---

**Dernière mise à jour** : 2025-11-16

---

## 🎓 Annexe : Exemples Complets

### Exemple 1 : Session Typique de Développement

```bash
# Session matinale
@gardien_projet Bonjour, où en sommes-nous ?
# → Répond: "Vous devez terminer le preprocessing et commencer NER"

# Développer le code
# ... écriture de src/preprocessing/clean_text.py ...

# Documenter
@doc_technique Ajoute docstrings à src/preprocessing/clean_text.py

# Tester
@testeur_code Crée tests pour src/preprocessing/clean_text.py
pytest tests/test_preprocessing/

# Commit
git add src/preprocessing/ tests/test_preprocessing/
@git_helper Commit pour preprocessing

# Mettre à jour état
@gardien_projet Preprocessing terminé, 1250 docs nettoyés
```

---

### Exemple 2 : Validation Complète NER

```bash
# Lancer extraction NER
python src/ner/gliner_extractor.py

# Validation
@validateur_donnees Évalue qualité NER sur échantillon de 100 docs
# → F1 = 0.75, Précision = 0.82, Rappel = 0.69

# Visualisation
@visualiseur_donnees Confusion matrix des types d'entités
@visualiseur_donnees Histogramme des scores de confiance

# Documentation méthodologique
@historien_computationnel Documente les résultats (F1=0.75, seuil=0.5)

# Commit
git add outputs/reports/ docs/METHODOLOGY.md
@git_helper Commit pour résultats validation NER

# Mise à jour projet
@gardien_projet NER validée, prêt pour analyse réseau
```

---

**Ce guide est votre référence pour utiliser efficacement les agents Claude !**
