const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(
  /\/$/,
  "",
);

async function request(path, { signal } = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    signal,
    headers: {
      Accept: "application/json",
    },
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;

    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") {
        message = payload.detail;
      } else if (payload?.detail) {
        message = JSON.stringify(payload.detail);
      }
    } catch {
      // Fall back to the HTTP status message.
    }

    throw new Error(message);
  }

  return response.json();
}

export function fetchHealth(options) {
  return request("/health", options);
}

export function fetchMovies(options) {
  return request("/movies", options);
}

export function fetchRecommendations(movieId, options) {
  if (movieId === null || movieId === undefined) {
    throw new Error("A movie id is required.");
  }

  return request(`/recommendations?movie_id=${encodeURIComponent(movieId)}`, options);
}

export { API_URL };
