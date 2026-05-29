const API_BASE_URL = 'http://localhost:8000/api';

const regionFilter = document.getElementById('region-filter');
const platformFilter = document.getElementById('platform-filter');
const moviesGrid = document.getElementById('movies-grid');

document.addEventListener('DOMContentLoaded', async () => {
    await loadFilters();
    loadMovies();

    regionFilter.addEventListener('change', loadMovies);
});

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

async function loadFilters() {
    try {
        const regionRes = await fetch(`${API_BASE_URL}/filters/regions`);
        const regions = await regionRes.json();
        regions.forEach(region => {
            if (region) {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                regionFilter.appendChild(option);
            }
        });

        const platformRes = await fetch(`${API_BASE_URL}/filters/platforms`);
        const platforms = await platformRes.json();
        const checkboxesContainer = document.getElementById('platform-checkboxes');

        platforms.forEach(platform => {
            if (platform) {
                const label = document.createElement('label');

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = platform;

                checkbox.checked = true;

                checkbox.addEventListener('change', loadMovies);

                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(platform));
                checkboxesContainer.appendChild(label);
            }
        });
    } catch (error) {
        console.error("Błąd ładowania filtrów:", error);
    }
}

async function loadMovies() {
    moviesGrid.innerHTML = '<p>Ładowanie filmów...</p>';

    let url = `${API_BASE_URL}/movies`;
    const params = new URLSearchParams();

    if (regionFilter.value) {
        params.append('region', regionFilter.value);
    }

    const checkedPlatforms = document.querySelectorAll('#platform-checkboxes input[type="checkbox"]:checked');
    checkedPlatforms.forEach(checkbox => {
        params.append('platform', checkbox.value);
    });

    if (params.toString()) {
        url += `?${params.toString()}`;
    }

    try {
        const response = await fetch(url);
        const movies = await response.json();

        moviesGrid.innerHTML = '';

        if (movies.length === 0) {
            moviesGrid.innerHTML = '<p>Brak filmów dla podanych kryteriów.</p>';
            return;
        }

        movies.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-card';

            const posterUrl = movie.poster_path
                ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                : 'placeholder.png';

            card.innerHTML = `
                <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
                <div class="movie-info">
                    <h3 class="movie-title">${movie.title} (${movie.year || 'Brak roku'})</h3>
                    <p class="movie-stats">
                        ⭐ ${movie.user_rating ? movie.user_rating : 'Brak oceny'} | 
                        ⏱️ ${movie.runtime ? movie.runtime + ' min' : 'Brak czasu'}
                    </p>
                </div>
            `;
            moviesGrid.appendChild(card);
        });
    } catch (error) {
        console.error("Błąd ładowania filmów:", error);
        moviesGrid.innerHTML = '<p style="color: red;">Nie udało się połączyć z API.</p>';
    }
}