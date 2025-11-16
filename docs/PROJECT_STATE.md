# 📊 PROJECT STATE - test-gliner2

**Dernière mise à jour** : 2025-11-16
**Géré par** : `@gardien_projet` (agent Claude)

---

## 🎯 Objectif du Projet

Extraction d'entités nommées (NER) via GLiNER2 sur corpus historique en Esperanto de la Société des Nations, pour analyse de réseau des acteurs et organisations.

---

## 📈 État Actuel

**Phase** : 🟢 Setup initial complet

**Statut global** : Projet initialisé, prêt à démarrer les travaux de recherche.

---

## ✅ Complété

### Setup Infrastructure
- [x] Structure de dossiers créée
- [x] Environnement conda configuré (`environment.yml`)
- [x] .gitignore adapté au projet
- [x] Documentation de base (README, METHODOLOGY, DATA_SOURCES, AGENTS_GUIDE)
- [x] 11 agents Claude installés dans `.claude/agents/`
- [x] Scripts d'initialisation créés

---

## 🚧 En Cours

**Rien pour le moment** - En attente du démarrage des travaux de recherche.

---

## 📋 À Faire (Prochaines Étapes)

### Phase 1 : Préparation des Données
- [ ] Obtenir le corpus SDN-Esperanto (placer dans `data/raw/`)
- [ ] Initialiser l'environnement conda (`./init_project.sh`)
- [ ] Télécharger le modèle GLiNER2 (`./scripts/download_models.sh`)
- [ ] Explorer le corpus (notebook `01_exploration/`)

### Phase 2 : Preprocessing
- [ ] Développer script de nettoyage texte (`src/preprocessing/clean_text.py`)
- [ ] Normaliser les textes Esperanto
- [ ] Exporter textes nettoyés dans `data/processed/`
- [ ] Tests unitaires du preprocessing

### Phase 3 : Extraction NER
- [ ] Configurer GLiNER2 (définir labels d'entités dans `models/configs/`)
- [ ] Développer script d'extraction NER (`src/ner/gliner_extractor.py`)
- [ ] Lancer extraction sur corpus complet
- [ ] Valider qualité avec `@validateur_donnees` (métriques F1, précision, rappel)

### Phase 4 : Analyse de Réseau
- [ ] Construire graphe d'entités (`src/network/build_network.py`)
- [ ] Analyse de centralité, communautés, etc.
- [ ] Visualisations interactives (Pyvis, Plotly)
- [ ] Exporter graphes (GraphML, CSV)

### Phase 5 : Finalisation
- [ ] Rédiger rapport méthodologique complet
- [ ] Créer visualisations finales pour publication
- [ ] Tests complets de reproductibilité
- [ ] Archivage et documentation finale

---

## 🐛 Problèmes Connus

**Aucun pour le moment**

---

## 📝 Notes de Session

### Session 2025-11-16 - Setup Initial

**Réalisé** :
- Création automatique de la structure complète du projet
- Configuration environnement conda avec toutes dépendances (GLiNER, NetworkX, etc.)
- Documentation de base créée
- Scripts d'initialisation prêts

**Décisions** :
- Utilisation de conda (préférence utilisateur)
- GLiNER2 pour NER zeroshot (pas besoin de modèle supervisé pré-entraîné sur Esperanto)
- NetworkX pour analyse de réseau (standard en Python)

**Prochaine session** :
- Obtenir le corpus SDN-Esperanto
- Lancer `./init_project.sh` pour initialiser l'environnement
- Commencer exploration du corpus

---

## 🔗 Liens Utiles

- **README principal** : `../README.md`
- **Méthodologie** : `METHODOLOGY.md`
- **Sources de données** : `DATA_SOURCES.md`
- **Guide des agents** : `AGENTS_GUIDE.md`

---

## 💡 Utilisation

Ce fichier est automatiquement mis à jour par l'agent `@gardien_projet`.

**Commandes utiles** :
```bash
# Consulter l'état actuel
@gardien_projet Où en sommes-nous ?

# Marquer une tâche comme complétée
@gardien_projet J'ai terminé l'exploration du corpus

# Ajouter une note de session
@gardien_projet Note : problème d'encodage dans certains fichiers raw
```

---

**Dernière révision par** : Claude Code (Setup automatique)
