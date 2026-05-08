import pandas as pd
import sqlite3

df = pd.read_csv("df_ml_final.csv")#read my cleaned file here and put into a df for making SQL db and finding out more about data
df = df.reset_index(drop=True)#index it with 0
df.index.name = "title_id"#every title has an index and has a unique id
df = df.reset_index()#put title into a column so i can use it for joins. HELP OF CGPT CODEBENCH

#building a separate country table for I dont keep repeating a country in every line its used
countries = df[["country_primary", "is_us"]] #i have 2 columns in my df about the country of the content
countries = countries.drop_duplicates(subset=["country_primary"])#drop duplicate countries so when a country is mentioned 5 times in the dataset for the content, i only have it once now
countries = countries.dropna(subset=["country_primary"])#drop any null just being safe for cleaning df
countries = countries.reset_index(drop=True)#resit index
countries = countries.rename(columns={"country_primary": "country_name"})#renaming column to correlate with proper concept help of CGPT CODEBENCH
countries.index.name = "country_id"#each country gets its own id
countries = countries.reset_index()#cleaning stuff

ratings = df[["rating"]]#same concept as conuntries applied to ratings
ratings = ratings.drop_duplicates()#cleaning this new db
ratings = ratings.dropna()

ratings = ratings.reset_index(drop=True)#everything the same
ratings = ratings.rename(columns={"rating": "rating_code"})
ratings.index.name = "rating_id"
ratings = ratings.reset_index()


genre_exploded = df[["title_id", "listed_in"]]#genres, one title can have many, so I will explode the way i did with cast
genre_exploded = genre_exploded.dropna(subset=["listed_in"])#drop all null created from the genre explode
genre_exploded = genre_exploded.copy()
genre_exploded["genre"] = genre_exploded["listed_in"].str.split(",")#slipt the string that has all genres into a list
genre_exploded = genre_exploded.explode("genre")#explode the list same concept as cast
genre_exploded["genre"] = genre_exploded["genre"].str.strip()#just cleaning the names
genre_exploded["genre"] = genre_exploded["genre"].str.lower()#formatting cleaning stuff

unique_genres = genre_exploded["genre"].drop_duplicates()#dropped duplicated from exploded genres
unique_genres = unique_genres.reset_index(drop=True)#reset index so the dropped stuff doesnt affect
unique_genres = unique_genres.to_frame()#help fo CGPT codebench

unique_genres = unique_genres.rename(columns={"genre": "genre_name"})#rename the column with help of CGPT codebench
unique_genres.index.name = "genre_id"
unique_genres = unique_genres.reset_index()#make put nice new index clean help of CGPT codebench


genre_tags = genre_exploded[["title_id", "genre"]]# a table to connet titles to genres, one row per title and genre pair
genre_tags = genre_tags.merge(unique_genres, left_on="genre", right_on="genre_name")
genre_tags = genre_tags[["title_id", "genre_id"]] #many to many concept coded this with the help of CGPT on codebench
genre_tags = genre_tags.drop_duplicates()

titles_base = df.merge( #merges so countryid is in the same df and the titles, creates a relation. help or Activebook for the doe for this
    countries[["country_id", "country_name"]],
    left_on="country_primary",
    right_on="country_name",
    how="left"
)

titles_base = titles_base.merge(#with help of active book merges so rating id is in the same df as the titles
    ratings[["rating_id", "rating_code"]],
    left_on="rating",
    right_on="rating_code",
    how="left"
)

titles = titles_base[[#keeping only the columns I need and finally removing all the strings stuff I didnt need anymore, like original genres and cast
    "title_id", "title", "type", "release_year", "age", "is_recent",
    "duration_num", "is_tv", "is_us", "year_added", "genre_primary",
    "has_known_actor", "country_id", "rating_id"
]].copy()

engagement = df[["title_id", "imdb_rating", "imdb_votes", "trending"]].copy()#separate imdb info into its own table

