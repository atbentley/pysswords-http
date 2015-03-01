Pysswords-HTTP: A HTTP API for Pysswords
========================================
Pysswords is a login credential manager. Pysswords-HTTP exposes Pysswords to an API that browser extensions (amongst other things) can call easily.

Pysswords-HTTP is built using Flask and Flask-Restful.

Pysswords-HTTP does not currently transmit over HTTPS, however passwords are transmitted in their encyrpted Pysswords form.
API
---
There is only one end-point for the api, `/credential/<name>`

Examples
--------
First, initialize the Pysswords database from the commandline.
```
pysswords --init
```

Start the pysswords-http server
```
python pysswords-http.py
```

Add some credentials
```
curl localhost:5000/credentials/google.com \
    --data "login=andrew.t.bentley@gmail.com" \
    --data "password="secret" \
    -X PUT
```

Retrieve credentials
```
curl localhost:5000/credentials/google.com -X GET
```

Different databases can be selected by using the `database` argument
```
curl localhost:5000/credentials/google.com \
    --data "database=/home/andrew/.pysswords-db" \
    -X GET
```

