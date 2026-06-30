# Calcul d'atteinte de l'objectif pour le programme AMOén de SIG/OCEN

Application Streamlit qui calcule l'atteinte de l'objectif du programme AMOén
(SIG/OCEN), gère l'historique par site, et génère des rapports PDF.

🔗 **Dashboard**: [amoen-calcul.streamlit.app](https://amoen-calcul.streamlit.app/)

📖 **Documentation**: [denisiglesiasgarcia.github.io/amoen_calcul_objectif_dashboard](https://denisiglesiasgarcia.github.io/amoen_calcul_objectif_dashboard/)

## Fonctionnalités

- Calcul de l'atteinte de l'objectif (méthodologie AMOén)
- Historique des calculs par site, avec graphiques
- Génération de rapports PDF
- Extraction et gestion de la base de données (admin)
- Gestion des utilisateurs avec mots de passe robustes et réinitialisation
- Mode sombre / clair

## Stack technique

- Python 3.13, géré avec [uv](https://docs.astral.sh/uv/)
- [Streamlit](https://streamlit.io/) + `streamlit-authenticator`
- MongoDB (`pymongo`)
- Polars / Pandas pour le traitement de données
- Plotly, Altair, Matplotlib/Seaborn pour les graphiques
- ReportLab pour la génération de PDF

## Démarrage local

### Prérequis

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Un URI de connexion MongoDB

### Installation

```bash
uv sync
```

### Configuration

L'application lit l'URI MongoDB depuis les secrets Streamlit. Créer
`.streamlit/secrets.toml` (non versionné) avec :

```toml
MONGODB_URI = "mongodb+srv://..."
```

### Lancer l'application

```bash
uv run streamlit run dashboard_amoen.py
```

## Tests et qualité

```bash
uv run pytest                              # tests unitaires
uv run ruff check                          # lint
uv run mypy sections/ --ignore-missing-imports   # typage
uv run bandit -r sections/ -ll             # analyse de sécurité
```

Ces mêmes vérifications tournent dans la CI (`.github/workflows/run_test.yml`) à chaque push.
Les hooks pre-commit (`.pre-commit-config.yaml`) lancent ruff et le bump de version automatiquement.

## Structure du projet

```
dashboard_amoen.py        # point d'entrée Streamlit
sections/                 # pages/onglets de l'UI
sections/helpers/         # logique métier (calculs, requêtes Mongo, rapports PDF, etc.)
tests/                    # tests pytest
mkdocs/                   # source de la documentation utilisateur
scripts/                  # scripts de versioning/release
```

## Versioning et release

`make commit m="message"` bump la version patch, met à jour le lock uv, régénère
`requirements.txt`, puis crée le commit (voir [Makefile](Makefile)).
