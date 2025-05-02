from flask import Flask, render_template, request, send_from_directory
import os
from poker_analysis import parser, stats, plots
import datetime
import json
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash, generate_password_hash
from poker_analysis import matrix
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MATRIX_FOLDER'] = 'matrices'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MATRIX_FOLDER'], exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    charts_html = []
    matrix_file = None

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".csv"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            log_path = os.path.join(app.config['UPLOAD_FOLDER'], "upload_log.json")

            # Load existing log
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    upload_log = json.load(f)
            else:
                upload_log = []

            # Append new log entry
            upload_log.append({
                "filename": filename,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            # Save log
            with open(log_path, "w") as f:
                json.dump(upload_log, f, indent=4)

            df = parser.load_log(filepath)
            player_dict = parser.create_player_dict(df)

            #player presence, number of hands
            hands = stats.track_player_presence(df, player_dict)
            callcount = stats.get_preflop_actions(df, player_dict, 'calls')
            raisecount = stats.get_preflop_actions(df, player_dict, 'raises')
            vpip = stats.calc_VPIP(df, player_dict)
            pfr = stats.calc_PFR(df, player_dict)

            calls = stats.get_action_counts(df, 'calls', player_dict)
            raises = stats.get_action_counts(df, 'raises', player_dict)
            bets = stats.get_action_counts(df, 'bets', player_dict)
            folds = stats.get_action_counts(df, 'folds', player_dict, 3)

            af = stats.calc_aggression_factor(bets, raises, calls, player_dict)
            player_stacks = stats.track_player_stacks(df, player_dict)

            players = list(vpip.keys())
            charts_html.append(plots.plot_bar_chart(player_dict, af, "Aggression Factor", "Player", "AF"))
            charts_html.append(plots.plot_bar_chart(player_dict, calls, "Calls", "Player", "Number of Calls"))
            charts_html.append(plots.plot_bar_chart(player_dict, raises, "Raises", "Player", "Number of Raises"))
            charts_html.append(plots.plot_bar_chart(player_dict, bets, "Bets", "Player", "Number of Bets"))
            charts_html.append(plots.plot_bar_chart(player_dict, folds, "Folds", "Player", "Number of Folds"))
            charts_html.append(plots.plot_vpip_vs_pfr(vpip, pfr, players))
            charts_html.append(plots.plot_vpip_vs_af(vpip, af, players))
            charts_html.append(plots.plot_player_stacks(player_stacks))

            # Generate and save matrix
            matrix_df = matrix.constructMatrix(filepath)
            matrix_file = f"matrix_{filename}"
            matrix_path = os.path.join(app.config['MATRIX_FOLDER'], matrix_file)
            matrix_df.to_csv(matrix_path)

    return render_template("index.html", charts=charts_html, matrix_file=matrix_file)

# Route to download the matrix CSV
@app.route("/matrices/<filename>")
def download_matrix(filename):
    return send_from_directory(os.path.abspath(app.config['MATRIX_FOLDER']), filename, as_attachment=True)


# Authorization -- very simple, used to lock admin page
auth = HTTPBasicAuth()

users = {
    "admin": generate_password_hash("password")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

@app.route("/admin")
@auth.login_required
def admin():
    log_path = os.path.join(app.config['UPLOAD_FOLDER'], "upload_log.json")
    uploads = []
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            uploads = json.load(f)
    return render_template("admin.html", uploads=uploads)

if __name__ == "__main__":
    app.run(debug=True)
