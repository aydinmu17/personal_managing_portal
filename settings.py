DEBUG = True
SECRET_KEY = "secret"
WTF_CSRF_ENABLED = True
PASSWORDS = {
    "admin": "$pbkdf2-sha256$29000$PIdwDqH03hvjXAuhlLL2Pg$B1K8TX6Efq3GzvKlxDKIk4T7yJzIIzsuSegjZ6hAKLk",
    "cordi": "$pbkdf2-sha256$29000$fk9J6f0fQ8hZSykFwJjT2g$kvI6dSWvHo6y1XMb9Nj8/tuykxTrbU8oTSY7W8Fbyyc",
    "normaluser":"$pbkdf2-sha256$29000$g5CS8n7PeY9xDmGslbJW6g$2sDoK21bAwKtxmQsgXpMS2hRJfeCRDdQJ/j6CttpqDE",
}

ADMIN_USERS = ["admin"]
COORDINATORS = ["cordi"]