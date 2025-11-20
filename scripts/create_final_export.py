#!/usr/bin/env python3
"""
Script: Création fichier export final pour les 40 premières personnes
Combine: person_FINAL_CLEAN + aliases Wikidata + articles Impresso
Format: Modèle prosopographique fourni

Auteur: Claude Code
Date: 2025-11-20
"""

import pandas as pd
from pathlib import Path

# ============================================
# CONFIGURATION
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent

# Fichiers sources
FILE_PERSONS = PROJECT_ROOT / "outputs" / "person_FINAL_CLEAN.xlsx"
FILE_WIKIDATA_ALIASES = PROJECT_ROOT / "outputs" / "personnes_avec_aliases_wikidata.xlsx"
FILE_PRESSE = PROJECT_ROOT / "outputs" / "impresso_resultats_dedupliques.xlsx"

# Fichier de sortie
FILE_OUTPUT = PROJECT_ROOT / "outputs" / "export_final_40_personnes.xlsx"

NOMBRE_PERSONNES = 40

# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def traduire_nationalite(nat_en: str) -> str:
    """Traduit la nationalité en français"""
    if pd.isna(nat_en):
        return ""

    nat_str = str(nat_en).strip()

    # Traductions complètes
    traductions = {
        # Anglais
        'Swiss': 'Suisse',
        'British': 'Britannique',
        'Japanese': 'Japonais',
        'French': 'Français',
        'Polish': 'Polonais',
        'American': 'Américain',
        'Belgian': 'Belge',
        'Italian': 'Italien',
        'German': 'Allemand',
        'Danish': 'Danois',
        'Irish': 'Irlandais',
        'Brazilian': 'Brésilien',
        'Dutch': 'Néerlandais',
        'Austrian': 'Autrichien',
        'Spanish': 'Espagnol',
        'Russian': 'Russe',
        'Norwegian': 'Norvégien',
        'Swedish': 'Suédois',
        'Portuguese': 'Portugais',
        'Greek': 'Grec',
        'Romanian': 'Roumain',
        'Bulgarian': 'Bulgare',
        'Czech': 'Tchèque',
        'Hungarian': 'Hongrois',
        'Finnish': 'Finlandais',
        # Noms de pays directs
        'France': 'Français',
        'Germany': 'Allemand',
        'United Kingdom': 'Britannique',
        'United States': 'Américain',
        'Switzerland': 'Suisse',
        'Belgium': 'Belge',
        'Italy': 'Italien',
        'Spain': 'Espagnol',
        'Poland': 'Polonais',
        'Austria': 'Autrichien',
        'Netherlands': 'Néerlandais',
        'Japan': 'Japonais',
        'Brazil': 'Brésilien',
        'Russia': 'Russe',
        'Norway': 'Norvégien',
        'Sweden': 'Suédois',
        'Denmark': 'Danois',
        'Portugal': 'Portugais',
        'Greece': 'Grec',
        'Romania': 'Roumain',
        'Bulgaria': 'Bulgare',
        # Cas spéciaux
        'Russian Empire': 'Russe (Empire russe)',
        'Polish (Russian Empire)': 'Polonais (Empire russe)',
        'Poland (Russian Empire)': 'Polonais (Empire russe)',
        'United Kingdom, Austrian': 'Britannique, Autrichien',
    }

    # Essayer traduction directe
    if nat_str in traductions:
        return traductions[nat_str]

    # Essayer traduction partielle pour les cas composés
    for key, value in traductions.items():
        if key.lower() in nat_str.lower():
            return nat_str.replace(key, value)

    # Si pas de traduction, retourner tel quel
    return nat_str

def traduire_genre(gender: str) -> str:
    """Traduit le genre en français"""
    if pd.isna(gender):
        return ""
    gender_str = str(gender).upper()
    if gender_str in ['M', 'H']:
        return 'Homme'
    elif gender_str == 'F':
        return 'Femme'
    return ""

def determiner_categorie(docs_officiels: str, description: str) -> str:
    """Détermine la catégorie (SDN ou Sociétés membres)"""
    # Par défaut, considérer comme SDN si mention d'assemblée ou commission
    if pd.isna(docs_officiels):
        docs_officiels = ""
    if pd.isna(description):
        description = ""

    texte_combine = (str(docs_officiels) + " " + str(description)).lower()

    # Mots-clés SDN
    keywords_sdn = ['assemblée', 'commission', 'secrétaire', 'délégué', 'league of nations']

    if any(kw in texte_combine for kw in keywords_sdn):
        return 'SDN'
    else:
        return 'Sociétés membres'

# ============================================
# CHARGEMENT DES DONNÉES
# ============================================

