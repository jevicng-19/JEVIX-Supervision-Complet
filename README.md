# JEVIX Supervision

Application de supervision de machines sur un réseau local. Chaque poste client exécute l'agent JEVIX, qui envoie ses mesures au serveur. Le serveur les stocke dans MySQL et les affiche dans un tableau de bord web.

## Fonctionnalités

- Tableau de bord de supervision des machines
- Collecte des informations CPU, mémoire, disque, système et réseau
- Détection des machines hors ligne et gestion des alertes
- Connexion et gestion des comptes administrateurs
- Agent Windows compilé, utilisable sans installer Python sur les postes clients
- Démarrage automatique facultatif de l'agent à l'ouverture de session Windows

## Contenu du dépôt

- `JEVIX - Supervision/` : code Python du serveur Flask, code source de l'agent, pages du site, script SQL et scripts de construction.
- `agent-windows/` : exécutable Windows et fichiers nécessaires à son utilisation.
- `LISEZ-MOI-AVANT-DEMARRAGE.txt` : guide détaillé d'installation et d'utilisation.

## Prérequis

**Sur la machine serveur :** Windows, Python, XAMPP/MySQL et un navigateur. Apache dans XAMPP sert à ouvrir phpMyAdmin ; MySQL et le serveur Flask doivent tourner pendant la supervision.

**Sur les postes clients Windows :** aucun Python à installer. Il faut copier `JEVIX-Agent.exe` et `agent_config.json` depuis `agent-windows/`.

## Démarrage rapide du serveur

1. Démarrer MySQL dans XAMPP.
2. Importer `JEVIX - Supervision/Jevix.sql` dans phpMyAdmin pour créer la base et les tables.
3. Ouvrir PowerShell dans le dossier `JEVIX - Supervision/`, puis installer les dépendances :

   ```powershell
   py -m pip install -r requirements-server.txt
   ```

4. Générer la clé secrète locale de Flask :

   ```powershell
   py generer_cle_flask.py
   ```

5. Créer le premier compte administrateur :

   ```powershell
   py creer_premier_admin.py
   ```

   Le mot de passe saisi est haché avant son enregistrement dans MySQL. Sur la page de connexion, utiliser le mot de passe normal choisi, jamais le hash.

6. Lancer le serveur :

   ```powershell
   py serveurFlask.py
   ```

7. Ouvrir `http://127.0.0.1:5000` sur le serveur. Pour les instructions détaillées et la configuration des clients, lire `LISEZ-MOI.txt`.

## Sécurité et configuration

- Le fichier `.flask_secret` est créé localement par `generer_cle_flask.py`. Il n'est pas fourni dans le dépôt et doit rester privé sur la machine serveur.
- Ne jamais publier de mot de passe, de clé secrète ou de sauvegarde de la base de données.
- `agent-windows/agent_config.json` contient une adresse d'exemple : la remplacer par l'adresse IP locale du serveur, en gardant `/metrics` à la fin.
- Le projet est configuré pour un réseau local. GitHub héberge le code source, mais n'exécute pas l'application Flask ni la base MySQL.

## Auteur

NGONGO KAMBALA Jevic 
