import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px


#Import data from webscrapping
df_sales=pd.read_csv("df_sales.csv")

#========================= Gabriel - Cleaning df =======================================
#getting my code right(gabriel)
df = pd.read_csv("data.csv")
Nintendodb = df
#droping nan values when they are in both meta_score and user_score columns
nintendo1 = Nintendodb.dropna(how="all",subset=("meta_score","user_score")).drop(labels="esrb_rating", axis=1)
#there are values with "TBA" in date column, therefore we need to change it to nan
# replace 'TBA' with NaN
nintendo1['date'] = nintendo1['date'].replace('TBA', np.nan)
# convert the 'date_column' to datetime type
nintendo1['date'] = pd.to_datetime(nintendo1['date'], format='%b %d, %Y')


#============================== Louis - Cleaning and homogenized the genres list by text processing ==============
#Adjust the dataframe
#Adjust the columns of the data set (main_genre and year)
df['year'] = df['date'].str.split(',').str[1].str.strip()
df['genres'] = df['genres'].apply(lambda x : "[]" if type(x) != str else x)\
    .apply(lambda x : eval(x))

#Create a main genre category 
top16 = df['genres']\
        .explode().value_counts().index[0:16] # I decided to go with 16 genres after seeing that I could grab 95% of the titles with these 16 genres

def grab_the_most_produced(genre_list, top_list): # This function allows the attribution of one main genre to every game
#turn into set and intersect !!!     
    crossing_genres = np.intersect1d(np.array(genre_list), np.array(top_list))
    output = []
    if len(crossing_genres)>0:
        for item in top_list:
            if item in crossing_genres:
                output.append(item)
        return output[0]
    elif 'Simulation' in genre_list:
        return 'Simulation'
    elif 'Driving' in genre_list:
        return 'Driving'
    else :    
        return 'Other'
df['main_genre'] = df['genres'].apply(grab_the_most_produced, top_list = top16)
 
#===================================== Build the streamlite dashboard ====================================

#Streamlite configuration
st.set_page_config(
    page_title="Project 3 - Webscrapping and Video Games Analysis",
    page_icon=":smiley:",
    layout="wide",
)

    # CSS to inject contained in a string
hide_table_row_index = """
        <style>
        thead tr th:first-child {display:none}
        tbody th {display:none}
        </style>
        """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
# Designed of a sidebar to go from one dashboard to the other
dash = st.sidebar.radio(
    "What dashboard do you want to see ?",
    ('What happened to games ?', 'Tips for your game', 'Clash & Platforms', "What about Sales?"))

#=============================== 1st dashboard - Gabriel - "What happened to the games?" =================

if dash == "What happened to games ?":
    st.header("What Happened to games?")
    st.subheader("Are games getting worst as years go by?")
    st.header("")
    col1, col2 = st.columns(2)
    with col2:
        st.subheader("Do the experts agree?")
        st.header("")
        fig, ax = plt.subplots(1,1)
        viz_bar1 = sns.scatterplot(data=nintendo1, x="date", y="meta_score")
        plt.xticks(rotation=45)
        plt.title('Customer Evaluation vs Meta score, per year')
        st.pyplot((viz_bar1.figure))
    with col1:
        st.subheader("Do you notice how as we approach to more recent years, people enjoy the games less and less?")
        fig, ax = plt.subplots(1,1)
        viz_bar1 = sns.scatterplot(data=nintendo1, x="date", y="user_score")
        plt.xticks(rotation=45)
        plt.title('Customer Evaluation per year')
        st.pyplot((viz_bar1.figure))
    st.subheader("As we can see even there are differences between how experts(meta_score) and customers rate the game.")
    col3, col4 = st.columns(2)    
    with col3:
        st.subheader("this raises the question: how different are experts rating the games relative to customers?" )
        fig, ax = plt.subplots(1,1)
        viz_bar2 = sns.scatterplot(data=nintendo1, x="date", y="user_score", hue="meta_score")
        plt.xticks(rotation=45)
        plt.title('Customer Evaluation per year')
        st.pyplot((viz_bar2.figure))
        st.write("the max rated game by the users over this years was:")
        st.write(nintendo1[["title", "user_score"]].max())

    with col4:
        st.subheader("Are games for new platforms worst than the games for old platforms?")
        fig, ax = plt.subplots(1,1)
        viz_bar3=sns.histplot(data = nintendo1, x="platform", y="meta_score")
        plt.xticks(rotation=45)
        plt.title('Customer Score per platform')
        st.pyplot((viz_bar3.figure))
