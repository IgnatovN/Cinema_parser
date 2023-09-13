from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os

load_dotenv()

cinemapark_url = "https://kinoteatr.ru/raspisanie-kinoteatrov/mega-himki/"
kinosfera_url = "https://kinosfera-imax.ru/#/"
kinopoisk_api_url = "https://api.kinopoisk.dev/v1.3/movie"

headers = {
    "Accept": os.environ.get("Accept"),
    "User-Agent": os.environ.get("User-Agent")
}

# Send requests
cinemapark_req = requests.get(cinemapark_url, headers=headers)
kinosfera_req = requests.get(kinosfera_url, headers=headers)
kinosfera_req.encoding = 'unicode-escape'

cinemapark_src = cinemapark_req.text
kinosfera_src = kinosfera_req.text

# Cinemapark parser
soup = BeautifulSoup(cinemapark_src, "lxml")
movies = soup.find_all(class_="movie_card_header title")
cinemapark_movies = [movie.text.strip() for movie in movies]

# Kinosfera parser
soup = BeautifulSoup(kinosfera_src, "lxml")
movies = soup.find("movies")[":movies"]
kinosfera_movies = [film for film in movies.split("}") if "age_limit" in film]
kinosfera_movies = [film[film.find("name") + 7:film.find('"age_limit"') - 2] for film in kinosfera_movies]
kinosfera_movies = [film[:film.find('предсеанс')].strip() if 'предсеанс' in film else film for film in kinosfera_movies]

movies = cinemapark_movies + kinosfera_movies
movies = set(map(lambda x: x.lower(), movies))

headers["X-API-KEY"] = os.environ.get("X-API-KEY")

# Select movies
to_watch = []

for movie in movies:
    param = {"name": movie}
    req = requests.get(kinopoisk_api_url, headers=headers, params=param).json()

    if len(req['docs']) == 0:
        continue

    kp = req['docs'][0]['rating']['kp']
    imdb = req['docs'][0]['rating']['imdb']

    if kp >= 7 <= imdb:
        to_watch.append(movie)

print(to_watch)







