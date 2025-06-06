# 🚀 Plateforme de Blog Django Isitech

Une plateforme de blog moderne et complète développée avec Django, offrant des fonctionnalités avancées de gestion de contenu, d'analyse et d'intelligence artificielle.

## 📋 Table des Matières

- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Technologies Utilisées](#-technologies-utilisées)
- [Architecture du Projet](#-architecture-du-projet)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [API REST](#-api-rest)
- [Gestion des Utilisateurs](#-gestion-des-utilisateurs)
- [Fonctionnalités Avancées](#-fonctionnalités-avancées)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)
- [Support](#-support)

## ✨ Fonctionnalités Principales

### 🎯 Gestion de Contenu
- **Création et édition d'articles** avec éditeur riche
- **Système de catégories** avec icônes et couleurs personnalisables
- **Système de tags** avec tendances et popularité
- **Gestion des médias** avec upload d'images
- **Brouillons et publication** avec gestion des statuts
- **Système de commentaires** avec modération

### 👥 Gestion des Utilisateurs
- **Système de rôles** : Lecteur, Auteur, Éditeur, Admin
- **Profils utilisateurs** complets avec avatars et bio
- **Authentification sécurisée** avec JWT
- **Permissions granulaires** basées sur les rôles
- **Dashboard personnalisé** pour chaque type d'utilisateur

### 🔍 Recherche et Navigation
- **Recherche avancée** avec filtres multiples
- **Autocomplétion** en temps réel
- **Mise en évidence** des termes recherchés
- **Filtrage par catégories** et tags
- **Navigation intuitive** avec pagination

### 📊 Analytics et Statistiques
- **Dashboard analytics** complet pour les administrateurs
- **Suivi des vues** et temps de lecture
- **Métriques d'engagement** (likes, commentaires, partages)
- **Analyse des tendances** mensuelles
- **Statistiques utilisateurs** et contenu
- **Exports de données** pour analyse externe

### 🤖 Intelligence Artificielle
- **Générateur d'articles IA** utilisant l'API Gemini
- **Création automatique** de contenu basé sur des sujets
- **Suggestions intelligentes** pour l'amélioration du contenu
- **Analyse de sentiment** des commentaires

### 🌍 Internationalisation
- **Support multilingue** : Français, Anglais, Espagnol
- **Interface traduite** complètement
- **Changement de langue** en temps réel
- **Localisation** des dates et formats

### 💡 Fonctionnalités Sociales
- **Système de likes** pour les articles
- **Bookmarks** pour sauvegarder les articles favoris
- **Profils publics** des auteurs
- **Système de followers** (en développement)
- **Partage social** intégré

## 🛠 Technologies Utilisées

### Backend
- **Django 5.2.1** - Framework web Python
- **Python 3.13** - Langage de programmation
- **PostgreSQL** - Base de données relationnelle
- **Django REST Framework** - API REST
- **JWT Authentication** - Authentification sécurisée

### Frontend
- **HTML5 / CSS3** - Structure et style
- **Bootstrap 4** - Framework CSS responsive
- **JavaScript (ES6+)** - Interactivité côté client
- **jQuery** - Manipulation DOM simplifiée
- **Chart.js** - Visualisation de données

### Outils et Services
- **Google Gemini API** - Intelligence artificielle
- **Crispy Forms** - Rendu de formulaires
- **Django Filters** - Filtrage avancé
- **Pillow** - Traitement d'images
- **Python Dotenv** - Gestion des variables d'environnement

### DevOps et Monitoring
- **Logging avancé** - Suivi des erreurs et activités
- **Middleware personnalisé** - Analytics et permissions
- **Tests unitaires** - Assurance qualité
- **Documentation API** - Swagger/OpenAPI

## 🏗 Architecture du Projet

```
Isitech_django/
├── 📁 Isitech_django/          # Configuration principale
│   ├── settings.py             # Paramètres Django
│   ├── urls.py                 # URLs principales
│   └── wsgi.py                 # Configuration WSGI
├── 📁 isitechdjango/           # Application principale
│   ├── models.py               # Modèles de données
│   ├── views.py                # Vues et logique métier
│   ├── forms.py                # Formulaires Django
│   ├── middleware.py           # Middleware personnalisé
│   ├── 📁 api/                 # API REST
│   ├── 📁 templates/           # Templates HTML
│   ├── 📁 static/              # Fichiers statiques
│   └── 📁 migrations/          # Migrations de base
├── 📁 analytics/               # Module d'analytics
├── 📁 notifications/           # Système de notifications
├── 📁 locale/                  # Fichiers de traduction
├── 📁 media/                   # Fichiers uploadés
└── 📁 logs/                    # Logs de l'application
```

## 🔧 Prérequis

- **Python 3.11+** (testé avec Python 3.13)
- **PostgreSQL 12+** 
- **Git** pour la gestion de version
- **Virtualenv** ou **conda** pour l'environnement virtuel

### Optionnel
- **Redis** pour le cache (production)
- **Nginx** pour le serveur web (production)
- **Docker** pour la conteneurisation

## 🚀 Installation

### 1. Cloner le Projet

```bash
git clone https://github.com/votre-username/isitech-django-blog.git
cd isitech-django-blog
```

### 2. Créer un Environnement Virtuel

```bash
# Avec virtualenv
python3 -m venv isitech_env
source isitech_env/bin/activate
```

### 3. Installer les Dépendances

```bash
# Installer les packages Python requis
pip install django==5.2.1
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-filter
pip install django-crispy-forms
pip install crispy-bootstrap4
pip install django-widget-tweaks
pip install pillow
pip install psycopg2-binary
pip install python-dotenv
pip install google-generativeai

# Ou créer un requirements.txt et l'utiliser
pip freeze > requirements.txt
```

### 4. Configuration de la Base de Données

#### PostgreSQL
```bash
# Se connecter à PostgreSQL
psql -U postgres

# Créer la base de données
CREATE DATABASE isitech;
CREATE USER maxime WITH PASSWORD 'admin';
GRANT ALL PRIVILEGES ON DATABASE isitech TO maxime;
\q
```

### 5. Variables d'Environnement

Créer un fichier `.env` à la racine du projet :

```env
# Base de données
DB_NAME=isitech
DB_USER=maxime
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=votre-clé-secrète-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# API Gemini (optionnel)
GEMINI_API_KEY=votre-clé-api-gemini

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
```

### 6. Migrations et Configuration

```bash
# Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Compiler les traductions
python manage.py compilemessages
```

### 7. Données de Test (Optionnel)

```bash
# Charger des données de démonstration
python manage.py loaddata fixtures/categories.json
python manage.py loaddata fixtures/articles.json
```

## ⚙️ Configuration

### Configuration Django (settings.py)

Le projet utilise plusieurs configurations importantes :

#### Base de Données
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'isitech',
        'USER': 'maxime',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### Internationalisation
```python
LANGUAGES = [
    ('en', 'English'),
    ('fr', 'French'),
    ('es', 'Spanish'),
]

USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / 'locale']
```

#### API REST
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}
```

### Configuration des Médias

```python
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## 🎮 Utilisation

### Démarrer le Serveur de Développement

```bash
python manage.py runserver
```

L'application sera accessible à : `http://127.0.0.1:8000/`

### Interface d'Administration

Accéder à l'admin Django : `http://127.0.0.1:8000/admin/`

### Workflow Typique

1. **Créer des Catégories** via l'interface admin ou l'interface web
2. **Ajouter des Articles** avec le générateur IA ou manuellement
3. **Gérer les Utilisateurs** et leurs rôles
4. **Modérer les Commentaires** via le dashboard
5. **Analyser les Performances** avec le tableau de bord analytics

## 🔌 API REST

### Authentification JWT

```bash
# Obtenir un token
curl -X POST http://localhost:8000/en/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "votre_username", "password": "votre_password"}'

# Utiliser le token
curl -H "Authorization: Bearer votre_token" \
  http://localhost:8000/en/api/v1/articles/
```

### Endpoints Principaux

- **Articles** : `/api/v1/articles/`
- **Catégories** : `/api/v1/categories/`
- **Tags** : `/api/v1/tags/`
- **Commentaires** : `/api/v1/comments/`
- **Likes** : `/api/v1/likes/`
- **Bookmarks** : `/api/v1/bookmarks/`

### Exemples d'Utilisation

```python
# Test de l'API avec Python
import requests

# Authentification
response = requests.post('http://localhost:8000/en/api/v1/auth/token/', {
    'username': 'votre_username',
    'password': 'votre_password'
})
token = response.json()['access']

# Récupérer les articles
headers = {'Authorization': f'Bearer {token}'}
articles = requests.get('http://localhost:8000/en/api/v1/articles/', headers=headers)
```

## 👤 Gestion des Utilisateurs

### Rôles et Permissions

| Rôle | Permissions |
|------|-------------|
| **Lecteur** | Lecture, commentaires, likes, bookmarks |
| **Auteur** | + Création d'articles, dashboard personnel |
| **Éditeur** | + Modération commentaires, édition articles autres |
| **Admin** | + Gestion utilisateurs, analytics, configuration |

### Création d'Utilisateurs

```python
# Via le shell Django
python manage.py shell

from django.contrib.auth.models import User
from isitechdjango.models import UserProfile

user = User.objects.create_user('username', 'email@example.com', 'password')
profile = UserProfile.objects.create(user=user, role='author')
```

## 🔥 Fonctionnalités Avancées

### Générateur d'Articles IA

Le système utilise l'API Google Gemini pour générer automatiquement du contenu :

```python
# Configuration dans settings.py
GEMINI_API_KEY = 'votre-clé-api'

# Utilisation dans views.py
from google.generativeai import configure, GenerativeModel

def generate_article(topic):
    configure(api_key=settings.GEMINI_API_KEY)
    model = GenerativeModel('gemini-pro')
    response = model.generate_content(f"Écris un article de blog sur : {topic}")
    return response.text
```

### Analytics Avancées

Le système de tracking inclut :

- **Vues d'articles** avec temps de lecture
- **Engagement utilisateur** (likes, commentaires, partages)
- **Sources de trafic** et données démographiques
- **Performance du contenu** et tendances
- **Métriques en temps réel**

### Système de Recherche

Recherche intelligente avec :

```python
# Recherche multicritères
class SearchEngine:
    @staticmethod
    def search(query, filters=None):
        # Recherche dans titre, contenu, tags
        articles = Article.objects.filter(
            Q(titre__icontains=query) |
            Q(contenu__icontains=query) |
            Q(tags__nom__icontains=query)
        ).distinct()
        
        # Application des filtres
        if filters:
            if filters.get('category'):
                articles = articles.filter(categorie=filters['category'])
            if filters.get('author'):
                articles = articles.filter(auteur=filters['author'])
                
        return articles
```

### Middleware Personnalisé

```python
# Analytics Middleware
class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Tracking avant la requête
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Tracking après la requête
        PageView.objects.create(
            path=request.path,
            user=request.user if request.user.is_authenticated else None,
            ip_address=self.get_client_ip(request),
            response_time=time.time() - start_time
        )
        
        return response
```

## 📱 Interface Utilisateur

### Design Responsive

L'interface utilise Bootstrap 4 avec des composants personnalisés :

- **Navigation adaptative** avec menu mobile
- **Cards modernes** pour l'affichage des articles
- **Formulaires stylisés** avec validation côté client
- **Dashboard interactif** avec graphiques Chart.js
- **Mode sombre** (en développement)

### Composants Réutilisables

```html
<!-- Template de base -->
{% extends 'blog/base.html' %}
{% load i18n %}
{% load widget_tweaks %}

{% block content %}
<div class="modern-card">
    <div class="card-header">
        <h2>{% trans "Article Title" %}</h2>
    </div>
    <div class="card-body">
        <!-- Contenu -->
    </div>
</div>
{% endblock %}
```

## 🧪 Tests

### Tests Unitaires

```bash
# Lancer tous les tests
python manage.py test

# Tests spécifiques
python manage.py test isitechdjango.tests.ArticleModelTest
python manage.py test analytics.tests
```

### Tests API

```bash
# Tester l'API REST
python test_api.py
```

### Coverage

```bash
# Installation de coverage
pip install coverage

# Lancer les tests avec coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Monitoring et Logs

### Configuration des Logs

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### Surveillance en Production

- **Logs centralisés** dans le dossier `/logs/`
- **Monitoring des erreurs** avec alertes
- **Métriques de performance** intégrées
- **Health checks** automatiques

## 🌐 Déploiement

### Déploiement sur Serveur Linux

#### 1. Préparation du Serveur

```bash
# Mise à jour du système
sudo apt update && sudo apt upgrade -y

# Installation des dépendances
sudo apt install python3 python3-pip python3-venv postgresql nginx supervisor -y
```

#### 2. Configuration PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE isitech_prod;
CREATE USER isitech_user WITH PASSWORD 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE isitech_prod TO isitech_user;
\q
```

#### 3. Configuration du Projet

```bash
# Cloner le projet
git clone https://github.com/votre-repo/isitech-django.git /var/www/isitech
cd /var/www/isitech

# Environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Dépendances
pip install -r requirements.txt

# Variables d'environnement production
cp .env.example .env.prod
# Éditer .env.prod avec les valeurs de production
```

#### 4. Configuration Nginx

```nginx
# /etc/nginx/sites-available/isitech
server {
    listen 80;
    server_name votre-domaine.com;

    location /static/ {
        alias /var/www/isitech/static/;
    }

    location /media/ {
        alias /var/www/isitech/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 5. Configuration Supervisor

```ini
# /etc/supervisor/conf.d/isitech.conf
[program:isitech]
command=/var/www/isitech/venv/bin/gunicorn Isitech_django.wsgi:application
directory=/var/www/isitech
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/isitech.log
environment=DJANGO_SETTINGS_MODULE="Isitech_django.settings"
```

### Déploiement avec Docker

#### Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "Isitech_django.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:password@db:5432/isitech
    depends_on:
      - db
    volumes:
      - ./media:/app/media
      - ./static:/app/static

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: isitech
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/var/www/static
      - ./media:/var/www/media
    depends_on:
      - web

volumes:
  postgres_data:
```

### Déploiement Cloud

#### Heroku

```bash
# Installation Heroku CLI
npm install -g heroku

# Login et création de l'app
heroku login
heroku create isitech-blog-app

# Configuration des variables
heroku config:set SECRET_KEY="votre-clé-secrète"
heroku config:set DEBUG=False
heroku config:set DATABASE_URL="postgres://..."

# Déploiement
git push heroku main

# Migrations
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

#### AWS/DigitalOcean

Configuration similaire avec des services managés :
- **RDS** pour PostgreSQL
- **S3** pour les fichiers statiques
- **CloudFront** pour le CDN
- **Elastic Beanstalk** ou **App Platform**

## 🔧 Maintenance

### Sauvegarde

```bash
# Sauvegarde de la base de données
pg_dump -U maxime -h localhost isitech > backup_$(date +%Y%m%d).sql

# Sauvegarde des médias
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/

# Script automatisé
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U maxime isitech > /backups/db_$DATE.sql
tar -czf /backups/media_$DATE.tar.gz media/
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

### Mise à Jour

```bash
# Mise à jour du code
git pull origin main

# Mise à jour des dépendances
pip install -r requirements.txt --upgrade

# Migrations
python manage.py migrate

# Collecte des statiques
python manage.py collectstatic --noinput

# Redémarrage du service
sudo supervisorctl restart isitech
```

### Monitoring des Performances

```python
# Scripts de monitoring
import psutil
import django
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        # CPU et mémoire
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Base de données
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_session")
            active_sessions = cursor.fetchone()[0]
        
        # Logs
        self.stdout.write(f"CPU: {cpu_percent}%")
        self.stdout.write(f"Memory: {memory.percent}%")
        self.stdout.write(f"Active sessions: {active_sessions}")
```

## 🤝 Contribution

### Guide de Contribution

1. **Fork** le projet
2. **Créer une branche** pour votre fonctionnalité
   ```bash
   git checkout -b feature/nouvelle-fonctionnalite
   ```
3. **Commiter** vos changements
   ```bash
   git commit -m "Ajout de la nouvelle fonctionnalité"
   ```
4. **Pousser** vers la branche
   ```bash
   git push origin feature/nouvelle-fonctionnalite
   ```
5. **Créer une Pull Request**

### Standards de Code

- **PEP 8** pour Python
- **Docstrings** pour toutes les fonctions
- **Tests unitaires** pour les nouvelles fonctionnalités
- **Commentaires** en français
- **Messages de commit** descriptifs

### Structure des Commits

```
type(scope): description

body (optionnel)

footer (optionnel)
```

Types : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 📚 Documentation Supplémentaire

### API Documentation
- Documentation Swagger disponible à `/api/docs/`
- Postman Collection dans `/docs/postman/`

### Guides Utilisateur
- `/docs/user-guide.md` - Guide utilisateur complet
- `/docs/admin-guide.md` - Guide administrateur
- `/docs/api-guide.md` - Guide développeur API

### Troubleshooting

#### Problèmes Courants

**Erreur de Base de Données**
```bash
# Vérifier la connexion PostgreSQL
pg_isready -h localhost -p 5432 -U maxime

# Recréer la base si nécessaire
python manage.py flush
python manage.py migrate
```

**Problème de Permissions**
```bash
# Vérifier les permissions des fichiers
chmod -R 755 media/
chown -R www-data:www-data media/
```

**Erreur de Traduction**
```bash
# Recompiler les traductions
python manage.py compilemessages
```

## 🆘 Support

### Canaux de Support

- **Issues GitHub** : Pour les bugs et demandes de fonctionnalités
- **Discussions** : Pour les questions générales
- **Email** : support@isitech-blog.com
- **Documentation** : Wiki GitHub

### FAQ

**Q: Comment ajouter une nouvelle langue ?**
R: Ajoutez la langue dans `LANGUAGES` dans settings.py, créez les fichiers de traduction avec `makemessages`, traduisez et compilez avec `compilemessages`.

**Q: Comment personnaliser le thème ?**
R: Modifiez les fichiers CSS dans `/static/css/` et les templates dans `/templates/`.

**Q: Comment configurer l'API Gemini ?**
R: Obtenez une clé API sur Google AI Studio et ajoutez-la dans vos variables d'environnement.

### Ressources

- **Django Documentation** : https://docs.djangoproject.com/
- **Bootstrap Documentation** : https://getbootstrap.com/docs/
- **PostgreSQL Guide** : https://www.postgresql.org/docs/
- **Chart.js Documentation** : https://www.chartjs.org/docs/

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Équipe Django** pour le framework exceptionnel
- **Bootstrap Team** pour les composants UI
- **Google** pour l'API Gemini
- **Communauté Open Source** pour les packages utilisés

---

**Version** : 1.0.0  
**Dernière mise à jour** : 6 juin 2025  
**Développé avec** ❤️ **par l'équipe Isitech**

Pour plus d'informations, visitez notre [site web](https://isitech-blog.com) ou consultez la [documentation complète](https://docs.isitech-blog.com).
