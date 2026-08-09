# Movie Recommendation System

A Streamlit movie recommendation application based on a precomputed similarity matrix and TMDB movie posters.

## Project structure

```text
movie_recommendation/
├── app.py
├── notebooks/
│   ├── artificats/
│   │   ├── movie_list.pkl
│   │   └── similarity.pkl
│   └── tmdb.ipynb
├── src/movie_recommendation/
│   ├── __init__.py
│   ├── config.py
│   ├── recommender.py
│   └── tmdb.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

```bash
python -m venv .venv
```

Activate the virtual environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and replace the placeholder with your TMDB API key.

## Run the application

```bash
streamlit run app.py
```

## Security

Never commit the `.env` file or your TMDB API key to GitHub.
