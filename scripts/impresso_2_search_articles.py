#!/usr/bin/env python3
"""
Script 2: Recherche dans Impresso

Objectif: Rechercher les mentions des 40 personnes enrichies dans les archives
Impresso pendant la 3ème Assemblée de la Société des Nations (août-octobre 1922)

Auteur: Claude Code
Date: 2025-11-20
Projet: Recherche Impresso - 3ème Assemblée SDN
"""

import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from impresso import connect, DateRange
from tqdm import tqdm

# ============================================
# CONFIGURATION
# ============================================

# Chemins des fichiers
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / "outputs" / "personnes_avec_aliases_wikidata.xlsx"
OUTPUT_DETAILED = PROJECT_ROOT / "outputs" / "impresso_resultats_detailles.xlsx"
OUTPUT_DEDUPLICATED = PROJECT_ROOT / "outputs" / "impresso_resultats_dedupliques.xlsx"
OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "impresso_search_report.txt"
CHECKPOINT_FILE = PROJECT_ROOT / ".checkpoint_impresso.json"

# Période de recherche: 3ème Assemblée SDN
DATE_DEBUT = "1922-08-01"
DATE_FIN = "1922-10-31"

# Paramètres
LANGUES = ["fr", "en", "de"]
PAUSE_API = 0.5  # Secondes entre chaque requête Impresso
MAX_RESULTATS = 100  # Limite par requête
CHECKPOINT_FREQ = 5  # Sauvegarder tous les N personnes


# ============================================
# PRÉPARATION DES DONNÉES
# ============================================

def parser_aliases(texte_aliases: str) -> List[str]:
    """
    Convertit 'alias1, alias2, alias3' en ['alias1', 'alias2', 'alias3']
    Filtre les alias trop courts (< 3 caractères)
    """
    if pd.isna(texte_aliases) or not isinstance(texte_aliases, str) or not texte_aliases.strip():
        return []

    # Séparer par les virgules
    liste = [alias.strip() for alias in texte_aliases.split(',')]

    # Nettoyer et filtrer
    liste_nettoyee = []
    for alias in liste:
        if alias and len(alias) >= 3:  # Éviter les alias trop courts
            liste_nettoyee.append(alias)

    return liste_nettoyee


def preparer_donnees_recherche(df: pd.DataFrame) -> List[Dict]:
    """
    Prépare une structure de données optimisée pour la recherche
    """
    personnes_enrichies = []

    for idx, row in df.iterrows():
        personne = {
            "index": idx,
            "entity": row["entity_normalized"],
            "nom": row.get("Nom", ""),
            "prenom": row.get("Prénom", ""),
            "wikidata_id": row.get("wikidata_id", None),
            "aliases_par_langue": {}
        }

        # Parser les alias pour chaque langue
        for langue in LANGUES:
            colonne = f"aliases_wikidata_{langue}"
            if colonne in row:
                texte_aliases = row[colonne]
                personne["aliases_par_langue"][langue] = parser_aliases(texte_aliases)
            else:
                personne["aliases_par_langue"][langue] = []

        personnes_enrichies.append(personne)

    return personnes_enrichies


# ============================================
# RECHERCHE IMPRESSO
# ============================================

