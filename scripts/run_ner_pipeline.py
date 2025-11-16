#!/usr/bin/env python3
"""
NER Pipeline Production Script
Runs complete NER extraction and evaluation pipeline
Author: Claude Code
Date: 2025-11-16
"""

import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import pandas as pd
from gliner import GLiNER


# Configuration par défaut
DEFAULT_MODEL_PATH = "/home/steeven/PycharmProjects/gliner2Tests/models/checkpoints/gliner_multi-v2.1"
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data/annotated/ocr_results"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# Labels NER à extraire
LABELS = ["person", "organization", "location"]

# Scores minimums pour filtrage
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
    """Découpe intelligente en chunks avec overlap"""
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


def extract_context(entity, full_text, window=150):
    """Extrait contexte autour d'une entité"""
    text_lower = full_text.lower()
    entity_lower = entity['text'].lower()

    pos = text_lower.find(entity_lower)
    if pos == -1:
        return ""

    start = max(0, pos - window)
    end = min(len(full_text), pos + len(entity['text']) + window)

    return full_text[start:end]


def process_document(file_path, folder_name, model, verbose=True):
    """Traite un document et extrait les entités NER"""
    if verbose:
        print(f"  Processing: {file_path.name}")

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
            entity['full_text'] = text_clean
            all_entities.append(entity)

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

    # Préparer résultats
    results = []
    for entity in filtered:
        # Normaliser le type (GPE pour location)
        entity_type = entity['label'].upper()
        if entity_type == 'LOCATION':
            entity_type = 'GPE'

        results.append({
            'Folder': folder_name,
            'Document': file_path.stem,
            'Entity': entity['text'],
            'Type': entity_type,
            'Score': round(entity['score'], 3)
        })

    return results


def process_folder(folder_path, model, verbose=True):
    """Traite tous les documents d'un dossier"""
    folder_name = folder_path.name

    if verbose:
        print(f"\nFolder: {folder_name}")

    # Trouver tous les fichiers .md
    md_files = sorted(folder_path.glob("*.md"))

    if verbose:
        print(f"  Files: {len(md_files)}")

    all_results = []
    for md_file in md_files:
        results = process_document(md_file, folder_name, model, verbose)
        all_results.extend(results)

    if verbose:
        print(f"  Entities: {len(all_results)}")

    return all_results


def deduplicate_results(results):
    """Déduplique les entités par (Folder, Document, Type, Entity normalisée)"""
    # Grouper par clé unique
    groups = defaultdict(list)

    for result in results:
        key = (
            result['Folder'],
            result['Document'],
            result['Type'],
            result['Entity'].lower().strip()
        )
        groups[key].append(result)

    # Garder celle avec le meilleur score
    deduplicated = []
    for key, group in groups.items():
        best = max(group, key=lambda x: x['Score'])
        deduplicated.append(best)

    return deduplicated


def create_excel_report(results, output_path):
    """Crée un fichier Excel avec 3 sheets (PERSON, ORGANIZATION, GPE)"""
    df = pd.DataFrame(results)

    # Créer ExcelWriter
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Sheet pour chaque type
        for entity_type in ['PERSON', 'ORGANIZATION', 'GPE']:
            df_type = df[df['Type'] == entity_type].copy()
            df_type = df_type.sort_values(['Folder', 'Document', 'Score'], ascending=[True, True, False])
            df_type.to_excel(writer, sheet_name=entity_type, index=False)

    print(f"\nExcel report saved: {output_path}")


