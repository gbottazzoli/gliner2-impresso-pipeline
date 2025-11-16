# 🚀 Démarrage Rapide

Bienvenue! Ce template vous permet de créer un projet de recherche complet en 5-20 minutes.

## Étapes

### 1. Choisir Votre Prompt

Deux options:
- **`QUICK_PROMPT.md`** (5-10 min) - Pour projets standards
- **`PROMPT_TEMPLATE.md`** (15-20 min) - Pour projets complexes ou premier usage

**Pas sûr?** Lisez `PROMPTS_INDEX.md`

### 2. Utiliser dans Claude Code

1. Ouvrir le prompt choisi
2. Copier TOUT le contenu
3. Coller dans Claude Code
4. Remplir les informations sur votre projet
5. Claude crée automatiquement la structure complète!

### 3. Ce Qui Sera Créé

- ✅ Structure de dossiers adaptée
- ✅ 11 agents dans `.claude/agents/`
- ✅ Documentation complète
- ✅ Scripts de configuration
- ✅ .gitignore adapté

### 4. Commencer à Travailler

Une fois le setup créé:
```bash
./init_project.sh  # Initialiser l'environnement
@gardien_projet Où en sommes-nous?  # Utiliser les agents
```

## 🤖 Les 11 Agents

Agents créés automatiquement:
1. **gardien_projet** ⭐ - Continuité entre sessions
2. **gestionnaire_contexte** ⭐ - Gestion mémoire
3. **git_helper** - Messages de commit
4. **doc_technique** - Documentation
5. **testeur_code** - Tests unitaires
6. **nettoyeur_projet** - Refactoring
7. **validateur_donnees** - Métriques qualité
8. **architecte_projet** - Structure projet
9. **visualiseur_donnees** - Graphiques
10. **historien_computationnel** - Méthodologie
11. **gestionnaire_environnement** - Docker/dépendances

## 📚 Documentation

- **Guides complets**: `USING_PROMPTS.md`
- **Copier vers autre projet**: `COPIER_NOUVEAU_PROJET.txt`

## ⚡ TL;DR

```bash
cat QUICK_PROMPT.md  # Ouvrir
# Copier dans Claude Code
# Remplir le formulaire
# Claude fait le reste!
```

**Gain de temps**: 2-4h par projet 🎉
