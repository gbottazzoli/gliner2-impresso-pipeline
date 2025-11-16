#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enrichissement contextuel PERSON - TEST TOP 3
==============================================

Test de l'extraction contextuelle sur les 3 personnes les plus fréquentes :
- Privat (49 occ)
- Gilbert Murray (36 occ)
- Inazo Nitobe (29 occ)

Méthode hybride : Regex + Matching ORG/GPE + LLM (Ollama)

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


# ============================================================
# CONFIGURATION
# ============================================================

CORPUS_DIR = 'data/annotated/ocr_results'
PERSON_FILE = 'outputs/person_FINAL_CLEAN.xlsx'
ORG_FILE = 'outputs/org_FINAL_CLEAN.xlsx'
GPE_FILE = 'outputs/gpe_FINAL_CLEAN.xlsx'
OUTPUT_FILE = 'outputs/acteurs_SDN_TEST_TOP3.xlsx'

CONTEXT_WINDOW = 500  # ~100 mots (500 caractères ≈ 100 mots)
OLLAMA_MODEL = 'llama3.1:8b'  # Modèle disponible localement


# ============================================================
# 1. CHARGEMENT ET INDEXATION
# ============================================================

def load_data():
    """Charger les 3 fichiers Excel"""
    print("📂 Chargement des données...")

    df_person = pd.read_excel(PERSON_FILE)
    df_org = pd.read_excel(ORG_FILE)
    df_gpe = pd.read_excel(GPE_FILE)

    print(f"   ✅ {len(df_person)} personnes, {len(df_org)} organisations, {len(df_gpe)} lieux")

    return df_person, df_org, df_gpe


def build_indexes(df_org, df_gpe):
    """Créer index inversés pour matching rapide"""
    print("🔍 Construction des index...")

    # Index ORG : {alias → entity_normalized}
    org_index = {}
    for _, row in df_org.iterrows():
        entity = row['entity_normalized']
        org_index[entity.lower()] = entity

        if pd.notna(row['aliases']):
            for alias in row['aliases'].split(', '):
                org_index[alias.lower()] = entity

    # Index GPE : {alias → entity_normalized}
    gpe_index = {}
    for _, row in df_gpe.iterrows():
        entity = row['entity_normalized']
        gpe_index[entity.lower()] = entity

        if pd.notna(row['aliases']):
            for alias in row['aliases'].split(', '):
                gpe_index[alias.lower()] = entity

    print(f"   ✅ Index ORG: {len(org_index)} entrées, GPE: {len(gpe_index)} entrées")

    return org_index, gpe_index


# ============================================================
# 2. EXTRACTION CONTEXTUELLE
# ============================================================

def load_document(doc_id: str) -> Optional[str]:
    """Charger un document .md depuis le corpus"""
    # Format: R1048-13C-26594-23516_doc14
    # Structure: data/annotated/ocr_results/R1048-13C-26594-23516/R1048-13C-26594-23516_doc14.md

    parts = doc_id.split('_')
    if len(parts) != 2:
        return None

    folder = parts[0]
    filepath = os.path.join(CORPUS_DIR, folder, f"{doc_id}.md")

    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return None


def extract_contexts(person_name: str, aliases: str, documents: str) -> List[str]:
    """
    Extraire tous les contextes de ±100 mots pour une personne
    """
    contexts = []

    # Liste des variantes du nom
    name_variants = [person_name]
    if pd.notna(aliases):
        name_variants.extend([a.strip() for a in aliases.split(', ')])

    # Pour chaque document
    doc_list = [d.strip() for d in documents.split(', ')]

    for doc_id in doc_list:
        doc_text = load_document(doc_id)
        if not doc_text:
            continue

        # Chercher chaque variante du nom
        for variant in name_variants:
            # Échapper les caractères spéciaux regex
            escaped = re.escape(variant)
            pattern = rf'\b{escaped}\b'

            for match in re.finditer(pattern, doc_text, re.IGNORECASE):
                # Extraire contexte ±CONTEXT_WINDOW
                start = max(0, match.start() - CONTEXT_WINDOW)
                end = min(len(doc_text), match.end() + CONTEXT_WINDOW)
                context = doc_text[start:end]
                contexts.append(context)

    return contexts


