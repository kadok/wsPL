import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pymongo import MongoClient
from config import Config
import numpy as np
from matplotlib.animation import PillowWriter
from matplotlib.animation import FFMpegWriter

# Connect to MongoDB
client = MongoClient(Config.DB_LINK)
db = client[Config.DATABASE]
collection = db[Config.COLLECTION]

# List all registers
docs = list(collection.find({}, {"season": 1, "value": 1, "_id": 0}))

# Convert to Dataframe
df = pd.DataFrame(docs)

# Rename Value
df = df.rename(columns={"value": "goals"})

# Sum the total goals by season 
df_total = df.groupby("season")["goals"].sum().reset_index()

# Sort the seasons
df_total["season_year"] = df_total["season"].str[:4].astype(int)
df_total = df_total.sort_values("season_year")

# Remove the last Session, the incomplete one
last_season = df_total["season"].iloc[-1]
df_total = df_total[df_total["season"] != last_season]

# Data will be used in the animation
years = df_total["season_year"].values
goals = df_total["goals"].values
seasons = df_total["season"].values

# Create the figure and the axis
fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor('#f8f9fa')
ax.set_facecolor('#ffffff')

# Graph initial configuration
ax.set_xlim(years[0] - 1, years[-1] + 1)
ax.set_ylim(0, goals.max() * 1.1)
ax.set_xlabel('Season', fontsize=12, fontweight='bold')
ax.set_ylabel('Scored Goals', fontsize=12, fontweight='bold')
ax.set_title('Scored Goals by Season Evolution', fontsize=16, fontweight='bold', pad=20)

# Add grid to enhance the visualization
ax.grid(True, linestyle='--', alpha=0.7)

# Add a text box to the current season
year_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=14, 
                    fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", 
                    facecolor="lightblue", edgecolor="black", alpha=0.8))

# Add a text box to the total goals
goals_text = ax.text(0.02, 0.85, '', transform=ax.transAxes, fontsize=12, 
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))

# Function to init the animation
def init():
    ax.clear()
    ax.set_xlim(years[0] - 1, years[-1] + 1)
    ax.set_ylim(0, goals.max() * 1.1)
    ax.set_xlabel('Season', fontsize=12, fontweight='bold')
    ax.set_ylabel('Scored Goals', fontsize=12, fontweight='bold')
    ax.set_title('Scored Goals by Season Evolution', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, linestyle='--', alpha=0.7)
    return ax,

# Function to animate for each frame
def animate(i):
    ax.clear()
    
    # Keep graph configuration
    ax.set_xlabel('Season', fontsize=12, fontweight='bold')
    ax.set_ylabel('Scored Goals', fontsize=12, fontweight='bold')
    ax.set_title('Scored Goals by Season Evolution', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, linestyle='--', alpha=0.7)
    

    # Calculate the final statistics
    total_goals = goals.sum()
    mean_goals = goals.mean()
    max_goals = goals.max()
    season_max = seasons[goals.argmax()]

    # Update texts
    year_text.set_text('Stats')
    goals_text.set_text(f'Total: {total_goals:.0f} goals \nMean: {mean_goals:.1f} goals/season\nMax: {max_goals} goals ({season_max})')

    # Define limits based on current frame
    if i < len(years):
        # Year by year
        current_year = years[i]
        current_goals = goals[i]
        current_season = seasons[i]
        
        ax.set_xlim(years[0] - 1, years[-1] + 1)
        ax.set_ylim(0, goals.max() * 1.1)
        
        # Plot data until the current year
        ax.plot(years[:i+1], goals[:i+1], 'o-', color='#2E86AB', linewidth=3, markersize=8, markerfacecolor='#A23B72')
        
        # Highlight the current point
        ax.plot(current_year, current_goals, 'o', markersize=12, markerfacecolor='#F18F01', markeredgecolor='black', markeredgewidth=1.5)
        
        # Add value to the current point
        ax.annotate(f'{current_goals}', 
                   xy=(current_year, current_goals), 
                   xytext=(0, 15), 
                   textcoords='offset points', 
                   ha='center', 
                   fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
                   arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"))
        
        # Update season text
        year_text.set_text(f'Season: {current_season}')
        goals_text.set_text(f'Goals: {current_goals}')
        
    elif i < len(years) + 10:
        # Zoom out to show the complete graph
        progress = (i - len(years) + 1) / 10.0
        
        # Plot all data
        ax.plot(years, goals, 'o-', color='#2E86AB', linewidth=3, markersize=8, markerfacecolor='#A23B72')
        
        '''
        # Update texts
        year_text.set_text('Stats')
        goals_text.set_text(f'Total: {total_goals:.0f} goals \nMean: {mean_goals:.1f} goals/season\nMax: {max_goals} goals ({season_max})')
        '''
        
    else:
        # Show the complete graph
        ax.plot(years, goals, 'o-', color='#2E86AB', linewidth=3, markersize=8, markerfacecolor='#A23B72')
        
        '''
        # Update texts
        year_text.set_text('Stats')
        goals_text.set_text(f'Total: {total_goals:.0f} goals \nMean: {mean_goals:.1f} goals/season\nMax: {max_goals} goals ({season_max})')
        '''
        
        # Add mean line
        ax.axhline(y=mean_goals, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_goals:.1f} goals')
        ax.legend(loc='upper left')
    
    # Add text boxes in every frame
    ax.add_artist(year_text)
    ax.add_artist(goals_text)
    
    return ax,

# Create animation
ani = FuncAnimation(fig, animate, frames=len(years)+20, init_func=init, 
                    interval=1000, blit=False, repeat=False)

# Add information subtitles
info_text = f"Animation showing goals scored by season evolution \nData from {seasons[0]} to {seasons[-1]} | Total {len(seasons)} seasons"
fig.text(0.5, 0.01, info_text, ha='center', fontsize=10, style='italic', bbox=dict(facecolor='lightgray', alpha=0.5))

plt.tight_layout()
plt.subplots_adjust(bottom=0.1)
plt.show()

# Saving the animation with GIF file
# from matplotlib.animation import PillowWriter
ani.save('evolution_goals_by_season.gif', writer=PillowWriter(fps=1))

# Configure to save a MP4 file
#writer = FFMpegWriter(fps=1, metadata=dict(artist='Me'), bitrate=1800)
#ani.save('evolution_goals_by_season.mp4', writer=writer)