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

### TODO
1. Add user [admin] 
    /adduser -> esce la lista degli utenti che si possono aggiungere in base a quelli presenti nel gruppo meno quelli già aggiunte nel bot
    /adduser nomeutente -> aggiunge l'utente
2. Remove user [admin] 
	/deluser -> lista degli utenti che si possono eliminare dal bot 
	/deluser nomeutente -> cancella l'utente
3. Set calendar [admin]
	/set -> esce la lista dei giorni -> selezione di un giorno -> visualizza lista del materiale per la raccolta (alcuni default oppure testo libero)
