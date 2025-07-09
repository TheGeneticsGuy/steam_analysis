import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# For visual output
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
sns.set_style('whitegrid') # plotting style
plt.rcParams['figure.figsize'] = (12, 8) # This is setting the default figure size

# Pure Aesthetics
print()
print("--- Steam Data Analysis Project ---")
print()

# Load the Data from Local File - the CSV is HUGE at close to 300MB and nearly 100,000 games
print("Loading Steam Data...")
steam_file = pd.read_csv('data/steam_games.csv')    # No need to make a try block as this file will always be there
print("Data Successfully Loaded.")
print(f"Dataset contains {steam_file.shape[0]} games.")
print()

# Data cleanup before analysis
print("--- Processing Data and Preparing for Analysis ---")
print()

# Renaming columns and removing white space
steam_file.rename(columns={
    'Release date': 'Release_Date',
    'Estimated owners': 'Estimated_Owners',
    'Peak CCU': 'Peak_CCU',
    'Required age': 'Required_Age',
    'DLC count': 'DLC_Count',
    'Metacritic score': 'Metacritic_Score',
    'User score': 'User_Score',
    'Average playtime forever': 'Avg_Playtime_Forever',
    'Median playtime forever': 'Median_Playtime_Forever'
}, inplace=True)

# FILTER OUT ADULT GAMES
# I had to add this as so many games popping up in resutls were "adult content" games
# Only way I found to truly filter it out was with "tags"
adult_tags = ['Hentai', 'NSFW', 'Adult Only']
adult_tags_pattern = '|'.join(adult_tags) # Regex patter to find the patterns

# Ensure the 'Tags' column is a string to use .str methods
steam_file['Tags'] = steam_file['Tags'].fillna('')

# Implement the filter by masking the rows with the tags
adult_mask = steam_file['Tags'].str.contains(adult_tags_pattern, case=False, na=False)
initial_rows_before_adult_filter = len(steam_file)

# Inverting mask to KEEP only the rows that are NOT adult games
steam_file = steam_file[~adult_mask].copy()

# Method:           clean_price(price)
# What it Does:     Takes the price from the price column of the game, converts it to number, and returns it
# Purpose:          The data in the columns has USD formatted cost which needs to be converted into an actual number.
#                   In some cases there is a string saying "Free to Play" for the cost, that needs to be returned as 0.0 for cost.add()
#                   Unable to anlalyze until everything is in number format.
def clean_price(price):
    if pd.isna(price) or not isinstance(price, (str, int, float)):
        return None
    try:
        # If price is already a number, just return it
        if isinstance(price, (int, float)):
            return float(price)

        # Some prices are strings and say "Free to Play"
        price_str = str(price).lower()
        if 'free' in price_str:
            return 0.0

        # Remove '$' or commas and convert to float
        return float(price_str.replace('$', '').replace(',', ''))
    except (ValueError, TypeError):
        return None

# DATA CONVERSION
steam_file['Price_Numeric'] = steam_file['Price'].apply(clean_price)

# Release Date: Convert to common datetime format, and extract the year.
steam_file['Release_Date_dt'] = pd.to_datetime(steam_file['Release_Date'], errors='coerce')
steam_file['Release_Year'] = steam_file['Release_Date_dt'].dt.year

# Reviews: Build a new review structure
# So there is a count of positive and count of negative reviews. I want to make a ratio of positive count over total for percent positive
steam_file['Total_Reviews'] = steam_file['Positive'] + steam_file['Negative']
steam_file['Review_Score'] = 0.0
mask = steam_file['Total_Reviews'] > 0
steam_file.loc[mask, 'Review_Score'] = steam_file.loc[mask, 'Positive'] / steam_file.loc[mask, 'Total_Reviews']

# Ensuring no NaN values in the genres column
steam_file['Genres'] = steam_file['Genres'].fillna('')

