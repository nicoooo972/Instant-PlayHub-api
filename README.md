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

Se déplacer dans le répertoire du projet
```shell
cd pfr-api
```

Création de l'environnement virtuel
```shell
virtualenv flask
```

Activer l'environnement virtuel
```shell
source flask/bin/activate
```

Installer les dépendances dans l'environnement virtuel
```shell
pip3 install flask
```

Lancer l'application
```shell
export FLASK_APP=app.py flask run
```

Afin de faire fonctionner flask_socketio, il faut lancer la commande suivante :
```shell
pip install Flask Flask-SocketIO
```