def rechercher_articles_impresso(client, terme_recherche: str, date_debut: str, date_fin: str) -> List[Dict]:
    """
    Recherche des articles dans Impresso

    Args:
        client: Client Impresso connecté
        terme_recherche: Terme à rechercher
        date_debut: Date de début (format: YYYY-MM-DD)
        date_fin: Date de fin (format: YYYY-MM-DD)

    Returns:
        Liste de dictionnaires contenant les informations des articles
    """
    try:
        # Rechercher dans Impresso avec DateRange
        # Syntaxe basée sur la documentation officielle
        search_results = client.search.find(
            term=terme_recherche,
            date_range=DateRange(date_debut, date_fin),
            limit=MAX_RESULTATS,
            with_text_contents=True
        )

        articles = []

        # Accéder au DataFrame contenant les résultats
        if not hasattr(search_results, 'df'):
            return articles

        df = search_results.df

        # Vérifier qu'il y a des résultats
        if df.empty:
            return articles

        # Convertir chaque ligne du DataFrame en dictionnaire
        for idx, row in df.iterrows():
            try:
                # idx contient le uid de l'article
                article_id = idx if isinstance(idx, str) else str(idx)

                # Extraire les informations
                # Note: certains champs peuvent être NaN, on les convertit en chaînes vides
                article = {
                    "id": article_id,
                    "title": str(row.get('title', '')) if pd.notna(row.get('title')) else '',
                    "date": str(row.get('publicationDate', '')) if pd.notna(row.get('publicationDate')) else '',
                    "language": str(row.get('languageCode', '')) if pd.notna(row.get('languageCode')) else '',
                    "newspaper_id": str(row.get('mediaUid', '')) if pd.notna(row.get('mediaUid')) else '',
                    "newspaper_title": str(row.get('mediaUid', '')) if pd.notna(row.get('mediaUid')) else '',  # Utiliser mediaUid comme titre par défaut
                    "url": f"https://impresso-project.ch/app/article/{article_id}",
                    "snippet": ""  # Le snippet n'est pas dans les résultats de recherche basique
                }
                articles.append(article)
            except Exception as e:
                print(f"        ⚠️  Erreur extraction article: {e}")
                continue

        return articles

    except Exception as e:
        print(f"        ❌ Erreur recherche: {e}")
        return []


# ============================================
# CHECKPOINT / RESUME
# ============================================

def sauvegarder_checkpoint(personnes_traitees: int, resultats: List[Dict]):
    """Sauvegarde l'état actuel dans un fichier checkpoint"""
    checkpoint_data = {
        "personnes_traitees": personnes_traitees,
        "timestamp": datetime.now().isoformat(),
        "nb_resultats": len(resultats)
    }
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2)


