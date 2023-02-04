## Config
### conf/conf.json
```
{
  "telegram_noobot_trash_bot": {
      "api": "https://api.telegram.org/bot",
      "token": "API_TOKEN"
  }
}
```

### chat.json
```
{
  "telegram_chat_id": {
    "trash-turn": [
      {
        "id": telegram_id,
        "time": 1588283338
      },
      {
        "id": telegram_id,
        "time": 1588381381
      },
      {
        "id": telegram_id,
        "time": 1588456688
      }
    ],
    "users": {
      "telegram_id": {
      },
      "telegram_id": {
      },
      "telegram_id": {
      }
    },
    "trash_threw": 5,
    "calendar": {
      "4": "Umido",
      "3": "Carta/Plastica",
      "5": "",
      "6": "Umido",
      "2": "Indifferenziato",
      "1": "Umido/Vetro",
      "0": "Carta/Plastica"
    },
    "trash-list": [
      {
        "id": telegram_id,
        "time": 1588100755
      },
      {
        "id": telegram_id,
        "time": 1588283338
      },
      {
        "id": telegram_id,
        "time": 1588381381
      },
      {
        "id": telegram_id,
        "time": 1588456688
      }
    ]
  }
}
```

### TODO
1. Add user [admin] 
    /adduser -> esce la lista degli utenti che si possono aggiungere in base a quelli presenti nel gruppo meno quelli già aggiunte nel bot
    /adduser nomeutente -> aggiunge l'utente
2. Remove user [admin] 
	/deluser -> lista degli utenti che si possono eliminare dal bot 
	/deluser nomeutente -> cancella l'utente
3. Set calendar [admin]
	/set -> esce la lista dei giorni -> selezione di un giorno -> visualizza lista del materiale per la raccolta (alcuni default oppure testo libero)
