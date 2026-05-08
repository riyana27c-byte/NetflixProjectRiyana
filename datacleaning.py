import pandas as pd
import os
os.makedirs("charts", exist_ok=True)


df =pd.read_csv("netflix_titles.csv")#This is the Kaggle file with all of the title movie and show titles that I dowloaded and imported
df= df.drop(columns=["show_id", "director", "description"]) #these columns are the ones I decided to drop because they were primarily descriptive and unusable for machine learning training. I had also removed cast before but I have since then changed that
df.columns = df.columns.str.strip() #basic cleaning by striping all entries in all columns so that the formatting stays even
df.columns= df.columns.str.lower()#basic cleaning everything in lower case so content has no off formatting stuff
df = df.dropna(subset=["title", "date_added", "release_year", "listed_in", "type"]) #these are crucial identifiers needed for the ml so none of these columns can have null values. thus dropped their null values
df["release_year"] =pd.to_numeric(df["release_year"])#before I think the release_year was an object or string when I printed the column data types. so just to be I changed to numeric




df["date_added"]= df["date_added"].str.strip()#stripped extra spaces and stuff I think i did this before
df["date_added"]= pd.to_datetime(df["date_added"])#changed dateadded object to a datetime object instead
df["year_added"]= df["date_added"].dt.year#extracted just the year and made it into its own column
df["listed_in"]= df["listed_in"].str.lower()#made sure all of the genres are in lowercase only
df["age"] =2026 -df["release_year"]#since release is numeric returns the age of the content
df["is_recent"]= df["release_year"] >= 2015#I classified anything younger than a decade as recent, possible since everything is numbers

df["is_recent"] =df["is_recent"].astype(int) #0 for no, 1 for yes, easier in ml
df["is_tv"] =df["type"] == "TV Show"#instead of having tv show and movie written manually had a column to classify if tv or not
df["is_tv"]= df["is_tv"].astype(int) #0 for movie, 1 for tv show

def parseduration(row): #a method so if the columns say seasons of minutes everything is cleaned well
    durate = str(row["duration"]) #converted the row to a string incase its an object so I can use string methods
    
    if "min" in durate:#if the durations string uses the word min or minutes, basically remove it with a replace
        durate = durate.replace("min", "")
        durate = durate.strip()#and remove all extra spacing
        return int(durate)#now i have a number for minutes
    
    elif "Season" in durate: #same approach for seasons just a number of how many seasons
        durate = durate.replace("Seasons", "")
        durate = durate.replace("Season", "")
        durate = durate.strip()
        return int(durate)
    return None #now this method might introduce some noise/innacuracy  in the ml since 3 seasons vs 153 minute movie has no large differentiation besides is_tv. which the ml should learn
df["duration_num"] = df.apply(parseduration, axis=1) #apply my method and store results in duration number columns


df = df.dropna(subset=["country"]) #drop any null in country column for cleaning 
df["country_primary"] =df["country"].str.split(",") #splits all countries listed from the string into a list
df["country_primary"] =df["country_primary"].str[0]#only takes the first movie listed. easier for cleaning and made assumption that first country listed is primary country of content
df["country_primary"] = df["country_primary"].str.strip() #removes any extra spaces and formatting stuff
df["is_us"] = df["country_primary"] == "United States" #since I saw so many US movies I made a column for that information to use data to understand the data in charts
df["is_us"] = df["is_us"].astype(int) #0 for not us, 1 for yes
df["genre_primary"] =df["listed_in"].str.split(",") #same assumption for genre to create simplicity in data 
df["genre_primary"] = df["genre_primary"].str[0]
df["genre_primary"] =df["genre_primary"].str.strip() #have nly one genry which i assumed was main one left 
df["cast"]= df["cast"].fillna("")#a few entries dont have cast names, but i didnt want to drop because of that since its not extremely needed. so fill null columns and not drop

