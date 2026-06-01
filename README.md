# ASI_movies

## docker setup instructions
ODPALANIE DEV ŚRODOWISKA:  
docker compose up --build -d  
SPRAWDZENIE W PRZEGLĄDARCE:  
http://localhost:3000  
ZAMYKANIE:  
docker compose down  

ODPALANIE TEST SRODOWISKA: 
docker compose -f docker-compose.test.yml up --build -d
SPRAWDZANIE WYNIKÓW TESTÓW: 
docker compose -f docker-compose.test.yml logs unit_tests
SPRAWDZANIE WYNIKOW LOCUST: 
http://localhost:8089
ZAMYKANIE: 
docker compose -f docker-compose.test.yml down

ODPALANIE PROD ŚRODOWISKA: 
docker compose -f docker-compose.prod.yml up --build -d
SPRAWDZENIE W PRZEGLĄDARCE: 
http://localhost
ZAMYKANIE: 
docker compose -f docker-compose.prod.yml down
