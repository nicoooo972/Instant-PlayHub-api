# PFR-api

Assurez-vous que pip3 est à jour (facultatif)
```shell
python3 -m pip install --upgrade pip
```

Installation de virtualenv
```shell
python3 -m pip install virtualenv
```

Cloner ou télécharger le code source de l'application
```shell
git clone https://github.com/nicoooo972/pfr-api.git 
```


Création de l'environnement virtuel en dehors du projet
```shell
python3 -m venv nom_de_votre_env
```

Activer l'environnement virtuel
```shell
source nom_de_votre_env/bin/activate
```
Rentrer dans le projet

Installer les dépendances dans l'environnement virtuel
```shell
pip3 install -r requirements.txt
```

Lancer l'application
```shell
export FLASK_APP=app.py flask run
```
