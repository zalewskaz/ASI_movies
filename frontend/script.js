const API_BASE_URL = 'http://localhost:8000/api';

const regionFilter = document.getElementById('region-filter');
const moviesGrid = document.getElementById('movies-grid');

let chartInstances = {
    movieCount: null,
    ratings: null,
    prices: null
};

document.addEventListener('DOMContentLoaded', async () => {
    await loadFilters();
    loadMovies();

    regionFilter.addEventListener('change', loadMovies);
    
    const statsRegionFilter = document.getElementById('stats-region-filter');
    if (statsRegionFilter) {
        statsRegionFilter.addEventListener('change', loadPriceChart);
    }
});

function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
    
    if (tabId === 'stats-tab') {
        loadMovieCountChart();
        loadRatingsChart();
        loadStatsRegionFilter();
    }
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
        checkboxesContainer.innerHTML = ''; // Czyszczenie przed renderem

        platforms.forEach(platform => {
            if (platform) {
                const label = document.createElement('label');

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = platform;
                checkbox.checked = true; 

                checkbox.addEventListener('change', loadMovies);

                label.appendChild(checkbox);
                label.appendChild(document.createTextNode(` ${platform}`));
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
    
    if (checkedPlatforms.length > 0) {
        checkedPlatforms.forEach(checkbox => {
            params.append('platform', checkbox.value);
        });
    } else {
        moviesGrid.innerHTML = '<p>Brak filmów dla podanych kryteriów.</p>';
        return;
    }

    if (params.toString()) {
        url += `?${params.toString()}`;
    }

    try {
        const response = await fetch(url);
        const movies = await response.json();

        moviesGrid.innerHTML = '';

        if (!movies || movies.length === 0) {
            moviesGrid.innerHTML = '<p>Brak filmów dla podanych kryteriów.</p>';
            return;
        }

        movies.forEach(movie => {
            const card = document.createElement('div');
            card.className = 'movie-card';

            const posterUrl = movie.poster_path && movie.poster_path !== 'placeholder.jpg'
                ? `https://image.tmdb.org/t/p/w500${movie.poster_path}`
                : 'placeholder.png';

            card.innerHTML = `
                <img src="${posterUrl}" alt="${movie.title}" class="movie-poster">
                <div class="movie-info">
                    <h3 class="movie-title">${movie.title} (${movie.year || 'Brak roku'})</h3>
                    <p class="movie-stats">
                                <i class="fa-solid fa-star" style="color: #f1c40f;"></i> 
                                ${movie.user_rating ? movie.user_rating : 'Brak oceny'} | 
                                <i class="fa-regular fa-clock" style="color: #95a5a6;"></i> 
                                ${movie.runtime ? movie.runtime + ' min' : 'Brak czasu'}
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

async function loadMovieCountChart() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats/platform-distribution`);
        const data = await response.json();
        const ctx = document.getElementById('movieCountChart').getContext('2d');

        if (chartInstances.movieCount) chartInstances.movieCount.destroy();

        chartInstances.movieCount = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.service_name),
                datasets: [{
                    label: 'Liczba filmów',
                    data: data.map(item => item.movie_count),
                    backgroundColor: '#3498db'
                }]
            },
            options: {
                plugins: { legend: { display: false } }
            }
        });
    } catch (e) {
        console.error("Błąd wykresu liczby filmów:", e);
    }
}

async function loadRatingsChart() {
    try {
        const [userRes, criticRes] = await Promise.all([
            fetch(`${API_BASE_URL}/stats/ratings/users`),
            fetch(`${API_BASE_URL}/stats/ratings/critics`)
        ]);
        
        const userData = await userRes.json();
        const criticData = await criticRes.json();
        
        const ctx = document.getElementById('ratingsChart').getContext('2d');
        if (chartInstances.ratings) chartInstances.ratings.destroy();

        chartInstances.ratings = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: userData.map(item => item.service_name),
                datasets: [
                    {
                        label: 'Użytkownicy',
                        data: userData.map(item => item.avg_rating),
                        backgroundColor: '#3498db'
                    },
                    {
                        label: 'Krytycy',
                        data: criticData.map(item => item.avg_rating),
                        backgroundColor: '#9b59b6'
                    }
                ]
            },
            options: {
                plugins: { legend: { display: true } }, 
                scales: { y: { beginAtZero: true, max: 10 } }
            }
        });
    } catch (e) {
        console.error("Błąd wykresu ocen:", e);
    }
}

async function loadPriceChart() {
    const regionFilterEl = document.getElementById('stats-region-filter');
    if (!regionFilterEl || !regionFilterEl.value) return;

    const region = regionFilterEl.value;
    
    try {
        const url = `${API_BASE_URL}/stats/prices?region=${encodeURIComponent(region)}`;
        const response = await fetch(url);
        const data = await response.json();
        const ctx = document.getElementById('priceChart').getContext('2d');

        if (chartInstances.prices) chartInstances.prices.destroy();

        chartInstances.prices = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(item => item.service_name),
                datasets: [{
                    label: 'Średnia cena',
                    data: data.map(item => item.average_price),
                    backgroundColor: '#27ae60'
                }]
            },
            options: {
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true } }
            }
        });
    } catch (e) {
        console.error("Błąd wykresu cen:", e);
    }
}

async function loadStatsRegionFilter() {
    const filter = document.getElementById('stats-region-filter');
    if (!filter) return;

    try {
        const response = await fetch(`${API_BASE_URL}/filters/regions`);
        const regions = await response.json();
        
        filter.innerHTML = ''; 
        
        regions.forEach(region => {
            if (region) {
                const option = document.createElement('option');
                option.value = region;
                option.textContent = region;
                filter.appendChild(option);
            }
        });

        if (filter.options.length > 0) {
            loadPriceChart();
        }
    } catch (error) {
        console.error("Błąd loading regionów statystyk:", error);
    }
}