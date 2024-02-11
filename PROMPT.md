  # Application Flask

  J'ai une application en Python avec Flask et qui communique avec une base de donnéer MongoDB.
  J'ai une certaine structure de projet avec des dossiers `application`, `domain` et `infrastructure`.

  ## Technologies

  - Python
  - Flask
  - MongoDB

  ## Architecture de l'application

  ```markdown
  app/application/_init_.py
  app/application/chat_service.py
  app/application/game_service.py
  app/application/score_service.py
  app/application/user_service.py
  app/domain/_init_.py
  app/domain/chat_message.py
  app/domain/game.py
  app/domain/score.py
  app/domain/user.py
  app/infrastructure/_init_.py
  app/infrastructure/game_repository.py
  app/_init_.py
  flask/bin
  flask/lib
  templates/index.html
  tests/test_game_service.py
  test_user_service.py
  app.py
  db.py
  requirements.txt
  ```

  ## Ma demande

  J'ai une certaine structure de projet avec les dossiers `application`, `domain` et `infrastructure`. Je veux ajouter un système d'authentification.

  Je n'ai pas encore créé la base de données MongoDB. Je veux créer une base de données MongoDB avec une collection "users".
  
  J'ai crée ma base de données qui se nomme -> `instantplayhub`, elle a une collection `users`.
  J'ai mis en place un système d'insciption pour les utilisateurs.
  J'ai ce code pour chaque fichiers :
