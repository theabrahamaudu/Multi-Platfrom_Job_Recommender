backend/
├── app.py
├── config/
│   └── config.yaml
├── cronjob
├── dir_tree_backend.md
├── Dockerfile
├── docs/
│   ├── commands.rst
│   ├── conf.py
│   ├── getting-started.rst
│   ├── index.rst
│   ├── make.bat
│   └── Makefile
├── etl/
│   ├── databases/
│   │   ├── cassandra/
│   │   │   ├── cassandra_conn.py
│   │   │   ├── data_models.py
│   │   │   ├── routes/
│   │   │   │   ├── clicks.py
│   │   │   │   ├── job.py
│   │   │   │   ├── search.py
│   │   │   │   └── user.py
│   │   │   ├── setup_db.py
│   │   │   └── table_models.py
│   │   ├── chroma/
│   │   │   ├── chroma_conn.py
│   │   │   ├── data_models.py
│   │   │   ├── routes/
│   │   │   │   └── job_index.py
│   │   │   └── setup_db.py
│   │   └── routes/
│   │       └── admin.py
│   ├── extract/
│   │   └── site_scraper.py
│   ├── load/
│   │   ├── load_cassandra.py
│   │   └── load_chroma.py
│   ├── transform/
│   │   └── vectorizer.py
│   └── utils/
│       └── utilities.py
├── logs/
│   ├── backend.log
│   └── pipeline.log
├── models/
├── notebooks/
│   ├── cassandra_exp.ipynb
│   ├── chroma_exp.ipynb
│   ├── embedding_exp.ipynb
│   ├── milvus_exp.ipynb
│   ├── sample_jobs.csv
│   └── scraping_exp.ipynb
├── pipelines/
│   └── scrape_jobs.py
├── README.md
├── references/
├── reports/
│   └── figures/
├── requirements.txt
├── setup.py
├── src/
│   ├── features/
│   ├── models/
│   │   └── embedding_model.py
│   ├── utils/
│   │   ├── backend_log_config.py
│   │   ├── dir_tree_gen.py
│   │   ├── get_model.py
│   │   └── pipeline_log_config.py
│   └── validation/
│       └── validate.py
├── src.egg-info/
│   ├── dependency_links.txt
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   └── top_level.txt
└── tests/
    ├── site_scraping/
    │   └── test_site_scraping.py
    ├── utilities/
    │   └── test_etl_utils.py
    └── vectorize/
        └── test_vectorize.py
