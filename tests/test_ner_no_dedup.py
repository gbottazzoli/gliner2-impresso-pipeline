#!/usr/bin/env python3
"""
Script test - Extraction NER SANS déduplication
Garde TOUTES les mentions dans CHAQUE document
"""

import re
from pathlib import Path
import pandas as pd
from gliner import GLiNER


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data/annotated/ocr_results"
OUTPUT_EXCEL = PROJECT_ROOT / "outputs/tests/test_ner_no_dedup_R1048-13C-25688-23516.xlsx"

# Labels NER
LABELS = ["person", "organization", "location"]

# Score minimum
MIN_SCORE = 0.50


def clean_markdown(text):
    """Nettoie le texte Markdown OCR"""
    # CORRECTION: Extraire le contenu des tables au lieu de les supprimer
    def extract_table_text(match):
        table_html = match.group(0)
        # Extraire tout le texte entre les balises <td> et <th>
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', table_html, flags=re.DOTALL|re.IGNORECASE)
        # Nettoyer les cellules et joindre avec des espaces
        cleaned_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
        # Filtrer les cellules vides
        cleaned_cells = [c for c in cleaned_cells if c]
        return ' '.join(cleaned_cells)

    text = re.sub(r'<table>.*?</table>', extract_table_text, text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---+$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def smart_chunk(text, max_length=400, overlap=50):
    """Découpe en chunks avec overlap"""
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_length = len(sent.split())

        if current_length + sent_length > max_length and current_chunk:
            chunks.append(" ".join(current_chunk))

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


def filter_incomplete_persons(entities_list):
    """Filtre les mentions incomplètes de personnes (titres seuls)"""
    filtered = []

    titles = [
        "monsieur", "madame", "mademoiselle", "madam",
        "m.", "mme", "mme.", "mlle", "mlle.",
        "professeur", "prof.", "docteur", "dr.", "sénateur", "député",
        "président", "délégué", "ministre", "ambassadeur", "directeur",
        "le", "la", "l'", "sir", "lord", "lady"
    ]

    for entity in entities_list:
        if entity['type_entite'] != 'person':
            filtered.append(entity)
            continue

        name = entity['nom_complet_original'].lower().strip()
        words = name.split()
        non_title_words = [w for w in words if w not in titles]

        if len(non_title_words) >= 1:
            filtered.append(entity)

    return filtered


def process_document(file_path, model):
    """Traite un document - garde TOUTES les mentions"""
    text = file_path.read_text(encoding='utf-8')
    text_clean = clean_markdown(text)

    chunks = smart_chunk(text_clean, max_length=400, overlap=50)

    all_entities = []

    for chunk in chunks:
        entities = model.predict_entities(chunk, LABELS, threshold=0.35)

        for entity in entities:
            if entity['score'] >= MIN_SCORE:
                all_entities.append({
                    "nom_complet_original": entity['text'],
                    "type_entite": entity['label'],
                    "score_confiance": round(entity['score'], 3),
                    "source_document": file_path.name
                })

    return all_entities


def main():
    """Fonction principale"""
    print("=" * 80)
    print("  EXTRACTION NER SANS DÉDUPLICATION")
    print("  Toutes les mentions conservées par document")
    print("=" * 80)

    # Charger le modèle
    model_path = "/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1"
    print(f"\n📦 Chargement du modèle...")
    model = GLiNER.from_pretrained(model_path)
    print("✅ Modèle chargé")

    # Documents de test - NOUVEAU DOSSIER
    sample_folder = DATA_DIR / "R1048-13C-25688-23516"
    sample_docs = sorted(sample_folder.glob("*.md"))[:5]

    print(f"\n📂 Dossier: R1048-13C-25688-23516")
    print(f"   Documents: {len(sample_docs)}")
    for doc in sample_docs:
        print(f"   - {doc.name}")

    # Traiter
    all_entities = []

    for doc in sample_docs:
        print(f"\n📄 {doc.name}")
        entities = process_document(doc, model)
        print(f"   → {len(entities)} entités (avant filtrage titres)")
        all_entities.extend(entities)

    print(f"\n📊 Total avant filtrage titres: {len(all_entities)}")

    # Filtrage titres seuls uniquement
    filtered = filter_incomplete_persons(all_entities)
    print(f"📊 Après filtrage titres seuls: {len(filtered)}")

    # PAS DE DÉDUPLICATION - On garde tout!
    print(f"📊 Total final (SANS déduplication): {len(filtered)}")

    # Créer DataFrame
    df = pd.DataFrame(filtered)

    # Trier par type puis document puis score
    df = df.sort_values(['type_entite', 'source_document', 'score_confiance'],
                        ascending=[True, True, False])

    # Sauvegarder avec 3 sheets séparés (person, organization, location)
    OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        # Sheet 1: Personnes
        df_persons = df[df['type_entite'] == 'person'].sort_values(
            ['source_document', 'score_confiance'], ascending=[True, False]
        )
        df_persons.to_excel(writer, sheet_name='PERSON', index=False)

        # Sheet 2: Organisations
        df_orgs = df[df['type_entite'] == 'organization'].sort_values(
            ['source_document', 'score_confiance'], ascending=[True, False]
        )
        df_orgs.to_excel(writer, sheet_name='ORGANIZATION', index=False)

        # Sheet 3: Lieux (GPE - Geo-Political Entity)
        df_locs = df[df['type_entite'] == 'location'].sort_values(
            ['source_document', 'score_confiance'], ascending=[True, False]
        )
        df_locs.to_excel(writer, sheet_name='GPE', index=False)

    print(f"\n{'='*80}")
    print(f"✅ Fichier: {OUTPUT_EXCEL}")
    print(f"   3 sheets séparés: PERSON | ORGANIZATION | GPE")
    print(f"{'='*80}")

    # Stats par type
    print("\n📊 Statistiques par type (sheets):")
    print(f"   - Sheet PERSON: {len(df_persons)} occurrences")
    print(f"   - Sheet ORGANIZATION: {len(df_orgs)} occurrences")
    print(f"   - Sheet GPE (lieux): {len(df_locs)} occurrences")

    # Aperçu par document
    print("\n" + "=" * 80)
    print("DÉTAIL PAR DOCUMENT")
    print("=" * 80)

    for doc_name in df['source_document'].unique():
        doc_entities = df[df['source_document'] == doc_name]
        print(f"\n{doc_name}:")
        print(f"  Total: {len(doc_entities)} entités")

        for entity_type in ['person', 'organization', 'location']:
            subset = doc_entities[doc_entities['type_entite'] == entity_type]
            if len(subset) > 0:
                print(f"  {entity_type.upper()} ({len(subset)}):")
                for idx, row in subset.iterrows():
                    print(f"    • {row['nom_complet_original']:50s} | {row['score_confiance']:.2f}")

    print(f"\n💡 Ouvrez: {OUTPUT_EXCEL}")
    print("\nToutes les mentions sont conservées (pas de déduplication)")


if __name__ == "__main__":
    main()
