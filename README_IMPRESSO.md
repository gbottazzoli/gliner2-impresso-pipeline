# Intégration Impresso - Recherche Presse Historique SDN

**Date**: 2025-11-20
**Session**: #8 - Phase 11
**Auteur**: Claude Code
**Statut**: ✅ FINALISÉ

---

## Objectif

Rechercher les mentions de 40 acteurs du mouvement Esperanto liés à la Société des Nations (SDN) dans les archives de presse historiques durant la **3ème Assemblée de la SDN** (août-octobre 1922).

---

## Architecture

```
Script 1: Enrichissement Wikidata
↓
personnes_avec_aliases_wikidata.xlsx (40 personnes, 215 alias)
↓
Script 2: Recherche Impresso API
↓
311 articles uniques trouvés
```

---

## Scripts

### Script 1 : `scripts/impresso_1_wikidata_enrichment.py`

**Fonction**: Extraction des alias multilingues depuis Wikidata

**Entrée**: `outputs/person_FINAL_CLEAN.xlsx` (818 personnes)

**Traitement**:
1. Prend les 40 premières personnes
2. Extrait les identifiants Wikidata (ex: Q12571)
3. Interroge l'API Wikidata pour récupérer tous les alias en FR, EN, DE
4. Pour les personnes sans Wikidata: utilise le nom/prénom officiel

**Sortie**: `outputs/personnes_avec_aliases_wikidata.xlsx`
- 40 lignes × 19 colonnes
- 215 alias totaux (FR: 61, EN: 90, DE: 64)
- 26 personnes avec Wikidata ID, 14 sans

**Durée**: ~30 secondes

**Exemple de résultat**:
```
Gilbert Murray (Q538478):
  FR: Gilbert Murray
  EN: G. G. Murray, George Gilbert Murray, Sir Gilbert Murray...
  DE: Gilbert Murray
```

**Commande**:
```bash
python3 scripts/impresso_1_wikidata_enrichment.py
```

---

### Script 2 : `scripts/impresso_2_search_articles.py`

**Fonction**: Recherche dans les archives Impresso

**Entrée**: `outputs/personnes_avec_aliases_wikidata.xlsx`

**Traitement**:
1. Connexion à l'API Impresso (token requis)
2. Pour chaque personne, pour chaque langue, pour chaque alias:
   - Recherche articles entre 1922-08-01 et 1922-10-31
   - Maximum 100 articles par requête
3. Déduplication (un article peut mentionner plusieurs personnes)
4. Génération de rapports statistiques

**Paramètres**:
- **Période**: 1922-08-01 à 1922-10-31 (3 mois)
- **Langues**: FR, EN, DE
- **Limite**: 100 articles par requête
- **Pause**: 0.5s entre requêtes (rate limiting)
- **Checkpoint**: Sauvegarde tous les 5 personnes (reprise possible)

**Sorties**:

1. **`outputs/impresso_resultats_dedupliques.xlsx`** ⭐ FICHIER PRINCIPAL
   - **311 articles uniques**
   - Colonnes: person_entity, person_nom, person_prenom, search_term, search_language, article_id, article_title, article_date, article_language, newspaper_id, newspaper_title, article_url
   - Un article apparaît une seule fois même s'il mentionne plusieurs personnes

2. **`outputs/impresso_resultats_detailles.xlsx`**
   - 339 entrées
   - Trace complète: quel alias a trouvé quel article

3. **`outputs/impresso_search_report.txt`**
   - Statistiques complètes
   - Top personnes, journaux, distribution langues

**Durée**: ~4.7 minutes (219 requêtes)

**Commande**:
```bash
python3 scripts/impresso_2_search_articles.py
```

**Reprise après interruption**:
Le script crée un fichier `.checkpoint_impresso.json`. En cas d'interruption, relancer la commande et répondre "o" pour reprendre.

---

## Résultats

### Statistiques Globales

| Métrique | Valeur |
|----------|--------|
| Personnes recherchées | 40 |
| Alias Wikidata | 215 |
| Requêtes API | 219 |
| **Articles uniques trouvés** | **311** |
| Personnes avec articles | 17 |
| Personnes sans articles | 23 |
| Durée totale | ~5.2 minutes |

### Top 5 Personnes les Plus Mentionnées

1. **Robert Cecil** (Q12702): 105 articles
2. **Henri Bergson** (Q42156): 62 articles
3. **Gilbert Murray** (Q538478): 28 articles
4. **Eric Drummond** (Q335120): 23 articles
5. **De Brouckere** (?): 20 articles

### Distribution par Langue

- 🇫🇷 **Français**: 276 articles (88.7%)
- 🇩🇪 **Allemand**: 35 articles (11.3%)

### Top 5 Journaux