cast_df = df[["title", "cast"]].copy() # came up with this after seeing the results of the ml. this is how I included cast without extreme data altering and a new system
cast_df["cast"] =cast_df["cast"].str.split(",")#after making a new df with cast info to keep from messiness, I split all cast names, if any into a list by the comma
cast_exploded = cast_df.explode("cast")#exploded on the list, found this feature in pandas documentation. Now a lot of the titles are listed mutlilple times, for every cast memeber the title or entry is listed

cast_exploded["cast"] = cast_exploded["cast"].str.strip()#cleaned after checking data manually didnt need lower since names capitalized correctly

cast_exploded= cast_exploded[cast_exploded["cast"] != ""]#filters own empty cast rows just in case explosion created them if a comma then nothing after name


actor_counts =cast_exploded["cast"].value_counts() #counts occurances of each actor name across exploded cast column

actor_counts_filtered = actor_counts[actor_counts >= 3]#filters out to the actors that have been counted at least 3 times
known_actors =set(actor_counts_filtered.index) #make a non repeating, so set, of the indexes of the frequently counted actors, if not set the count would show up with the actor everytime the actor was counted, all repeated

#with the help of CGPT in codebench
cast_per_title =cast_exploded.groupby("title")["cast"].apply(set)#this groups all the exploded cast rows back by title, and actor names into a set. one row per title with set of all actors in title
def check_known_actor(title):#CGPT in codebench help
    cast_set= cast_per_title.get(title, set())#CGPT in codebench help
    overlap= cast_set & known_actors#CGPT in codebench help
    return int(bool(overlap))#CGPT in codebench help

df["has_known_actor"] = df["title"].map(check_known_actor)#CGPT in codebench help this stores result in new columns for knownactor 1 for yes 0 for no


df = df.drop_duplicates(subset=["title"]).copy()#just in case any title duplicates came over, so not really needed, made a copy just for safety

omdb = pd.read_csv("df_enriched.csv") #I used my api key and free policy and CGPT help to get ombd data before, I didnt want that to keep calling and causing errors so commented and removed all that api code
omdb["imdb_rating"] = pd.to_numeric(omdb["imdb_rating"], errors="coerce")#make rating into number, coerce suggested by CGPT codebench
omdb["imdb_votes"]= omdb["imdb_votes"].astype(str) #made votes into a string if its an object or something
omdb["imdb_votes"] =omdb["imdb_votes"].str.replace(",", "")#removes comma for number if number is like 15,000
omdb["imdb_votes"] = pd.to_numeric(omdb["imdb_votes"], errors="coerce")#made votes into a number

omdb = omdb[["title", "imdb_rating", "imdb_votes"]]#made a table with just the information I need while is title and rating info other ombd given info not needed for too advanced to interpret

df = df.merge(omdb,on="title", how="inner") #merged omdb data with the netflix show data on the title, so now my df has the info about the content and the imdb rating


df = df.dropna(subset=["imdb_rating", "imdb_votes"])#if data was missing and converted space into numeric, remove the whole row and title now


df["trending"] =df["imdb_votes"] >= 10000 #I made an assumption here that can cause poor accuracy in the real world. that 10000+ votes is popular, this can be very incorrect i didnt not have another approach to find popularity
df["trending"] = df["trending"].astype(int)#0 if less than 10000 votes, otherwise more

#keep has the name of the columns, I actually want to have in my df, i dont want country, duration, date_added, I cleaned all this into diff columns
keep = ["title","type","release_year","age", "is_recent", "duration_num", "is_tv", "is_us", "year_added", "country_primary", "genre_primary", "rating", "listed_in", "cast", "has_known_actor", "imdb_rating", "imdb_votes", "trending"]
df = df[keep].copy()#made a copy for clean concept
df.to_csv("df_ml_final.csv",index=False) #put it in a csv file to view my work, had to add some lower and replace after doing this up above


print("df saved:",df.shape[0],"rows,", df.shape[1], "cols")
print("trending:", df["trending"].value_counts().to_dict())#CGPT from codebench suggested todict
print("has_known_actor:",df["has_known_actor"].value_counts().to_dict())
print("known actors:", len(known_actors), "unique actors appearing more than 3 times")
