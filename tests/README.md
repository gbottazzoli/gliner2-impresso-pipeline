# 🧪 tests/

**Tests unitaires avec pytest**

Ce dossier contient les tests pour assurer la fiabilité et la reproductibilité du code.

---

## Structure

```
tests/
├── test_preprocessing/    # Tests pour src/preprocessing/
├── test_ner/              # Tests pour src/ner/
└── test_network/          # Tests pour src/network/
```

---

## 🚀 Lancer les Tests

### Tous les tests
```bash
pytest
```

### Tests avec couverture de code
```bash
pytest --cov=src --cov-report=html
# Ouvrir htmlcov/index.html pour voir le rapport
```

### Tests d'un module spécifique
```bash
pytest tests/test_ner/
pytest tests/test_preprocessing/test_clean_text.py
```

### Tests avec verbose
```bash
pytest -v
```

---

## 📝 Créer des Tests

### Utiliser l'agent `@testeur_code`
```bash
@testeur_code Crée des tests pour src/ner/gliner_extractor.py
```

### Exemple de test manuel

**Structure** : `test_<module>.py` dans le dossier correspondant

**Exemple** : `tests/test_preprocessing/test_clean_text.py`
```python
import pytest
from src.preprocessing.clean_text import normalize_unicode, remove_special_chars

def test_normalize_unicode():
    """Test normalisation Unicode pour Esperanto"""
    text = "Ĝenevo"
    result = normalize_unicode(text)
    assert result == "Ĝenevo"  # Vérifier caractères préservés

def test_remove_special_chars():
    """Test suppression caractères non-textuels"""
    text = "Texto kun @#$ specialaj signoj!"
    result = remove_special_chars(text)
    assert "@" not in result
    assert "Texto" in result

@pytest.mark.parametrize("input,expected", [
    ("test1", "test1"),
    ("test2  ", "test2"),
    ("  test3", "test3"),
])
def test_strip_whitespace(input, expected):
    """Test suppression espaces avec paramétrage"""
    result = input.strip()
    assert result == expected
```

---

## 🎯 Bonnes Pratiques

1. **Nommage** : `test_<fonction>.py` ou `test_<feature>.py`
2. **Docstrings** : Décrire ce que teste chaque fonction
3. **Isolation** : Chaque test doit être indépendant
4. **Fixtures** : Utiliser fixtures pytest pour données de test
5. **Paramétrage** : `@pytest.mark.parametrize` pour tests multiples

---

## 🗂️ Organisation

### `test_preprocessing/`
**Tests pour** : `src/preprocessing/`

**Exemples de tests** :
- Normalisation Unicode
- Suppression de caractères
- Segmentation de documents
- Gestion d'encodages

### `test_ner/`
**Tests pour** : `src/ner/`

**Exemples de tests** :
- Extraction d'entités (mocks ou petits exemples)
- Post-processing (déduplication, normalisation)
- Validation de format JSON
- Calcul de métriques (F1, précision, rappel)

### `test_network/`
**Tests pour** : `src/network/`

**Exemples de tests** :
- Construction de graphes
- Calcul de co-occurrences
- Métriques de réseau (centralité, etc.)
- Export GraphML/CSV

---

## 🔧 Configuration

### `pytest.ini` (optionnel)
Créez à la racine du projet :
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Fixtures partagées : `conftest.py`
Créez `tests/conftest.py` pour fixtures communes :
```python
import pytest

@pytest.fixture
def sample_text():
    """Fixture: texte Esperanto de test"""
    return "La Ligo de Nacioj kunvenis en Ĝenevo."

@pytest.fixture
def sample_entities():
    """Fixture: liste d'entités de test"""
    return [
        {"text": "Ligo de Nacioj", "label": "ORGANIZATION"},
        {"text": "Ĝenevo", "label": "LOCATION"},
    ]
```

---

## 📊 Couverture de Code

**Objectif** : > 80% de couverture pour code critique

**Voir rapport** :
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## 🤖 Agents Utiles

```bash
@testeur_code Crée tests pour src/ner/gliner_extractor.py
@testeur_code Lance tous les tests et affiche résultats
```

---

## 📝 TODO

- [ ] Créer tests pour `src/preprocessing/clean_text.py`
- [ ] Créer tests pour `src/ner/gliner_extractor.py`
- [ ] Créer tests pour `src/network/build_network.py`
- [ ] Atteindre > 80% couverture de code
- [ ] Configurer CI/CD (GitHub Actions) pour tests automatiques

---

**Voir aussi** : Documentation pytest : https://docs.pytest.org/
