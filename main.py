# API_KEY = "c8a093f4"
#THIS IS A MESS NOT REAL CODE JUST CHUNKS OF WHAT I DONT NEED IN CASE I NEED IT LATER
# sample 750 from df_ml with a fixed seed so you get the same sample every 
# results = []
# merge back onto the sample
# omdb_df = pd.DataFrame(results)
# df_enriched = sample.merge(omdb_df, on="title", how="left")
# clean up numeric columns
# df_enriched["imdb_rating"] = pd.to_numeric(df_enriched["imdb_rating"], errors="coerce")
# df_enriched["imdb_votes"]  = (df_enriched["imdb_votes"]
 #                               .str.replace(",", "", regex=False)
 #                               .pipe(pd.to_numeric, errors="coerce"))
# df_enriched["metascore"]   = pd.to_numeric(df_enriched["metascore"], errors="coerce")
# df_enriched.to_csv("df_enriched.csv", index=False)
# print(f"\ndone — {df_enriched['imdb_rating'].notna().sum()} / 750 titles matched")
# print(df_enriched[["title", "imdb_rating", "imdb_votes", "metascore", "awards"]].head(10))
# API_KEY = "c8a093f4"

# existing_sample = pd.read_csv("df_enriched.csv")
# remaining = df_ml[~df_ml["title"].isin(existing_sample["title"])]
# new_sample = remaining.sample(n=1000, random_state=99).copy()

# # merge new batch and combine with existing
# new_omdb = pd.DataFrame(results)
# new_enriched = new_sample.merge(new_omdb, on="title", how="left")

# # combine old and new and save
# df_enriched_combined = pd.concat([existing_sample, new_enriched], ignore_index=True)
# df_enriched_combined.to_csv("df_enriched.csv", index=False)

# print(f"\ndone — total rows: {len(df_enriched_combined)}")
# print(f"new matches: {new_enriched['imdb_rating'].notna().sum()} / 1000")

# df_enriched = pd.read_csv("df_enriched.csv")
# df_enriched["imdb_rating"] = pd.to_numeric(df_enriched["imdb_rating"], errors="coerce")
# df_enriched["imdb_votes"] = pd.to_numeric(df_enriched["imdb_votes"].astype(str).str.replace(",", "", regex=False), errors="coerce")

# existing_sample = pd.read_csv("df_enriched.csv")
# remaining = df_ml[~df_ml["title"].isin(existing_sample["title"])]
# print(len(remaining))
# print(df_ml_final["has_awards"].value_counts())
# print(df_ml_final["trending"].value_counts())



# df_ml_final = df_ml_final.drop(columns=["awards", "has_awards", "runtime", "language"])
# print(df_ml_final.columns.tolist())

# conn = sqlite3.connect("netflix.db")
# df_ml_final.to_sql("ml_ready", conn, if_exists="replace", index=False)
# conn.close()

