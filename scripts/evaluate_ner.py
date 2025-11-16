#!/usr/bin/env python3
"""
NER Evaluation Script
Evaluates GLiNER predictions against gold standard annotations
Author: Claude Code
Date: 2025-11-16
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import pandas as pd


class NERAnnotation:
    """Represents a single NER annotation"""
    def __init__(self, folder: str, document: str, entity_type: str, entity_text: str):
        self.folder = folder
        self.document = document
        self.entity_type = entity_type
        self.entity_text = entity_text

    def __eq__(self, other):
        """Two annotations are equal if they have the same folder, document, type, and normalized text"""
        return (self.folder == other.folder and
                self.document == other.document and
                self.entity_type == other.entity_type and
                self.normalize(self.entity_text) == self.normalize(other.entity_text))

    def __hash__(self):
        return hash((self.folder, self.document, self.entity_type, self.normalize(self.entity_text)))

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize text for comparison (lowercase, strip whitespace)"""
        return text.strip().lower()

    def __repr__(self):
        return f"{self.folder}|{self.document}|{self.entity_type}|{self.entity_text}"


class NERMetrics:
    """Calculate precision, recall, F1 for NER predictions"""

    def __init__(self):
        self.tp = 0  # True Positives
        self.fp = 0  # False Positives
        self.fn = 0  # False Negatives
        self.false_positives_list = []
        self.false_negatives_list = []

    @property
    def precision(self) -> float:
        """Calculate precision: TP / (TP + FP)"""
        if self.tp + self.fp == 0:
            return 0.0
        return self.tp / (self.tp + self.fp)

    @property
    def recall(self) -> float:
        """Calculate recall: TP / (TP + FN)"""
        if self.tp + self.fn == 0:
            return 0.0
        return self.tp / (self.tp + self.fn)

    @property
    def f1(self) -> float:
        """Calculate F1 score: 2 * (precision * recall) / (precision + recall)"""
        p, r = self.precision, self.recall
        if p + r == 0:
            return 0.0
        return 2 * (p * r) / (p + r)

    def update(self, gold: Set[NERAnnotation], pred: Set[NERAnnotation]):
        """Update metrics with a new set of predictions"""
        tp_set = gold & pred
        fp_set = pred - gold
        fn_set = gold - pred

        self.tp += len(tp_set)
        self.fp += len(fp_set)
        self.fn += len(fn_set)

        self.false_positives_list.extend(fp_set)
        self.false_negatives_list.extend(fn_set)


class GoldStandardLoader:
    """Load gold standard annotations from text file"""

    @staticmethod
    def load(filepath: Path) -> Dict[str, List[NERAnnotation]]:
        """
        Load gold standard annotations
        Returns: dict mapping folder names to lists of annotations
        """
        annotations_by_folder = defaultdict(list)

        with open(filepath, 'r', encoding='utf-8') as f:
            current_folder = None
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    # Check if it's a folder marker
                    if line.startswith('## DOSSIER:'):
                        current_folder = line.split(':', 1)[1].strip()
                    continue

                # Parse annotation: FOLDER|DOCUMENT|TYPE|ENTITY
                parts = line.split('|')
                if len(parts) != 4:
                    continue

                folder, document, entity_type, entity_text = parts
                annotation = NERAnnotation(folder, document, entity_type, entity_text)
                annotations_by_folder[folder].append(annotation)

        return dict(annotations_by_folder)