conn = sqlite3.connect("netflix_relational.db")#basic SQL setup from Activebook
cur  = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")#help of CGPT on codebench because rerunning was causing errors before, this stopped them
cur.execute("DROP TABLE IF EXISTS genre_tags")
cur.execute("DROP TABLE IF EXISTS engagement")
cur.execute("DROP TABLE IF EXISTS titles")
cur.execute("DROP TABLE IF EXISTS genres")
cur.execute("DROP TABLE IF EXISTS countries")
cur.execute("DROP TABLE IF EXISTS ratings")

cur.executescript("""
CREATE TABLE countries (
    country_id   INTEGER PRIMARY KEY,
    country_name TEXT    NOT NULL UNIQUE,
    is_us        INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE ratings (
    rating_id   INTEGER PRIMARY KEY,
    rating_code TEXT    NOT NULL UNIQUE
);
CREATE TABLE genres (
    genre_id   INTEGER PRIMARY KEY,
    genre_name TEXT    NOT NULL UNIQUE
);
CREATE TABLE titles (
    title_id      INTEGER PRIMARY KEY,
    title         TEXT,
    type          TEXT,
    release_year  INTEGER,
    age           INTEGER,
    is_recent     INTEGER,
    duration_num  INTEGER,
    is_tv         INTEGER,
    is_us         INTEGER,
    year_added    INTEGER,
    genre_primary TEXT,
    has_known_actor INTEGER,
    country_id    INTEGER REFERENCES countries(country_id),
    rating_id     INTEGER REFERENCES ratings(rating_id)
);
CREATE TABLE genre_tags (
    title_id  INTEGER REFERENCES titles(title_id),
    genre_id  INTEGER REFERENCES genres(genre_id),
    PRIMARY KEY (title_id, genre_id)
);
CREATE TABLE engagement (
    title_id    INTEGER PRIMARY KEY REFERENCES titles(title_id),
    imdb_rating REAL,
    imdb_votes  INTEGER,
    trending    INTEGER
);
""")




conn.commit()
#this creates a bunch of separate tables for each chunk of relevant data, code referred from Activebook

countries.to_sql("countries",  conn, if_exists="append", index=False)#this putsa ll the data i separated and cleaned into the sql, with the help of CGPT on codebench and activebook
ratings.to_sql("ratings",      conn, if_exists="append", index=False)
unique_genres.to_sql("genres", conn, if_exists="append", index=False)
titles.to_sql("titles",        conn, if_exists="append", index=False)
genre_tags.to_sql("genre_tags",conn, if_exists="append", index=False)
engagement.to_sql("engagement",conn, if_exists="append", index=False)
conn.commit()


