from flask import Flask, render_template, request
import pandas as pd
import os
from poker_analysis import parser, stats, plots

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    charts_html = []

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".csv"):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            df = parser.load_log(filepath)
            player_dict = parser.create_player_dict(df)

            #player presence, number of hands
            hands = stats.track_player_presence(df, player_dict)
            print("Hands: ", hands)
            callcount = stats.track_all_preflop_actions(df, player_dict, 'calls')
            raisecount = stats.track_all_preflop_actions(df, player_dict, 'raises')
            vpip = stats.calc_VPIP(df, player_dict)
            print("CALL COUNTS: ", callcount)
            print("RAISECOUNT: ",raisecount)
            print("VPIP: ", vpip)

            # Collect stats for calls, raises, bets, and aggression factor
            calls = stats.get_action_counts(df, 'calls', player_dict)
            raises = stats.get_action_counts(df, 'raises', player_dict)
            bets = stats.get_action_counts(df, 'bets', player_dict)
            folds = stats.get_action_counts(df, 'folds', player_dict, 3)

            aggression = stats.calc_aggression_factor(bets, raises, calls)

            # Generate interactive charts for each stat
            charts_html.append(plots.plot_bar_chart(player_dict, aggression, "Aggression Factor", "Player", "AF"))
            charts_html.append(plots.plot_bar_chart(player_dict, calls, "Calls", "Player", "Number of Calls"))
            charts_html.append(plots.plot_bar_chart(player_dict, raises, "Raises", "Player", "Number of Raises"))
            charts_html.append(plots.plot_bar_chart(player_dict, bets, "Bets", "Player", "Number of Bets"))
            charts_html.append(plots.plot_bar_chart(player_dict, folds, "Folds", "Player", "Number of Folds"))

    return render_template("index.html", charts=charts_html)

if __name__ == "__main__":
    app.run(debug=True)
