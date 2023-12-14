Multi-Platform_Job_Recommender/
├── backend/
│   ├── app.py
│   ├── config/
│   │   └── config.yaml
│   ├── cronjob
│   ├── data/
│   │   ├── external/
│   │   ├── interim/
│   │   ├── processed/
│   │   └── raw/
│   ├── dir_tree_backend.md
│   ├── Dockerfile
│   ├── docs/
│   │   ├── commands.rst
│   │   ├── conf.py
│   │   ├── getting-started.rst
│   │   ├── index.rst
│   │   ├── make.bat
│   │   └── Makefile
│   ├── etl/
│   │   ├── databases/
│   │   │   ├── cassandra/
│   │   │   │   ├── cassandra_conn.py
│   │   │   │   ├── data_models.py
│   │   │   │   ├── routes/
│   │   │   │   ├── setup_db.py
│   │   │   │   └── table_models.py
│   │   │   ├── chroma/
│   │   │   │   ├── chroma_conn.py
│   │   │   │   ├── data_models.py
│   │   │   │   ├── routes/
│   │   │   │   └── setup_db.py
│   │   │   └── routes/
│   │   │       └── admin.py
│   │   ├── extract/
│   │   │   └── site_scraper.py
│   │   ├── load/
│   │   │   ├── load_cassandra.py
│   │   │   └── load_chroma.py
│   │   ├── transform/
│   │   │   └── vectorizer.py
│   │   └── utils/
│   │       └── utilities.py
│   ├── logs/
│   │   ├── backend.log
│   │   └── pipeline.log
│   ├── models/
│   ├── notebooks/
│   │   ├── cassandra_exp.ipynb
│   │   ├── chroma_exp.ipynb
│   │   ├── embedding_exp.ipynb
│   │   ├── milvus_exp.ipynb
│   │   ├── sample_jobs.csv
│   │   └── scraping_exp.ipynb
│   ├── pipelines/
│   │   └── scrape_jobs.py
│   ├── README.md
│   ├── references/
│   ├── reports/
│   │   └── figures/
│   ├── requirements.txt
│   ├── setup.py
│   ├── src/
│   │   ├── data/
│   │   │   └── make_dataset.py
│   │   ├── features/
│   │   ├── models/
│   │   │   └── embedding_model.py
│   │   ├── utils/
│   │   │   ├── backend_log_config.py
│   │   │   ├── dir_tree_gen.py
│   │   │   ├── get_model.py
│   │   │   └── pipeline_log_config.py
│   │   └── validation/
│   │       └── validate.py
│   ├── src.egg-info/
│   │   ├── dependency_links.txt
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   └── top_level.txt
│   └── tests/
│       ├── site_scraping/
│       │   └── test_site_scraping.py
│       ├── utilities/
│       │   └── test_etl_utils.py
│       └── vectorize/
│           └── test_vectorize.py
├── databases/
│   ├── cassandra_db/
│   │   └── cassandra/
│   │       └── data/
│   │           ├── commitlog/
│   │           ├── data/
│   │           ├── hints/
│   │           └── saved_caches/
│   └── chroma_db/
├── docker-compose.yml
├── frontend/
│   ├── assets/
│   │   ├── bg_img.jpg
│   │   └── form_bg.jpg
│   ├── config/
│   │   └── config.yaml
│   ├── dir_tree_frontend.md
│   ├── Dockerfile
│   ├── Home.py
│   ├── logs/
│   │   └── frontend.log
│   ├── pages/
│   │   ├── 0_Search_Jobs.py
│   │   └── 1_Profile.py
│   ├── README.md
│   ├── requirements.txt
│   ├── setup.py
│   ├── src/
│   │   └── utils/
│   │       ├── config.py
│   │       ├── frontend_log_config.py
│   │       ├── hasher.py
│   │       └── page_styling.py
│   ├── src.egg-info/
│   │   ├── dependency_links.txt
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   └── top_level.txt
│   └── tests/
│       ├── config/
│       │   └── test_config.py
│       ├── hashing/
│       │   └── test_hashing.py
│       ├── page_styling/
│       │   └── test_page_styling.py
│       └── test_files/
│           ├── test_docker_config.yaml
│           └── test_local_config.yaml
├── LICENSE
├── Makefile
├── README.md
├── src.egg-info/
│   ├── dependency_links.txt
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   └── top_level.txt
├── test_environment.py
└── tox.ini
