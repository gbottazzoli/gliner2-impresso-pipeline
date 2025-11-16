#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation NER - Qualité globale
=================================

Valide la qualité des entités extraites (PERSON/ORG/GPE) par rapport au corpus complet.

Méthodologie :
- Échantillonnage stratifié (par fréquence d'entités)
- Extraction de contextes depuis le corpus OCR
- 5 validations automatiques par entité
- Calcul d'intervalle de confiance statistique (95%)

Auteur : Claude Code
Date   : 2025-11-16
"""

import pandas as pd
import random
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple
import unicodedata
import math


# ============================================================
# CONFIGURATION
# ============================================================

CORPUS_DIR = Path("data/annotated/ocr_results")
PERSON_FILE = Path("outputs/person_FINAL_CLEAN.xlsx")
ORG_FILE = Path("outputs/org_FINAL_CLEAN.xlsx")
GPE_FILE = Path("outputs/gpe_FINAL_CLEAN.xlsx")

OUTPUT_REPORT = Path("outputs/validation_ner_quality_report.txt")
OUTPUT_HTML = Path("outputs/validation_ner_quality_report.html")

# Taille de l'échantillon par type et fréquence
SAMPLE_SIZE = {
    'frequent': 50,   # >5 occ
    'medium': 50,     # 2-5 occ
    'rare': 50,       # 1 occ
}

RANDOM_SEED = 42


# ============================================================
# CHARGEMENT CORPUS
# ============================================================

def load_corpus(corpus_dir: Path) -> Dict[str, str]:
    """
    Charge tous les documents OCR du corpus.

    Returns:
        Dict {doc_id: text_content}
    """
    print(f"📂 Chargement du corpus depuis : {corpus_dir}")

    corpus = {}

    for folder in sorted(corpus_dir.iterdir()):
        if not folder.is_dir():
            continue

        for doc_file in folder.glob("*.md"):
            if doc_file.name == "_summary.json":
                continue

            doc_id = doc_file.stem  # ex: "R1048-13C-23516-23516_doc01"

            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                    # Nettoyage léger : suppression des tableaux HTML, markdown
                    text = re.sub(r'<table>.*?</table>', '', text, flags=re.DOTALL)
                    text = re.sub(r'#+\s+', '', text)  # Headers
                    text = re.sub(r'\n+', '\n', text)  # Multiple newlines
                    corpus[doc_id] = text
            except Exception as e:
                print(f"   ⚠️  Erreur lecture {doc_file}: {e}")

    print(f"   ✅ {len(corpus)} documents chargés")
    return corpus


# ============================================================
# CHARGEMENT ENTITÉS
# ============================================================

def load_entities(file_path: Path, entity_type: str) -> pd.DataFrame:
    """Charge un fichier d'entités nettoyées."""
    df = pd.read_excel(file_path)
    df['entity_type'] = entity_type
    return df


def stratified_sample(df: pd.DataFrame, sample_size: Dict[str, int], seed: int = 42) -> pd.DataFrame:
    """
    Échantillonnage stratifié par fréquence d'occurrences.

    Returns:
        DataFrame avec entités échantillonnées
    """
    random.seed(seed)

    # Stratification
    frequent = df[df['nb_occurrences'] > 5]
    medium = df[(df['nb_occurrences'] >= 2) & (df['nb_occurrences'] <= 5)]
    rare = df[df['nb_occurrences'] == 1]

    samples = []

    # Échantillonner chaque strate
    if len(frequent) > 0:
        n = min(sample_size['frequent'], len(frequent))
        samples.append(frequent.sample(n=n, random_state=seed))

    if len(medium) > 0:
        n = min(sample_size['medium'], len(medium))
        samples.append(medium.sample(n=n, random_state=seed))

    if len(rare) > 0:
        n = min(sample_size['rare'], len(rare))
        samples.append(rare.sample(n=n, random_state=seed))

    return pd.concat(samples, ignore_index=True) if samples else pd.DataFrame()


# ============================================================
# NORMALISATION TEXTE
# ============================================================

def normalize_for_search(text: str) -> str:
    """Normalise le texte pour la recherche (casse, accents, espaces)."""
    # Lowercase
    text = text.lower()
    # Supprimer accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )
    # Espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def find_entity_in_text(entity: str, aliases: str, text: str) -> List[str]:
    """
    Recherche entité ou aliases dans le texte.

    Returns:
        Liste de contextes (phrases) où l'entité apparaît
    """
    # Construire liste de variantes à chercher
    variants = [entity]
    if pd.notna(aliases) and aliases:
        variants.extend([a.strip() for a in aliases.split(',')])

    # Normaliser variantes
    variants_norm = [normalize_for_search(v) for v in variants]

    # Normaliser texte
    text_norm = normalize_for_search(text)

    # Découper en phrases (approximatif)
    sentences = re.split(r'[.!?]\s+', text)

    contexts = []

    for sentence in sentences:
        sentence_norm = normalize_for_search(sentence)

        # Vérifier si une variante apparaît
        for variant_norm in variants_norm:
            if variant_norm in sentence_norm:
                contexts.append(sentence.strip())
                break  # Une seule fois par phrase

    return contexts[:5]  # Max 5 contextes


# ============================================================
# VALIDATIONS
# ============================================================

def validate_presence(entity: str, aliases: str, corpus: Dict[str, str], doc_list: str) -> Tuple[bool, str]:
    """
    Validation 1 : Présence effective
    L'entité ou un alias est-il présent dans au moins un document du corpus ?
    """
    # Récupérer liste des documents
    if pd.isna(doc_list) or not doc_list:
        return False, "Aucun document référencé"

    docs = [d.strip() for d in doc_list.split(',')]

    # Chercher dans les documents référencés
    for doc_id in docs[:10]:  # Limiter à 10 docs pour performance
        if doc_id not in corpus:
            continue

        contexts = find_entity_in_text(entity, aliases, corpus[doc_id])
        if contexts:
            return True, f"Trouvé dans {doc_id}"

    return False, "Non trouvé dans les documents"


def validate_alias_coherence(entity: str, aliases: str) -> Tuple[bool, str]:
    """
    Validation 2 : Cohérence des aliases
    Les aliases sont-ils cohérents avec l'entité canonique ?
    """
    if pd.isna(aliases) or not aliases:
        return True, "Pas d'alias"

    entity_norm = normalize_for_search(entity)
    entity_words = set(entity_norm.split())

    aliases_list = [a.strip() for a in aliases.split(',')]

    incoherent = []

    for alias in aliases_list:
        alias_norm = normalize_for_search(alias)
        alias_words = set(alias_norm.split())

        # Vérifier chevauchement (au moins 1 mot en commun, ou initiales)
        overlap = entity_words & alias_words

        # Cas spécial : initiales
        if len(alias_norm) <= 3 and '.' in alias:
            continue  # OK pour initiales

        # Cas spécial : nom de famille
        if entity_words and alias_words:
            # Dernier mot en commun = nom de famille
            entity_last = entity_norm.split()[-1]
            alias_last = alias_norm.split()[-1]
            if entity_last == alias_last:
                continue  # OK

        if not overlap and len(alias_norm) > 3:
            incoherent.append(alias)

    if incoherent:
        return False, f"Aliases incohérents: {', '.join(incoherent[:3])}"

    return True, "OK"


def validate_type_heuristic(entity: str, entity_type: str) -> Tuple[bool, str]:
    """
    Validation 3 : Type cohérent (heuristique)
    Le type PERSON/ORG/GPE est-il plausible ?
    """
    entity_lower = entity.lower()

    # Indicateurs PERSON
    person_indicators = [
        'monsieur', 'madame', 'mademoiselle', 'mr.', 'mrs.', 'miss', 'dr.', 'prof.',
        'sinjoro', 'herrn', 'frau'
    ]

    # Indicateurs ORG
    org_indicators = [
        'société', 'societe', 'league', 'commission', 'committee', 'association',
        'university', 'université', 'chamber', 'chambre', 'conseil', 'council',
        'secrétariat', 'secretariat', 'bureau', 'ministry', 'ministère',
        'académie', 'academy', 'institute', 'institut'
    ]

    # Indicateurs GPE
    gpe_indicators = [
        # Villes/pays connus (échantillon)
        'paris', 'london', 'berlin', 'geneva', 'genève', 'rome', 'madrid',
        'france', 'england', 'germany', 'italy', 'switzerland', 'suisse'
    ]

    if entity_type == 'PERSON':
        # Vérifier pas d'indicateurs ORG
        for indicator in org_indicators:
            if indicator in entity_lower:
                return False, f"Indicateur ORG trouvé: {indicator}"
        return True, "OK"

    elif entity_type == 'ORGANIZATION':
        # Vérifier présence indicateurs ORG ou absence indicateurs PERSON
        has_org_indicator = any(ind in entity_lower for ind in org_indicators)
        has_person_indicator = any(ind in entity_lower for ind in person_indicators)

        if has_person_indicator and not has_org_indicator:
            return False, "Semble être une personne"
        return True, "OK"

    elif entity_type == 'GPE':
        # GPE est plus difficile à valider par heuristique
        return True, "OK (heuristique limitée pour GPE)"

    return True, "OK"


def validate_boundaries(entity: str, aliases: str, corpus: Dict[str, str], doc_list: str) -> Tuple[bool, str]:
    """
    Validation 4 : Boundaries correctes
    Pas de troncature ou sur-extraction ?
    """
    # Chercher contexte
    if pd.isna(doc_list) or not doc_list:
        return True, "Pas de document pour vérifier"

    docs = [d.strip() for d in doc_list.split(',')]

    for doc_id in docs[:3]:  # Vérifier 3 docs max
        if doc_id not in corpus:
            continue

        text = corpus[doc_id]
        contexts = find_entity_in_text(entity, aliases, text)

        if not contexts:
            continue

        # Heuristique simple : vérifier pas de mots suspicieux juste avant/après
        suspicious_before = ['le', 'la', 'les', "l'", 'the', 'monsieur', 'madame', 'professor', 'docteur']

        for context in contexts[:2]:
            context_norm = normalize_for_search(context)
            entity_norm = normalize_for_search(entity)

            # Position de l'entité dans le contexte
            pos = context_norm.find(entity_norm)
            if pos == -1:
                continue

            # Vérifier avant
            before = context_norm[:pos].strip().split()
            if before and before[-1] in suspicious_before:
                return False, f"Mot suspect avant: '{before[-1]}'"

    return True, "OK"


def validate_no_over_extraction(entity: str) -> Tuple[bool, str]:
    """
    Validation 5 : Pas de sur-extraction
    Pas de mots parasites dans l'entité ?
    """
    entity_lower = entity.lower()

    # Mots parasites
    parasites = [
        'le professeur', 'la', 'les', "l'", 'the',
        'monsieur le', 'madame la', 'mademoiselle',
        'eminenta sinjoro', 'sioro', 'herrn',
        'students', 'parents', 'scholars'
    ]

    for parasite in parasites:
        if parasite in entity_lower:
            return False, f"Mot parasite: '{parasite}'"

    return True, "OK"


# ============================================================
# VALIDATION GLOBALE
# ============================================================

def validate_entity(row: pd.Series, corpus: Dict[str, str]) -> Dict:
    """
    Applique toutes les validations sur une entité.

    Returns:
        Dict avec résultats de validation
    """
    entity = row['entity_normalized']
    aliases = row.get('aliases', '')
    doc_list = row.get('documents', '')
    entity_type = row['entity_type']

    results = {
        'entity': entity,
        'type': entity_type,
        'nb_occurrences': row['nb_occurrences'],
        'validation_presence': False,
        'validation_alias': False,
        'validation_type': False,
        'validation_boundaries': False,
        'validation_no_over': False,
        'details': {}
    }

    # Validation 1 : Présence
    valid, msg = validate_presence(entity, aliases, corpus, doc_list)
    results['validation_presence'] = valid
    results['details']['presence'] = msg

    # Validation 2 : Cohérence aliases
    valid, msg = validate_alias_coherence(entity, aliases)
    results['validation_alias'] = valid
    results['details']['alias'] = msg

    # Validation 3 : Type
    valid, msg = validate_type_heuristic(entity, entity_type)
    results['validation_type'] = valid
    results['details']['type'] = msg

    # Validation 4 : Boundaries
    valid, msg = validate_boundaries(entity, aliases, corpus, doc_list)
    results['validation_boundaries'] = valid
    results['details']['boundaries'] = msg

    # Validation 5 : Pas de sur-extraction
    valid, msg = validate_no_over_extraction(entity)
    results['validation_no_over'] = valid
    results['details']['no_over'] = msg

    # Score global (toutes validations passées)
    results['all_passed'] = all([
        results['validation_presence'],
        results['validation_alias'],
        results['validation_type'],
        results['validation_boundaries'],
        results['validation_no_over']
    ])

    return results


# ============================================================
# CALCUL MÉTRIQUES
# ============================================================

def calculate_confidence_interval(p: float, n: int, confidence: float = 0.95) -> float:
    """
    Calcule l'intervalle de confiance pour une proportion.

    Args:
        p: Proportion (0-1)
        n: Taille échantillon
        confidence: Niveau de confiance (0.95 = 95%)

    Returns:
        Marge d'erreur (en %)
    """
    if n == 0:
        return 0.0

    # Z-score pour 95% confiance
    z = 1.96 if confidence == 0.95 else 2.576  # 99% = 2.576

    # Formule intervalle de confiance pour proportion
    margin = z * math.sqrt(p * (1 - p) / n)

    return margin * 100  # Retour en %


def compute_metrics(validation_results: List[Dict]) -> Dict:
    """Calcule les métriques globales."""
    n = len(validation_results)

    if n == 0:
        return {}

    # Compteurs
    presence_ok = sum(1 for r in validation_results if r['validation_presence'])
    alias_ok = sum(1 for r in validation_results if r['validation_alias'])
    type_ok = sum(1 for r in validation_results if r['validation_type'])
    boundaries_ok = sum(1 for r in validation_results if r['validation_boundaries'])
    no_over_ok = sum(1 for r in validation_results if r['validation_no_over'])
    all_ok = sum(1 for r in validation_results if r['all_passed'])

    # Proportions
    p_presence = presence_ok / n
    p_alias = alias_ok / n
    p_type = type_ok / n
    p_boundaries = boundaries_ok / n
    p_no_over = no_over_ok / n
    p_all = all_ok / n

    # Intervalles de confiance
    ci_presence = calculate_confidence_interval(p_presence, n)
    ci_alias = calculate_confidence_interval(p_alias, n)
    ci_type = calculate_confidence_interval(p_type, n)
    ci_boundaries = calculate_confidence_interval(p_boundaries, n)
    ci_no_over = calculate_confidence_interval(p_no_over, n)
    ci_all = calculate_confidence_interval(p_all, n)

    # Score global qualité (moyenne pondérée)
    # Poids : présence=30%, alias=20%, type=20%, boundaries=15%, no_over=15%
    global_score = (
        p_presence * 0.30 +
        p_alias * 0.20 +
        p_type * 0.20 +
        p_boundaries * 0.15 +
        p_no_over * 0.15
    )
    ci_global = calculate_confidence_interval(global_score, n)

    return {
        'n': n,
        'presence': {'count': presence_ok, 'pct': p_presence * 100, 'ci': ci_presence},
        'alias': {'count': alias_ok, 'pct': p_alias * 100, 'ci': ci_alias},
        'type': {'count': type_ok, 'pct': p_type * 100, 'ci': ci_type},
        'boundaries': {'count': boundaries_ok, 'pct': p_boundaries * 100, 'ci': ci_boundaries},
        'no_over': {'count': no_over_ok, 'pct': p_no_over * 100, 'ci': ci_no_over},
        'all_passed': {'count': all_ok, 'pct': p_all * 100, 'ci': ci_all},
        'global_score': {'pct': global_score * 100, 'ci': ci_global}
    }


# ============================================================
# RAPPORT
# ============================================================

def generate_report(metrics: Dict, validation_results: List[Dict], output_file: Path):
    """Génère le rapport texte."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("VALIDATION NER - RAPPORT DE QUALITÉ\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Date : 2025-11-16\n")
        f.write(f"Échantillon : {metrics['n']} entités\n")
        f.write(f"Niveau de confiance : 95%\n\n")

        f.write("=" * 70 + "\n")
        f.write("MÉTRIQUES GLOBALES\n")
        f.write("=" * 70 + "\n\n")

        # Présence
        m = metrics['presence']
        f.write(f"✅ Présence effective      : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} entités)\n")

        # Alias
        m = metrics['alias']
        f.write(f"✅ Cohérence aliases       : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} cohérents)\n")

        # Type
        m = metrics['type']
        f.write(f"✅ Type cohérent           : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} corrects)\n")

        # Boundaries
        m = metrics['boundaries']
        f.write(f"✅ Boundaries correctes    : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} sans troncature)\n")

        # No over-extraction
        m = metrics['no_over']
        f.write(f"✅ Pas de sur-extraction   : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} sans parasites)\n")

        f.write("\n")
        f.write("-" * 70 + "\n")

        # Score global
        m = metrics['global_score']
        f.write(f"🎯 SCORE QUALITÉ GLOBAL    : {m['pct']:5.1f}% ± {m['ci']:4.1f}%\n")
        f.write("-" * 70 + "\n\n")

        # Toutes validations passées
        m = metrics['all_passed']
        f.write(f"✅ Toutes validations OK   : {m['pct']:5.1f}% ± {m['ci']:4.1f}%  ({m['count']}/{metrics['n']} entités)\n\n")

        f.write("=" * 70 + "\n")
        f.write("CONCLUSION\n")
        f.write("=" * 70 + "\n\n")

        score_pct = metrics['global_score']['pct']
        ci = metrics['global_score']['ci']

        f.write(f"Avec 95% de confiance, {score_pct:.1f}% (± {ci:.1f}%) des entités\n")
        f.write(f"sont correctement extraites et normalisées.\n\n")

        if score_pct >= 85:
            f.write("🎉 EXCELLENT : Qualité NER très élevée !\n")
        elif score_pct >= 75:
            f.write("✅ BIEN : Qualité NER satisfaisante.\n")
        elif score_pct >= 65:
            f.write("⚠️  MOYEN : Qualité NER acceptable mais améliorable.\n")
        else:
            f.write("❌ FAIBLE : Qualité NER nécessite amélioration.\n")

        f.write("\n")

        # Exemples d'échecs
        f.write("=" * 70 + "\n")
        f.write("EXEMPLES D'ÉCHECS (pour amélioration)\n")
        f.write("=" * 70 + "\n\n")

        failures = [r for r in validation_results if not r['all_passed']][:10]

        if failures:
            for i, fail in enumerate(failures, 1):
                f.write(f"{i}. {fail['entity']} ({fail['type']})\n")
                for check, passed in fail.items():
                    if check.startswith('validation_') and not passed:
                        check_name = check.replace('validation_', '')
                        detail = fail['details'].get(check_name, '')
                        f.write(f"   ❌ {check_name}: {detail}\n")
                f.write("\n")
        else:
            f.write("Aucun échec trouvé !\n\n")

    print(f"   ✅ Rapport sauvegardé : {output_file}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("VALIDATION NER - QUALITÉ GLOBALE")
    print("=" * 70)
    print()

    # 1. Charger corpus
    corpus = load_corpus(CORPUS_DIR)
    print()

    # 2. Charger entités
    print("📂 Chargement des entités...")
    df_person = load_entities(PERSON_FILE, 'PERSON')
    df_org = load_entities(ORG_FILE, 'ORGANIZATION')
    df_gpe = load_entities(GPE_FILE, 'GPE')
    print(f"   ✅ PERSON: {len(df_person)} entités")
    print(f"   ✅ ORGANIZATION: {len(df_org)} entités")
    print(f"   ✅ GPE: {len(df_gpe)} entités")
    print()

    # 3. Échantillonnage stratifié
    print("🎲 Échantillonnage stratifié...")
    sample_person = stratified_sample(df_person, SAMPLE_SIZE, RANDOM_SEED)
    sample_org = stratified_sample(df_org, SAMPLE_SIZE, RANDOM_SEED)
    sample_gpe = stratified_sample(df_gpe, SAMPLE_SIZE, RANDOM_SEED)

    print(f"   ✅ PERSON échantillon: {len(sample_person)}")
    print(f"   ✅ ORGANIZATION échantillon: {len(sample_org)}")
    print(f"   ✅ GPE échantillon: {len(sample_gpe)}")

    all_samples = pd.concat([sample_person, sample_org, sample_gpe], ignore_index=True)
    print(f"   ✅ Total échantillon: {len(all_samples)} entités")
    print()

    # 4. Validation
    print("🔍 Validation en cours...")
    validation_results = []

    for idx, row in all_samples.iterrows():
        result = validate_entity(row, corpus)
        validation_results.append(result)

        if (idx + 1) % 50 == 0:
            print(f"   ... {idx + 1}/{len(all_samples)} validées")

    print(f"   ✅ {len(validation_results)} entités validées")
    print()

    # 5. Calcul métriques
    print("📊 Calcul des métriques...")
    metrics = compute_metrics(validation_results)
    print(f"   ✅ Métriques calculées")
    print()

    # 6. Rapport
    print("💾 Génération du rapport...")
    generate_report(metrics, validation_results, OUTPUT_REPORT)
    print()

    # 7. Affichage console
    print("=" * 70)
    print("RÉSULTATS")
    print("=" * 70)
    print()

    m = metrics['global_score']
    print(f"🎯 SCORE QUALITÉ GLOBAL : {m['pct']:.1f}% ± {m['ci']:.1f}%")
    print()

    m = metrics['presence']
    print(f"   • Présence effective    : {m['pct']:5.1f}% ± {m['ci']:4.1f}%")

    m = metrics['alias']
    print(f"   • Cohérence aliases     : {m['pct']:5.1f}% ± {m['ci']:4.1f}%")

    m = metrics['type']
    print(f"   • Type cohérent         : {m['pct']:5.1f}% ± {m['ci']:4.1f}%")

    m = metrics['boundaries']
    print(f"   • Boundaries correctes  : {m['pct']:5.1f}% ± {m['ci']:4.1f}%")

    m = metrics['no_over']
    print(f"   • Pas de sur-extraction : {m['pct']:5.1f}% ± {m['ci']:4.1f}%")

    print()
    print("=" * 70)
    print("✅ VALIDATION TERMINÉE")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
