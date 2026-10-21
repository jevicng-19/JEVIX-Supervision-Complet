"""Interactively create the first JEVIX administrator with a hashed password."""

from getpass import getpass

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "jevix",
}


def main():
    username = input("Nom du premier administrateur : ").strip()
    if not username:
        print("Le nom d'utilisateur ne peut pas être vide.")
        return

    password = getpass("Mot de passe : ")
    confirmation = getpass("Confirme le mot de passe : ")
    if password != confirmation:
        print("Les deux mots de passe ne correspondent pas. Aucun compte créé.")
        return
    if len(password) < 8:
        print("Choisis un mot de passe d'au moins 8 caractères. Aucun compte créé.")
        return

    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id FROM administrateurs WHERE username = %s",
            (username,),
        )
        if cursor.fetchone():
            print("Ce nom existe déjà. Aucun changement effectué.")
            return

        password_hash = generate_password_hash(password)
        cursor.execute(
            """
            INSERT INTO administrateurs (username, password, role)
            VALUES (%s, %s, 'superadmin')
            """,
            (username, password_hash),
        )
        connection.commit()
        print("Compte super administrateur créé. Le mot de passe a été haché.")
    except Error as exc:
        print(f"Erreur MySQL : {exc}")
        print("Vérifie que MySQL tourne et que la base jevix a été importée.")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    main()
