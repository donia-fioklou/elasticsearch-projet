"""
seed_data.py
Insère un jeu de données de films dans l'index Elasticsearch 'movies'.
Exécuter APRÈS setup_index.py.

Usage : python seed_data.py
"""

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ES_URL = "http://localhost:9200"
INDEX_NAME = "movies"

# 25 films variés pour démontrer les capacités d'ES
MOVIES = [
    {
        "title": "Inception",
        "description": "Un voleur qui s'infiltre dans les rêves des autres pour leur dérober des secrets utilise une technologie révolutionnaire pour planter une idée dans l'esprit d'un PDG.",
        "genre": ["Science-Fiction", "Thriller"],
        "year": 2010,
        "rating": 8.8,
        "votes": 2300000,
        "director": "Christopher Nolan",
        "actors": ["Leonardo DiCaprio", "Joseph Gordon-Levitt", "Elliot Page"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg"
    },
    {
        "title": "Le Parrain",
        "description": "La saga de la famille Corleone, une des familles mafieuses les plus puissantes de New York. Vito Corleone, patriarche vieillissant, doit transmettre le pouvoir à son fils Michael.",
        "genre": ["Crime", "Drame"],
        "year": 1972,
        "rating": 9.2,
        "votes": 1900000,
        "director": "Francis Ford Coppola",
        "actors": ["Marlon Brando", "Al Pacino", "James Caan"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsLLeHjnRx6Yw.jpg"
    },
    {
        "title": "Interstellar",
        "description": "Dans un futur proche où la Terre est mourante, un groupe d'astronautes voyage à travers un trou de ver pour trouver une nouvelle planète habitable pour l'humanité.",
        "genre": ["Science-Fiction", "Aventure"],
        "year": 2014,
        "rating": 8.6,
        "votes": 1800000,
        "director": "Christopher Nolan",
        "actors": ["Matthew McConaughey", "Anne Hathaway", "Jessica Chastain"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg"
    },
    {
        "title": "Parasite",
        "description": "Une famille pauvre s'infiltre habilement dans la vie d'une famille riche, jusqu'à ce qu'un événement inattendu vienne tout bouleverser.",
        "genre": ["Thriller", "Drame", "Comédie noire"],
        "year": 2019,
        "rating": 8.5,
        "votes": 850000,
        "director": "Bong Joon-ho",
        "actors": ["Song Kang-ho", "Lee Sun-kyun", "Cho Yeo-jeong"],
        "language": "Coréen",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg"
    },
    {
        "title": "Le Voyage de Chihiro",
        "description": "Une fillette de dix ans se retrouve dans un monde fantastique peuplé de dieux et de monstres, et doit travailler dans un établissement de bains pour retrouver ses parents transformés en cochons.",
        "genre": ["Animation", "Fantastique", "Aventure"],
        "year": 2001,
        "rating": 8.6,
        "votes": 750000,
        "director": "Hayao Miyazaki",
        "actors": ["Daveigh Chase", "Suzanne Pleshette"],
        "language": "Japonais",
        "poster_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg"
    },
    {
        "title": "Pulp Fiction",
        "description": "Les histoires entrelacées de criminels, maris, boxeurs et bandits à Los Angeles forment une mosaïque de violence et de rédemption dans le Los Angeles souterrain.",
        "genre": ["Crime", "Thriller"],
        "year": 1994,
        "rating": 8.9,
        "votes": 2100000,
        "director": "Quentin Tarantino",
        "actors": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"
    },
    {
        "title": "La La Land",
        "description": "À Los Angeles, une actrice en herbe et un pianiste de jazz tombent amoureux, mais leurs ambitions respectives risquent de mettre à l'épreuve leur relation.",
        "genre": ["Romance", "Musical", "Drame"],
        "year": 2016,
        "rating": 8.0,
        "votes": 600000,
        "director": "Damien Chazelle",
        "actors": ["Ryan Gosling", "Emma Stone"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg"
    },
    {
        "title": "The Dark Knight",
        "description": "Batman fait face à son ennemi le plus redoutable, le Joker, un anarchiste criminel qui sème la terreur à Gotham City en défiant les lois de la logique.",
        "genre": ["Action", "Crime", "Drame"],
        "year": 2008,
        "rating": 9.0,
        "votes": 2800000,
        "director": "Christopher Nolan",
        "actors": ["Christian Bale", "Heath Ledger", "Aaron Eckhart"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"
    },
    {
        "title": "Forrest Gump",
        "description": "La vie extraordinaire d'un homme simple d'Alabama qui, malgré son QI limité, assiste aux grands événements de l'histoire américaine du XXe siècle.",
        "genre": ["Drame", "Romance"],
        "year": 1994,
        "rating": 8.8,
        "votes": 2000000,
        "director": "Robert Zemeckis",
        "actors": ["Tom Hanks", "Robin Wright", "Gary Sinise"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"
    },
    {
        "title": "Matrix",
        "description": "Un programmeur informatique découvre que la réalité est une simulation informatique et rejoint une rébellion contre les machines qui ont asservi l'humanité.",
        "genre": ["Science-Fiction", "Action"],
        "year": 1999,
        "rating": 8.7,
        "votes": 1900000,
        "director": "Les Wachowski",
        "actors": ["Keanu Reeves", "Laurence Fishburne", "Carrie-Anne Moss"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
    },
    {
        "title": "Schindler's List",
        "description": "L'histoire vraie d'Oskar Schindler, un industriel allemand qui a sauvé plus de mille Juifs polonais pendant la Seconde Guerre mondiale en les employant dans ses usines.",
        "genre": ["Drame", "Histoire", "Guerre"],
        "year": 1993,
        "rating": 9.0,
        "votes": 1400000,
        "director": "Steven Spielberg",
        "actors": ["Liam Neeson", "Ben Kingsley", "Ralph Fiennes"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/sF1U4EUQS8YHUYjNl3pMGNIQyr0.jpg"
    },
    {
        "title": "Avengers: Endgame",
        "description": "Les Avengers restants et leurs alliés s'unissent pour annuler les actions de Thanos et restaurer l'ordre dans l'univers après la destruction de la moitié de toute vie.",
        "genre": ["Action", "Aventure", "Science-Fiction"],
        "year": 2019,
        "rating": 8.4,
        "votes": 1100000,
        "director": "Anthony et Joe Russo",
        "actors": ["Robert Downey Jr.", "Chris Evans", "Scarlett Johansson"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg"
    },
    {
        "title": "Joker",
        "description": "L'histoire d'Arthur Fleck, un comédien raté à Gotham City qui, méprisé par la société, sombre peu à peu dans la folie et devient le célèbre criminel Joker.",
        "genre": ["Crime", "Drame", "Thriller"],
        "year": 2019,
        "rating": 8.4,
        "votes": 1050000,
        "director": "Todd Phillips",
        "actors": ["Joaquin Phoenix", "Robert De Niro", "Zazie Beetz"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg"
    },
    {
        "title": "Titanic",
        "description": "Une romance tragique entre un artiste pauvre et une jeune aristocrate à bord du paquebot Titanic lors de sa traversée inaugurale et fatale en 1912.",
        "genre": ["Romance", "Drame", "Histoire"],
        "year": 1997,
        "rating": 7.9,
        "votes": 1100000,
        "director": "James Cameron",
        "actors": ["Leonardo DiCaprio", "Kate Winslet", "Billy Zane"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/9xjZS2rlVxm8SFx8kPC3aIGCOYQ.jpg"
    },
    {
        "title": "Intouchables",
        "description": "L'amitié improbable entre Philippe, un aristocrate tétraplégique, et Driss, un jeune homme de banlieue embauché comme aide-soignant, qui va transformer leur vie à tous les deux.",
        "genre": ["Comédie", "Drame"],
        "year": 2011,
        "rating": 8.5,
        "votes": 800000,
        "director": "Olivier Nakache et Eric Toledano",
        "actors": ["François Cluzet", "Omar Sy"],
        "language": "Français",
        "poster_url": "https://image.tmdb.org/t/p/w500/6mqqEJB8nErjz3b0sXOKw0Q7Zb8.jpg"
    },
    {
        "title": "Amélie",
        "description": "Amélie Poulain, une jeune serveuse timide et imaginative, décide de changer la vie des gens autour d'elle et trouve peut-être le grand amour dans le quartier de Montmartre à Paris.",
        "genre": ["Romance", "Comédie"],
        "year": 2001,
        "rating": 8.3,
        "votes": 750000,
        "director": "Jean-Pierre Jeunet",
        "actors": ["Audrey Tautou", "Mathieu Kassovitz"],
        "language": "Français",
        "poster_url": "https://image.tmdb.org/t/p/w500/wM7tizSy6BV93NcHkqPTuFwnTAW.jpg"
    },
    {
        "title": "Spirited Away",
        "description": "Chihiro, une fillette de dix ans, se retrouve dans un monde fantastique après que ses parents soient transformés en cochons. Elle doit travailler pour retrouver sa forme humaine.",
        "genre": ["Animation", "Fantastique"],
        "year": 2001,
        "rating": 8.6,
        "votes": 760000,
        "director": "Hayao Miyazaki",
        "actors": ["Daveigh Chase", "Suzanne Pleshette"],
        "language": "Japonais",
        "poster_url": ""
    },
    {
        "title": "The Shawshank Redemption",
        "description": "Deux prisonniers créent un lien fort sur plusieurs décennies, trouvant la réconfort et une rédemption éventuelle à travers des actes de décence commune dans l'univers brutal d'une prison.",
        "genre": ["Drame"],
        "year": 1994,
        "rating": 9.3,
        "votes": 2600000,
        "director": "Frank Darabont",
        "actors": ["Tim Robbins", "Morgan Freeman"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"
    },
    {
        "title": "Gladiator",
        "description": "Un général romain trahi par le fils corrompu de l'empereur est réduit en esclavage. Il devient gladiateur et cherche à se venger du prince qui a assassiné sa famille.",
        "genre": ["Action", "Aventure", "Drame"],
        "year": 2000,
        "rating": 8.5,
        "votes": 1400000,
        "director": "Ridley Scott",
        "actors": ["Russell Crowe", "Joaquin Phoenix", "Connie Nielsen"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/ty8TGRuvJLPUmAR1H1nRIsgwvim.jpg"
    },
    {
        "title": "Fight Club",
        "description": "Un employé de bureau insomniaque et un savonnier itinérant forment un club de combat souterrain qui évolue en quelque chose de bien plus radical.",
        "genre": ["Drame", "Thriller"],
        "year": 1999,
        "rating": 8.8,
        "votes": 2200000,
        "director": "David Fincher",
        "actors": ["Brad Pitt", "Edward Norton", "Helena Bonham Carter"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
    },
    {
        "title": "Coco",
        "description": "Miguel, un jeune garçon passionné de musique, se retrouve transporté dans le pays des morts et cherche l'aide de son arrière-arrière-grand-père musicien légendaire.",
        "genre": ["Animation", "Famille", "Musique"],
        "year": 2017,
        "rating": 8.4,
        "votes": 520000,
        "director": "Lee Unkrich",
        "actors": ["Anthony Gonzalez", "Gael García Bernal"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/gGEsBPAijhVUFoiNpgZXqRVWJt2.jpg"
    },
    {
        "title": "Whiplash",
        "description": "Un jeune batteur de jazz ambitieux entre dans l'un des meilleurs conservatoires de musique des États-Unis, où il est poussé à ses limites par un chef d'orchestre tyrannique.",
        "genre": ["Drame", "Musique"],
        "year": 2014,
        "rating": 8.5,
        "votes": 700000,
        "director": "Damien Chazelle",
        "actors": ["Miles Teller", "J.K. Simmons"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg"
    },
    {
        "title": "Blade Runner 2049",
        "description": "Un blade runner découvre un secret enfoui depuis longtemps qui menace de plonger ce qui reste de la civilisation dans le chaos, le poussant à retrouver Rick Deckard.",
        "genre": ["Science-Fiction", "Thriller"],
        "year": 2017,
        "rating": 8.0,
        "votes": 470000,
        "director": "Denis Villeneuve",
        "actors": ["Ryan Gosling", "Harrison Ford", "Ana de Armas"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"
    },
    {
        "title": "Le Lion",
        "description": "Après la mort de son père, le jeune lion Simba fuit son royaume, honteux et terrorisé. Devenu adulte, il doit affronter son destin et libérer son royaume de la tyrannie.",
        "genre": ["Animation", "Aventure", "Musical"],
        "year": 1994,
        "rating": 8.5,
        "votes": 980000,
        "director": "Roger Allers et Rob Minkoff",
        "actors": ["Matthew Broderick", "Jeremy Irons", "James Earl Jones"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/sKCr78MXSLixwmZ8DyJLrpMsd15.jpg"
    },
    {
        "title": "Oppenheimer",
        "description": "L'histoire de J. Robert Oppenheimer et de son rôle dans le développement de la bombe atomique lors du Projet Manhattan pendant la Seconde Guerre mondiale.",
        "genre": ["Biographie", "Drame", "Histoire"],
        "year": 2023,
        "rating": 8.3,
        "votes": 580000,
        "director": "Christopher Nolan",
        "actors": ["Cillian Murphy", "Emily Blunt", "Matt Damon"],
        "language": "Anglais",
        "poster_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg"
    }
]


def seed_movies():
    es = Elasticsearch(ES_URL)

    if not es.ping():
        print("❌ Elasticsearch non accessible. Lance docker-compose up -d d'abord.")
        return

    print(f"✅ Connecté à Elasticsearch")

    # Vérifier que l'index existe
    if not es.indices.exists(index=INDEX_NAME):
        print(f"❌ L'index '{INDEX_NAME}' n'existe pas. Lance d'abord : python setup_index.py")
        return

    # Préparer les actions pour le bulk insert
    actions = [
        {
            "_index": INDEX_NAME,
            "_source": movie
        }
        for movie in MOVIES
    ]

    # Insertion en masse (bulk)
    success, errors = bulk(es, actions)
    print(f"✅ {success} films indexés avec succès !")

    if errors:
        print(f"⚠️  {len(errors)} erreurs lors de l'indexation")
        for err in errors:
            print(f"   - {err}")

    # Rafraîchir l'index pour rendre les docs immédiatement disponibles
    es.indices.refresh(index=INDEX_NAME)

    # Vérification finale
    count = es.count(index=INDEX_NAME)
    print(f"\n📊 Total documents dans l'index : {count['count']}")
    print("\n👉 Lance maintenant : python app.py")
    print("   Puis ouvre http://localhost:5000 dans ton navigateur")


if __name__ == "__main__":
    seed_movies()
