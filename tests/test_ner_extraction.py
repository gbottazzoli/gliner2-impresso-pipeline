#!/usr/bin/env python3
"""
Script de test - Extraction NER avec GLiNER2 vers Excel
Teste sur un échantillon de 5 documents
"""

import re
from pathlib import Path
import pandas as pd
from gliner import GLiNER


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
MODEL_PATH = PROJECT_ROOT / "models/checkpoints/gliner_multi-v2.1"
DATA_DIR = PROJECT_ROOT / "data/annotated/ocr_results"
OUTPUT_EXCEL = PROJECT_ROOT / "outputs/tests/test_ner_results.xlsx"

# Labels NER à extraire
LABELS = ["person", "organization", "location", "title", "date"]


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


def parse_person_name(full_name):
    """
    Parse un nom de personne pour extraire titre, prénom, nom
    Ex: "Monsieur Bergson" -> {"title": "Monsieur", "first": "", "last": "Bergson"}
    Ex: "Prof. Gilbert Murray" -> {"title": "Prof.", "first": "Gilbert", "last": "Murray"}
    """
    # Normalisation des titres
    titles_map = {
        "M.": "Monsieur",
        "Mme": "Madame",
        "Mme.": "Madame",
        "Mlle": "Mademoiselle",
        "Mlle.": "Mademoiselle",
        "Prof.": "Professeur",
        "Dr.": "Docteur",
        "Me": "Maître",
        "Sr.": "Sénateur"
    }

    # Liste des titres possibles
    known_titles = [
        "Monsieur", "Madame", "Mademoiselle",
        "Professeur", "Docteur", "Sénateur", "Maître",
        "M.", "Mme", "Mme.", "Mlle", "Mlle.", "Prof.", "Dr.", "Me", "Sr."
    ]

    name = full_name.strip()
    title = ""
    first = ""
    last = ""

    # Chercher un titre au début
    for t in known_titles:
        if name.startswith(t + " ") or name.startswith(t):
            title = titles_map.get(t, t)
            name = name[len(t):].strip()
            break

    # Séparer prénom et nom (simple heuristique)
    parts = name.split()
    if len(parts) == 1:
        last = parts[0]
    elif len(parts) == 2:
        first = parts[0]
        last = parts[1]
    elif len(parts) > 2:
        # Prendre le premier comme prénom, le reste comme nom
        first = parts[0]
        last = " ".join(parts[1:])

    return {
        "title": title,
        "first_name": first,
        "last_name": last
    }


def extract_context(entity, text, window=100):
    """Extrait le contexte autour d'une entité pour trouver organisation, lieu, rôle"""
    start = max(0, entity['start'] - window)
    end = min(len(text), entity['end'] + window)
    context = text[start:end]
    return context


def process_document(file_path, model):
    """Traite un document et extrait les entités NER"""
    print(f"\n📄 Traitement: {file_path.name}")

    # Lire le document
    text = file_path.read_text(encoding='utf-8')

    # Nettoyer
    text_clean = clean_markdown(text)

    # Extraction NER
    entities = model.predict_entities(text_clean, LABELS, threshold=0.4)

    print(f"   → {len(entities)} entités brutes détectées")

    # Post-traitement
    processed_entities = []

    for entity in entities:
        # Base
        result = {
            "nom_complet": entity['text'],
            "type_entite": entity['label'],
            "score_confiance": round(entity['score'], 3),
            "source_document": file_path.name,
            "contexte": extract_context(entity, text_clean)[:200]  # 200 chars max
        }

        # Si c'est une personne, parser le nom
        if entity['label'].lower() == 'person':
            parsed = parse_person_name(entity['text'])
            result.update(parsed)
        else:
            result.update({
                "title": "",
                "first_name": "",
                "last_name": ""
            })

        # Champs supplémentaires (à remplir plus tard via contexte ou règles)
        result.update({
            "organisation": "",  # À extraire du contexte
            "ville": "",
            "pays": "",
            "role_fonction": ""
        })

        processed_entities.append(result)

    return processed_entities


def main():
    """Fonction principale"""
    print("=" * 70)
    print("  TEST EXTRACTION NER → EXCEL")
    print("=" * 70)

    # Charger le modèle (utiliser le chemin absolu direct)
    model_path_abs = "/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1"
    print(f"\n📦 Chargement du modèle: {model_path_abs}")
    model = GLiNER.from_pretrained(model_path_abs)
    print("✅ Modèle chargé")

    # Sélectionner 5 documents de test
    sample_folder = DATA_DIR / "R1048-13C-23516-23516"
    sample_docs = sorted(sample_folder.glob("*.md"))[:5]

    print(f"\n📂 Documents à traiter: {len(sample_docs)}")
    for doc in sample_docs:
        print(f"   - {doc.name}")

    # Traiter tous les documents
    all_entities = []

    for doc in sample_docs:
        entities = process_document(doc, model)
        all_entities.extend(entities)

    # Créer DataFrame
    df = pd.DataFrame(all_entities)

    # Réordonner les colonnes
    column_order = [
        "nom_complet",
        "title",
        "first_name",
        "last_name",
        "type_entite",
        "organisation",
        "ville",
        "pays",
        "role_fonction",
        "source_document",
        "score_confiance",
        "contexte"
    ]

    df = df[column_order]

    # Sauvegarder en Excel
    OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_EXCEL, index=False, sheet_name="Entités NER")

    print(f"\n{'='*70}")
    print(f"✅ Extraction terminée!")
    print(f"   Total entités: {len(all_entities)}")
    print(f"   Fichier Excel: {OUTPUT_EXCEL}")
    print(f"{'='*70}")

    # Afficher statistiques
    print("\n📊 Statistiques par type d'entité:")
    type_counts = df['type_entite'].value_counts()
    for entity_type, count in type_counts.items():
        print(f"   - {entity_type}: {count}")

    print("\n📋 Aperçu des premières entités (personnes):")
    persons = df[df['type_entite'] == 'person'].head(10)
    for idx, row in persons.iterrows():
        print(f"   • {row['nom_complet']:30s} → Titre: {row['title']:15s} | Score: {row['score_confiance']:.2f}")

    print(f"\n💡 Ouvrez le fichier Excel pour voir tous les résultats:")
    print(f"   {OUTPUT_EXCEL}")


if __name__ == "__main__":
    main()
