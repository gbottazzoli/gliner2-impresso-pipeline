#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichissement contextuel PERSON - COMPLET (832 personnes)
===========================================================

Traitement complet de toutes les personnes avec :
- Parallélisation (multiprocessing)
- Progress bar (tqdm)
- Cache de documents
- Logging

Auteur : Claude Code
Date   : 2025-11-16
"""

import pandas as pd
import os
import re
import json
from typing import Dict, List, Tuple, Optional
from collections import Counter
import ollama
from multiprocessing import Pool, Manager
from tqdm import tqdm
import time


# ============================================================
# CONFIGURATION
# ============================================================

CORPUS_DIR = 'data/annotated/ocr_results'
PERSON_FILE = 'outputs/person_FINAL_CLEAN.xlsx'
ORG_FILE = 'outputs/org_FINAL_CLEAN.xlsx'
GPE_FILE = 'outputs/gpe_FINAL_CLEAN.xlsx'
OUTPUT_FILE = 'outputs/acteurs_SDN_enriched.xlsx'
REPORT_FILE = 'outputs/enrichment_report.txt'

CONTEXT_WINDOW = 500  # ~100 mots
OLLAMA_MODEL = 'llama3.1:8b'
NUM_WORKERS = 4  # Parallélisation


# ============================================================
# CACHE GLOBAL (partagé entre workers)
# ============================================================

# Cache de documents chargés
DOCUMENT_CACHE = {}


# ============================================================
# FONCTIONS RÉUTILISÉES DU SCRIPT TEST
# ============================================================

def load_document(doc_id: str) -> Optional[str]:
    """Charger un document .md depuis le corpus avec cache"""
    if doc_id in DOCUMENT_CACHE:
        return DOCUMENT_CACHE[doc_id]

    parts = doc_id.split('_')
    if len(parts) != 2:
        return None

    folder = parts[0]
    filepath = os.path.join(CORPUS_DIR, folder, f"{doc_id}.md")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            DOCUMENT_CACHE[doc_id] = content
            return content
    except:
        return None


def extract_contexts(person_name: str, aliases: str, documents: str) -> List[str]:
    """Extraire tous les contextes de ±100 mots pour une personne"""
    contexts = []

    name_variants = [person_name]
    if pd.notna(aliases):
        name_variants.extend([a.strip() for a in aliases.split(', ')])

    doc_list = [d.strip() for d in documents.split(', ')]

    for doc_id in doc_list:
        doc_text = load_document(doc_id)
        if not doc_text:
            continue

        for variant in name_variants:
            escaped = re.escape(variant)
            pattern = rf'\b{escaped}\b'

            for match in re.finditer(pattern, doc_text, re.IGNORECASE):
                start = max(0, match.start() - CONTEXT_WINDOW)
                end = min(len(doc_text), match.end() + CONTEXT_WINDOW)
                context = doc_text[start:end]
                contexts.append(context)

    return contexts


def split_name(full_name: str, aliases: str = "") -> Tuple[str, str]:
    """Séparer nom et prénom"""
    parts = full_name.strip().split()

    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        nom = parts[0]
        prenom = ""

        if pd.notna(aliases):
            for alias in aliases.split(', '):
                alias_parts = alias.strip().split()
                if len(alias_parts) > 1 and alias_parts[-1].lower() == nom.lower():
                    prenom = " ".join(alias_parts[:-1])
                    prenom = re.sub(r'\b(Dr\.|Dr|M\.|Monsieur|Mr\.|Prof\.|Professor|Dro|D-ro|Sro|S-ro)\b', '', prenom, flags=re.IGNORECASE).strip()
                    if prenom and not prenom.endswith('.'):
                        break

        return nom, prenom
    else:
        nom = parts[-1]
        prenom = " ".join(parts[:-1])
        return nom, prenom


def create_identifier(nom: str, prenom: str) -> str:
    """Créer identifiant format NomPrénom"""
    return nom + prenom.replace(" ", "")


def extract_with_rules(contexts: List[str], org_index: Dict, gpe_index: Dict) -> Dict:
    """Extraction rapide par matching et regex"""
    results = {
        'functions': [],
        'organizations': [],
        'locations': [],
        'nationalities': [],
        'gender_hints': []
    }

    full_context = "\n".join(contexts)

    # Fonctions
    function_patterns = [
        r'(Professor|Prof\.|Dr\.|Doctor|Director|Secretary|Member|President|Senator|Minister|General)',
        r'(Professeur|Directeur|Secrétaire|Membre|Président|Sénateur|Ministre|Général)',
        r'(Sous-secrétaire\s+général|Under-Secretary|Assistant\s+Professor)',
        r'(Member\s+of\s+(?:the\s+)?[\w\s]+)',
        r'(Membre\s+de\s+(?:la\s+)?[\w\s]+)',
    ]

    for pattern in function_patterns:
        matches = re.findall(pattern, full_context, re.IGNORECASE)
        results['functions'].extend(matches)

    # Organisations
    for org_alias, org_canonical in org_index.items():
        if org_alias in full_context.lower():
            results['organizations'].append(org_canonical)

    # Lieux
    for gpe_alias, gpe_canonical in gpe_index.items():
        if gpe_alias in full_context.lower():
            results['locations'].append(gpe_canonical)

    # Nationalités
    country_patterns = [
        r'\b(Angleterre|England|Grande-Bretagne|Royaume-Uni|United Kingdom)\b',
        r'\b(Allemagne|Germany|Deutschland)\b',
        r'\b(France)\b',
        r'\b(Suisse|Switzerland)\b',
        r'\b(Japon|Japan)\b',
        r'\b(États-Unis|United States|U\.S\.A|USA|America)\b',
        r'\b(Italie|Italy|Italia)\b',
        r'\b(Espagne|Spain|España)\b',
    ]

    for pattern in country_patterns:
        matches = re.findall(pattern, full_context, re.IGNORECASE)
        results['nationalities'].extend(matches)

    # Adresses
    address_pattern = r'(?:Oxford|Cambridge|Londres|London),\s*([A-Za-zé]+)|(?:Paris|Lyon|Marseille),\s*([A-Za-zé]+)|(?:Genève|Geneva|Berne|Bern),\s*([A-Za-zé]+)|(?:Berlin|Munich|Baden-Baden),\s*([A-Za-zé]+)'
    address_matches = re.findall(address_pattern, full_context, re.IGNORECASE)
    for match in address_matches:
        country = [m for m in match if m]
        if country:
            results['nationalities'].extend(country)

    # Genre
    gender_patterns = {
        'homme': [r'\b(Mr\.|Mister|Monsieur|M\.|Herr|Herrn|Prof\.|Dr\.)\b'],
        'femme': [r'\b(Mrs\.|Miss|Ms\.|Mme|Madame|Mlle|Mademoiselle|Melle|Frau|Fräulein|Madam)\b']
    }

    for gender, patterns in gender_patterns.items():
        for pattern in patterns:
            if re.search(pattern, full_context, re.IGNORECASE):
                results['gender_hints'].append(gender)
                break

    return results


def extract_with_ollama(person_name: str, contexts: List[str]) -> Dict:
    """Utiliser Ollama pour extraction structurée"""
    if not contexts:
        return {}

    sample_contexts = "\n---\n".join(contexts[:3])

    prompt = f"""Tu es un assistant d'extraction d'informations historiques.

