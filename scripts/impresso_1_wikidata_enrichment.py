#!/usr/bin/env python3
"""
Script 1: Enrichissement avec Wikidata

Objectif: Extraire les IDs Wikidata et récupérer tous les alias en FR, EN, DE
pour les 40 premières personnes de person_FINAL_CLEAN.xlsx

Auteur: Claude Code
Date: 2025-11-20
Projet: Recherche Impresso - 3ème Assemblée SDN
"""

import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests
from tqdm import tqdm

# ============================================
# CONFIGURATION
# ============================================

# Chemins des fichiers
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_FILE = PROJECT_ROOT / "outputs" / "person_FINAL_CLEAN.xlsx"
OUTPUT_FILE = PROJECT_ROOT / "outputs" / "personnes_avec_aliases_wikidata.xlsx"
CHECKPOINT_FILE = PROJECT_ROOT / ".checkpoint_wikidata.json"

# Paramètres
NOMBRE_PERSONNES = 40
LANGUES = ["fr", "en", "de"]
PAUSE_API = 0.3  # Secondes entre chaque requête Wikidata
TIMEOUT_API = 10  # Timeout pour les requêtes HTTP

# User-Agent requis par Wikidata
# Voir: https://meta.wikimedia.org/wiki/User-Agent_policy
HEADERS = {
    'User-Agent': 'ImPressoResearchBot/1.0 (SDN-Esperanto Research Project; steeven@example.com) Python/requests'
}


# ============================================
# EXTRACTION ID WIKIDATA
# ============================================

def extraire_id_wikidata(texte_entity: str) -> Optional[str]:
    """
    Extrait l'ID Wikidata de 'Edmond Privat (Q12571)'

    Args:
        texte_entity: Texte contenant potentiellement un ID Wikidata

    Returns:
        L'ID Wikidata (ex: 'Q12571') ou None si non trouvé
    """
    if pd.isna(texte_entity) or not isinstance(texte_entity, str):
        return None

    # Pattern: (Q suivi de chiffres)
    pattern = r'\(Q\d+\)'
    match = re.search(pattern, texte_entity)

    if match:
        # Extraire sans les parenthèses
        return match.group(0)[1:-1]  # Enlève les ( )

    return None


# ============================================
# RÉCUPÉRATION ALIASES WIKIDATA
# ============================================

def recuperer_aliases_wikidata(qid: str, langues: List[str]) -> Optional[Dict[str, List[str]]]:
    """
    Interroge l'API Wikidata pour récupérer tous les alias d'une entité

    Args:
        qid: Identifiant Wikidata (ex: 'Q12571')
        langues: Liste des langues à récupérer (ex: ['fr', 'en', 'de'])

    Returns:
        Dictionnaire {langue: [alias1, alias2, ...]} ou None en cas d'erreur
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"

    try:
        # Faire la requête HTTP avec User-Agent
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_API)
        response.raise_for_status()

        donnees = response.json()

        # Vérifier que l'entité existe
        if "entities" not in donnees or qid not in donnees["entities"]:
            return None

        entite = donnees["entities"][qid]

        # Dictionnaire pour stocker les alias par langue
        aliases_par_langue = {}

        for langue in langues:
            alias_set = set()  # Pour éviter les doublons

            # 1. Récupérer le label principal (nom officiel)
            if "labels" in entite and langue in entite["labels"]:
                label = entite["labels"][langue]["value"]
                alias_set.add(label)

            # 2. Récupérer les alias alternatifs
            if "aliases" in entite and langue in entite["aliases"]:
                for alias_obj in entite["aliases"][langue]:
                    alias = alias_obj["value"]
                    alias_set.add(alias)

            # 3. Convertir en liste triée
            aliases_par_langue[langue] = sorted(list(alias_set))

        return aliases_par_langue

    except requests.exceptions.RequestException as e:
        print(f"      ❌ Erreur HTTP: {e}")
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"      ❌ Erreur parsing JSON: {e}")
        return None


def formater_aliases(liste_aliases: List[str]) -> str:
    """
    Convertit ['alias1', 'alias2', 'alias3'] en 'alias1, alias2, alias3'
    """
    if not liste_aliases:
        return ""
    return ", ".join(liste_aliases)


# ============================================
# CHECKPOINT / RESUME
# ============================================

def sauvegarder_checkpoint(df: pd.DataFrame):
    """Sauvegarde l'état actuel dans un fichier checkpoint"""
    checkpoint_data = {
        "last_row": len(df),
        "timestamp": time.time()
    }
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f)


def charger_checkpoint() -> Optional[int]:
    """Charge le dernier checkpoint s'il existe"""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("last_row", 0)
        except Exception:
            return None
    return None


def nettoyer_checkpoint():
    """Supprime le fichier checkpoint"""
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()


# ============================================
# PROCEDURE PRINCIPALE
# ============================================

