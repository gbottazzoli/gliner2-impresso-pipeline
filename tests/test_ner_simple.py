#!/usr/bin/env python3
"""
Script de test SIMPLIFIÉ - Extraction NER brute avec GLiNER2
Version simple: juste les détections, pas de parsing
"""

import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
from gliner import GLiNER


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data/annotated/ocr_results"
OUTPUT_EXCEL = PROJECT_ROOT / "outputs/tests/test_ner_simple.xlsx"

# Labels NER
LABELS = ["person", "organization", "location"]

# Score minimum
MIN_SCORE = 0.50


def clean_markdown(text):
    """Nettoie le texte Markdown OCR"""
    # Enlever les tables HTML
    text = re.sub(r'<table>.*?</table>', '', text, flags=re.DOTALL|re.IGNORECASE)

    # Enlever les headers Markdown
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)

    # Enlever les séparateurs
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)

    # Enlever lignes vides multiples
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def smart_chunk(text, max_length=400, overlap=50):
    """Découpe en chunks avec overlap pour éviter troncature"""
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_length = len(sent.split())

        if current_length + sent_length > max_length and current_chunk:
            chunks.append(" ".join(current_chunk))

            # Overlap
            overlap_sentences = []
            overlap_len = 0
            for s in reversed(current_chunk):
                s_len = len(s.split())
                if overlap_len + s_len > overlap:
                    break
                overlap_sentences.insert(0, s)
                overlap_len += s_len

            current_chunk = overlap_sentences + [sent]
            current_length = sum(len(s.split()) for s in current_chunk)
        else:
            current_chunk.append(sent)
            current_length += sent_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_document(file_path, model):
    """Traite un document - version simplifiée"""
    # Lire et nettoyer
    text = file_path.read_text(encoding='utf-8')
    text_clean = clean_markdown(text)

    # Découper en chunks
    chunks = smart_chunk(text_clean, max_length=400, overlap=50)

    # Extraire NER sur tous les chunks
    all_entities = []

    for chunk in chunks:
        entities = model.predict_entities(chunk, LABELS, threshold=0.35)

        for entity in entities:
            # Filtrer par score
            if entity['score'] >= MIN_SCORE:
                all_entities.append({
                    "nom_complet_original": entity['text'],
                    "type_entite": entity['label'],
                    "score_confiance": round(entity['score'], 3),
                    "source_document": file_path.name
                })

    return all_entities


def filter_incomplete_persons(entities_list):
    """Filtre les mentions incomplètes de personnes (titres seuls)"""
    filtered = []

    # Titres/civilités à détecter (en minuscules)
    titles = [
        "monsieur", "madame", "mademoiselle", "madam",  # madam = erreur OCR ou anglais
        "m.", "mme", "mme.", "mlle", "mlle.",
        "professeur", "prof.", "docteur", "dr.", "sénateur", "député",
        "président", "délégué", "ministre", "ambassadeur", "directeur",
        "le", "la", "l'", "sir", "lord", "lady"
    ]

    for entity in entities_list:
        # Si ce n'est pas une personne, on garde
        if entity['type_entite'] != 'person':
            filtered.append(entity)
            continue

        # Pour les personnes: vérifier qu'il y a un nom (pas juste un titre)
        name = entity['nom_complet_original'].lower().strip()

        # Enlever tous les titres/civilités connus
        words = name.split()
        non_title_words = [w for w in words if w not in titles]

        # Si il reste au moins 1 mot (un vrai nom), on garde
        if len(non_title_words) >= 1:
            filtered.append(entity)
        else:
            # Sinon c'est juste un titre, on ignore
            pass

    return filtered


def deduplicate_simple(entities_list):
    """Déduplication simple par nom exact (case-insensitive)"""
    groups = defaultdict(list)

    for entity in entities_list:
        # Clé: nom normalisé + type
        key = f"{entity['nom_complet_original'].lower().strip()}_{entity['type_entite']}"
        groups[key].append(entity)

    deduplicated = []

    for key, group in groups.items():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # Garder celle avec le meilleur score
            best = max(group, key=lambda x: x['score_confiance'])
            deduplicated.append(best)

    return deduplicated


def main():
    """Fonction principale"""
    print("=" * 80)
    print("  EXTRACTION NER SIMPLIFIÉE - Version brute")
    print("=" * 80)

    # Charger le modèle
    model_path = "/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1"
    print(f"\n📦 Chargement du modèle...")
    model = GLiNER.from_pretrained(model_path)
    print("✅ Modèle chargé")

    # Sélectionner documents de test (UNIQUEMENT ocr_results)
    sample_folder = DATA_DIR / "R1048-13C-23516-23516"
    sample_docs = sorted(sample_folder.glob("*.md"))[:5]

    print(f"\n📂 Documents à traiter: {len(sample_docs)}")
    for doc in sample_docs:
        print(f"   - {doc.name}")

    # Traiter
    all_entities = []

    for doc in sample_docs:
        print(f"\n📄 {doc.name}")
        entities = process_document(doc, model)
        print(f"   → {len(entities)} entités détectées")
        all_entities.extend(entities)

    print(f"\n📊 Total avant filtrage: {len(all_entities)}")

    # Filtrage des titres seuls (personnes sans nom)
    filtered = filter_incomplete_persons(all_entities)
    print(f"📊 Après filtrage titres seuls: {len(filtered)}")

    # Déduplication
    deduplicated = deduplicate_simple(filtered)
    print(f"📊 Après déduplication: {len(deduplicated)}")

    # Créer DataFrame
    df = pd.DataFrame(deduplicated)

    # Trier par type puis score
    df = df.sort_values(['type_entite', 'score_confiance'], ascending=[True, False])

    # Sauvegarder
    OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_EXCEL, index=False, sheet_name="NER Brute")

    print(f"\n{'='*80}")
    print(f"✅ Fichier: {OUTPUT_EXCEL}")
    print(f"{'='*80}")

    # Stats
    print("\n📊 Statistiques par type:")
    for entity_type, count in df['type_entite'].value_counts().items():
        print(f"   - {entity_type}: {count}")

    # Aperçu par type
    print("\n" + "=" * 80)
    print("APERÇU DES ENTITÉS")
    print("=" * 80)

    for entity_type in ['person', 'organization', 'location']:
        subset = df[df['type_entite'] == entity_type]
        if len(subset) > 0:
            print(f"\n{entity_type.upper()} (top 10):")
            for idx, row in subset.head(10).iterrows():
                print(f"   • {row['nom_complet_original']:50s} | Score: {row['score_confiance']:.2f} | {row['source_document']}")

    print(f"\n💡 Ouvrez: {OUTPUT_EXCEL}")


if __name__ == "__main__":
    main()