def run_evaluation(excel_path, gold_standard_path, output_report_path):
    """Lance l'évaluation en appelant le script evaluate_ner.py"""
    import subprocess

    eval_script = Path(__file__).parent / "evaluate_ner.py"

    if not eval_script.exists():
        print(f"\nWarning: Evaluation script not found: {eval_script}")
        return False

    if not gold_standard_path.exists():
        print(f"\nWarning: Gold standard not found: {gold_standard_path}")
        return False

    if not excel_path.exists():
        print(f"\nWarning: Excel results not found: {excel_path}")
        return False

    print("\n" + "=" * 80)
    print("RUNNING EVALUATION")
    print("=" * 80)

    cmd = [
        sys.executable,
        str(eval_script),
        "--gold", str(gold_standard_path),
        "--predictions", str(excel_path),
        "--output", str(output_report_path)
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running evaluation: {e}")
        print(e.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Run complete NER extraction and evaluation pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on all folders
  python run_ner_pipeline.py

  # Run on specific folder
  python run_ner_pipeline.py --folder R1048-13C-23516-23516

  # Run on gold standard folders only
  python run_ner_pipeline.py --gold-only

  # Skip evaluation
  python run_ner_pipeline.py --no-eval
        """
    )

    parser.add_argument(
        '--model',
        type=Path,
        default=Path(DEFAULT_MODEL_PATH),
        help='Path to GLiNER model'
    )

    parser.add_argument(
        '--data-dir',
        type=Path,
        default=DATA_DIR,
        help='Path to data directory containing OCR results'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=OUTPUT_DIR,
        help='Path to output directory'
    )

    parser.add_argument(
        '--folder',
        type=str,
        help='Process specific folder only'
    )

    parser.add_argument(
        '--gold-only',
        action='store_true',
        help='Process only folders in gold standard'
    )

    parser.add_argument(
        '--no-eval',
        action='store_true',
        help='Skip evaluation step'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Quiet mode (less verbose)'
    )

    args = parser.parse_args()

    verbose = not args.quiet

    # Validate model path
    if not args.model.exists():
        print(f"Error: Model not found: {args.model}")
        sys.exit(1)

    if not args.data_dir.exists():
        print(f"Error: Data directory not found: {args.data_dir}")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    if verbose:
        print("=" * 80)
        print("NER EXTRACTION PIPELINE")
        print("=" * 80)
        print(f"\nLoading GLiNER model from: {args.model}")

    model = GLiNER.from_pretrained(str(args.model))

    if verbose:
        print("Model loaded successfully\n")

    # Determine which folders to process
    if args.folder:
        # Specific folder
        folder_path = args.data_dir / args.folder
        if not folder_path.exists():
            print(f"Error: Folder not found: {folder_path}")
            sys.exit(1)
        folders = [folder_path]
    elif args.gold_only:
        # Load gold standard to get folder list
        gold_standard_path = PROJECT_ROOT / "data" / "gold_standard_annotations.txt"
        if not gold_standard_path.exists():
            print(f"Error: Gold standard not found: {gold_standard_path}")
            sys.exit(1)

        # Parse gold standard for folder names
        gold_folders = set()
        with open(gold_standard_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## DOSSIER:'):
                    folder_name = line.split(':', 1)[1].strip()
                    gold_folders.add(folder_name)

        folders = [args.data_dir / fname for fname in gold_folders if (args.data_dir / fname).exists()]

        if verbose:
            print(f"Processing {len(folders)} gold standard folders")
    else:
        # All folders
        folders = [f for f in args.data_dir.iterdir() if f.is_dir()]

    if verbose:
        print(f"Total folders to process: {len(folders)}\n")

    # Process all folders
    all_results = []
    for folder_path in sorted(folders):
        results = process_folder(folder_path, model, verbose)
        all_results.extend(results)

    if verbose:
        print(f"\n" + "=" * 80)
        print(f"Total entities extracted: {len(all_results)}")

    # Deduplicate
    deduplicated = deduplicate_results(all_results)

    if verbose:
        print(f"After deduplication: {len(deduplicated)}")
        print("=" * 80)

    # Create Excel report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_path = args.output_dir / f"ner_results_{timestamp}.xlsx"
    create_excel_report(deduplicated, excel_path)

    # Statistics
    df = pd.DataFrame(deduplicated)

    if verbose:
        print("\nStatistics by type:")
        for entity_type, count in df['Type'].value_counts().items():
            print(f"  {entity_type}: {count}")

    # Run evaluation if requested
    if not args.no_eval:
        gold_standard_path = PROJECT_ROOT / "data" / "gold_standard_annotations.txt"
        eval_report_path = args.output_dir / f"evaluation_report_{timestamp}.txt"

        success = run_evaluation(excel_path, gold_standard_path, eval_report_path)

        if success and verbose:
            print(f"\nEvaluation report saved: {eval_report_path}")

    if verbose:
        print("\n" + "=" * 80)
        print("PIPELINE COMPLETED")
        print("=" * 80)
        print(f"\nResults: {excel_path}")


if __name__ == '__main__':
    main()
