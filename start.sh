#!/bin/bash

# Lancer le serveur API (dans le dossier 'api')
cd client  # Accéder au dossier du serveur API
flask run -p 5000 &  # Démarrer le serveur API en arrière-plan

# Revenir au dossier principal (où se trouve le serveur Flask d'affichage)
cd ..

# Lancer le serveur Flask d'affichage
flask run -p 5001