#=============================== 2nd dashboard - Louis - Tips for your game ===================
# This idea here is to give some tips to potential developer to have an idea about the market which could be interesting to target. I used the rating to compare the games but we can imagine to do the same things with the sales depending on what is important for you.

elif dash == 'Tips for your game':
    #You can adjust the period to consider : the last 2 years, 5 years, 10 years ? It's up to you.
    start_year = st.slider('What is the first year do you want to consider ?', 1996, 2020, 2015)
    
    #Filtering the dataframe regarding the slider
    df['year'] = df['year'].apply(lambda x : float(x))
    df_tempo = df[df['year']>start_year]
    
    #The most well rated genres - You can choose to see the user score or the score from professional reviewers
    #Filtering before the plot
    st.subheader('Top 10 well rated genres (user score in red and meta score in blue)')
    df_tempo_bis = pd.DataFrame()
    df_tempo_bis['main_genre'] = df_tempo['main_genre'].value_counts().sort_index().index
    df_tempo_bis['number_of_games'] = df_tempo['main_genre'].value_counts().sort_index().values
    df_tempo_bis['avg_user_score'] = df_tempo['user_score'].groupby(by = df_tempo['main_genre']).mean().sort_index().values
    df_tempo_bis['avg_meta_score'] = df_tempo['meta_score'].groupby(by = df_tempo['main_genre']).mean().sort_index().values
    df_tempo_user_10_bis = df_tempo_bis.sort_values(by = 'avg_user_score', ascending = False)[0:10]
    df_tempo_meta_10_bis = df_tempo_bis.sort_values(by = 'avg_meta_score', ascending = False)[0:10]
    
    #Plot 
    fig_1_3, ax = plt.subplots(1,2, figsize=(3, 1.5))
    st.write("The darker is the bar, the more games we have for this genre.")
    #sns.barplot(x = df_tempo_bis['main_genre'], y = df_tempo_bis['avg_user_score'], hue= df_tempo_bis['number_of_games'].apply(lambda x:int(x)))
    my_cmap1 = plt.get_cmap("Reds") #cmap to also consider in the plot the number of games per genre 
    ax[0].bar(x=  df_tempo_user_10_bis['main_genre'],
            height = df_tempo_user_10_bis['avg_user_score'],
            color=my_cmap1(df_tempo_user_10_bis['number_of_games']), label = True)
    my_cmap2 = plt.get_cmap("Blues")
    ax[0].tick_params('x', labelrotation=90, labelsize = 7)
    ax[0].set_ylabel("Score")
    ax[1].bar(x=  df_tempo_meta_10_bis['main_genre'],
            height = df_tempo_meta_10_bis['avg_meta_score']/10,
            color=my_cmap2(df_tempo_meta_10_bis['number_of_games']), label = True)
    ax[1].set_ylabel("")
    ax[1].set_yticks([], [])
    plt.xticks(rotation = 90, fontsize = 7)
    st.pyplot(fig_1_3)
    
    #The platform to target - Same schema as the previous one
    st.subheader('The platform to target : Average rating per platform')
    #Filtering before plotting
    df['year'] = df['year'].apply(lambda x : float(x))
    df_tempo = df[df['year']>start_year]
    df_tempo_bis = pd.DataFrame()
    df_tempo_bis['platform'] = df_tempo['platform'].value_counts().sort_index().index
    df_tempo_bis['number_of_games'] = df_tempo['platform'].value_counts().sort_index().values
    df_tempo_bis['avg_user_score'] = df_tempo['user_score'].groupby(by = df_tempo['platform']).mean().sort_index().values
    df_tempo_bis['avg_meta_score'] = df_tempo['meta_score'].groupby(by = df_tempo['platform']).mean().sort_index().values
    df_tempo_user_10_bis = df_tempo_bis.sort_values(by = 'avg_user_score', ascending = False)[0:10]
    df_tempo_meta_10_bis = df_tempo_bis.sort_values(by = 'avg_meta_score', ascending = False)[0:10]
    
    #plot
    fig2_3, ax = plt.subplots(1,2, figsize=(3, 1.5))
    my_cmap1 = plt.get_cmap("Reds")
    ax[0].bar(x=  df_tempo_user_10_bis['platform'],
            height = df_tempo_user_10_bis['avg_user_score'],
            color=my_cmap1(df_tempo_user_10_bis['number_of_games']), label = True)
    my_cmap2 = plt.get_cmap("Blues")
    ax[0].tick_params('x', labelrotation=90, labelsize = 7)
    ax[0].set_ylabel("Score")
    ax[1].bar(x=  df_tempo_meta_10_bis['platform'],
            height = df_tempo_meta_10_bis['avg_meta_score']/10,
            color=my_cmap2(df_tempo_meta_10_bis['number_of_games']), label = True)
    ax[1].set_ylabel("")
    ax[1].set_yticks([], [])
    plt.xticks(rotation = 90, fontsize = 7)
    st.pyplot(fig2_3)

    #Study the competitors    
    st.subheader('The most active competitors : Are they loved by the users ?')
    df['developers'] = df['developers'].apply(lambda x : "[]" if type(x) != str else x).apply(lambda x : x.strip())\
    .apply(lambda x : eval(x))
    
    #Filtering - The most active competitors
    df['year'] = df['year'].apply(lambda x : float(x))
    df_tempo = df[df['year']>start_year].explode('developers')
    df_tempo_bis = pd.DataFrame()
    df_tempo_bis['developers'] = df_tempo['developers'].value_counts().sort_index().index
    df_tempo_bis['number_of_games'] = df_tempo['developers'].value_counts().sort_index().values
    df_tempo_bis['avg_user_score'] = df_tempo['user_score'].groupby(by = df_tempo['developers']).mean().sort_index().values
    df_tempo_10_bis = df_tempo_bis.sort_values(by = 'number_of_games', ascending = False)[0:10]

    #Plot
    fig3_3, ax = plt.subplots(1, figsize=(4, 2))
    ax = sns.scatterplot(x = df_tempo_10_bis['developers'], y = df_tempo_10_bis['avg_user_score'], size= df_tempo_10_bis['number_of_games'], legend=True, sizes=(5, 250), color = 'red')
    #sns.move_legend(ax, "lower right", fontsize = 8)
    # for legend text
    plt.setp(ax.get_legend().get_texts(), fontsize='6')  
    # for legend title
    plt.setp(ax.get_legend().get_title(), fontsize='6') 
    plt.xticks(rotation = 90, fontsize = 5)
    plt.ylabel('Average user score', size = 7)
    plt.xlabel('')
    plt.yticks(fontsize = 5)
    plt.ylim((0, 10))
    st.pyplot(fig3_3)
    
    st.subheader('What about a collaboration ?') #By digging inside the datas, we can see that lots of studios are working together...
    

