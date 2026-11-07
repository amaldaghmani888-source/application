# Carnet de santé de la femme — prototype Flask

## Installation
1. Installer Python 3.10 ou plus récent.
2. Dans le dossier du projet :
   ```bash
   python -m venv .venv
   # Windows : .venv\\Scripts\\activate
   # macOS/Linux : source .venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```
3. Ouvrir http://127.0.0.1:5000

La base SQLite `carnet_femme.db` est créée automatiquement.

## Rubriques intégrées
Identification, vaccination, examen prénuptial, planification familiale, suivi de grossesse, accouchement et post-partum, dépistage des cancers du sein et du col de l’utérus, consultations médicales, chirurgie, maladies chroniques et ménopause.

Les champs reprennent les rubriques du carnet PDF fourni. Le carnet indique notamment le dépistage du sein entre 45 et 69 ans avec répétition tous les deux ans, et celui du col entre 30 et 49 ans avec répétition tous les trois ans. Ces repères sont affichés dans le document source ; ils doivent être validés avec les protocoles nationaux actuels avant un usage clinique.

## Sécurité — important
Ce projet est un prototype pédagogique, pas un logiciel médical prêt pour la production. Avant toute utilisation réelle : ajouter authentification forte et rôles, chiffrement, sauvegardes sécurisées, journal d’audit, protection CSRF, hébergement conforme, gestion du consentement et validation par les responsables médicaux/juridiques. Ne pas y saisir de vraies données de santé avant ces mesures.
