#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exploration de la structure des données
========================================

Analyse les fichiers PERSON, ORG, GPE pour comprendre leur structure
et préparer l'enrichissement contextuel.

Auteur : Claude Code
Date   : 2025-11-16
"""

import pandas as pd
import os

def main():
    print("="*80)
    print("EXPLORATION DE LA STRUCTURE DES DONNÉES")
    print("="*80)
    print()

    # Chemins
    person_file = 'outputs/person_FINAL_CLEAN.xlsx'
    org_file = 'outputs/org_FINAL_CLEAN.xlsx'
    gpe_file = 'outputs/gpe_FINAL_CLEAN.xlsx'

    # Charger PERSON
    print("📂 FICHIER PERSON")
    print("-"*80)
    df_person = pd.read_excel(person_file)
    print(f"   • Nombre d'entités : {len(df_person)}")
    print(f"   • Colonnes : {list(df_person.columns)}")
    print()
    print("   • Aperçu des 3 premières lignes :")
    print(df_person.head(3).to_string())
    print()
    print("   • TOP 5 personnes par fréquence :")
    top_person = df_person.nlargest(5, 'nb_occurrences')
    for idx, row in top_person.iterrows():
        print(f"      {row['entity_normalized']:30s} - {row['nb_occurrences']:3d} occ - Docs: {row['documents'][:100]}...")
    print()

    # Charger ORG
    print("📂 FICHIER ORGANIZATION")
    print("-"*80)
    df_org = pd.read_excel(org_file)
    print(f"   • Nombre d'entités : {len(df_org)}")
    print(f"   • Colonnes : {list(df_org.columns)}")
    print()
    print("   • TOP 5 organisations par fréquence :")
    top_org = df_org.nlargest(5, 'nb_occurrences')
    for idx, row in top_org.iterrows():
        print(f"      {row['entity_normalized']:50s} - {row['nb_occurrences']:3d} occ")
    print()

    # Charger GPE
    print("📂 FICHIER GPE")
    print("-"*80)
    df_gpe = pd.read_excel(gpe_file)
    print(f"   • Nombre d'entités : {len(df_gpe)}")
    print(f"   • Colonnes : {list(df_gpe.columns)}")
    print()
    print("   • TOP 5 lieux par fréquence :")
    top_gpe = df_gpe.nlargest(5, 'nb_occurrences')
    for idx, row in top_gpe.iterrows():
        print(f"      {row['entity_normalized']:30s} - {row['nb_occurrences']:3d} occ")
    print()

    # Analyser le corpus
    print("📂 CORPUS OCR")
    print("-"*80)
    corpus_dir = 'data/annotated/ocr_results'

    if os.path.exists(corpus_dir):
        # Compter les fichiers
        total_files = 0
        for root, dirs, files in os.walk(corpus_dir):
            txt_files = [f for f in files if f.endswith('.txt')]
            total_files += len(txt_files)

        print(f"   • Nombre total de fichiers .txt : {total_files}")

        # Lire un exemple
        for root, dirs, files in os.walk(corpus_dir):
            txt_files = [f for f in files if f.endswith('.txt')]
            if txt_files:
                example_file = os.path.join(root, txt_files[0])
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"   • Exemple de fichier : {example_file}")
                print(f"   • Taille : {len(content)} caractères")
                print(f"   • Extrait (200 premiers caractères) :")
                print(f"      {content[:200]}...")
                break
    else:
        print(f"   ⚠️  Corpus non trouvé : {corpus_dir}")

    print()
    print("="*80)
    print("✅ EXPLORATION TERMINÉE")
    print("="*80)

if __name__ == '__main__':
    main()
