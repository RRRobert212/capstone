import matplotlib.pyplot as plt
import mpld3

def plot_bar_chart(players, data, title, xlabel, ylabel):
    player_names = list(players.values())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(player_names, values, color='g')
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticklabels(player_names, rotation=45, ha='right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Convert the plot to an interactive HTML string using mpld3
    return mpld3.fig_to_html(fig)
