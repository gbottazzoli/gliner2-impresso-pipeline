# 📤 outputs/

**Résultats du projet (NER, réseaux, visualisations, rapports)**

Ce dossier contient tous les résultats produits par le projet. **Partiellement git-ignored** (fichiers volumineux).

---

## Structure

```
outputs/
├── ner_results/      # Entités extraites par document
├── networks/         # Graphes générés (GraphML, CSV)
├── visualizations/   # Figures PNG/SVG/HTML
└── reports/          # Métriques de qualité, statistiques
```

---

## 📁 Sous-dossiers

### `ner_results/`
**Contenu** : Résultats NER détaillés par document

**Généré par** : `src/ner/gliner_extractor.py`

**Format** : JSON (un fichier par document)

**Git-ignored** : OUI

**Exemple** : `SDN_ESP_1925_042_entities.json`

### `networks/`
**Contenu** : Graphes de co-occurrences d'entités

**Généré par** : `src/network/build_network.py`

**Fichiers** :
- `entities_network.graphml` - Graphe complet (format GraphML)
- `entities_edgelist.csv` - Liste d'arêtes (CSV)
- `entities_nodes.csv` - Liste de nœuds avec attributs

**Git-ignored** : OUI

### `visualizations/`
**Contenu** : Figures et graphiques

**Généré par** : Notebooks dans `notebooks/03_network/` ou `@visualiseur_donnees`

**Formats** : PNG, SVG, PDF, HTML (interactifs)

**Git-ignored** : Fichiers images (.png, .svg, .pdf) ignorés, HTML conservés

**Types de visualisations** :
- Graphes de réseau (statiques et interactifs)
- Histogrammes (types d'entités, scores)
- Heatmaps (co-occurrences)
- Courbes (métriques de qualité)

### `reports/`
**Contenu** : Rapports de métriques et statistiques

**Généré par** : `src/ner/validate_ner.py`, `src/network/analyze_network.py`, ou `@validateur_donnees`

**Fichiers** :
- `ner_quality_metrics.csv` - F1, précision, rappel par type d'entité
- `network_metrics.csv` - Centralité, clustering, etc.
- `corpus_statistics.json` - Stats globales du corpus

**Git-ignored** : NON (fichiers légers, importants pour reproductibilité)

---

## 📊 Exemples de Fichiers

### `ner_quality_metrics.csv`
```csv
entity_type,precision,recall,f1_score,count
PERSON,0.82,0.75,0.78,145
ORGANIZATION,0.79,0.71,0.75,98
LOCATION,0.88,0.83,0.85,112
```

### `network_metrics.csv`
```csv
entity,degree,betweenness,closeness,pagerank,community
Ĝenevo,45,0.12,0.78,0.05,1
Ligo de Nacioj,89,0.25,0.92,0.12,1
Eŭropo,34,0.08,0.65,0.03,1
```

---

## 🔄 Workflow

```bash
# 1. NER
python src/ner/gliner_extractor.py
# → Génère outputs/ner_results/

# 2. Validation
python src/ner/validate_ner.py
# → Génère outputs/reports/ner_quality_metrics.csv

# 3. Réseau
python src/network/build_network.py
# → Génère outputs/networks/

# 4. Analyse
python src/network/analyze_network.py
# → Génère outputs/reports/network_metrics.csv

# 5. Visualisation
jupyter lab notebooks/03_network/
# → Génère outputs/visualizations/
```

---

## 💾 Sauvegarde

**Recommandations** :
- Sauvegarder régulièrement `reports/` (légers, critiques)
- Archiver `networks/` après analyses finalisées
- `ner_results/` peut être régénéré depuis `data/annotated/`

---

## 📝 TODO

- [ ] Configurer .gitkeep dans chaque sous-dossier pour préserver structure
- [ ] Documenter format exact des fichiers générés
- [ ] Créer scripts de sauvegarde automatique

---

**Voir aussi** : `docs/METHODOLOGY.md` pour détails sur métriques calculées