def charger_donnees():
    """Charge tous les fichiers sources"""
    print("📂 Chargement des données...")

    # Personnes principales
    df_persons = pd.read_excel(FILE_PERSONS)
    print(f"  ✅ {len(df_persons)} personnes chargées")

    # Aliases Wikidata
    df_wikidata = pd.read_excel(FILE_WIKIDATA_ALIASES)
    print(f"  ✅ {len(df_wikidata)} personnes avec aliases Wikidata")

    # Articles presse
    df_presse = pd.read_excel(FILE_PRESSE)
    print(f"  ✅ {len(df_presse)} articles de presse")

    return df_persons, df_wikidata, df_presse

# ============================================
# CONSTRUCTION DU FICHIER FINAL
# ============================================

def construire_export(df_persons, df_wikidata, df_presse):
    """Construit le fichier d'export selon le modèle"""

    print(f"\n🔨 Construction de l'export pour {NOMBRE_PERSONNES} personnes...")

    # Limiter aux 40 premières
    df_persons_40 = df_persons.head(NOMBRE_PERSONNES).copy()

    # Créer le DataFrame final
    resultats = []

    for idx, person in df_persons_40.iterrows():
        print(f"  [{idx+1}/{NOMBRE_PERSONNES}] {person['Prénom']} {person['Nom']}")

        # ============================================
        # COLLECTE DES DONNÉES
        # ============================================

        # Identifiant
        identifiant = person['entity_normalized']

        # Nom, Prénom
        nom = person['Nom'] if pd.notna(person['Nom']) else ""
        prenom = person['Prénom'] if pd.notna(person['Prénom']) else ""

        # Nationalité (traduite)
        nationalite = traduire_nationalite(person['nationalité'])

        # Genre (traduit)
        genre = traduire_genre(person['Gender'])

        # Description
        description = person['Unnamed: 9'] if pd.notna(person['Unnamed: 9']) else ""

        # Documents officiels
        docs_officiels = person['Unnamed: 8'] if pd.notna(person['Unnamed: 8']) else ""

        # Catégorie
        categorie = determiner_categorie(docs_officiels, description)

        # Archives de correspondance (tous les documents séparés par ;)
        archives = person['documents'] if pd.notna(person['documents']) else ""
        if archives:
            # Remplacer virgules par point-virgules
            archives = archives.replace(', ', ';')

        # ============================================
        # VARIANTES (aliases + aliases Wikidata)
        # ============================================

        variantes = []

        # Aliases d'origine
        if pd.notna(person['aliases']):
            aliases_origin = [a.strip() for a in str(person['aliases']).split(',')]
            variantes.extend(aliases_origin)

        # Aliases Wikidata
        person_wikidata = df_wikidata[df_wikidata['entity_normalized'] == identifiant]
        if not person_wikidata.empty:
            for langue in ['fr', 'en', 'de']:
                col_alias = f'aliases_wikidata_{langue}'
                if col_alias in person_wikidata.columns:
                    aliases_lang = person_wikidata.iloc[0][col_alias]
                    if pd.notna(aliases_lang) and aliases_lang:
                        aliases_list = [a.strip() for a in str(aliases_lang).split(',')]
                        variantes.extend(aliases_list)

        # Dédupliquer et joindre par virgule
        variantes_uniques = list(dict.fromkeys(variantes))  # Preserve order
        variantes_str = ', '.join(variantes_uniques)

        # ============================================
        # PRESSE (articles Impresso séparés par ;)
        # Avec formule HYPERLINK Excel sur le titre
        # ============================================

        articles_personne = df_presse[df_presse['person_entity'] == identifiant]

        if not articles_personne.empty:
            # Format avec formule Excel HYPERLINK
            presse_entries = []
            for _, article in articles_personne.iterrows():
                article_id = article['article_id'] if pd.notna(article['article_id']) else ""
                title = article['article_title'] if pd.notna(article['article_title']) else "[Sans titre]"
                date = str(article['article_date'])[:10] if pd.notna(article['article_date']) else ""
                newspaper = article['newspaper_id'] if pd.notna(article['newspaper_id']) else ""
                url = article['article_url'] if pd.notna(article['article_url']) else ""

                # Échapper les guillemets dans le titre pour la formule Excel
                title_escaped = title.replace('"', '""')

                # Format avec HYPERLINK si URL disponible
                if url:
                    # Formule Excel: =HYPERLINK("url", "texte")
                    title_with_link = f'=HYPERLINK("{url}","{title_escaped}")'
                else:
                    title_with_link = title

                # Format: article_id | HYPERLINK | date | newspaper
                entry = f"{article_id} | {title_with_link} | {date} | {newspaper}"
                presse_entries.append(entry)

            presse_str = '; '.join(presse_entries)
        else:
            presse_str = ""

        # ============================================
        # CONSTRUCTION DE LA LIGNE
        # ============================================

        ligne = {
            'Nom': nom,
            'Prénom': prenom,
            'Identifiant': identifiant,
            'Variantes': variantes_str,
            'Description': description,
            'Archives de correspondance': archives,
            'Documents officiels': docs_officiels,
            'Presse': presse_str,
            'Nationalité': nationalite,
            'Genre': genre,
            'Catégorie': categorie
        }

        resultats.append(ligne)

    return pd.DataFrame(resultats)