#=============================== 3rd dashboard - Joao - "Clash and Platforms" =================

elif dash == 'Clash & Platforms':
    # Define the colors to use for the charts
    colors = ['orange', 'blue', 'green', 'red', 'purple', 'gray', 'cyan', 'magenta', 'yellow', 'brown']
    # Create a Streamlit app
    st.title('Clash & Platforms Dashboard')
    # Add a chart showing the number of games per platform as a pie chart
    platform_counts = df['platform'].value_counts().sort_values(ascending=False)
    fig_pie = go.Figure(go.Pie(
        labels=platform_counts.index,
        values=platform_counts.values,
        marker=dict(colors=colors[:len(platform_counts)])
    ))
    fig_pie.update_layout(
        title='Number of Games per Platform (Pie Chart)',
    )
    st.plotly_chart(fig_pie)
    # Add a chart showing the number of games per platform as a bar chart
    fig_bar, ax = plt.subplots(figsize = (3, 1.5))
    fig_bar = go.Figure(go.Bar(
        x=platform_counts.index,
        y=platform_counts.values,
        marker_color=colors[:len(platform_counts)],
        text=platform_counts.values,
        textposition='inside',
    ))
    fig_bar.update_layout(
        title='Number of Games per Platform (Bar Chart)',
        xaxis_title='Platform',
        yaxis_title='Number of Games')
    
    st.plotly_chart(fig_bar)

    # Create separate DataFrames for Super Mario and Pokemon games
    mario_df = df[df['title'].str.contains('Mario')]
    pokemon_df = df[df['title'].str.contains('Pokemon')]
    # Compare the number of games released for each franchise
    mario_count = len(mario_df)
    pokemon_count = len(pokemon_df)
    st.write(f'Super Mario: {mario_count} games')
    st.write(f'Pokemon: {pokemon_count} games')
    # Compare the average user ratings for each franchise
    mario_rating = mario_df['user_score'].mean()
    pokemon_rating = pokemon_df['user_score'].mean()
    st.write(f'Super Mario: {mario_rating:.2f} average rating')
    st.write(f'Pokemon: {pokemon_rating:.2f} average rating')
    # Create a bar chart of the number of games released for each franchise
    fig, ax = plt.subplots()
    ax.bar(['Super Mario', 'Pokemon'], [mario_count, pokemon_count])
    ax.set_title('Number of Games Released')
    ax.set_ylabel('Count')
    st.pyplot(fig)
    # Create a new DataFrame with the relevant columns for the box plot
    boxplot_df = pd.concat([mario_df[['title', 'user_score']].assign(Franchise='Super Mario'),
                            pokemon_df[['title', 'user_score']].assign(Franchise='Pokemon')])
    # Create a box plot comparing the user ratings distribution
    fig_box = px.box(boxplot_df, x='Franchise', y='user_score', color='Franchise',
                 title='User Ratings Distribution for Super Mario and Pokemon Games',
                 labels={'Franchise': 'Game Franchise', 'user_score': 'User Rating (out of 10)'})
    st.plotly_chart(fig_box)


#Datas from Webscrapping on vgchartz - See  Web_scrapping_together.ipynb for more details    
elif dash == "What about Sales?":
    st.header("The 10 best sellers from Nintendo")
    top10 = df_sales.sort_values(by = 'Total sales in million', ascending = False).head(10)
    fig_4, ax = plt.subplots(1, figsize=(3, 1.5))
    viz_bar4=sns.barplot(data=top10, x="Titles", y= "Total sales in million", color = 'red')
    plt.xticks(rotation=90, fontsize = 5)
    plt.yticks(fontsize = 5)
    plt.ylabel('Total sales in milions $', size = 5)
    plt.xlabel('', size = 5)
    plt.title('Top 10 Sales', fontsize = 5)
    st.pyplot((viz_bar4.figure))
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Top 10 best games')    
        st.table(top10['Titles'].head(10))
    with col2: #Here it's not very relievant to plot this values since we have few games with 0.00 $ of sales... probably due to a rounding issue on vgchartz
        tail10 = df_sales.sort_values(by = 'Total sales in million').head(10)
        st.subheader('Top 10 worst games')
        st.table(tail10['Titles'].head(10))
    

