# ASI_movies

## opis
Repozytorium poświęcone projektowi ASI_movies, realizowanego w ramach przedmiotu Architektura Systemów Informatycznych w semestrze letnim 2025/2026 przez zespół w składzie: [Hanna Szczerbińska](https://github.com/zabolot7/), [Zuzanna Zalewska](https://github.com/zalewskaz/). W ramach projektu powstała aplikacja składająca się z czterech modułów: 
 - moduł data_ingestion ściąga dane z TMDB i Watchmode API i przeprowadza prosty proces ETL w celu umieszczenia danych w bazie danych; jest w nim również zaimplemnetowane automatyczne uruchamianie procesu ETL raz na tydzień, w celu odświeżenia dostępnych w bazie danych; 
 - baza danych PostgreSQL zawierająca informacje pozyskane z Watchmode i TMDB;
 - moduł backend, który za pomocą FastAPI udostępnia dane z bazy
 - moduł frontend, który udostępnia dane użytkownikom za pomocą prostego interfejsu zbudowanego w HTML, CSS i Javascript. 
W aplikacji została również zastosowana konteneryzacja za pomocą Dockera. 

## dokumentacja
Pełna dokumentacja projektu jest zawarta w pliku asi_dokumentacja.pdf. 

## docker setup instructions
W celu uruchomienia projektu samodzielnie, należy w linii poleceń w folderze projektowym wykonać następujące polecenia: 

ODPALANIE DEV ŚRODOWISKA: docker compose up --build -d  
SPRAWDZENIE W PRZEGLĄDARCE: http://localhost:3000  
ZAMYKANIE: docker compose down  

ODPALANIE TEST SRODOWISKA: docker compose -f docker-compose.test.yml up --build -d  
SPRAWDZANIE WYNIKÓW TESTÓW: docker compose -f docker-compose.test.yml logs unit_tests  
SPRAWDZANIE WYNIKOW LOCUST: http://localhost:8089  
ZAMYKANIE: docker compose -f docker-compose.test.yml down  

ODPALANIE PROD ŚRODOWISKA: docker compose -f docker-compose.prod.yml up --build -d  
SPRAWDZENIE W PRZEGLĄDARCE: http://localhost  
ZAMYKANIE: docker compose -f docker-compose.prod.yml down  
