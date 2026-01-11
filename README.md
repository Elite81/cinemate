
# cinemate
### Video Demo:  <https://www.youtube.com/watch?v=q1LUCQi6iVc>
### Live Demo:   <https://cinemate-6cht.onrender.com/>


## Project Overview
Cinemate is a full-stack movie web application developed for my CS50x Final Project. It allows users to explore movies using real-time data from the TMDB API, view detailed movie information, and interact with content through favorites, likes, and comments. The project is built with Django and Bootstrap.


---

## Features

- Browse and discover movies using the TMDB API
- View detailed movie information (overview, rating, release date, poster)
- User authentication (sign up, login, logout)
- Like movies and add them to personal favorites
- Comment on movies
- Persistent user data stored in the database
- Responsive interface built with Bootstrap

---

## Technologies Used

    ### Backend
    - Python
    - Django
    - Django Authentication System

    ### Frontend
    - HTML5
    - CSS3
    - Bootstrap

    ### Database
    - PostgreSQL (hosted on Neon)
    -  Database design is documented in the [ERD on GitHub Gist](https://gist.github.com/Elite81/ee559d93b68a536b0d4e965302168030#file-ciname_erd-svg)


    ### API
    - The Movie Database (TMDB) API

    ## Project Structure

    ── cinemate
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── cinemate_movie.dot
    ├── cinemate_movie.svg
    ├── context_processor.py
    ├── manage.py
    ├── movies
    │   ├── admin.py
    │   ├── apps.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── tests.py
    │   ├── urls.py
    │   ├── utils.py
    │   └── views.py
    ├── README.md
    └── requirements.txt



## Installation & Setup

    ### Prerequisites
    - Python 3.x
    - pip
    - Virtual environment (recommended)

    ### Instalation Steps

    1. Clone the repository:
        git clone https://github.com/elite81/cinemate.git
        cd cinemate

    2. Create and activate a virtua             l environment:
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\\Scripts\\activate

    3. Install dependencies:
        pip install -r requirements.txt

    4.  Set up environment variables:
        Create a .env file

    5.  Add your TMDB API key:
        TMDB_API_KEY=your_api_key_here

    6.  Run database migrations:
        python manage.py makemigrations
        python manage.py migrate

    7. Start the development server:
        python manage.py runserver

    8. Open your browser and visit:
        http://127.0.0.1:8000/


## Deployment / Live Demo
    Cinemate is hosted online and can be accessed at:
    https://cinemate-6cht.onrender.com/

    Users can explore movies, add favorites, like, and comment without needing to run the project locally.


## Cinemate (CS50x Final Project)
    Cinemate was submitted as the Final Project for CS50x. It demonstrates:
    Practical use of Python and Django
    REST API integration
    Relational database usage
    Authentication and authorization
    Clean project structure and documentation


## Future Improvements
    Advanced movie search and filtering
    User profiles with watch history
    Pagination and performance optimizations
    API caching



## Author
    Edoh Mensah Akpedzene
    CS50x Student | Full-Stack Developer

## License
    This project is for educational purposes as part of CS50x.

---

**Note:** This README.md was written with assistance from ChatGPT to ensure clarity and professionalism. The project code and implementation are entirely my own.