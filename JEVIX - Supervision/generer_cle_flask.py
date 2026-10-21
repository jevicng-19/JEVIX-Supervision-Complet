"""Create the private random key used to sign Flask session cookies."""

import secrets
from pathlib import Path


key_file = Path(__file__).with_name(".flask_secret")
if key_file.exists():
    print(f"La clé existe déjà : {key_file}")
    print("Elle est conservée pour ne pas déconnecter les sessions existantes.")
else:
    key_file.write_text(secrets.token_hex(32), encoding="ascii")
    print(f"Clé Flask créée dans : {key_file}")
    print("Ne partagez pas ce fichier et ne l'envoyez pas sur GitHub.")