#all the stuff below tells me more about my data and my assumptions
print("Trending rate by genre")#which genres had the most trending
q1 = pd.read_sql_query("""
    SELECT
        g.genre_name,
        COUNT(DISTINCT t.title_id)       AS total_titles,
        SUM(e.trending)                  AS trending_count,
        ROUND(AVG(e.trending)*100, 1)    AS trending_pct,
        ROUND(AVG(e.imdb_rating), 2)     AS avg_imdb_rating
    FROM genres g
    JOIN genre_tags gt ON g.genre_id  = gt.genre_id
    JOIN titles t      ON gt.title_id = t.title_id
    JOIN engagement e  ON t.title_id  = e.title_id
    GROUP BY g.genre_name
    HAVING total_titles > 20
    ORDER BY trending_pct DESC
    LIMIT 12
""", conn)
print(q1.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench



print("Top producing countries by avg IMDb rating")#if country of orig affeted quality or popularity
q2 = pd.read_sql_query("""
    SELECT
        c.country_name,
        COUNT(t.title_id)              AS title_count,
        ROUND(AVG(e.imdb_rating), 2)   AS avg_rating,
        ROUND(AVG(e.imdb_votes), 0)    AS avg_votes,
        ROUND(AVG(e.trending)*100, 1)  AS trending_pct
    FROM countries c
    JOIN titles t    ON c.country_id = t.country_id
    JOIN engagement e ON t.title_id  = e.title_id
    GROUP BY c.country_name
    HAVING title_count > 10
    ORDER BY avg_rating DESC
    LIMIT 15
""", conn)
print(q2.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench

print("Recent (2015+) vs older content")
q3 = pd.read_sql_query("""
    SELECT
        CASE WHEN t.is_recent = 1 THEN '2015+' ELSE 'Pre-2015' END AS era,
        COUNT(*)                       AS total,
        ROUND(AVG(e.imdb_rating), 2)   AS avg_rating,
        ROUND(AVG(e.imdb_votes), 0)    AS avg_votes,
        ROUND(AVG(e.trending)*100, 1)  AS trending_pct
    FROM titles t
    JOIN engagement e ON t.title_id = e.title_id
    GROUP BY t.is_recent
""", conn)
print(q3.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench


print("IMDb stats by content rating")
q4 = pd.read_sql_query("""
    SELECT
        r.rating_code,
        COUNT(t.title_id)              AS title_count,
        ROUND(AVG(e.imdb_rating), 2)   AS avg_imdb_rating,
        ROUND(AVG(e.imdb_votes), 0)    AS avg_votes,
        ROUND(AVG(e.trending)*100, 1)  AS trending_pct
    FROM ratings r
    JOIN titles t     ON r.rating_id = t.rating_id
    JOIN engagement e ON t.title_id  = e.title_id
    GROUP BY r.rating_code
    HAVING title_count > 5
    ORDER BY avg_imdb_rating DESC
""", conn)
print(q4.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench


print("Movies vs TV Shows")
q5 = pd.read_sql_query("""
    SELECT
        t.type,
        COUNT(*)                       AS total,
        ROUND(AVG(e.imdb_rating), 2)   AS avg_rating,
        ROUND(AVG(e.imdb_votes), 0)    AS avg_votes,
        ROUND(AVG(e.trending)*100, 1)  AS trending_pct,
        ROUND(AVG(t.duration_num), 1)  AS avg_duration
    FROM titles t
    JOIN engagement e ON t.title_id = e.title_id
    GROUP BY t.type
""", conn)
print(q5.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench


print("Known actor vs unknown — trending impact")#just basically have the name and titles written of what the data tells me before each join and aggregate SQL query
q6 = pd.read_sql_query("""
    SELECT
        CASE WHEN t.has_known_actor = 1 THEN 'Known Actor' ELSE 'No Known Actor' END AS cast_tier,
        COUNT(*)                       AS total,
        ROUND(AVG(e.imdb_rating), 2)   AS avg_rating,
        ROUND(AVG(e.imdb_votes), 0)    AS avg_votes,
        ROUND(AVG(e.trending)*100, 1)  AS trending_pct
    FROM titles t
    JOIN engagement e ON t.title_id = e.title_id
    GROUP BY t.has_known_actor
""", conn)
print(q6.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench

#i learned that case when is a if else inside SQL from CGPT and sql website
print("Trending content added per year")#Formed the Select in the From portions of the query with codebench
q7 = pd.read_sql_query("""
    SELECT year_added, total_added, trending_added, ROUND(CAST(trending_added AS FLOAT) / total_added * 100, 1) AS trending_pct
    FROM (
        SELECT
            t.year_added,
            COUNT(*)        AS total_added,
            SUM(e.trending) AS trending_added
        FROM titles t
        JOIN engagement e ON t.title_id = e.title_id
        WHERE t.year_added IS NOT NULL
        GROUP BY t.year_added
    )
    ORDER BY year_added
""", conn)
print(q7.to_string(index=False))#FORMED join conditions with the help of cgpt on codebench
#but i did come up with the aggregations, I just used Join instead of left and right to make it easy for me to understand since I was struggling on it before Exam 2
conn.close()