# ============================================================
# 3. DÉCOMPOSITION NOM/PRÉNOM
# ============================================================

def split_name(full_name: str, aliases: str = "") -> Tuple[str, str]:
    """
    Séparer nom et prénom
    Règle : dernier mot = Nom, reste = Prénom
    Si nom incomplet, chercher prénom dans aliases
    """
    parts = full_name.strip().split()

    if len(parts) == 0:
        return "", ""
    elif len(parts) == 1:
        # Un seul mot : chercher prénom dans aliases
        nom = parts[0]
        prenom = ""

        if pd.notna(aliases):
            # Chercher une variante avec prénom
            for alias in aliases.split(', '):
                alias_parts = alias.strip().split()
                # Si l'alias se termine par le même nom et a plus de mots
                if len(alias_parts) > 1 and alias_parts[-1].lower() == nom.lower():
                    prenom = " ".join(alias_parts[:-1])
                    # Nettoyer les titres du prénom
                    prenom = re.sub(r'\b(Dr\.|Dr|M\.|Monsieur|Mr\.|Prof\.|Professor|Dro|D-ro|Sro|S-ro)\b', '', prenom, flags=re.IGNORECASE).strip()
                    if prenom and not prenom.endswith('.'):  # Éviter initiales seules
                        break

        return nom, prenom
    else:
        nom = parts[-1]
        prenom = " ".join(parts[:-1])
        return nom, prenom


def create_identifier(nom: str, prenom: str) -> str:
    """
    Créer identifiant format NomPrénom
    """
    return nom + prenom.replace(" ", "")


# ============================================================
# 4. EXTRACTION PAR RÈGLES (RAPIDE)
# ============================================================

def extract_with_rules(contexts: List[str], org_index: Dict, gpe_index: Dict) -> Dict:
    """
    Extraction rapide par matching et regex
    """
    results = {
        'functions': [],
        'organizations': [],
        'locations': [],
        'nationalities': [],
        'gender_hints': []
    }

    # Fusionner tous les contextes
    full_context = "\n".join(contexts)

    # 1. FONCTIONS - Patterns regex
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

    # 2. ORGANISATIONS - Matching avec index
    for org_alias, org_canonical in org_index.items():
        if org_alias in full_context.lower():
            results['organizations'].append(org_canonical)

    # 3. LIEUX - Matching avec index
    for gpe_alias, gpe_canonical in gpe_index.items():
        if gpe_alias in full_context.lower():
            results['locations'].append(gpe_canonical)

    # 4. NATIONALITÉS - Patterns spécifiques + adresses
    # Pattern 1: Pays directs
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

    # Pattern 2: Adresses avec ville, pays
    address_pattern = r'(?:Oxford|Cambridge|Londres|London),\s*([A-Za-zé]+)|(?:Paris|Lyon|Marseille),\s*([A-Za-zé]+)|(?:Genève|Geneva|Berne|Bern),\s*([A-Za-zé]+)|(?:Berlin|Munich|Baden-Baden),\s*([A-Za-zé]+)'
    address_matches = re.findall(address_pattern, full_context, re.IGNORECASE)
    for match in address_matches:
        country = [m for m in match if m]  # Filtrer groupes vides
        if country:
            results['nationalities'].extend(country)

    # 5. GENRE - Indices dans les titres
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


# ============================================================
# 5. EXTRACTION PAR LLM (INTELLIGENT)
# ============================================================

def extract_with_ollama(person_name: str, contexts: List[str]) -> Dict:
    """
    Utiliser Ollama pour extraction structurée (cas complexes)
    """
    if not contexts:
        return {}

    # Prendre les 3 premiers contextes (limiter la taille)
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

        # Parser la réponse JSON
        response_text = response['response'].strip()

        # Nettoyer le texte (parfois le LLM ajoute des backticks)
        if response_text.startswith('```'):
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]

        parsed = json.loads(response_text)
        return parsed

    except Exception as e:
        print(f"      ⚠️  Erreur LLM : {e}")
        return {}


