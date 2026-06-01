
import random
from locust import HttpUser, task, between

class MovieAppLoadTest(HttpUser):
    wait_time = between(1, 3)

    @task(4)  
    def view_movies_default(self):
        #Użytkownik wchodzi na stronę główną i ładuje filmy bez filtrów
        self.client.get("/api/movies")

    @task(2)
    def view_movies_with_filter(self):
        #Użytkownik filtruje filmy po losowym regionie i/lub platformie
        regions = ["US", "PL", "GB" ""]
        platforms = ["Netflix", "Disney+", "Amazon"]
        
        chosen_region = random.choice(regions)
        
        # symulujemy, że użytkownik może zaznaczyć od 0 do 2 platform na raz
        num_platforms = random.randint(0, 2)
        chosen_platforms = random.sample(platforms, num_platforms)
        
        query_params = []
        if chosen_region:
            query_params.append(f"region={chosen_region}")
        
        for p in chosen_platforms:
            query_params.append(f"platform={p}")
            
        url = "/api/movies"
        if query_params:
            url += "?" + "&".join(query_params)
            
        self.client.get(url)

    @task(1)
    def view_platform_stats(self):
        #Użytkownik klika w zakładkę statystyk i ładuje rozkład platform
        self.client.get("/api/stats/platform-distribution")

    @task(1)
    def view_price_stats(self):
        #Użytkownik sprawdza wykres cen dla wybranego regionu
        regions = ["US", "PL", "GB"]
        chosen_region = random.choice(regions)
        self.client.get(f"/api/stats/prices?region={chosen_region}")

    @task(1)
    def view_rating_stats(self):
        # Użytkownik sprawdza wykresy ocen użytkowników i krytyków
        self.client.get("/api/stats/ratings/users")
        self.client.get("/api/stats/ratings/critics")
