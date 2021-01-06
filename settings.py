DEBUG = True
SECRET_KEY = "secret"
WTF_CSRF_ENABLED = True
PASSWORDS = {
    "admin": "$pbkdf2-sha256$29000$HYOw1rqXUmpNKaWUMkZICQ$nsn1h6DZSameEQ1OnaWzypXoBpDJyPIQVkuUdknOpRE",
    "cordi": "$pbkdf2-sha256$29000$mnMupRQiJOS8956T8n4PwQ$EJQxhgigjBqOPFWkB.jnkwrNb6zqzEHM73EcU/B6vIw",
    "normaluser":"$pbkdf2-sha256$29000$g5CS8n7PeY9xDmGslbJW6g$2sDoK21bAwKtxmQsgXpMS2hRJfeCRDdQJ/j6CttpqDE",
}

ADMIN_USERS = ["admin", 15,5]
COORDINATORS = ["cordi",2,16]