# 📊 data/

**Dossier de données du projet test-gliner2**

Ce dossier contient toutes les données du projet à différents stades de traitement. **Important** : Les fichiers dans ce dossier sont git-ignored pour éviter de versionner des données volumineuses.

---

## Structure

```
data/
├── raw/          # Corpus brut (textes originaux SDN-Esperanto)
├── processed/    # Textes nettoyés et normalisés
├── annotated/    # Résultats NER (entités extraites avec GLiNER2)
└── network/      # Données pour construction de graphes
```

---

## 📁 Sous-dossiers

### `raw/`
**Contenu** : Corpus brut en Esperanto de la Société des Nations

**Format attendu** : TXT, PDF, ou autre format source

**Instructions** :
- Placez ici vos fichiers sources non modifiés
- Conservez toujours les originaux intacts
- Ajoutez un fichier `metadata.csv` avec informations sur chaque document (date, auteur, type)

**Exemple de structure** :
```
raw/
├── SDN_ESP_1925_042.txt
├── SDN_ESP_1926_013.pdf
├── ...
└── metadata.csv
```

### `processed/`
**Contenu** : Textes nettoyés et normalisés en UTF-8

**Généré par** : `src/preprocessing/clean_text.py`

**Transformations appliquées** :
- Normalisation Unicode (caractères Esperanto : ĉ, ĝ, ĥ, ĵ, ŝ, ŭ)
- Suppression caractères non-textuels
- Segmentation en unités logiques

**Format** : TXT (UTF-8)

### `annotated/`
**Contenu** : Entités nommées extraites par GLiNER2

**Généré par** : `src/ner/gliner_extractor.py`

**Format** : JSON (un fichier par document source)

**Structure JSON** :
```json
{
  "doc_id": "SDN_ESP_1925_042",
  "entities": [
    {
      "text": "Ĝenevo",
      "label": "LOCATION",
      "start": 42,
      "end": 48,
      "confidence": 0.95
    },
    ...
  ]
}
```

**Agrégation** : `entities_all.csv` (table complète de toutes les entités)

### `network/`
**Contenu** : Données préparées pour analyse de réseau

**Généré par** : `src/network/build_network.py`

**Fichiers** :
- `entities_list.csv` - Liste unique des entités (nœuds)
- `cooccurrences.csv` - Paires d'entités avec poids (arêtes)

**Format `cooccurrences.csv`** :
```csv
entity1,entity2,weight
Ĝenevo,Ligo de Nacioj,15
Ligo de Nacioj,Eŭropo,8
...
```

---

## 🚨 Gestion des Données

### Git et Versionning

**Git-ignored** : OUI (voir `.gitignore`)

**Raison** : Éviter de versionner des données volumineuses ou sensibles

**Exception** : Les README.md dans chaque sous-dossier sont versionnés

### Sauvegarde

**Recommandations** :
- Conservez une copie de sauvegarde de `raw/` (originaux)
- Sauvegardez régulièrement `processed/` et `annotated/` (résultats intermédiaires)
- Utilisez un service de stockage externe (serveur, cloud) pour archivage long terme

### Reproductibilité

**Traçabilité** :
- `data/processed/processing_log.json` - Log des transformations appliquées
- Métadonnées préservées à chaque étape

---

## 📝 TODO

- [ ] Obtenir le corpus SDN-Esperanto
- [ ] Placer les fichiers dans `raw/`
- [ ] Créer `metadata.csv` avec infos sur chaque document
- [ ] Lancer preprocessing (`src/preprocessing/clean_text.py`)
- [ ] Vérifier qualité des textes nettoyés dans `processed/`

---

**Voir aussi** : `docs/DATA_SOURCES.md` pour description détaillée du corpus
