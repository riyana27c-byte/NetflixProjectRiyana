import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D #help from documentation online
import os

os.makedirs("charts", exist_ok=True)

df  = pd.read_csv("df_ml_final.csv")#load my cleaned data
conn = sqlite3.connect("netflix_relational.db")#connect with my relational database

def save(path, title):#made a helper function to reduce repetition of code, help of codebench activebook
    plt.title(title)
    plt.tight_layout()#suggested by activebook
    plt.savefig("charts/" + path)
    plt.close()



type_counts = df["type"].value_counts()#counting how many movies vs tv shows there are in my data
type_counts.plot(kind="bar", color=["steelblue", "salmon"])#two colors I picked one per type, from matplot documentation
plt.ylabel("Count")#help of activebook set label
plt.xticks(rotation=0)#keeping labels horizontal, from documentation
save("01type.png", "Movie vs TV Show Split")#use method to save graph


genre_exploded = df.copy()#same concept reexploded genre for the graph with the same functions I used before everywhere
genre_exploded["genre"] = genre_exploded["listed_in"].str.split(",")
genre_exploded = genre_exploded.explode("genre")
genre_exploded["genre"] = genre_exploded["genre"].str.strip()
genre_exploded["genre"] = genre_exploded["genre"].str.lower()

top_genres = genre_exploded["genre"].value_counts()#counts how many titles each genre appears in
top_genres = top_genres.head(10)#only want top 10 genres
top_genres = top_genres.sort_values()#sort values my ascending from documentation
top_genres.plot(kind="barh")

plt.xlabel("Unique Titles")#save title after specifying chart type
save("02_top_genres.png", "Top 10 Genres by Title Count")


titles_per_year = df["year_added"].value_counts()
titles_per_year = titles_per_year.sort_index()#sorting by year and not by count so the line goes left to right in order
titles_per_year.plot(kind="line", marker="o", color="steelblue")#color change with documentation

plt.ylabel("Titles Added")
plt.xlabel("Year") #make labels for my graphs
save("03titlesaddedyear.png", "Titles Added to Netflix Per Year")



top_countries = df["country_primary"].value_counts()#counts th enumber of times each country come up in the country_primary, how many times a country is listed first 
top_countries = top_countries.head(15)#takes head so top 15 most listed countries
top_countries = top_countries.sort_values()#same sort as genres so longest bar is on top
top_countries.plot(kind="barh")

plt.xlabel("Count")#label sides
save("04topcountry.png", "Top 15 Producing Countries")


top_ratings = df["rating"].value_counts()#counts the number of times a certain rating is given to a titles so like TV_MA is given a _ amount of times
top_ratings = top_ratings.head(10)#takes top 10 ratings given
top_ratings.plot(kind="bar")#makes bar chart

plt.ylabel("Count")
plt.xticks(rotation=45)#labels my axis
save("05ratingdist.png", "Content Rating Distribution")

imdb_ratings = df["imdb_rating"].dropna()#removes all entries where rating not given and put this into a db of its own so not affect original db
plt.hist(imdb_ratings, bins=30, color="steelblue", edgecolor="white")#color of chart, used matpllot documentation

plt.xlabel("IMDb Rating")#my chart labels 
plt.ylabel("Count")
save("06imdbratings.png", "IMDb Rating Distribution")


colors = df["trending"].map({0: "steelblue", 1: "tomato"})#mappin 0 and 1 to colors so trending titles show up differently. trending just means more than 10000 votes, nothing else

plt.scatter(df["imdb_rating"], df["imdb_votes"], c=colors, alpha=0.4, s=12)#played with alpha from documentation it makes dots more visible
plt.xlabel("IMDb Rating")#name the axis for both sides
plt.ylabel("IMDb Votes")
plt.yscale("log")#votes vary too much so cgpt from codebench said log would look cleaner

trending_dot     = Line2D([0], [0], marker="o", color="w", markerfacecolor="tomato",   label="Trending")#from documentation makes lines much cleaner I did not have this before so my chart was notclean
not_trending_dot = Line2D([0], [0], marker="o", color="w", markerfacecolor="steelblue", label="Not Trending")
legend_handles   = [trending_dot, not_trending_dot]

plt.legend(handles=legend_handles)#all from 2D lines implementation documentation, which 2D lines was suggest by Cgpt from codebench
save("07ratingvsvotes.png", "IMDb Rating vs Votes)")

#copied and pasted my SQL from data basework here for the chart
q6 = pd.read_sql_query("""
    SELECT
        CASE WHEN t.has_known_actor = 1 THEN 'Known Actor' ELSE 'No Known Actor' END AS cast_tier,
        ROUND(AVG(e.trending)*100, 1) AS trending_pct,
        ROUND(AVG(e.imdb_rating), 2)  AS avg_rating
    FROM titles t
    JOIN engagement e ON t.title_id = e.title_id
    GROUP BY t.has_known_actor
""", conn)
q8_indexed = q6.set_index("cast_tier")#used documentation and active book to make a visual out of the query results
q8_indexed = q8_indexed[["trending_pct", "avg_rating"]]
q8_indexed.plot(kind="bar")
plt.xticks(rotation=0)
plt.ylabel("Value")#labeled my axis of course
save("08knownactoreffect.png", "Known Actor vs No Known Actor")

conn.close()