# ============================================
# FONCTION PRINCIPALE
# ============================================

def main():
    """Fonction principale"""

    print("=" * 70)
    print("CRÉATION FICHIER EXPORT FINAL - 40 PERSONNES")
    print("=" * 70)
    print()

    # Charger les données
    df_persons, df_wikidata, df_presse = charger_donnees()

    # Construire l'export
    df_export = construire_export(df_persons, df_wikidata, df_presse)

    # ============================================
    # STATISTIQUES
    # ============================================

    print("\n" + "=" * 70)
    print("STATISTIQUES DE L'EXPORT")
    print("=" * 70)
    print(f"Personnes exportées: {len(df_export)}")
    print(f"Avec articles presse: {(df_export['Presse'] != '').sum()}")
    print(f"Avec description: {(df_export['Description'] != '').sum()}")
    print(f"Avec documents officiels: {(df_export['Documents officiels'] != '').sum()}")
    print()

    print("Distribution par catégorie:")
    cat_counts = df_export['Catégorie'].value_counts()
    for cat, count in cat_counts.items():
        print(f"  {cat}: {count}")

    print()
    print("Distribution par nationalité:")
    nat_counts = df_export['Nationalité'].value_counts().head(10)
    for nat, count in nat_counts.items():
        if nat:
            print(f"  {nat}: {count}")

    print()
    print("Distribution par genre:")
    genre_counts = df_export['Genre'].value_counts()
    for genre, count in genre_counts.items():
        if genre:
            print(f"  {genre}: {count}")

    # ============================================
    # SAUVEGARDE AVEC XLSXWRITER (pour formules)
    # ============================================

    print("\n💾 Sauvegarde du fichier avec hyperliens...")

    # Utiliser xlsxwriter pour supporter les formules
    writer = pd.ExcelWriter(FILE_OUTPUT, engine='xlsxwriter')
    df_export.to_excel(writer, index=False, sheet_name='Personnes')

    # Obtenir le workbook et worksheet
    workbook = writer.book
    worksheet = writer.sheets['Personnes']

    # Format pour les hyperliens (bleu souligné)
    link_format = workbook.add_format({
        'font_color': 'blue',
        'underline': 1,
        'text_wrap': True,
        'valign': 'top'
    })

    # Format général avec retour à la ligne automatique
    wrap_format = workbook.add_format({
        'text_wrap': True,
        'valign': 'top'
    })

    # Trouver la colonne Presse
    col_presse = df_export.columns.get_loc('Presse')

    # Ajuster la largeur des colonnes
    worksheet.set_column(0, 0, 15)  # Nom
    worksheet.set_column(1, 1, 15)  # Prénom
    worksheet.set_column(2, 2, 25)  # Identifiant
    worksheet.set_column(3, 3, 40)  # Variantes
    worksheet.set_column(4, 4, 50)  # Description
    worksheet.set_column(5, 5, 40)  # Archives
    worksheet.set_column(6, 6, 30)  # Documents officiels
    worksheet.set_column(col_presse, col_presse, 80)  # Presse (large)
    worksheet.set_column(8, 8, 20)  # Nationalité
    worksheet.set_column(9, 9, 10)  # Genre
    worksheet.set_column(10, 10, 20)  # Catégorie

    # Appliquer le format avec retour à la ligne pour la colonne Presse
    for row_idx in range(len(df_export)):
        worksheet.write(row_idx + 1, col_presse, df_export.iloc[row_idx]['Presse'], wrap_format)

    # Fermer le writer
    writer.close()

    print(f"✅ Fichier sauvegardé: {FILE_OUTPUT}")
    print(f"   {len(df_export)} lignes × {len(df_export.columns)} colonnes")
    print(f"   Hyperliens actifs dans la colonne Presse")

    print("\n" + "=" * 70)
    print("✅ EXPORT TERMINÉ")
    print("=" * 70)

if __name__ == "__main__":
    main()
