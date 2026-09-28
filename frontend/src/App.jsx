import { useDeferredValue, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { fetchMovies, fetchRecommendations } from "./api";

function App() {
  const [search, setSearch] = useState("");
  const [selectedMovieId, setSelectedMovieId] = useState(null);
  const deferredSearch = useDeferredValue(search);
  const normalizedSearch = deferredSearch.trim().toLowerCase();

  const moviesQuery = useQuery({
    queryKey: ["movies"],
    queryFn: ({ signal }) => fetchMovies({ signal }),
    staleTime: 5 * 60_000,
  });

  const recommendationsQuery = useQuery({
    queryKey: ["recommendations", selectedMovieId],
    queryFn: ({ signal }) => fetchRecommendations(selectedMovieId, { signal }),
    enabled: selectedMovieId !== null,
  });

  useEffect(() => {
    if (!selectedMovieId && moviesQuery.data?.movies?.length) {
      setSelectedMovieId(moviesQuery.data.movies[0].movie_id);
    }
  }, [moviesQuery.data, selectedMovieId]);

  const movies = moviesQuery.data?.movies ?? [];
  const filteredMovies = movies
    .filter((movie) => String(movie.title).toLowerCase().includes(normalizedSearch))
    .slice(0, 120);
  const selectedMovie = movies.find((movie) => movie.movie_id === selectedMovieId) ?? null;
  const recommendations = recommendationsQuery.data?.recommendations ?? [];

  return (
    <main className="app-shell">
      <section className="layout">
        <aside className="panel sidebar">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Catalogue</p>
              <h2>Pick a movie</h2>
            </div>
            <span className="count-badge">{filteredMovies.length}</span>
          </div>

          <label className="search-wrap" htmlFor="movie-search">
            <span className="search-label">Search</span>
            <input
              id="movie-search"
              className="search-input"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Type a title..."
              autoComplete="off"
            />
          </label>

          <div className="movie-list" role="listbox" aria-label="Movie catalogue">
            {moviesQuery.isLoading && (
              <>
                <div className="movie-skeleton" />
                <div className="movie-skeleton" />
                <div className="movie-skeleton" />
                <div className="movie-skeleton" />
              </>
            )}

            {moviesQuery.isError && (
              <div className="error-box">
                <strong>Unable to load movies.</strong>
                <span>{moviesQuery.error.message}</span>
              </div>
            )}

            {!moviesQuery.isLoading && !moviesQuery.isError && filteredMovies.length === 0 && (
              <div className="empty-state">
                No matches for <strong>{search || "your search"}</strong>.
              </div>
            )}

            {filteredMovies.map((movie) => {
              const isActive = movie.movie_id === selectedMovieId;

              return (
                <button
                  key={movie.movie_id}
                  type="button"
                  className={`movie-item ${isActive ? "is-active" : ""}`}
                  onClick={() => setSelectedMovieId(movie.movie_id)}
                >
                  <span className="movie-title">{movie.title}</span>
                  <span className="movie-id">#{movie.movie_id}</span>
                </button>
              );
            })}
          </div>
        </aside>

        <section className="panel results">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Recommendations</p>
              <h2>Similar movies</h2>
            </div>
            <span className="count-badge">{recommendations.length}</span>
          </div>

          {recommendationsQuery.isError && (
            <div className="error-box">
              <strong>Unable to load recommendations.</strong>
              <span>{recommendationsQuery.error.message}</span>
            </div>
          )}

          {recommendationsQuery.isLoading && (
            <div className="results-grid">
              <div className="result-skeleton" />
              <div className="result-skeleton" />
              <div className="result-skeleton" />
              <div className="result-skeleton" />
              <div className="result-skeleton" />
            </div>
          )}

          {!recommendationsQuery.isLoading && !recommendationsQuery.isError && (
            <>
              {!selectedMovie && (
                <div className="empty-state">
                  Select a movie to request recommendations from the backend.
                </div>
              )}

              {selectedMovie && recommendations.length === 0 && (
                <div className="empty-state">
                  No recommendations found for <strong>{selectedMovie.title}</strong>.
                </div>
              )}

              <div className="results-grid">
                {recommendations.map((movie, index) => (
                  <article
                    key={`${movie.movie_id}-${movie.title}`}
                    className="result-card"
                    style={{ "--delay": `${index * 70}ms` }}
                  >
                    <div className="poster-frame">
                      {movie.poster_url ? (
                        <img src={movie.poster_url} alt={movie.title} loading="lazy" />
                      ) : (
                        <div className="poster-placeholder">
                          <span>Poster unavailable</span>
                        </div>
                      )}
                    </div>
                    <div className="result-copy">
                      <h3>{movie.title}</h3>
                      <span>#{movie.movie_id}</span>
                    </div>
                  </article>
                ))}
              </div>
            </>
          )}
        </section>
      </section>
    </main>
  );
}

export default App;
