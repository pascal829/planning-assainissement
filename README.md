# Planning Assainissement

Petite application web pour gérer le planning hebdomadaire (remplace le
tableau Excel "REGIE ASSAINISSEMENT").

## Fonctionnalités

- Grille identique au tableau Excel : jours (Lundi→Vendredi) × demi-journées
  (Matin/Après-midi) × agents, avec des lignes par site/activité.
- Saisie libre du code dans chaque case (X, J, R, D, M, T, E ou ce que tu veux).
- Sauvegarde automatique de chaque case dès qu'elle est modifiée (pas de
  bouton "Enregistrer").
- Navigation semaine précédente / semaine suivante.
- Page "Gérer la légende" pour ajouter/modifier/supprimer des codes et leurs
  couleurs — les cases de la grille se colorent automatiquement selon la
  légende.
- Export PDF du planning de la semaine affichée (bouton "Exporter en PDF"),
  au format A3 paysage.

## Installation en local

```bash
python3 -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Puis ouvrir http://localhost:5000 dans le navigateur.

## Accès protégé à la gestion de la légende

La page "Gérer la légende" (codes + notes numérotées) est protégée par un
mot de passe. Par défaut, il est défini dans `config.py` :

```python
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "assainissement2026")
```

**À faire avant toute mise en service réelle :**
- Change le mot de passe par défaut (directement dans `config.py`, ou mieux,
  définis la variable d'environnement `ADMIN_PASSWORD` sur ton serveur pour
  ne pas le laisser en clair dans le code).
- Définis aussi `SECRET_KEY` (variable d'environnement) avec une valeur
  longue et aléatoire — elle sert à sécuriser la session de connexion.

La grille du planning elle-même (saisie des cases, consultation, export PDF)
reste accessible sans mot de passe à toute personne ayant le lien.

## Module Astreintes (planning mensuel annuel)

En plus du planning hebdomadaire, l'appli propose un onglet **Astreintes**
(lien "Astreintes" en haut de la page d'accueil) :

- Un calendrier mensuel (tous les jours du mois, avec la lettre du jour de
  la semaine et les week-ends grisés), navigable mois par mois — les 12 mois
  de l'année sont donc consultables/modifiables individuellement.
- Deux sections fixes : **ASTREINTES D'EXPLOITATION** et
  **ASTREINTES DE DECISION**.
- Chaque case se clique pour faire défiler 3 états : vide → astreinte
  semaine (bleu) → astreinte week-end (orange) → vide. Sauvegarde
  automatique, comme pour le planning hebdo.
- Page **"Gérer les agents"** (protégée par le même mot de passe que la
  légende) : ajouter un agent, modifier son nom ou sa section, ou le
  supprimer. Les astreintes déjà saisies restent enregistrées même si
  l'agent est ensuite renommé.

Les données sont stockées en JSON, un fichier par mois :
`data/astreintes/AAAA-MM.json`, et la liste des agents dans
`data/astreintes_agents.json`.

## Personnaliser la structure du tableau

Tout se règle dans **config.py** :

- `AGENTS` : liste des initiales des agents (colonnes).
- `DAYS` / `HALF_DAYS` : jours et demi-journées affichés.
- `ROWS` : les lignes du tableau (site/activité), regroupées par `section`
  (le bandeau de titre jaune). Tu peux ajouter d'autres sections.
- `DEFAULT_LEGEND` : légende de départ (modifiable ensuite depuis l'appli,
  page "Gérer la légende").

Après une modification de `config.py`, il suffit de relancer l'application.

## Où sont stockées les données

- Un fichier JSON par semaine dans `data/plannings/AAAA-Wss.json`
  (ex : `2026-W38.json`). Facile à sauvegarder, versionner ou inspecter.
- La légende est dans `data/legend.json`.

Pas de base de données à installer : tout est en fichiers texte.

## Déploiement (ex. Railway)

1. Pousser ce dossier sur un dépôt GitHub.
2. Créer un nouveau projet Railway à partir du dépôt.
3. Railway détecte `requirements.txt` (Python). Définir la commande de
   démarrage : `gunicorn app:app`.
4. Penser à monter un volume persistant sur le dossier `data/` si tu veux
   garder l'historique des semaines entre deux déploiements (sinon les
   fichiers JSON repartent de zéro à chaque déploiement).

## Pistes d'amélioration possibles

- Authentification simple (mot de passe) si l'appli est exposée sur internet.
- Historique / statistiques (jours de congés posés, etc.).
- Impression directe sans passer par le PDF (CSS `@media print`).