def main():
    """Fonction principale du script"""

    print("=" * 70)
    print("SCRIPT 1 : ENRICHISSEMENT WIKIDATA")
    print("=" * 70)
    print(f"Objectif: Extraire les alias Wikidata pour les {NOMBRE_PERSONNES} premières personnes")
    print(f"Langues: {', '.join(LANGUES)}")
    print()

    # ========================================
    # ÉTAPE 1 : CHARGER LES DONNÉES
    # ========================================
    print("📂 Chargement du fichier Excel...")

    if not INPUT_FILE.exists():
        print(f"❌ ERREUR: Fichier non trouvé: {INPUT_FILE}")
        return

    df = pd.read_excel(INPUT_FILE)
    print(f"✅ Fichier chargé: {len(df)} personnes trouvées")

    # ========================================
    # ÉTAPE 2 : LIMITER À 40 PERSONNES
    # ========================================
    print(f"\n📊 Limitation aux {NOMBRE_PERSONNES} premières personnes...")
    df_limite = df.head(NOMBRE_PERSONNES).copy()
    print(f"✅ {len(df_limite)} personnes sélectionnées")

    # ========================================
    # ÉTAPE 3 : EXTRAIRE LES IDS WIKIDATA
    # ========================================
    print("\n🔍 Extraction des IDs Wikidata...")

    df_limite["wikidata_id"] = df_limite["entity_normalized"].apply(extraire_id_wikidata)

    nb_avec_id = df_limite["wikidata_id"].notna().sum()
    nb_sans_id = df_limite["wikidata_id"].isna().sum()

    print(f"✅ {nb_avec_id} personnes avec ID Wikidata")
    print(f"⚠️  {nb_sans_id} personnes sans ID Wikidata")

    # ========================================
    # ÉTAPE 4 : CRÉER LES NOUVELLES COLONNES
    # ========================================
    for langue in LANGUES:
        df_limite[f"aliases_wikidata_{langue}"] = ""
        df_limite[f"count_aliases_{langue}"] = 0

    # ========================================
    # ÉTAPE 5 : RÉCUPÉRER LES ALIAS WIKIDATA
    # ========================================
    print("\n🌐 Récupération des alias depuis Wikidata...")
    print(f"Pause entre requêtes: {PAUSE_API}s")
    print()

    # Statistiques
    compteur_reussi = 0
    compteur_echec = 0

    # Barre de progression
    for idx, row in tqdm(df_limite.iterrows(), total=len(df_limite), desc="Traitement"):
        nom_complet = f"{row.get('Prénom', '')} {row.get('Nom', '')}".strip()
        wikidata_id = row["wikidata_id"]

        # Affichage dans la console
        print(f"[{idx+1}/{len(df_limite)}] {nom_complet}")

        # Si pas d'ID Wikidata, passer
        if pd.isna(wikidata_id):
            print("  ⏭️  Pas d'ID Wikidata - utilisation du nom prénom officiel")
            # On pourrait ajouter le nom/prénom comme alias par défaut
            for langue in LANGUES:
                df_limite.at[idx, f"aliases_wikidata_{langue}"] = nom_complet
                df_limite.at[idx, f"count_aliases_{langue}"] = 1
            continue

        print(f"  ({wikidata_id})")

        # Récupérer les alias
        aliases = recuperer_aliases_wikidata(wikidata_id, LANGUES)

        if aliases is not None:
            total_aliases = 0

            for langue in LANGUES:
                liste_aliases = aliases.get(langue, [])

                # Stocker dans le DataFrame
                df_limite.at[idx, f"aliases_wikidata_{langue}"] = formater_aliases(liste_aliases)
                df_limite.at[idx, f"count_aliases_{langue}"] = len(liste_aliases)

                total_aliases += len(liste_aliases)

            print(f"  ✅ {total_aliases} alias trouvés")
            compteur_reussi += 1
        else:
            print(f"  ❌ Échec récupération")
            compteur_echec += 1

        # Pause pour ne pas surcharger l'API
        time.sleep(PAUSE_API)

        # Checkpoint tous les 10
        if (idx + 1) % 10 == 0:
            sauvegarder_checkpoint(df_limite)

    # ========================================
    # ÉTAPE 6 : STATISTIQUES
    # ========================================
    print("\n" + "=" * 70)
    print("STATISTIQUES")
    print("=" * 70)
    print(f"Personnes traitées: {len(df_limite)}")
    print(f"Succès Wikidata: {compteur_reussi}")
    print(f"Échecs: {compteur_echec}")
    print()

    for langue in LANGUES:
        total = df_limite[f"count_aliases_{langue}"].sum()
        moyenne = df_limite[f"count_aliases_{langue}"].mean()

        print(f"{langue.upper()}: {total} alias au total (moyenne: {moyenne:.1f} par personne)")

    # ========================================
    # ÉTAPE 7 : SAUVEGARDER
    # ========================================
    print(f"\n💾 Sauvegarde du fichier...")

    # Réorganiser les colonnes pour la lisibilité
    colonnes_base = ["entity_normalized", "wikidata_id", "Nom", "Prénom", "nationalité", "Gender"]
    colonnes_aliases_originaux = ["aliases"] if "aliases" in df_limite.columns else []
    colonnes_wikidata = []

    for langue in LANGUES:
        colonnes_wikidata.extend([
            f"aliases_wikidata_{langue}",
            f"count_aliases_{langue}"
        ])

    # Colonnes restantes
    colonnes_restantes = [col for col in df_limite.columns
                         if col not in colonnes_base + colonnes_aliases_originaux + colonnes_wikidata]

    colonnes_ordre = colonnes_base + colonnes_aliases_originaux + colonnes_wikidata + colonnes_restantes

    # Sélectionner seulement les colonnes qui existent
    colonnes_finales = [col for col in colonnes_ordre if col in df_limite.columns]

    df_final = df_limite[colonnes_finales]

    # Sauvegarder
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_excel(OUTPUT_FILE, index=False)

    print(f"✅ Fichier sauvegardé : {OUTPUT_FILE}")
    print(f"   Dimensions: {df_final.shape[0]} lignes × {df_final.shape[1]} colonnes")

    # Nettoyer le checkpoint
    nettoyer_checkpoint()

    print("\n" + "=" * 70)
    print("✅ TRAITEMENT TERMINÉ")
    print("=" * 70)
    print()
    print(f"Fichier de sortie: {OUTPUT_FILE}")
    print(f"Prêt pour Script 2 (recherche Impresso)")


if __name__ == "__main__":
    main()
