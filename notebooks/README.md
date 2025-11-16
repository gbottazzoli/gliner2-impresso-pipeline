# 📓 notebooks/

**Jupyter Notebooks pour exploration et analyse**

Notebooks organisés en 3 phases : exploration, NER, et analyse de réseau.

---

## Structure

```
notebooks/
├── 01_exploration/    # EDA du corpus Esperanto
├── 02_ner/            # Tests et tuning GLiNER2
└── 03_network/        # Visualisation et analyse de réseau
```

---

## 📁 Sous-dossiers

### `01_exploration/`
**Objectif** : Exploration initiale du corpus

**Notebooks suggérés** :
- `corpus_statistics.ipynb` - Stats de base (nb docs, mots, vocabulaire)
- `text_quality.ipynb` - Vérification encodage, caractères Esperanto
- `temporal_analysis.ipynb` - Distribution temporelle des documents

### `02_ner/`
**Objectif** : Expérimentation et validation NER avec GLiNER2

**Notebooks suggérés** :
- `gliner_testing.ipynb` - Tests sur exemples, tuning threshold
- `ner_validation.ipynb` - Validation manuelle, calcul F1-score
- `error_analysis.ipynb` - Analyse des erreurs NER par type

### `03_network/`
**Objectif** : Visualisation et analyse du réseau d'entités

**Notebooks suggérés** :
- `network_visualization.ipynb` - Graphes statiques et interactifs
- `network_metrics.ipynb` - Centralité, communautés, statistiques
- `entity_analysis.ipynb` - Focus sur entités clés

---

## 🚀 Lancement

```bash
# Activer l'environnement
conda activate test-gliner2

# Lancer Jupyter Lab
jupyter lab

# Ou Jupyter Notebook classique
jupyter notebook
```

---

## 🎨 Visualisations

**Bibliothèques disponibles** :
- Matplotlib, Seaborn (graphiques statiques)
- Plotly (graphiques interactifs)
- Pyvis (réseaux interactifs HTML)
- NetworkX (graphes)

**Conseil** : Utilisez `@visualiseur_donnees` pour créer des visualisations

---

## 📝 Bonnes Pratiques

1. **Nommage clair** : `01_task_name.ipynb` (numérotation pour ordre)
2. **Documentation** : Markdown cells pour expliquer chaque étape
3. **Reproductibilité** : Fixer random seeds, documenter paramètres
4. **Sauvegarde** : Exporter figures dans `outputs/visualizations/`
5. **Nettoyage** : Clear outputs avant commit Git

---

## 🤖 Agents Utiles

```bash
@visualiseur_donnees Crée un graphe de réseau dans le notebook actuel
@validateur_donnees Calcule F1-score pour résultats NER
```

---

**Voir aussi** : `docs/METHODOLOGY.md` pour méthodologie complète