class GLiNERResultsLoader:
    """Load GLiNER predictions from Excel file"""

    @staticmethod
    def load(filepath: Path, folder_filter: Set[str] = None) -> Dict[str, List[NERAnnotation]]:
        """
        Load GLiNER predictions from Excel file
        Returns: dict mapping folder names to lists of annotations
        """
        annotations_by_folder = defaultdict(list)

        # Type mapping from Excel sheets to gold standard types
        type_mapping = {
            'PERSON': 'PERSON',
            'ORGANIZATION': 'ORGANIZATION',
            'GPE': 'LOCATION'  # Geographic Political Entity -> LOCATION
        }

        # Try to load Excel file
        try:
            excel_file = pd.ExcelFile(filepath)
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return dict(annotations_by_folder)

        # Read each sheet
        for sheet_name in excel_file.sheet_names:
            if sheet_name not in type_mapping:
                continue

            entity_type = type_mapping[sheet_name]
            df = pd.read_excel(excel_file, sheet_name=sheet_name)

            # Expected columns: Folder, Document, Entity (at minimum)
            if 'Folder' not in df.columns or 'Document' not in df.columns or 'Entity' not in df.columns:
                print(f"Warning: Sheet {sheet_name} missing required columns")
                continue

            for _, row in df.iterrows():
                folder = str(row['Folder'])
                document_full = str(row['Document'])
                entity_text = str(row['Entity'])

                # Skip if not in filter
                if folder_filter and folder not in folder_filter:
                    continue

                # Normalize document name: extract just "doc01" from "R1048-13C-23516-23516_doc01"
                if '_doc' in document_full:
                    document = 'doc' + document_full.split('_doc')[1]
                else:
                    document = document_full

                annotation = NERAnnotation(folder, document, entity_type, entity_text)
                annotations_by_folder[folder].append(annotation)

        return dict(annotations_by_folder)


