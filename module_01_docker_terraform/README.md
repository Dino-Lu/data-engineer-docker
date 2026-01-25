# Module 1 Homework: Docker & SQL

## Question 1: Understanding Docker images

Command used:

```bash
docker run -it --rm --entrypoint=bash python:3.13
pip --version
```

Answer: 25.3


## Question 2: Understanding Docker networking

Answer:
db:5432

Explanation:
Docker Compose creates a shared network for services.
Containers communicate with each other using the service name as the hostname
and the internal container port.
pgAdmin connects to PostgreSQL using the docker-compose service name which is db
and the internal container port which is 5432.

