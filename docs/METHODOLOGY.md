# 📐 METHODOLOGY - test-gliner2

**Méthodologie Scientifique Reproductible**

Documentation détaillée de la méthodologie pour l'extraction NER et l'analyse de réseau sur le corpus SDN-Esperanto.

---

## 🎯 Question de Recherche

**Problématique** : Quels sont les acteurs (personnes, organisations, lieux) principaux mentionnés dans les documents en Esperanto de la Société des Nations, et comment sont-ils reliés ?

**Objectifs scientifiques** :
1. Identifier automatiquement les entités nommées dans un corpus historique multilingue (Esperanto)
2. Construire un réseau de co-occurrences entre entités
3. Analyser la structure du réseau (centralité, communautés)
4. Produire un dataset annoté réutilisable pour futures recherches

---

## 🧪 Méthodologie

### 1. Collecte et Préparation des Données

**Source** : Corpus de la Société des Nations en Esperanto (voir `DATA_SOURCES.md`)

**Étapes de preprocessing** :
1. **Extraction** : Conversion PDF → texte (si nécessaire)
2. **Nettoyage** :
   - Suppression caractères non-textuels
   - Normalisation Unicode (Esperanto utilise caractères spéciaux : ĉ, ĝ, ĥ, ĵ, ŝ, ŭ)
   - Gestion des ligatures et abréviations historiques
3. **Segmentation** : Découpage en documents/paragraphes selon structure source
4. **Validation** : Vérification encodage et complétude

**Code** : `src/preprocessing/clean_text.py`

**Output** : `data/processed/` (textes nettoyés en UTF-8)

---

### 2. Extraction d'Entités Nommées (NER)

**Approche** : NER **zeroshot** avec GLiNER2

**Justification** :
- Absence de modèles NER pré-entraînés sur Esperanto historique
- GLiNER2 permet définir labels personnalisés sans réentraînement
- Efficace sur textes multilingues peu représentés

**Labels d'entités** (à définir dans `models/configs/labels.yaml`) :
- `PERSON` : Noms de personnes
- `ORGANIZATION` : Organisations, institutions, comités
- `LOCATION` : Lieux, pays, villes
- `EVENT` : Événements historiques, conférences
- `DATE` : Dates et périodes temporelles

**Paramètres GLiNER2** :
- Modèle de base : `urchade/gliner_multi-v2.1` (multilingue)
- Seuil de confiance : 0.5 (ajustable selon précision/rappel)
- Contexte max : 384 tokens

**Pipeline** :
1. Chargement du modèle GLiNER2
2. Extraction entités par document
3. Post-processing :
   - Déduplication des entités identiques
   - Normalisation des variantes (ex: "SDN" → "Société des Nations")
   - Liaison des entités à Wikidata (optionnel)

**Code** : `src/ner/gliner_extractor.py`

**Output** : `data/annotated/` (JSON avec entités + positions + scores)

---

### 3. Validation de la Qualité NER

**Méthode** :
1. **Échantillonnage** : Sélection aléatoire de 100 documents
2. **Annotation manuelle** : Validation humaine des entités extraites
3. **Calcul métriques** :
   - **Précision** : % d'entités correctes parmi celles extraites
   - **Rappel** : % d'entités trouvées parmi celles existantes
   - **F1-score** : Moyenne harmonique précision/rappel
   - **Confusion matrix** : Erreurs par type d'entité

**Code** : `@validateur_donnees` (agent Claude) ou `src/ner/validate_ner.py`

**Seuil de qualité acceptable** : F1 ≥ 0.70 (ajustable selon domaine)

**Output** : `outputs/reports/ner_quality_metrics.csv`

---

### 4. Construction du Réseau d'Entités

**Approche** : Réseau de **co-occurrences**

**Définition** :
- **Nœuds** : Entités extraites (PERSON, ORGANIZATION, LOCATION)
- **Arêtes** : Co-occurrence dans un même document ou paragraphe
- **Poids** : Fréquence de co-occurrence (normalisée)

**Algorithme** :
1. Pour chaque document :
   - Extraire toutes les entités
   - Créer arête entre chaque paire d'entités présentes
   - Incrémenter poids si arête existe déjà
2. Filtrage :
   - Supprimer arêtes avec poids < seuil (ex: 2 co-occurrences minimum)
   - Supprimer nœuds isolés (degré = 0)

**Code** : `src/network/build_network.py`

**Output** : `outputs/networks/entities_network.graphml` (format GraphML pour interopérabilité)

---