steam_file['Is_Indie'] = steam_file['Genres'].str.contains('Indie', na=False)
steam_file['Is_FreeToPlay'] = steam_file['Genres'].str.contains('Free To Play', na=False)
steam_file['Is_EarlyAccess'] = steam_file['Genres'].str.contains('Early Access', na=False)
steam_file['Is_Casual'] = steam_file['Genres'].str.contains('Casual', na=False) # Added Casual


# Genres and Developers
steam_file['Genres'] = steam_file['Genres'].fillna('Unknown')
steam_file['Developers'] = steam_file['Developers'].fillna('Unknown')

# Creating a new genre column, calling it 'Game_Genres'
non_genres = ['Indie', 'Free To Play', 'Early Access', 'Casual']
def filter_genres(genre_string):
    if not isinstance(genre_string, str):
        return ''
    genres_list = [genre.strip() for genre in genre_string.split(',')]
    # Filter out non-genre categories
    true_genres = [genre for genre in genres_list if genre not in non_genres and genre != '']
    return ','.join(true_genres)

steam_file['Game_Genres'] = steam_file['Genres'].apply(filter_genres)

# So, to answer my questions, I need to drop steam games that have incomplete info, like no reviews or genres
# A game w/o reviews, price, or genre cannot be used in this analaysis, and likely would be small indie unknown games anyway.
initial_rows = len(steam_file)
steam_file.dropna(subset=['Price_Numeric', 'Total_Reviews', 'Genres', 'Release_Year'], inplace=True)
steam_file = steam_file[steam_file['Genres'] != 'Unknown']
print(f"Data Cleaned up! Dropped {initial_rows - len(steam_file)} games for having incomplete data.")
print(f"Removed {initial_rows_before_adult_filter - len(steam_file)} games based on adult content tags.")
print(f"Final dataset for analysis: {steam_file.shape[0]} games.")
print()

# QUESTION 1
print("QUESTION 1: What are the 5 most common genres among top-rated games?")
# print("(Games must have > 90% positive reviews and > 100 reviews)")

# Filter the games to be analyzed:
# Note, it is important that I have a minimum number of reviews that way a game with say, only 5 reviews doesn't end up polluting the data
# because it's just not enough information. So, I set a minimum to 100 reviews.
steam_file_successful = steam_file[(steam_file['Review_Score'] >= 0.90) & (steam_file['Total_Reviews'] >= 100)].copy()
print('Games analyzed based on the following criteria:')
print('   90% Positive Reviews')
print('   100 Total Reviews')

# Data Processing and Aggregation of top 10
# By "exploding" the genere string I can count them individually by genre.
all_genres = steam_file_successful['Game_Genres'].str.split(',').explode().str.strip()
all_genres = all_genres[all_genres != '']
top_10_genres = all_genres.value_counts().head(5)

print()
print("Top 5 genres for top-rated games on Steam:")
print()
print(top_10_genres.to_string())

# Let's visualize the data!
plt.figure()
sns.barplot(x=top_10_genres.values, y=top_10_genres.index, palette='rocket')
plt.title('Top 5 Genres of Games on Steam', fontsize=16)
plt.xlabel('Number of Games', fontsize=12)
plt.ylabel('Genre', fontsize=12)
plt.tight_layout()
plt.savefig('q1_top_genres.png') # This generates an image for the chart
print()
print("Generated chart: 'q1_top_genres.png'")

# QUESTION 2
print()
print("QUESTION 2: Is there a correlation between game price and the review score?")

# Removing free editions (price is zero) and speecial edition type games where the price is > 80
steam_file_for_corr = steam_file[(steam_file['Price_Numeric'] >= 5) & (steam_file['Price_Numeric'] <= 80)].copy()

# Using Pearson Correlation to find between the two.
correlation = steam_file_for_corr['Price_Numeric'].corr(steam_file_for_corr['Review_Score'])
print(f"\nThe Pearson Correlation Coefficient between Price and Review Score is: {correlation:.4f}")

# Pearson correlation coefficient (r)
# value 	            Strength 	Direction
# Greater than .5 	    Strong 	    Positive
# Between .3 and .5 	Moderate 	Positive
# Between 0 and .3 	    Weak 	    Positive
# 0 	                None 	    None
# Between 0 and –.3 	Weak 	    Negative
# Between –.3 and –.5 	Moderate 	Negative
# Less than –.5 	    Strong 	    Negative