# ============================================================
# 6. FUSION DES RÉSULTATS
# ============================================================

def merge_results(rules_results: Dict, llm_results: Dict, person_name: str) -> Dict:
    """
    Fusionner résultats règles + LLM
    """
    merged = {}

    # 1. DESCRIPTION - FORMAT STRUCTURÉ LISIBLE
    description_parts = []

    # A. TITRES / FONCTIONS - dédupliquer (ignorer casse)
    functions = rules_results.get('functions', [])
    if llm_results.get('fonction'):
        functions.append(llm_results['fonction'])

    # Dédupliquer en normalisant la casse
    functions_normalized = {}
    for f in functions:
        f_lower = f.lower().strip()
        if f_lower not in functions_normalized:
            functions_normalized[f_lower] = f

    if functions_normalized:
        titres = ", ".join(list(functions_normalized.values())[:3])  # Max 3
        description_parts.append(f"Titre: {titres}")

    # B. ORGANISATIONS - dédupliquer
    orgs = list(set(rules_results.get('organizations', [])))
    if llm_results.get('organisation'):
        orgs.append(llm_results['organisation'])
    orgs = list(set(orgs))  # Dédupliquer
    if orgs:
        orgs_str = ", ".join(orgs[:2])  # Max 2
        description_parts.append(f"Organisation: {orgs_str}")

    # C. LIEUX (GPE) - dédupliquer et clarifier
    lieux = list(set(rules_results.get('locations', [])))
    if llm_results.get('lieu_residence'):
        lieux.append(llm_results['lieu_residence'])
    lieux = list(set(lieux))  # Dédupliquer
    if lieux:
        lieux_str = ", ".join(lieux[:2])  # Max 2
        description_parts.append(f"Lieu de travail/résidence: {lieux_str}")

    # Format final : séparation par " | " pour clarté
    merged['Description'] = " | ".join(description_parts) if description_parts else ""

    # 2. NATIONALITÉ - filtrer bruit et normaliser
    nats = rules_results.get('nationalities', [])
    if llm_results.get('nationalite'):
        nats.append(llm_results['nationalite'])

    # Filtrer mots courts et mots communs (bruit)
    stop_words = {'i', 'you', 'he', 'she', 'we', 'they', 'it', 'a', 'the', 'de', 'la', 'le', 'vous', 'je', 'tu', 'il', 'elle'}
    nats_clean = [n for n in nats if len(n) > 2 and n.lower() not in stop_words]

    # Normaliser pays similaires
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

    # Compter fréquences
    if nats_normalized:
        nat_counter = Counter(nats_normalized)
        merged['Nationalité'] = "; ".join([nat for nat, _ in nat_counter.most_common(3)])
    else:
        merged['Nationalité'] = ""

    # 3. GENRE
    gender_hints = rules_results.get('gender_hints', [])
    llm_gender = llm_results.get('genre', '')

    if gender_hints:
        # Majorité
        gender_counter = Counter(gender_hints)
        most_common = gender_counter.most_common(1)[0][0]
        merged['Genre'] = most_common.capitalize()
    elif llm_gender and llm_gender.lower() in ['homme', 'femme']:
        merged['Genre'] = llm_gender.capitalize()
    else:
        merged['Genre'] = "Inconnu"

    # 4. CATÉGORIE (règles sur description)
    desc_lower = merged['Description'].lower()

    if any(kw in desc_lower for kw in ['secretary', 'secrétaire', 'sous-secrétaire', 'secretariat']):
        merged['Catégorie'] = "Membres du secrétariat de la SDN"
    elif any(kw in desc_lower for kw in ['délégué', 'delegate', 'gouvernement', 'government']):
        merged['Catégorie'] = "Délégués des gouvernements"
    else:
        merged['Catégorie'] = "Personnalités externes"

    return merged


# ============================================================
# 7. ENRICHISSEMENT PRINCIPAL
# ============================================================

