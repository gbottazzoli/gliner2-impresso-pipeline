#!/usr/bin/env python3
"""
Script de test AMÉLIORÉ - Extraction NER avec GLiNER2 vers Excel
Version 2: Titres diplomatiques, filtrage, déduplication, chunking
"""

import re
from pathlib import Path
from collections import defaultdict
import pandas as pd
from gliner import GLiNER


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data/annotated/ocr_results"
OUTPUT_EXCEL = PROJECT_ROOT / "outputs/tests/test_ner_results_v2.xlsx"

# Labels NER à extraire (sans date)
LABELS = ["person", "organization", "location"]

# Score minimum pour filtrage
MIN_SCORE_PERSON = 0.60
MIN_SCORE_ORG = 0.70
MIN_SCORE_LOC = 0.65


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
    """
    Découpe intelligente en chunks avec overlap
    Préserve les phrases complètes
    """
    # Séparer en phrases (simple heuristique)
    sentences = re.split(r'(?<=[.!?])\s+', text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sent in sentences:
        sent_length = len(sent.split())

        if current_length + sent_length > max_length and current_chunk:
            # Sauvegarder le chunk actuel
            chunks.append(" ".join(current_chunk))

            # Commencer nouveau chunk avec overlap (garder dernières phrases)
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

    # Dernier chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def parse_diplomatic_title(full_name):
    """
    Parse les titres diplomatiques composés
    Ex: "Monsieur le Professeur Gilbert Murray"
        → civilite: Monsieur
          titre_honorifique: Professeur
          titre_complet: Monsieur le Professeur
          prenom: Gilbert
          nom: Murray
    """
    # Normalisation des abréviations
    titles_map = {
        "M.": "Monsieur",
        "Mme": "Madame",
        "Mme.": "Madame",
        "Mlle": "Mademoiselle",
        "Mlle.": "Mademoiselle",
        "Prof.": "Professeur",
        "Dr.": "Docteur",
        "Me": "Maître"
    }

    # Civilités
    civilites = ["Monsieur", "Madame", "Mademoiselle", "M.", "Mme", "Mme.", "Mlle", "Mlle."]

    # Titres honorifiques (après "le/la")
    titres_honorifiques = [
        "Professeur", "Docteur", "Sénateur", "Député", "Président",
        "Délégué", "Ministre", "Ambassadeur", "Baron", "Comte",
        "Directeur", "Secrétaire", "Rapporteur", "Général",
        "Prof.", "Dr."
    ]

    name = full_name.strip()
    civilite = ""
    titre_honorifique = ""
    titre_complet = ""
    prenom = ""
    nom = ""

    # 1. Normaliser les abréviations
    for abbrev, full in titles_map.items():
        if name.startswith(abbrev + " "):
            name = name.replace(abbrev, full, 1)

    original_name = name

    # 2. Extraire civilité
    for civ in civilites:
        if name.startswith(civ + " ") or name == civ:
            civilite = titles_map.get(civ, civ)
            name = name[len(civ):].strip()
            break

    # 3. Extraire titre honorifique (avec "le/la/l'")
    # Patterns: "le Professeur", "la Déléguée", "l'Ambassadeur"
    pattern = r"^(le|la|l')\s+([A-ZÉ][a-zéèêëàâîôûç]+)"
    match = re.match(pattern, name)
    if match:
        titre_candidat = match.group(2)
        # Vérifier que c'est bien un titre connu
        for titre in titres_honorifiques:
            if titre_candidat.lower() == titre.lower():
                titre_honorifique = titre
                # Construire titre complet
                titre_complet = civilite + (" " if civilite else "") + match.group(1) + " " + titre_honorifique
                # Enlever du nom
                name = name[match.end():].strip()
                break

    # 4. Sinon chercher titre honorifique direct (sans "le/la")
    if not titre_honorifique:
        for titre in titres_honorifiques:
            if name.startswith(titre + " ") or name == titre:
                titre_honorifique = titre
                titre_complet = civilite + (" " if civilite else "") + titre_honorifique
                name = name[len(titre):].strip()
                break

    # 5. Si on a juste civilité
    if civilite and not titre_honorifique:
        titre_complet = civilite

    # 6. Extraire prénom et nom du reste
    if name:
        parts = name.split()
        if len(parts) == 1:
            nom = parts[0]
        elif len(parts) == 2:
            prenom = parts[0]
            nom = parts[1]
        elif len(parts) > 2:
            # Gérer noms composés (ex: "de Torres Quevedo")
            # Heuristique: si un mot commence par minuscule (de, von, van), c'est partie du nom
            prenom_parts = []
            nom_parts = []
            in_nom = False

            for i, part in enumerate(parts):
                if part[0].islower() or in_nom:  # "de", "von", "van", ou déjà dans nom
                    nom_parts.append(part)
                    in_nom = True
                else:
                    if not in_nom:
                        prenom_parts.append(part)
                    else:
                        nom_parts.append(part)

            if not nom_parts:  # Tous en prénom, dernier devient nom
                nom = prenom_parts[-1]
                prenom = " ".join(prenom_parts[:-1])
            else:
                prenom = " ".join(prenom_parts)
                nom = " ".join(nom_parts)

    return {
        "nom_complet_original": full_name,
        "civilite": civilite,
        "titre_honorifique": titre_honorifique,
        "titre_complet": titre_complet,
        "prenom": prenom,
        "nom_famille": nom
    }


def extract_organization_from_context(entity_text, context):
    """Extrait l'organisation depuis le contexte"""
    # Patterns courants pour organisations
    org_patterns = [
        r"(Commission [^,\.]+)",
        r"(Institut [^,\.]+)",
        r"(Université [^,\.]+)",
        r"(Laboratoire [^,\.]+)",
        r"(Chambre [^,\.]+)",
        r"(Assemblée [^,\.]+)",
        r"(Société [^,\.]+)",
        r"(Comité [^,\.]+)"
    ]

    for pattern in org_patterns:
        match = re.search(pattern, context)
        if match:
            return match.group(1).strip()

    return ""


def extract_location_from_context(entity_text, context):
    """Extrait ville et/ou pays depuis le contexte"""
    # Villes connues dans le corpus
    villes = [
        "Paris", "Genève", "Rome", "Madrid", "Oxford", "Bruxelles",
        "Rio de Janeiro", "Berne", "Berlin", "Londres", "Christiania",
        "Baden-Baden", "California"
    ]

    # Pays connus
    pays = [
        "France", "Suisse", "Italie", "Espagne", "Angleterre",
        "Brésil", "Belgique", "Allemagne", "Danemark", "Norvège",
        "États-Unis", "U.S.A.", "Royaume-Uni"
    ]

    ville_trouvee = ""
    pays_trouve = ""

    # Chercher ville
    for ville in villes:
        if ville.lower() in context.lower():
            ville_trouvee = ville
            break

    # Chercher pays
    for pays_name in pays:
        if pays_name.lower() in context.lower():
            pays_trouve = pays_name
            break

    return ville_trouvee, pays_trouve


def extract_role_from_context(entity_text, context):
    """Extrait le rôle/fonction depuis le contexte"""
    # Patterns pour rôles
    role_patterns = [
        r"président[e]?\s+de\s+([^,\.]+)",
        r"délégué[e]?\s+de\s+([^,\.]+)",
        r"membre\s+de\s+([^,\.]+)",
        r"rapporteur\s+de\s+([^,\.]+)",
        r"directeur\s+de\s+([^,\.]+)",
        r"représentant[e]?\s+de\s+([^,\.]+)"
    ]

    for pattern in role_patterns:
        match = re.search(pattern, context.lower())
        if match:
            role = match.group(0).strip()
            return role.capitalize()

    return ""


def deduplicate_entities(entities_list):
    """Déduplique les entités similaires"""
    # Grouper par nom normalisé
    groups = defaultdict(list)

    for entity in entities_list:
        # Clé de normalisation
        if entity['type_entite'] == 'person':
            # Pour personnes: utiliser nom_famille + prenom
            key = f"{entity['nom_famille']}_{entity['prenom']}".lower().strip()
        else:
            # Pour orgs et lieux: normaliser le nom complet
            key = entity['nom_complet_original'].lower().strip()
            # Normaliser la casse
            key = re.sub(r'\s+', ' ', key)

        groups[key].append(entity)

    # Pour chaque groupe, garder celle avec le meilleur score
    deduplicated = []

    for key, group in groups.items():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # Trier par score et prendre la meilleure
            best = max(group, key=lambda x: x['score_confiance'])

            # Enrichir avec infos des autres (si vides)
            for entity in group:
                if not best['organisation'] and entity['organisation']:
                    best['organisation'] = entity['organisation']
                if not best['ville'] and entity['ville']:
                    best['ville'] = entity['ville']
                if not best['pays'] and entity['pays']:
                    best['pays'] = entity['pays']
                if not best['role_fonction'] and entity['role_fonction']:
                    best['role_fonction'] = entity['role_fonction']

            deduplicated.append(best)

    return deduplicated


def process_document(file_path, model):
    """Traite un document avec chunking et extraction améliorée"""
    print(f"\n📄 {file_path.name}")

    # Lire et nettoyer
    text = file_path.read_text(encoding='utf-8')
    text_clean = clean_markdown(text)

    # Découper en chunks intelligents
    chunks = smart_chunk(text_clean, max_length=400, overlap=50)
    print(f"   → {len(chunks)} chunks")

    # Extraire NER sur tous les chunks
    all_entities = []

    for chunk in chunks:
        entities = model.predict_entities(chunk, LABELS, threshold=0.35)

        for entity in entities:
            # Calculer position dans le texte original (approximative)
            entity['full_text'] = text_clean
            all_entities.append(entity)

    print(f"   → {len(all_entities)} entités brutes")

    # Filtrage par score
    filtered = []
    for entity in all_entities:
        label = entity['label'].lower()
        score = entity['score']

        if label == 'person' and score >= MIN_SCORE_PERSON:
            filtered.append(entity)
        elif label == 'organization' and score >= MIN_SCORE_ORG:
            filtered.append(entity)
        elif label == 'location' and score >= MIN_SCORE_LOC:
            filtered.append(entity)

    print(f"   → {len(filtered)} entités après filtrage")

    # Post-traitement
    processed = []

    for entity in filtered:
        # Extraire contexte
        context = extract_context_enhanced(entity, text_clean)

        # Base
        result = {
            "type_entite": entity['label'],
            "score_confiance": round(entity['score'], 3),
            "source_document": file_path.name
        }

        # Si personne, parser le nom
        if entity['label'].lower() == 'person':
            parsed = parse_diplomatic_title(entity['text'])
            result.update(parsed)

            # Extraire infos contextuelles
            org = extract_organization_from_context(entity['text'], context)
            ville, pays = extract_location_from_context(entity['text'], context)
            role = extract_role_from_context(entity['text'], context)

            result.update({
                "organisation": org,
                "ville": ville,
                "pays": pays,
                "role_fonction": role
            })
        else:
            # Organisation ou lieu
            result.update({
                "nom_complet_original": entity['text'],
                "civilite": "",
                "titre_honorifique": "",
                "titre_complet": "",
                "prenom": "",
                "nom_famille": "",
                "organisation": "",
                "ville": "",
                "pays": "",
                "role_fonction": ""
            })

        processed.append(result)

    return processed


def extract_context_enhanced(entity, full_text, window=150):
    """Extrait contexte étendu autour d'une entité"""
    # Trouver l'entité dans le texte
    text_lower = full_text.lower()
    entity_lower = entity['text'].lower()

    pos = text_lower.find(entity_lower)
    if pos == -1:
        return ""

    start = max(0, pos - window)
    end = min(len(full_text), pos + len(entity['text']) + window)

    return full_text[start:end]


def main():
    """Fonction principale"""
    print("=" * 80)
    print("  TEST EXTRACTION NER V2 - VERSION AMÉLIORÉE")
    print("=" * 80)

    # Charger le modèle
    model_path = "/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1"
    print(f"\n📦 Chargement du modèle GLiNER2...")
    model = GLiNER.from_pretrained(model_path)
    print("✅ Modèle chargé")

    # Sélectionner documents de test
    sample_folder = DATA_DIR / "R1048-13C-23516-23516"
    sample_docs = sorted(sample_folder.glob("*.md"))[:5]

    print(f"\n📂 Documents: {len(sample_docs)}")

    # Traiter
    all_entities = []

    for doc in sample_docs:
        entities = process_document(doc, model)
        all_entities.extend(entities)

    print(f"\n📊 Total avant déduplication: {len(all_entities)}")

    # Déduplication
    deduplicated = deduplicate_entities(all_entities)
    print(f"📊 Total après déduplication: {len(deduplicated)}")

    # Créer DataFrame
    df = pd.DataFrame(deduplicated)

    # Réordonner colonnes
    column_order = [
        "nom_complet_original",
        "civilite",
        "titre_honorifique",
        "titre_complet",
        "prenom",
        "nom_famille",
        "type_entite",
        "organisation",
        "ville",
        "pays",
        "role_fonction",
        "source_document",
        "score_confiance"
    ]

    df = df[column_order]

    # Sauvegarder
    OUTPUT_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_EXCEL, index=False, sheet_name="Entités NER V2")

    print(f"\n{'='*80}")
    print(f"✅ Fichier: {OUTPUT_EXCEL}")
    print(f"{'='*80}")

    # Stats
    print("\n📊 Par type:")
    for entity_type, count in df['type_entite'].value_counts().items():
        print(f"   - {entity_type}: {count}")

    # Aperçu personnes
    print("\n👤 Personnes (top 15):")
    persons = df[df['type_entite'] == 'person'].sort_values('score_confiance', ascending=False)
    for idx, row in persons.head(15).iterrows():
        titre_display = f"[{row['titre_complet']}]" if row['titre_complet'] else ""
        nom_display = f"{row['prenom']} {row['nom_famille']}".strip()
        org_display = f"({row['organisation'][:30]}...)" if row['organisation'] else ""
        print(f"   • {titre_display:35s} {nom_display:25s} {org_display:35s} | {row['score_confiance']:.2f}")

    print(f"\n💡 Ouvrez: {OUTPUT_EXCEL}")


if __name__ == "__main__":
    main()
