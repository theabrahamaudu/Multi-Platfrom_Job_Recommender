Multi-Platform Job Recommender
==============================

A webapp to recommend jobs scrapped from multiple job platforms to users based on their unique profiles and recent activity with the aid of NLP techniques.

Project Organization
------------
Tree Structures:
- [Overall](./dir_tree.md)
- [Frontend](./frontend/dir_tree_frontend.md)
- [Backend](./backend/dir_tree_backend.md)

------------


Quick Start
===========
Spin up an instannce of the Job Recommender app on your local machine in a few simple steps:

- Clone this repository
    ~~~
    git clone https://github.com/theabrahamaudu/Multi-Platfrom_Job_Recommender.git
    ~~~
- Create a virtual environment
- Install `transformers` package
    ~~~
    pip install transformers==4.35.2
    ~~~
- Download recommender model
    ~~~
    cd backend && python src/utils/get_model.py
    ~~~
- Build and spin up Docker containers
    ~~~
    cd .. && COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker compose up -d
    ~~~
- Open the URL of the frontend container via the Docker Desktop  

-----
Other Stuff:
~~~
pytest --cov=. tests/

python backend/src/utils/dir_tree_gen.py

python backend/src/utils/dir_tree_gen.py frontend

python backend/src/utils/dir_tree_gen.py backend
~~~