Analyse ces extraits de documents de la Société des Nations concernant **{person_name}**.

CONTEXTES :
{sample_contexts[:1500]}

Extraire au format JSON strict :
{{
    "fonction": "titre ou fonction de la personne (ex: 'Professor', 'Dr.', 'Secretary')",
    "organisation": "organisation d'appartenance (ex: 'Committee on Intellectual Co-operation')",
    "lieu_residence": "lieu de résidence ou de travail (ex: 'Oxford', 'Genève')",
    "nationalite": "pays ou nationalité (ex: 'Angleterre', 'France')",
    "genre": "Homme ou Femme ou Inconnu"
}}

IMPORTANT : Répondre UNIQUEMENT avec le JSON, sans texte additionnel."""

    try:
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt
        )

        response_text = response['response'].strip()

        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        parsed = json.loads(response_text)

        # Vérifier que c'est bien un dict (pas une liste)
        if not isinstance(parsed, dict):
            return {}

        return parsed

    except Exception as e:
        return {}


def merge_results(rules_results: Dict, llm_results, person_name: str) -> Dict:
    """Fusionner résultats règles + LLM"""
    merged = {}

    # Sécurité : vérifier que llm_results est bien un dict
    if not isinstance(llm_results, dict):
        llm_results = {}

    # DESCRIPTION - FORMAT STRUCTURÉ LISIBLE
    description_parts = []

    # A. TITRES / FONCTIONS - dédupliquer
    functions = rules_results.get('functions', [])
    if llm_results.get('fonction'):
        functions.append(llm_results['fonction'])

    functions_normalized = {}
    for f in functions:
        f_lower = f.lower().strip()
        if f_lower not in functions_normalized:
            functions_normalized[f_lower] = f

    if functions_normalized:
        titres = ", ".join(list(functions_normalized.values())[:3])
        description_parts.append(f"Titre: {titres}")

    # B. ORGANISATIONS - dédupliquer
    orgs = list(set(rules_results.get('organizations', [])))
    if llm_results.get('organisation'):
        orgs.append(llm_results['organisation'])
    orgs = list(set(orgs))
    if orgs:
        orgs_str = ", ".join(orgs[:2])
        description_parts.append(f"Organisation: {orgs_str}")

    # C. LIEUX (GPE) - clarifier
    lieux = list(set(rules_results.get('locations', [])))
    if llm_results.get('lieu_residence'):
        lieux.append(llm_results['lieu_residence'])
    lieux = list(set(lieux))
    if lieux:
        lieux_str = ", ".join(lieux[:2])
        description_parts.append(f"Lieu de travail/résidence: {lieux_str}")

    # Format final : séparation par " | "
    merged['Description'] = " | ".join(description_parts) if description_parts else ""

    # Nationalité - filtrer bruit
    nats = rules_results.get('nationalities', [])
    if llm_results.get('nationalite'):
        nats.append(llm_results['nationalite'])

    stop_words = {'i', 'you', 'he', 'she', 'we', 'they', 'it', 'a', 'the', 'de', 'la', 'le', 'vous', 'je', 'tu', 'il', 'elle'}
    nats_clean = [n for n in nats if len(n) > 2 and n.lower() not in stop_words]

    country_mapping = {
        'england': 'Angleterre',
        'angleterre': 'Angleterre',
        'germany': 'Allemagne',
        'allemagne': 'Allemagne',
        'france': 'France',
        'switzerland': 'Suisse',
        'suisse': 'Suisse',
        'japan': 'Japon',
        'japon': 'Japon',
        'united states': 'États-Unis',
        'usa': 'États-Unis',
        'u.s.a': 'États-Unis',
    }

    nats_normalized = []
    for n in nats_clean:
        n_lower = n.lower()
        nats_normalized.append(country_mapping.get(n_lower, n.capitalize()))

    if nats_normalized:
        nat_counter = Counter(nats_normalized)
        merged['Nationalité'] = "; ".join([nat for nat, _ in nat_counter.most_common(3)])
    else:
        merged['Nationalité'] = ""

    # Genre
    gender_hints = rules_results.get('gender_hints', [])
    llm_gender = llm_results.get('genre', '')

    if gender_hints:
        gender_counter = Counter(gender_hints)
        most_common = gender_counter.most_common(1)[0][0]
        merged['Genre'] = most_common.capitalize()
    elif llm_gender and llm_gender.lower() in ['homme', 'femme']:
        merged['Genre'] = llm_gender.capitalize()
    else:
        merged['Genre'] = "Inconnu"

    # Catégorie
    desc_lower = merged['Description'].lower()

    if any(kw in desc_lower for kw in ['secretary', 'secrétaire', 'sous-secrétaire', 'secretariat']):
        merged['Catégorie'] = "Membres du secrétariat de la SDN"
    elif any(kw in desc_lower for kw in ['délégué', 'delegate', 'gouvernement', 'government']):
        merged['Catégorie'] = "Délégués des gouvernements"
    else:
        merged['Catégorie'] = "Personnalités externes"

    return merged


def enrich_person(row: pd.Series, org_index: Dict, gpe_index: Dict, use_llm: bool = True, llm_count: dict = None) -> Dict:
    """Enrichir une personne avec extraction contextuelle"""
    person_name = row['entity_normalized']
    aliases = row['aliases']
    documents = row['documents']

    # Décomposer nom/prénom
    nom, prenom = split_name(person_name, aliases)
    identifier = create_identifier(nom, prenom)

    # Extraire contextes
    contexts = extract_contexts(person_name, aliases, documents)

    # Extraction par règles
    rules_results = extract_with_rules(contexts, org_index, gpe_index)

    # Extraction par LLM si nécessaire
    llm_results = {}
    confidence_score = len(rules_results['functions']) + len(rules_results['organizations']) + len(rules_results['nationalities'])

    nationality_suspicious = len(rules_results['nationalities']) == 0 or any(
        len(n) <= 2 for n in rules_results['nationalities']
    )

    if use_llm and (confidence_score < 3 or nationality_suspicious):
        llm_results = extract_with_ollama(person_name, contexts)
        if llm_count is not None:
            llm_count['count'] += 1

    # Fusionner résultats
    merged = merge_results(rules_results, llm_results, person_name)

    # Construire ligne finale
    enriched_row = {
        'Nom': nom,
        'Prénom': prenom,
        'Identifiant': identifier,
        'Variantes': aliases if pd.notna(aliases) else "",
        'Description': merged.get('Description', ""),
        'Archives de correspondance': documents.replace(', ', '; '),
        'Documents officiels': "",
        'Presse': "",
        'Nationalité': merged.get('Nationalité', ""),
        'Genre': merged.get('Genre', "Inconnu"),
        'Catégorie': merged.get('Catégorie', ""),
    }

    return enriched_row


def enrich_person_wrapper(args):
    """Wrapper pour parallélisation"""
    idx, row, org_index, gpe_index, llm_count = args
    return enrich_person(row, org_index, gpe_index, use_llm=True, llm_count=llm_count)


# ============================================================
# MAIN
# ============================================================

def main():
    print("="*80)
    print("ENRICHISSEMENT CONTEXTUEL PERSON - COMPLET (832 personnes)")
    print("="*80)
    print()

    start_time = time.time()

    # Charger données
    print("📂 Chargement des données...")
    df_person = pd.read_excel(PERSON_FILE)
    df_org = pd.read_excel(ORG_FILE)
    df_gpe = pd.read_excel(GPE_FILE)

    print(f"   ✅ {len(df_person)} personnes, {len(df_org)} organisations, {len(df_gpe)} lieux")

    # Construire index
    print("🔍 Construction des index...")
    org_index = {}
    for _, row in df_org.iterrows():
        entity = row['entity_normalized']
        org_index[entity.lower()] = entity
        if pd.notna(row['aliases']):
            for alias in row['aliases'].split(', '):
                org_index[alias.lower()] = entity

    gpe_index = {}
    for _, row in df_gpe.iterrows():
        entity = row['entity_normalized']
        gpe_index[entity.lower()] = entity
        if pd.notna(row['aliases']):
            for alias in row['aliases'].split(', '):
                gpe_index[alias.lower()] = entity

    print(f"   ✅ Index ORG: {len(org_index)} entrées, GPE: {len(gpe_index)} entrées")

    # Traitement avec parallélisation
    print("\n" + "="*80)
    print("ENRICHISSEMENT CONTEXTUEL")
    print("="*80)
    print()

    print(f"⚙️  Parallélisation : {NUM_WORKERS} workers")
    print()

    # Manager pour partager le compteur LLM entre workers
    manager = Manager()
    llm_count = manager.dict()
    llm_count['count'] = 0

    # Préparer arguments pour parallélisation
    args_list = [
        (idx, row, org_index, gpe_index, llm_count)
        for idx, row in df_person.iterrows()
    ]

    # Traiter avec progress bar
    enriched_rows = []

    with Pool(NUM_WORKERS) as pool:
        for result in tqdm(pool.imap(enrich_person_wrapper, args_list), total=len(df_person), desc="Enrichissement"):
            enriched_rows.append(result)

    # Créer DataFrame final
    df_enriched = pd.DataFrame(enriched_rows)

    # Sauvegarder
    print("\n" + "="*80)
    print("💾 SAUVEGARDE")
    print("="*80)

    df_enriched.to_excel(OUTPUT_FILE, index=False)
    print(f"   ✅ Fichier sauvegardé : {OUTPUT_FILE}")

    # Statistiques
    print("\n" + "="*80)
    print("📊 STATISTIQUES")
    print("="*80)
    print()

    total_time = time.time() - start_time

    desc_count = (df_enriched['Description'] != "").sum()
    nat_count = (df_enriched['Nationalité'] != "").sum()
    genre_count = (df_enriched['Genre'] != "Inconnu").sum()
    cat_count = (df_enriched['Catégorie'] != "").sum()

    print(f"   • Entités traitées      : {len(df_enriched)}")
    print(f"   • Temps total           : {total_time:.1f}s ({total_time/60:.1f} min)")
    print()
    print(f"   Taux de complétude :")
    print(f"      - Description        : {desc_count/len(df_enriched)*100:.1f}% ({desc_count}/{len(df_enriched)})")
    print(f"      - Nationalité        : {nat_count/len(df_enriched)*100:.1f}% ({nat_count}/{len(df_enriched)})")
    print(f"      - Genre              : {genre_count/len(df_enriched)*100:.1f}% ({genre_count}/{len(df_enriched)})")
    print(f"      - Catégorie          : {cat_count/len(df_enriched)*100:.1f}% ({cat_count}/{len(df_enriched)})")
    print()
    print(f"   • Utilisation LLM       : {llm_count['count']} appels ({llm_count['count']/len(df_enriched)*100:.1f}%)")
    print()

    # Sauvegarder rapport
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("RAPPORT D'ENRICHISSEMENT CONTEXTUEL\n")
        f.write("="*70 + "\n\n")
        f.write(f"Date : 2025-11-16\n")
        f.write(f"Input : {PERSON_FILE}\n")
        f.write(f"Output : {OUTPUT_FILE}\n\n")
        f.write("="*70 + "\n")
        f.write("STATISTIQUES\n")
        f.write("="*70 + "\n\n")
        f.write(f"Entités traitées         : {len(df_enriched)}\n")
        f.write(f"Temps total              : {total_time:.1f}s ({total_time/60:.1f} min)\n\n")
        f.write("Taux de complétude :\n")
        f.write(f"  - Description          : {desc_count/len(df_enriched)*100:.1f}% ({desc_count}/{len(df_enriched)})\n")
        f.write(f"  - Nationalité          : {nat_count/len(df_enriched)*100:.1f}% ({nat_count}/{len(df_enriched)})\n")
        f.write(f"  - Genre                : {genre_count/len(df_enriched)*100:.1f}% ({genre_count}/{len(df_enriched)})\n")
        f.write(f"  - Catégorie            : {cat_count/len(df_enriched)*100:.1f}% ({cat_count}/{len(df_enriched)})\n\n")
        f.write(f"Utilisation LLM          : {llm_count['count']} appels ({llm_count['count']/len(df_enriched)*100:.1f}%)\n\n")
        f.write("="*70 + "\n")
        f.write("CONCLUSION\n")
        f.write("="*70 + "\n\n")
        f.write(f"✅ {len(df_enriched)} personnes enrichies avec succès\n")
        f.write(f"✅ Fichier Excel généré : {OUTPUT_FILE}\n\n")

    print(f"   ✅ Rapport sauvegardé : {REPORT_FILE}")
    print()

    print("="*80)
    print("✅ ENRICHISSEMENT TERMINÉ")
    print("="*80)


if __name__ == '__main__':
    main()
