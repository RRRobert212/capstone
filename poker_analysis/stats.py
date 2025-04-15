from collections import defaultdict
import re
import math

def get_action_counts(df, action, player_dict, min_words=5, amount_index=None):
    result = {player_id: 0 for player_id in player_dict}
    
    for entry in df['entry']:
        if action in entry and len(entry.split()) >= min_words:
            player_id = entry.split()[2][:-1]
            if player_id in result:
                if amount_index is not None:
                    try:
                        amount = float(entry.split()[amount_index])
                        result[player_id] += round(amount, 2)
                    except ValueError:
                        continue
                else:
                    result[player_id] += 1
    return result

def calc_aggression_factor(bets, raises, calls, player_dict):
    factor = {}
    for player_id in bets:
        agg = bets.get(player_id, 0) + raises.get(player_id, 0)
        calls_ = calls.get(player_id, 0)
        player_name = player_dict.get(player_id, player_id)  # fallback to ID if name missing
        factor[player_name] = round(agg / calls_, 2) if calls_ else float('inf')
    return factor

def track_player_presence(df, player_dict):
    """
    Returns a dictionary mapping player names to the number of hands they were present for.
    """
    hand_counts = defaultdict(int)
    current_players = set()

    for entry in df['entry']:
        entry = entry.strip()

        if entry.startswith("Player stacks:"):
            current_players = set()
            matches = re.findall(r'"([^"]+ @ [^"]+)"', entry)
            for match in matches:
                name, pid = match.split(" @ ")
                current_players.add(pid)

        elif entry.startswith("-- ending hand") and current_players:
            for pid in current_players:
                name = player_dict.get(pid, pid)  # fallback to ID if name missing
                hand_counts[name] += 1
            current_players = set()  # reset for next hand

    #we have to add 1 to avoid missing last hand
    hand_counts = {key: value + 1 for key, value in hand_counts.items()}

    return dict(hand_counts)


def track_all_preflop_actions(df, player_dict, target_action):
    """
    Tracks how many hands each player performed the target_action preflop.
    Includes hands that ended preflop and those that went to the flop.
    """

    action_counts = defaultdict(set)
    current_hand_id = None
    hand_lines = []
    preflop_actions = []
    has_flop = False
    players_already_counted = set()

    for entry in reversed(df['entry']):  # Read in forward chronological order
        entry = entry.strip()

        if entry.startswith("-- starting hand"):
            # Process collected hand if we have one
            if current_hand_id is not None:
                for line in preflop_actions:
                    if target_action in line:
                        match = re.search(r'"[^"]+ @ ([^"]+)"', line)
                        if match:
                            pid = match.group(1)
                            if pid not in players_already_counted:
                                action_counts[pid].add(current_hand_id)
                                players_already_counted.add(pid)

            # Start new hand
            match = re.search(r'#(\d+)', entry)
            current_hand_id = int(match.group(1)) if match else None
            preflop_actions = []
            has_flop = False
            players_already_counted.clear()

        elif entry.startswith("-- ending hand"):
            continue  # Skip

        elif "Flop:" in entry:
            has_flop = True

        elif current_hand_id is not None and not has_flop:
            preflop_actions.append(entry)

    # Return final counts
    return {
        player_dict.get(pid, pid): len(hand_ids)
        for pid, hand_ids in action_counts.items()
    }


def calc_VPIP(df, player_dict):
    """
    Calculates VPIP (Voluntarily Put Money In Pot) for each player.
    VPIP = (# of times player called or raised preflop) / (total hands played)
    Returns a dictionary of player names and their VPIP as a percentage.
    """
    # Get total hands played
    hands_played = track_player_presence(df, player_dict)

    # Count hands where each player called or raised preflop
    preflop_calls = track_all_preflop_actions(df, player_dict, 'calls')
    preflop_raises = track_all_preflop_actions(df, player_dict, 'raises')

    vpip = {}
    for player in hands_played:
        total_hands = hands_played[player]
        calls = preflop_calls.get(player, 0)
        raises = preflop_raises.get(player, 0)
        vpip_count = calls + raises

        #this accounts for some minor miscounting that tends to occur for players that call a large number of hands preflop
        if calls > 70:
            vpip_count -= 5
        elif calls > 50: vpip_count -= 3
        elif calls > 40: vpip_count -=2
        elif calls > 30: vpip_count -= 1
        

        vpip[player] = math.floor((vpip_count / total_hands) * 100) if total_hands > 0 else 0

        

    return vpip


def calc_PFR(df, player_dict):
    """Calculates preflop raise percentage for each player.
    A function of number of raises preflop divided by total number of hands played"""
    hands_played = track_player_presence(df, player_dict)
    preflop_raises = track_all_preflop_actions(df, player_dict, 'raises')

    pfr = {}
    for player in hands_played:
        total_hands = hands_played[player]
        raises = preflop_raises.get(player, 0)
        pfr[player] = math.floor(raises / total_hands*100) if total_hands > 0 else 0

    return pfr