def charger_checkpoint() -> Optional[Dict]:
    """Charge le dernier checkpoint s'il existe"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    return None


def nettoyer_checkpoint():
    """Supprime le fichier checkpoint"""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


# ============================================
# DÉDUPLICATION
# ============================================

def dedupliquer_resultats(resultats: List[Dict]) -> List[Dict]:
    """
    Supprime les doublons (même article trouvé avec plusieurs alias)
    Garde la première occurrence de chaque article unique
    """
    articles_uniques = {}

    for resultat in resultats:
        article_id = resultat["article_id"]

        # Si on n'a pas encore vu cet article, on le garde
        if article_id not in articles_uniques:
            articles_uniques[article_id] = resultat

    return list(articles_uniques.values())


# ============================================
# GÉNÉRATION DE RAPPORT
# ============================================

def generer_rapport(personnes: List[Dict], resultats_detailles: List[Dict],
                   resultats_dedupliques: List[Dict], duree: float):
    """Génère un rapport statistique de la recherche"""

    rapport_lines = []
    rapport_lines.append("=" * 80)
    rapport_lines.append("RAPPORT DE RECHERCHE IMPRESSO")
    rapport_lines.append("3ème Assemblée de la Société des Nations (Août-Octobre 1922)")
    rapport_lines.append("=" * 80)
    rapport_lines.append("")

    rapport_lines.append(f"Date de recherche: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rapport_lines.append(f"Période couverte: {DATE_DEBUT} à {DATE_FIN}")
    rapport_lines.append(f"Durée du traitement: {duree/60:.1f} minutes")
    rapport_lines.append("")

    rapport_lines.append("=" * 80)
    rapport_lines.append("STATISTIQUES GÉNÉRALES")
    rapport_lines.append("=" * 80)
    rapport_lines.append(f"Personnes recherchées: {len(personnes)}")

    # Compter le total d'alias
    total_aliases = sum(
        len(p["aliases_par_langue"][lang])
        for p in personnes
        for lang in LANGUES
    )
    rapport_lines.append(f"Total d'alias recherchés: {total_aliases}")
    rapport_lines.append(f"Résultats détaillés (avec doublons): {len(resultats_detailles)}")
    rapport_lines.append(f"Résultats uniques (dédupliqués): {len(resultats_dedupliques)}")
    rapport_lines.append("")

    # Répartition par langue
    if resultats_dedupliques:
        df = pd.DataFrame(resultats_dedupliques)

        rapport_lines.append("=" * 80)
        rapport_lines.append("RÉPARTITION PAR LANGUE D'ARTICLE")
        rapport_lines.append("=" * 80)
        lang_counts = df['article_language'].value_counts()
        for lang, count in lang_counts.items():
            rapport_lines.append(f"  {lang}: {count} articles ({count/len(df)*100:.1f}%)")
        rapport_lines.append("")

        # Top journaux
        rapport_lines.append("=" * 80)
        rapport_lines.append("TOP 10 JOURNAUX")
        rapport_lines.append("=" * 80)
        newspaper_counts = df['newspaper_title'].value_counts().head(10)
        for newspaper, count in newspaper_counts.items():
            rapport_lines.append(f"  {newspaper}: {count} articles")
        rapport_lines.append("")

        # Top personnes mentionnées
        rapport_lines.append("=" * 80)
        rapport_lines.append("TOP 15 PERSONNES LES PLUS MENTIONNÉES")
        rapport_lines.append("=" * 80)
        person_counts = df['person_entity'].value_counts().head(15)
        for person, count in person_counts.items():
            rapport_lines.append(f"  {person}: {count} articles")
        rapport_lines.append("")

    # Sauvegarder le rapport
    rapport_text = "\n".join(rapport_lines)

    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        f.write(rapport_text)

    print("\n" + rapport_text)


# ============================================
# PROCEDURE PRINCIPALE
# ============================================

def main():
    """Fonction principale du script"""

    print("=" * 80)
    print("SCRIPT 2 : RECHERCHE IMPRESSO")
    print("=" * 80)
    print(f"Période: {DATE_DEBUT} à {DATE_FIN}")
    print(f"Événement: 3ème Assemblée de la Société des Nations")
    print()

    temps_debut = time.time()

    # ========================================
    # ÉTAPE 1 : CHARGER LES DONNÉES
    # ========================================
    print("📂 Chargement des données enrichies...")

    if not INPUT_FILE.exists():
        print(f"❌ ERREUR: Fichier non trouvé: {INPUT_FILE}")
        print("   Veuillez d'abord exécuter le Script 1")
        return

    df = pd.read_excel(INPUT_FILE)
    print(f"✅ {len(df)} personnes chargées")

    # ========================================
    # ÉTAPE 2 : PRÉPARER LES DONNÉES
    # ========================================
    print("\n📝 Préparation des données de recherche...")
    personnes = preparer_donnees_recherche(df)

    # Statistiques sur les alias
    total_requetes = sum(
        len(p["aliases_par_langue"][lang])
        for p in personnes
        for lang in LANGUES
    )

    print(f"✅ Données préparées")
    print(f"   Nombre total de requêtes estimé: {total_requetes}")
    print(f"   Temps estimé: {total_requetes * PAUSE_API / 60:.1f} minutes")

    # ========================================
    # ÉTAPE 3 : CONNEXION À IMPRESSO
    # ========================================
    print("\n🔌 Connexion à l'API Impresso...")
    print("   (Un token vous sera demandé si nécessaire)")

    try:
        client = connect(persisted_token=True)
        print("✅ Connecté à Impresso")
    except Exception as e:
        print(f"❌ ERREUR de connexion: {e}")
        print("   Assurez-vous d'avoir un compte Impresso et un token valide")
        return

    # ========================================
    # ÉTAPE 4 : CHECKPOINT
    # ========================================
    checkpoint = charger_checkpoint()
    index_debut = 0

    if checkpoint:
        print(f"\n📌 Checkpoint trouvé: {checkpoint['personnes_traitees']} personnes déjà traitées")
        reponse = input("Reprendre depuis le checkpoint? (o/n): ")
        if reponse.lower() == 'o':
            index_debut = checkpoint['personnes_traitees']
            print(f"✅ Reprise à partir de la personne {index_debut + 1}")

    # ========================================
    # ÉTAPE 5 : RECHERCHE
    # ========================================
    print("\n🔍 Recherche dans Impresso...")
    print()

    # Structure pour stocker tous les résultats
    tous_les_resultats = []

    # Compteurs pour les statistiques
    compteur_requetes = 0
    compteur_articles_total = 0

    # Barre de progression
    for personne in tqdm(personnes[index_debut:], desc="Traitement", initial=index_debut, total=len(personnes)):
        idx = personne["index"]
        nom_complet = f"{personne['prenom']} {personne['nom']}".strip()

        print(f"\n[{idx+1}/{len(personnes)}] {nom_complet}")

        # Dictionnaire pour stocker les articles uniques de cette personne
        articles_personne = {}

        # Rechercher dans chaque langue
        for langue in LANGUES:
            aliases = personne["aliases_par_langue"][langue]

            if not aliases:
                continue

            print(f"  📖 {langue.upper()} ({len(aliases)} alias)")

            # Rechercher avec chaque alias
            for alias in aliases:
                compteur_requetes += 1

                # Rechercher dans Impresso
                articles = rechercher_articles_impresso(
                    client,
                    alias,
                    DATE_DEBUT,
                    DATE_FIN
                )

                print(f"     '{alias}': {len(articles)} articles")

                # Ajouter les articles trouvés (sans doublons pour cette personne)
                for article in articles:
                    article_id = article["id"]

                    # Si c'est un nouvel article, l'ajouter
                    if article_id and article_id not in articles_personne:
                        # Créer l'entrée complète
                        resultat = {
                            "person_entity": personne["entity"],
                            "person_nom": personne["nom"],
                            "person_prenom": personne["prenom"],
                            "search_term": alias,
                            "search_language": langue,
                            "article_id": article["id"],
                            "article_title": article["title"],
                            "article_date": article["date"],
                            "article_language": article["language"],
                            "newspaper_id": article["newspaper_id"],
                            "newspaper_title": article["newspaper_title"],
                            "article_url": article["url"],
                            "article_snippet": article["snippet"]
                        }

                        articles_personne[article_id] = resultat
                        compteur_articles_total += 1

                # Pause pour respecter le rate limit
                time.sleep(PAUSE_API)

        # Ajouter tous les articles de cette personne
        for article in articles_personne.values():
            tous_les_resultats.append(article)

        nb_articles_personne = len(articles_personne)
        print(f"  ✅ Total pour cette personne: {nb_articles_personne} articles uniques")

        # Checkpoint tous les N personnes
        if (idx + 1) % CHECKPOINT_FREQ == 0:
            sauvegarder_checkpoint(idx + 1, tous_les_resultats)
            print(f"  💾 Checkpoint sauvegardé")

    # ========================================
    # ÉTAPE 6 : SAUVEGARDER LES RÉSULTATS
    # ========================================
    print("\n" + "=" * 80)
    print("SAUVEGARDE DES RÉSULTATS")
    print("=" * 80)

    if tous_les_resultats:
        # Fichier détaillé (avec tous les résultats)
        df_detailles = pd.DataFrame(tous_les_resultats)
        df_detailles.to_excel(OUTPUT_DETAILED, index=False)
        print(f"✅ Résultats détaillés: {OUTPUT_DETAILED}")
        print(f"   {len(df_detailles)} entrées")

        # Fichier dédupliqué (articles uniques)
        resultats_dedupliques = dedupliquer_resultats(tous_les_resultats)
        df_dedupliques = pd.DataFrame(resultats_dedupliques)
        df_dedupliques.to_excel(OUTPUT_DEDUPLICATED, index=False)
        print(f"✅ Résultats dédupliqués: {OUTPUT_DEDUPLICATED}")
        print(f"   {len(df_dedupliques)} articles uniques")

        # Générer le rapport
        duree = time.time() - temps_debut
        generer_rapport(personnes, tous_les_resultats, resultats_dedupliques, duree)
        print(f"✅ Rapport statistique: {OUTPUT_REPORT}")

    else:
        print("⚠️  Aucun résultat trouvé")

    # Nettoyer le checkpoint
    nettoyer_checkpoint()

    print("\n" + "=" * 80)
    print("✅ TRAITEMENT TERMINÉ")
    print("=" * 80)


if __name__ == "__main__":
    main()