### 5. Analyse de Réseau

**Métriques calculées** :

**Niveau global** :
- Nombre de nœuds et d'arêtes
- Densité du réseau
- Coefficient de clustering moyen
- Diamètre et longueur de chemin moyenne

**Niveau nœud** (centralité) :
- **Degré** : Nombre de connexions directes
- **Betweenness** : Nœuds "pont" entre communautés
- **Closeness** : Proximité avec tous les autres nœuds
- **PageRank** : Importance basée sur les connexions

**Détection de communautés** :
- Algorithme de Louvain (modularité)
- Identification de sous-groupes thématiques

**Code** : `src/network/analyze_network.py`

**Output** : `outputs/reports/network_metrics.csv`

---

### 6. Visualisation

**Types de visualisations** :

**Graphes statiques** (Matplotlib/Seaborn) :
- Distribution des degrés (log-log)
- Histogrammes de centralité
- Heatmap de co-occurrences

**Graphes interactifs** (Plotly/Pyvis) :
- Réseau complet avec filtrage dynamique
- Visualisation par communautés (couleurs)
- Tooltips avec informations sur nœuds/arêtes

**Code** : `notebooks/03_network/visualizations.ipynb`

**Output** : `outputs/visualizations/` (PNG, SVG, HTML)

---

## 🔬 Reproductibilité

### Environnement Technique

**Versions fixées** :
- Python 3.10
- GLiNER >= 0.1.0
- NetworkX >= 3.0
- Voir `environment.yml` pour liste complète

**Plateforme** :
- OS : Linux / macOS / Windows
- RAM recommandée : 16 GB
- GPU optionnel (accélération GLiNER2)

**Installation** :
```bash
./init_project.sh
conda activate test-gliner2
```

### Workflow Complet

**Pipeline reproductible** :
```bash
# 1. Preprocessing
python src/preprocessing/clean_text.py --input data/raw/ --output data/processed/

# 2. NER
python src/ner/gliner_extractor.py --input data/processed/ --output data/annotated/

# 3. Validation (optionnel)
python src/ner/validate_ner.py --input data/annotated/ --sample 100

# 4. Construction réseau
python src/network/build_network.py --input data/annotated/ --output outputs/networks/

# 5. Analyse
python src/network/analyze_network.py --input outputs/networks/entities_network.graphml
```

**Ou pipeline automatique** :
```bash
./scripts/run_full_pipeline.sh
```

### Traçabilité

**Gestion de version** :
- Git pour code et documentation
- Commits selon Conventional Commits (`@git_helper`)

**Documentation des choix** :
- Notes de session dans `PROJECT_STATE.md` (`@gardien_projet`)
- Justification des paramètres dans notebooks

**Archivage** :
- Données brutes : conservation originale
- Résultats : sauvegarde versions successives avec timestamps

---

## 📊 Métriques de Succès

**Critères d'évaluation** :

1. **Qualité NER** : F1-score ≥ 0.70
2. **Couverture corpus** : ≥ 95% des documents traités sans erreur
3. **Réseau cohérent** : Communautés identifiables et interprétables
4. **Reproductibilité** : Pipeline exécutable de bout en bout

---

## 🚨 Limites et Biais

**Limites identifiées** :

1. **NER zeroshot** : Moins précis qu'un modèle supervisé entraîné sur Esperanto
2. **Co-occurrences** : Ne capturent pas la nature des relations (positives/négatives)
3. **Biais temporel** : Documents de différentes périodes peuvent avoir vocabulaires différents
4. **Biais linguistique** : GLiNER2 multilingue peut être moins performant sur Esperanto que langues dominantes

**Mitigation** :
- Validation manuelle sur échantillon
- Documentation explicite des choix méthodologiques
- Analyse de sensibilité des paramètres (seuils, fenêtre de co-occurrence)

---

## 📚 Références

**Outils** :
- GLiNER: Zaratiana et al. (2024) - "GLiNER: Generalist Model for Named Entity Recognition"
- NetworkX: Hagberg et al. (2008)
- Louvain: Blondel et al. (2008) - "Fast unfolding of communities in large networks"

**Méthodologie** :
- Co-occurrence networks: Diesner & Carley (2005)
- NER evaluation: Tjong Kim Sang & De Meulder (2003) - CoNLL-2003

**Corpus** :
- Voir `DATA_SOURCES.md` pour références du corpus SDN-Esperanto

---

**Géré par** : `@historien_computationnel` (agent Claude)

**Dernière mise à jour** : 2025-11-16
