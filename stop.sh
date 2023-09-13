#!/bin/bash

# Arrêter le serveur API (dans le dossier 'api')
pkill -f "flask run -p 5000"

# Arrêter le serveur Flask d'affichage (dans le dossier principal)
pkill -f "flask run -p 5001"
