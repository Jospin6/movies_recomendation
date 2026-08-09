# 🎬 Movie Recommendation System

A content-based movie recommendation application built with Python and Streamlit.

The application recommends movies similar to a selected title using a precomputed similarity matrix. Movie posters are retrieved dynamically from the TMDB API and displayed through an interactive Streamlit interface.

## Screenshot

<!-- Replace assets/movie-recommendation-screenshot.png with your screenshot -->

![Movie Recommendation System](screenshot.png)

## Features

- Search and select a movie from the available catalogue
- Generate movies similar to the selected title
- Display recommended movie titles and posters
- Retrieve movie posters from the TMDB API
- Fast recommendations using a precomputed similarity matrix
- Simple and interactive Streamlit interface
- Environment-variable-based API key configuration

## Technologies

- Python
- Streamlit
- Pandas
- Requests
- Pickle
- TMDB API
- Scikit-learn

## Project Structure

```text
movie_recommendation/
├── app.py
├── assets/
│   └── movie-recommendation-screenshot.png
├── notebooks/
│   ├── artificats/
│   │   ├── movie_list.pkl
│   │   └── similarity.pkl
│   └── tmdb.ipynb
├── src/
│   └── movie_recommendation/
│       ├── __init__.py
│       ├── config.py
│       ├── recommender.py
│       └── tmdb.py
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Contributor

- Jospin Ndagano

## License

This project is licensed under the [MIT License](LICENSE).

Copyright © 2026 Jospin Ndagano