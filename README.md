<p align="center">
  <a href="https://google.com" target="blank"><img src="" width="200" alt="Instant PlayHub logo" /></a>
</p>

## Description

Dépôt Back-End du projet [Instant PlayHub](https://github.com/nicoooo972/Instant-PlayHub-api).

Dépôt Front-End du projet de [Instant PlayHub](https://github.com/FloFlo-L/instant-playhub-front)

**Instant PlayHub** est une plateforme de jeu en ligne en temps réel permettant aux joueurs de s'affronter dans des jeux tels que des quiz, des jeux de stratégie ou des jeux d'adresse.

## Les développeurs du chaos

- [Florian **LESCRIBAA**](https://github.com/FloFlo-L)
- [Nicolas **LE BOZEC**](https://github.com/nicoooo972)
- [Lisa **AU**](https://github.com/lis-a)
- [Steven **YAMBOS**](https://github.com/StevenYAMBOS)

## Technologies utilisées

### Front-End

- **ReactJS** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/React-icon.svg/2300px-React-icon.svg.png" width="30px" alt="ReactJS logo" />
- **Tailwind** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Tailwind_CSS_Logo.svg/1024px-Tailwind_CSS_Logo.svg.png" width="30px" alt="Tailwind logo" />

### Back-End

- **Flask** <img src="https://static-00.iconduck.com/assets.00/programming-language-flask-icon-2048x1826-wf5k5ugs.png" width="30px" alt="Flask logo" />
- **Flask-SocketIO** <img src="https://upload.wikimedia.org/wikipedia/commons/9/96/Socket-io.svg" width="30px" alt="Flask logo" />
- **Python** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1869px-Python-logo-notext.svg.png" width="30px" alt="ReactJS logo" />
- **MongoDB** <img src="https://cdn.worldvectorlogo.com/logos/mongodb-icon-1.svg" width="30px" alt="MongoDB logo" />

### Déploiement

- **Docker** <img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/Docker_%28container_engine%29_logo_%28cropped%29.png" width="30px" alt="Docker logo" />
- **Kubernetes** <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Kubernetes_logo_without_workmark.svg/2109px-Kubernetes_logo_without_workmark.svg.png" width="30px" alt="Kubernetes logo" />
- **Amazon Web Services** <img src="https://download.logo.wine/logo/Amazon_Web_Services/Amazon_Web_Services-Logo.wine.png" width="30px" alt="AWS logo" />

### Hébergement

- **o2Switch** <img src="https://www.o2switch.fr/wp-content/uploads/147.svg" width="30px" alt="o2Switch logo" />

## Fonctionnalités principales

- Inscription et connexion des joueurs
- Création de parties en ligne
- Choix de jeux disponibles en temps réel
- Affichage de classements pour chaque jeu
- Discussion en ligne entre les joueurs
- Partage de scores sur les réseaux sociaux

## Installation

Assurez-vous que **pip3** est à jour (facultatif)

```shell
python3 -m pip install --upgrade pip
```

Installation de **virtualenv**

```shell
python3 -m pip install virtualenv
```

**Cloner** ou **télécharger** le code source de l'application

```shell
git clone https://github.com/nicoooo972/pfr-api.git 
```

Création de l'**environnement virtuel** en dehors du projet

```shell
python3 -m venv nom_de_votre_env
```

Activer l'**environnement virtuel**

```shell
source nom_de_votre_env/bin/activate
```

Rentrer dans le projet. Installer les dépendances dans l'environnement virtuel

```shell
pip3 install -r requirements.txt
```

Lancer l'application

```shell
export FLASK_APP=app.py flask run

OU

python3 app.py
```