1. **JDG** (Journal de Genève): 73 articles
2. **Le Gaulois**: 34 articles
3. **GDL** (Gazette de Lausanne): 30 articles
4. **indeplux** (L'Indépendance Luxembourgeoise): 27 articles
5. **NZZ** (Neue Zürcher Zeitung): 25 articles

### Personnes SANS Articles (23/40)

Alice Vanderbilt Morris, André Baudet, Claire Richler, Dean Earl B. Babcock, Driesler, Edmund Beecher Wilson, Erich Weferling, Florence Wilson, Frederick G. Donnan, Frederick Gardner Cottrell, Friedrich Schneeberger, H. Fielding, Herbert N. Shenton, Louis Couturat, Louis de Beaufront, Marguerite E. Jones, Otto Jespersen, Ravizza, Samuel Wesley Stratton, Siegfried Auerbach, Vacardesco, Winifred Coombe Tennant, A. Barton Kent

**Raisons possibles**:
- Couverture presse limitée (acteurs moins visibles médiatiquement)
- Période restreinte (3 mois seulement)
- Couverture géographique (presse suisse/luxembourgeoise principalement)
- Base de données Impresso ne contient pas tous les journaux

---

## Prérequis

### Dépendances Python

Ajoutées dans `environment.yml`:
```yaml
- pip:
  - impresso       # API Impresso
  - requests>=2.31.0  # API Wikidata
  - python-dotenv>=1.0.0  # Variables environnement
```

Installation:
```bash
pip install impresso requests python-dotenv
```

### Token API Impresso

1. Créer un compte sur https://impresso-project.ch/datalab/
2. Obtenir un token API: https://impresso-project.ch/datalab/token
3. Le token sera demandé au premier lancement et sauvegardé

---

## Utilisation

### Workflow Complet

```bash
# 1. Enrichissement Wikidata (30s)
python3 scripts/impresso_1_wikidata_enrichment.py

# 2. Recherche Impresso (4.7 min)
python3 scripts/impresso_2_search_articles.py
```

### Test sur 3 Personnes

```bash
# Version TEST déjà créée (Privat, Murray, Nitobe)
python3 scripts/impresso_2_search_articles_TEST.py
```

### Modification des Paramètres

Dans `scripts/impresso_2_search_articles.py`:

```python
# Changer la période
DATE_DEBUT = "1922-08-01"
DATE_FIN = "1922-10-31"

# Changer le nombre de résultats max par requête
MAX_RESULTATS = 100

# Changer la pause entre requêtes (rate limiting)
PAUSE_API = 0.5  # secondes
```

---

## Interprétation des Résultats

### Fichier Principal: `impresso_resultats_dedupliques.xlsx`

**Colonnes**:
- `person_entity`: Identifiant personne (ex: "Robert Cecil (Q12702)")
- `person_nom`, `person_prenom`: Nom/prénom
- `search_term`: Alias ayant trouvé l'article
- `search_language`: Langue de recherche (fr/en/de)
- `article_id`: Identifiant unique article
- `article_title`: Titre article (peut être vide)
- `article_date`: Date publication (format ISO)
- `article_language`: Langue article
- `newspaper_id`: Code journal (ex: "JDG")
- `newspaper_title`: Nom journal (souvent = newspaper_id)
- `article_url`: Lien Impresso App (ex: https://impresso-project.ch/app/article/JDG-1922-09-05-a-i0012)

**Utilisation**:
- Filtrer par personne pour voir sa couverture médiatique
- Filtrer par journal pour analyser la ligne éditoriale
- Trier par date pour voir l'évolution temporelle
- Compter les mentions pour mesurer la visibilité

---

## Analyse Possible

### Questions de Recherche

1. **Visibilité médiatique**: Quels acteurs Esperanto-SDN étaient les plus visibles dans la presse ?
2. **Couverture temporelle**: Évolution des mentions avant/pendant/après l'Assemblée ?
3. **Couverture géographique**: Différences entre presse française et allemande ?
4. **Thématiques**: Quels sujets associés aux mentions (utiliser article_title) ?
5. **Réseaux**: Quels acteurs sont co-mentionnés dans les mêmes articles ?

### Outils Recommandés

- **Excel/LibreOffice**: Analyse basique, filtres, tableaux croisés dynamiques
- **Python pandas**: Analyses statistiques avancées
- **Voyant Tools**: Analyse textuelle des titres
- **Impresso Web App**: Lecture articles complets (cliquer sur article_url)

---

## Limitations

1. **Couverture géographique**: Principalement presse suisse/luxembourgeoise
2. **Période limitée**: 3 mois (août-oct 1922)
3. **Langues**: FR et DE principalement (pas d'anglais dans cette base)
4. **Complétude**: Tous les journaux de l'époque ne sont pas numérisés
5. **OCR**: Qualité variable selon l'état des documents originaux
6. **Titres**: Souvent absents ou incomplets (snippet non disponible)

---

## Extension Possible

### Élargir la Recherche

Pour trouver les 23 personnes sans articles:

1. **Période étendue**:
   ```python
   DATE_DEBUT = "1921-01-01"
   DATE_FIN = "1923-12-31"
   ```

2. **Recherche par organisation**:
   - Ajouter "Société des Nations", "League of Nations", etc.

3. **Recherche par rôle**:
   - Ajouter "secrétaire", "délégué", etc.

### Analyses Complémentaires

1. **Analyse réseau**: Co-occurrences personnes dans mêmes articles
2. **Timeline**: Visualisation temporelle des mentions
3. **Topic modeling**: Extraction thématiques automatique
4. **Comparaison corpus**: Mentions SDN vs corpus Esperanto global

---

## Fichiers Générés

```
outputs/
├── personnes_avec_aliases_wikidata.xlsx        # 40 personnes + alias (17KB)
├── impresso_resultats_dedupliques.xlsx         # 311 articles uniques (34KB) ⭐
├── impresso_resultats_detailles.xlsx           # 339 entrées trace (35KB)
└── impresso_search_report.txt                  # Rapport statistique (2KB)

.checkpoint_impresso.json                        # Fichier checkpoint (temporaire)
```

---

## Références

- **Impresso Project**: https://impresso-project.ch/
- **Impresso API Documentation**: https://impresso.github.io/impresso-py/
- **Wikidata**: https://www.wikidata.org/
- **Impresso Web App**: https://impresso-project.ch/app/

---

## Support

Pour toute question sur l'utilisation des scripts ou l'interprétation des résultats, consulter:
- Ce README
- Les commentaires dans les scripts Python
- La documentation Impresso officielle

---

**Dernière mise à jour**: 2025-11-20
**Version**: 1.0
**Licence**: Projet recherche académique
