# Cine Search

Cine Search is a web application that allows users to search for movies and TV shows. The application uses the data crawled from [IMDb](https://www.imdb.com/) to provide users with the most accurate and up-to-date information about movies and TV shows.

## Features

- Search for movies and TV shows based on title and description
- View detailed information about movies and TV shows

## Technologies

- [Streamlit](https://www.streamlit.io/)
- [NLTK](https://www.nltk.org/)
- [PyMongo](https://pymongo.readthedocs.io/en/stable/)
- [Scikit-learn](https://scikit-learn.org/stable/)

## Installation

Using HTTPS:

```bash
git clone https://github.com/hoanghai1803/cine-search.git
```

Using SSH:

```bash
git clone git@github.com:hoanghai1803/cine-search.git
```

Or you can also download the zip file.

## Usage

1. Create virtual environment:

Note: The version of your python should be 3.6 or higher.

```bash
python3 -m venv env
```

2. Activate the virtual environment:

For Linux:

```bash
source env/bin/activate
```

For Windows:

```bash
.\env\Scripts\activate
```

Note:
- In Windows, if you get an error like this: `cannot be loaded because running scripts is disabled on this system`, you can run this command in your terminal: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted` and then type `Y` to accept.
- If you want to deactivate the virtual environment, just type `deactivate` in your terminal.

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Database setup:

Use need to crawl data from IMDb to use the application. You should follow and modify the file `cine-search/crawl_data/crawl.py`.

5. Setup the environment variables:

Create a file named `.env` in the root directory of the project and add the following content:

```env
DB_CONNECTION_STRING=<your_db_connection_string>
GPT_API_KEY=<your_gpt_api_key>
```

6. Run the application:

```bash
streamlit run app.py
```

## Screenshots

The application will show top 20 movies and TV shows by default.

Query: "Người dơi"

![Batman](https://i.imgur.com/ZeQV3Nu.png)

Query: "Người nhện"

![SpiderMan](https://i.imgur.com/NkORQH5.png)

Have the best experience with our project!