def enrich_person(row: pd.Series, org_index: Dict, gpe_index: Dict, use_llm: bool = True) -> Dict:
    """
    Enrichir une personne avec extraction contextuelle
    """
    person_name = row['entity_normalized']
    aliases = row['aliases']
    documents = row['documents']

    print(f"\n   🔍 {person_name} ({row['nb_occurrences']} occ, {row['nb_documents']} docs)")

    # 1. Décomposer nom/prénom (avec aliases si besoin)
    nom, prenom = split_name(person_name, aliases)
    identifier = create_identifier(nom, prenom)

    print(f"      Nom={nom}, Prénom={prenom}, ID={identifier}")

    # 2. Extraire contextes
    contexts = extract_contexts(person_name, aliases, documents)
    print(f"      Contextes extraits : {len(contexts)}")

    # 3. Extraction par règles
    rules_results = extract_with_rules(contexts, org_index, gpe_index)
    print(f"      Règles → Fonctions: {len(rules_results['functions'])}, Orgs: {len(rules_results['organizations'])}, Lieux: {len(rules_results['locations'])}")

    # 4. Extraction par LLM si nécessaire
    llm_results = {}
    confidence_score = len(rules_results['functions']) + len(rules_results['organizations']) + len(rules_results['nationalities'])

    # Forcer LLM si nationalité vide ou suspecte
    nationality_suspicious = len(rules_results['nationalities']) == 0 or any(
        len(n) <= 2 for n in rules_results['nationalities']
    )

    if use_llm and (confidence_score < 3 or nationality_suspicious):
        print(f"      🤖 Appel LLM (score confiance: {confidence_score}, nationalité suspecte: {nationality_suspicious})")
        llm_results = extract_with_ollama(person_name, contexts)
        print(f"      LLM → {llm_results}")

    # 5. Fusionner résultats
    merged = merge_results(rules_results, llm_results, person_name)

    # 6. Construire ligne finale
    enriched_row = {
        'Nom': nom,
        'Prénom': prenom,
        'Identifiant': identifier,
        'Variantes': aliases if pd.notna(aliases) else "",
        'Description': merged.get('Description', ""),
        'Archives de correspondance': documents.replace(', ', '; '),  # Séparer par ;
        'Documents officiels': "",  # Vide
        'Presse': "",  # Vide
        'Nationalité': merged.get('Nationalité', ""),
        'Genre': merged.get('Genre', "Inconnu"),
        'Catégorie': merged.get('Catégorie', ""),
    }

    return enriched_row


# ============================================================
# 8. MAIN
# ============================================================

def main():
    print("="*80)
    print("ENRICHISSEMENT CONTEXTUEL PERSON - TEST TOP 3")
    print("="*80)
    print()

    # Charger données
    df_person, df_org, df_gpe = load_data()

    # Construire index
    org_index, gpe_index = build_indexes(df_org, df_gpe)

    # Sélectionner TOP 3
    print("\n📊 Sélection des TOP 3 personnes par fréquence...")
    top3 = df_person.nlargest(3, 'nb_occurrences')

    print("\nTOP 3 :")
    for idx, row in top3.iterrows():
        print(f"   • {row['entity_normalized']:30s} - {row['nb_occurrences']:3d} occ")

    # Enrichir chaque personne
    print("\n" + "="*80)
    print("EXTRACTION CONTEXTUELLE")
    print("="*80)

    enriched_rows = []

    for idx, row in top3.iterrows():
        enriched_row = enrich_person(row, org_index, gpe_index, use_llm=True)
        enriched_rows.append(enriched_row)
        print(f"      ✅ Enrichi : {enriched_row}")

    # Créer DataFrame final
    df_enriched = pd.DataFrame(enriched_rows)

    # Sauvegarder
    print("\n" + "="*80)
    print("💾 SAUVEGARDE")
    print("="*80)

    df_enriched.to_excel(OUTPUT_FILE, index=False)
    print(f"   ✅ Fichier sauvegardé : {OUTPUT_FILE}")

    # Afficher résultat
    print("\n" + "="*80)
    print("📊 RÉSULTAT FINAL")
    print("="*80)
    print()
    print(df_enriched.to_string(index=False))
    print()

    print("="*80)
    print("✅ TEST TERMINÉ - Vérifier manuellement les résultats")
    print("="*80)


if __name__ == '__main__':
    main()
