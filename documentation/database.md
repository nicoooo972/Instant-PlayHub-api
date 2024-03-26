# Documentation de la base de données

**Nom** : instantplayhub

## Collections

```json
users
messages
chat
```

## Documents

Documents avec leurs champs associés.

### users

```json
  {
    _id: '2c4516aa1e5545858fa0eb177814708d',
    username: 'Xxx_Dark_Sasuke_xxX',
    email: 'exemple@gmail.com',
    password: '$pbkdf2-sha256$29000$SllhNDclYXg3ZThNTDg6RCM9bS0$LiwiIcioqS0ViGzM6c2.zw6odERSrUbaeaPnyooqdEQ'
    created_at: 24/03/2024 16:25:14
  }
```

### chat

```json
{
    "_id": '2c8745aa1e5542014fa0eb177815555d',
    "name": 'Amis',
    "users": [Tableau de références avec les id des utilisateurs du chat],
    "messages": [Tableau de références qui contient tous les messages du chat (id des messages)],
    "created_at": 24/03/2024 18:45:10
}
```

### message

```json
{
    "_id": '2c8745aa1e5542014fa0eb177815555d',
    "user_id": ObjectId("61e9c7e1d9a087001f5c6115"),
    "users": [Tableau de référence avec les id des utilisateurs du chat],
    "content": "Bonjour tout le monde !",
    "created_at": 24/03/2024 18:45:10
}

```
