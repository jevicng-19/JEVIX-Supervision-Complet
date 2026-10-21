# JEVIX Supervision

JEVIX Supervision est une application web Flask/MySQL qui affiche l'état des machines équipées de l'agent JEVIX.

## Avant de commencer

- Le serveur (la machine qui héberge le tableau de bord) doit avoir Python, XAMPP/MySQL et les bibliothèques Python du serveur.
- Le navigateur ouvre le tableau de bord ; il n'a pas besoin de Python.
- Sur un poste client, `JEVIX-Agent.exe` contient Python et les bibliothèques de l'agent. Il n'est donc pas nécessaire d'installer Python sur les postes clients.
- GitHub conserve le code source ; il n'héberge pas automatiquement le serveur Flask ni la base MySQL.

## Installer et lancer le serveur pour la première fois

Fais ces étapes sur la machine serveur, dans le dossier du projet.

### 1. Démarrer MySQL et créer la base

1. Ouvre XAMPP et démarre **MySQL**. Apache est utile seulement si tu veux ouvrir phpMyAdmin.
2. Dans phpMyAdmin, importe `Jevix.sql` une seule fois. Le script crée la base `jevix` et ses tables.

### 2. Installer les bibliothèques du serveur

Installe Python sur cette machine, ouvre PowerShell dans le dossier du projet, puis exécute :

```powershell
py -m pip install -r requirements-server.txt
```

### 3. Créer la clé secrète Flask

Toujours dans le dossier du projet, exécute une seule fois :

```powershell
py generer_cle_flask.py
```

Cela crée le fichier privé `.flask_secret` à côté de `serveurFlask.py`. Il contient une clé aléatoire utilisée pour protéger les sessions de connexion du navigateur. Garde ce fichier sur le serveur et ne le publie jamais sur GitHub. Si tu le supprimes ou le remplaces, les sessions ouvertes devront se reconnecter.

### 4. Créer le premier compte administrateur

Exécute :

```powershell
py creer_premier_admin.py
```

Saisis le nom de compte et le mot de passe que tu veux utiliser sur la page de connexion. Le mot de passe est enregistré dans MySQL sous forme de hash. **Sur la page de connexion, tape le mot de passe normal que tu as choisi, jamais le hash.** Cette étape nécessite que MySQL tourne et que la base `jevix` ait été importée.

### 5. Lancer le site et ouvrir la page

Exécute :

```powershell
py serveurFlask.py
```

Sur la machine serveur, ouvre ensuite [http://127.0.0.1:5000](http://127.0.0.1:5000) dans ton navigateur et connecte-toi avec le compte créé à l'étape précédente.

Pour accéder au site depuis un autre ordinateur du même réseau, utilise l'adresse IP locale de la machine serveur, par exemple `http://192.168.1.20:5000`. Le pare-feu Windows doit autoriser le port 5000. Laisse la fenêtre du serveur ouverte pendant l'utilisation.

### Mot de passe MySQL XAMPP

Par défaut, `serveurFlask.py` et `creer_premier_admin.py` se connectent avec l'utilisateur MySQL `root` et un mot de passe vide, comme sur une installation XAMPP courante. Si tu as défini un mot de passe MySQL, remplace `password=""` dans les deux fichiers par ton mot de passe MySQL. Ce mot de passe MySQL est différent du mot de passe de connexion au site.

## Installer l'agent sur les postes clients

Le fichier `JEVIX-Agent.exe` est fourni dans l'archive Windows séparée. Modifie `agent_config.json` pour indiquer l'adresse du serveur, par exemple `http://192.168.1.20:5000/metrics`, puis place le fichier de configuration à côté de l'exécutable. Lance l'exécutable sur le poste client. Le poste doit pouvoir joindre le serveur sur le réseau.

Pour lancer l'agent automatiquement à chaque ouverture de session Windows, place les scripts `activer_demarrage_auto.*` et `desactiver_demarrage_auto.*` à côté de l'agent et de sa configuration, puis double-clique une fois sur `activer_demarrage_auto.cmd`. Pour désactiver ce démarrage, double-clique sur `desactiver_demarrage_auto.cmd`.

## Reconstruire l'exécutable de l'agent

La compilation se fait sur Windows, sur la machine de développement. Python est nécessaire sur cette machine de compilation, mais pas sur les postes clients.

1. Ouvre PowerShell dans le dossier du projet.
2. Exécute `./build-agent.ps1`.
3. Dans `dist/agent_config.json`, indique l'adresse IP ou le nom du serveur.
4. Copie `JEVIX-Agent.exe`, `agent_config.json` et les scripts de démarrage automatique sur le poste client.

## Reprendre le projet sur un nouvel ordinateur avec GitHub

GitHub contient le dépôt distant. Pour récupérer le projet sur ton nouvel ordinateur :

1. Installe et ouvre **GitHub Desktop**, puis connecte-toi au compte qui possède le dépôt.
2. Choisis **File > Clone repository**, sélectionne le dépôt JEVIX, puis choisis un dossier sur le nouvel ordinateur.
3. Le dossier cloné est ta copie de travail. N'efface pas le dépôt GitHub et ne remplace pas son dossier `.git`.
4. Si tu dois y reporter les changements de cette archive, copie les fichiers du projet dans le dossier cloné en conservant `.git`, puis consulte l'onglet **Changes** dans GitHub Desktop.
5. Vérifie les changements, écris un résumé, clique **Commit to main**, puis **Push origin** pour les envoyer sur GitHub.

Le fichier `.flask_secret` et les configurations locales sont exclus de Git. Après avoir cloné le projet sur une autre machine serveur, crée sa propre clé en exécutant `py generer_cle_flask.py`, puis crée/configure la base et le compte administrateur selon les étapes ci-dessus.

## Auteur

NGONGO KAMBALA Jevic — projet de fin d'année (3ème Licence en Informatique).


