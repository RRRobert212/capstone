
import matplotlib.pyplot as plt
import io
import base64
import datetime
import matplotlib.dates as mdates
from datetime import datetime

def plot_bar_chart(players, data, title, xlabel, ylabel):
    player_names = list(players.values())
    values = list(data.values())

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(player_names, values, color='green')

    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=16)
    ax.set_xticks(range(len(player_names)))
    ax.set_xticklabels(player_names, rotation=45, ha='right', fontsize=12, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer to base64 and embed as HTML
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return f'<img src="data:image/png;base64,{encoded}" />'


def plot_vpip_vs_pfr(vpip, pfr, players):
    fig, ax = plt.subplots(figsize=(12, 8)) 


    ax.scatter(vpip.values(), pfr.values(), color='green')

    # Add player name labels
    for player in players:
        ax.text(vpip[player] + 1.5, pfr[player]+0.5, player,
                fontsize=14, fontweight='bold', ha='right')

    ax.set_xlabel("VPIP (%)", fontsize=16)
    ax.set_ylabel("PFR (%)", fontsize=16)
    ax.set_title("VPIP vs PFR", fontsize=18)
    ax.grid(True)

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer to base64 and embed as HTML
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)  # Close the plot to free memory

    return f'<img src="data:image/png;base64,{encoded}" />'


#yes this is like copy pasted, but it ends up being simpler
def plot_vpip_vs_af(vpip, af, players):
    fig, ax = plt.subplots(figsize=(12, 8))

    # Create x and y arrays with consistent ordering
    x_vals = []
    y_vals = []
    for player in vpip:
        if player in af:
            x_vals.append(vpip[player])
            y_vals.append(af[player])

    ax.scatter(x_vals, y_vals, color='green')

    # Add player name labels
    for player in vpip:
        if player in af:
            ax.text(vpip[player]+2, af[player]+0.05, player,
                    fontsize=14, fontweight='bold', ha='right')

    ax.set_xlabel("VPIP (%)", fontsize=16)
    ax.set_ylabel("Aggression Factor", fontsize=16)
    ax.set_title("VPIP vs Aggression Factor", fontsize=18)
    ax.grid(True)

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer to base64 and embed as HTML
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return f'<img src="data:image/png;base64,{encoded}" />'




def plot_player_stacks(player_stacks):
    """
    Plots the stack amounts of players over hands.
    """
    fig, ax = plt.subplots(figsize=(16, 9))

    for player, stack_data in player_stacks.items():

        times = []
        for entry in stack_data:
            timestamp = entry[0]
            if isinstance(timestamp, str):

                timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            times.append(timestamp)

        stacks = [entry[1] for entry in stack_data]
        
        ax.plot(times, stacks, label=player)

    # Format the x-axis to display time in HH:MM format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax.set_xlabel("Time", fontsize=16)
    ax.set_ylabel("Stack Size", fontsize=16)
    ax.set_title("Player Stacks Over Time", fontsize=18)
    ax.legend(loc='upper left')
    ax.grid(True)

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Convert buffer to base64 and embed as HTML
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)

    return f'<img src="data:image/png;base64,{encoded}" />'