if abs(correlation) < 0.1:
    print(f"The correlation coefficient of {correlation:.4f} is extremely close to zero, indicating no meaningful linear relationship between Price and Review Score. The variables appear to be independent.")

# VISUALIZATION:
plt.figure()
sns.regplot(
    data=steam_file_for_corr,
    x='Price_Numeric',
    y='Review_Score',
    scatter_kws={'alpha': 0.1, 's': 15}, # Smaller, transparent points for the sake of density
    line_kws={'color': 'red', 'linewidth': 2}
)
plt.title('Game Price vs. User Review Score\n(Games priced $5 to \$80)', fontsize=16)
plt.xlabel('Price ($)', fontsize=12)
plt.ylabel('Review Score (Positive Ratio)', fontsize=12)
plt.ylim(0, 1.05) # Y-axis from 0% to 100%
plt.tight_layout()
plt.savefig('q2_price_vs_review.png')
print()
print("Generated chart: 'q2_price_vs_review.png'")

# QUESTION 3 - Note, this is DEVELOPERS not PUBLISHERS. Developers actually make the games.
print()
print("QUESTION 3: Which developers have the best track record for releasing top rated games?")
print('Developers analyzed based on the following criteria:')
print('   At least 3 published games')
print('   Average review score of all games with 100 or more reviews')
print()

# Follow previous standards - ensure my review only includes devs with games with 100+ reviews.
steam_file['Developers'] = steam_file['Developers'].fillna('Unknown')
steam_file_significant_games = steam_file[steam_file['Total_Reviews'] >= 100].copy()
print(f"\nAnalyzing {steam_file_significant_games.shape[0]} games with at least 100 reviews.")

# Ok next, I need to count how many games each dev has.
dev_counts = steam_file['Developers'].value_counts()
# This will be the list of all devs with 3 or more games.
dev_counts = steam_file_significant_games['Developers'].value_counts()
# Get list of developers with 5 or more significant games.
prolific_devs = dev_counts[dev_counts >= 5].index.tolist()

# Filter the significant games list to only include these prolific developers.
steam_file_prolific = steam_file_significant_games[steam_file_significant_games['Developers'].isin(prolific_devs)].copy()


developer_performance = steam_file_prolific.groupby('Developers').agg(
    Average_Review_Score=('Review_Score', 'mean'),
    Game_Count=('Name', 'count')
).sort_values(by='Average_Review_Score', ascending=False).head(15)  # Showing 15 developers

print("\nTop 15 Developers by Average Review Score (min. 3 games):")
# I don't really know devs that well, so I included their 3 most popular games
for dev_name, row in developer_performance.iterrows():
    avg_score = row['Average_Review_Score']
    game_count = row['Game_Count']

    # This gets the top 3 games for each developer from the prolific list (devs wqith 3+ games)
    top_3_games = steam_file_prolific[steam_file_prolific['Developers'] == dev_name]\
                                .sort_values('Review_Score', ascending=False)\
                                .head(3)['Name'].tolist()

    # Print the formatted output
    print(f"\n- {dev_name} (Avg Score: {avg_score:.2%})")
    print("  Top Games:")
    for i, game in enumerate(top_3_games, 1):
        print(f"    {i}. {game}")

# 3. VISUALIZATION
plt.figure()
sns.barplot(
    x='Average_Review_Score',
    y=developer_performance.index,
    data=developer_performance,
    palette='viridis'
)
plt.title('Top 15 Developers by Average Review Score\n(Minimum 3 Games Published)', fontsize=16)
plt.xlabel('Average Review Score (0.0 to 1.0)', fontsize=12)
plt.ylabel('Developer', fontsize=12)
plt.xlim(0.75, 1.0)
plt.tight_layout()
plt.savefig('q3_top_developers.png')
print()
print("Generated chart: 'q3_top_developers.png'")
print()

print("--- Analysis Complete ---")