class NEREvaluator:
    """Main evaluation class"""

    def __init__(self, gold_standard_path: Path, predictions_path: Path):
        self.gold_standard_path = gold_standard_path
        self.predictions_path = predictions_path
        self.gold_annotations = {}
        self.pred_annotations = {}

    def load_data(self):
        """Load both gold standard and predictions"""
        print(f"Loading gold standard from: {self.gold_standard_path}")
        self.gold_annotations = GoldStandardLoader.load(self.gold_standard_path)

        # Get list of folders in gold standard
        gold_folders = set(self.gold_annotations.keys())
        print(f"Found {len(gold_folders)} folders in gold standard")

        print(f"Loading predictions from: {self.predictions_path}")
        self.pred_annotations = GLiNERResultsLoader.load(self.predictions_path, gold_folders)
        print(f"Found {len(self.pred_annotations)} folders in predictions")

    def evaluate(self) -> Dict[str, NERMetrics]:
        """
        Evaluate predictions against gold standard
        Returns: dict mapping entity types to metrics
        """
        # Initialize metrics for each type
        metrics_by_type = {
            'PERSON': NERMetrics(),
            'ORGANIZATION': NERMetrics(),
            'LOCATION': NERMetrics()
        }

        # Overall metrics
        metrics_overall = NERMetrics()

        # Get all folders (union of gold and pred)
        all_folders = set(self.gold_annotations.keys()) | set(self.pred_annotations.keys())

        for folder in all_folders:
            gold_anns = self.gold_annotations.get(folder, [])
            pred_anns = self.pred_annotations.get(folder, [])

            # Group by type
            gold_by_type = defaultdict(set)
            pred_by_type = defaultdict(set)

            for ann in gold_anns:
                gold_by_type[ann.entity_type].add(ann)

            for ann in pred_anns:
                pred_by_type[ann.entity_type].add(ann)

            # Update metrics for each type
            for entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                gold_set = gold_by_type[entity_type]
                pred_set = pred_by_type[entity_type]
                metrics_by_type[entity_type].update(gold_set, pred_set)

                # Also update overall
                metrics_overall.update(gold_set, pred_set)

        # Add overall metrics
        metrics_by_type['OVERALL'] = metrics_overall

        return metrics_by_type

    def generate_report(self, metrics: Dict[str, NERMetrics], output_path: Path):
        """Generate detailed evaluation report"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("NER EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Gold Standard: {self.gold_standard_path}\n")
            f.write(f"Predictions:   {self.predictions_path}\n")
            f.write(f"Generated:     {pd.Timestamp.now()}\n\n")

            # Summary table
            f.write("=" * 80 + "\n")
            f.write("SUMMARY METRICS\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"{'Type':<15} {'Precision':>10} {'Recall':>10} {'F1':>10} {'TP':>6} {'FP':>6} {'FN':>6}\n")
            f.write("-" * 80 + "\n")

            # Print metrics for each type
            for entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                m = metrics[entity_type]
                f.write(f"{entity_type:<15} {m.precision:>10.3f} {m.recall:>10.3f} {m.f1:>10.3f} "
                       f"{m.tp:>6} {m.fp:>6} {m.fn:>6}\n")

            f.write("-" * 80 + "\n")

            # Overall metrics
            m = metrics['OVERALL']
            f.write(f"{'MICRO-AVG':<15} {m.precision:>10.3f} {m.recall:>10.3f} {m.f1:>10.3f} "
                   f"{m.tp:>6} {m.fp:>6} {m.fn:>6}\n")

            # Macro-average
            macro_p = sum(metrics[t].precision for t in ['PERSON', 'ORGANIZATION', 'LOCATION']) / 3
            macro_r = sum(metrics[t].recall for t in ['PERSON', 'ORGANIZATION', 'LOCATION']) / 3
            macro_f1 = sum(metrics[t].f1 for t in ['PERSON', 'ORGANIZATION', 'LOCATION']) / 3
            f.write(f"{'MACRO-AVG':<15} {macro_p:>10.3f} {macro_r:>10.3f} {macro_f1:>10.3f}\n")

            f.write("\n")

            # Detailed errors
            for entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION']:
                m = metrics[entity_type]

                if m.false_positives_list or m.false_negatives_list:
                    f.write("=" * 80 + "\n")
                    f.write(f"ERRORS FOR TYPE: {entity_type}\n")
                    f.write("=" * 80 + "\n\n")

                    if m.false_positives_list:
                        f.write(f"False Positives ({len(m.false_positives_list)}):\n")
                        f.write("-" * 80 + "\n")
                        for fp in sorted(m.false_positives_list, key=lambda x: (x.folder, x.document, x.entity_text)):
                            f.write(f"  {fp.folder} | {fp.document} | {fp.entity_text}\n")
                        f.write("\n")

                    if m.false_negatives_list:
                        f.write(f"False Negatives ({len(m.false_negatives_list)}):\n")
                        f.write("-" * 80 + "\n")
                        for fn in sorted(m.false_negatives_list, key=lambda x: (x.folder, x.document, x.entity_text)):
                            f.write(f"  {fn.folder} | {fn.document} | {fn.entity_text}\n")
                        f.write("\n")

            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")

        print(f"\nReport saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Evaluate NER predictions against gold standard',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  python evaluate_ner.py \\
    --gold data/gold_standard_annotations.txt \\
    --predictions outputs/ner_results.xlsx \\
    --output outputs/evaluation_report.txt
        """
    )

    parser.add_argument(
        '--gold',
        type=Path,
        default=Path('data/gold_standard_annotations.txt'),
        help='Path to gold standard annotations file'
    )

    parser.add_argument(
        '--predictions',
        type=Path,
        default=Path('outputs/ner_results.xlsx'),
        help='Path to GLiNER predictions Excel file'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=Path('outputs/evaluation_report.txt'),
        help='Path to output evaluation report'
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.gold.exists():
        print(f"Error: Gold standard file not found: {args.gold}")
        sys.exit(1)

    if not args.predictions.exists():
        print(f"Error: Predictions file not found: {args.predictions}")
        sys.exit(1)

    # Create output directory if needed
    args.output.parent.mkdir(parents=True, exist_ok=True)

    # Run evaluation
    evaluator = NEREvaluator(args.gold, args.predictions)
    evaluator.load_data()
    metrics = evaluator.evaluate()
    evaluator.generate_report(metrics, args.output)

    # Print summary to console
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"{'Type':<15} {'Precision':>10} {'Recall':>10} {'F1':>10}")
    print("-" * 80)

    for entity_type in ['PERSON', 'ORGANIZATION', 'LOCATION']:
        m = metrics[entity_type]
        print(f"{entity_type:<15} {m.precision:>10.3f} {m.recall:>10.3f} {m.f1:>10.3f}")

    print("-" * 80)
    m = metrics['OVERALL']
    print(f"{'MICRO-AVG':<15} {m.precision:>10.3f} {m.recall:>10.3f} {m.f1:>10.3f}")

    macro_f1 = sum(metrics[t].f1 for t in ['PERSON', 'ORGANIZATION', 'LOCATION']) / 3
    print(f"{'MACRO-AVG F1':<15} {macro_f1:>32.3f}")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
