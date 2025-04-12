from collections import defaultdict
import re

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

def calc_aggression_factor(bets, raises, calls):
    factor = {}
    for player_id in bets:
        agg = bets[player_id] + raises[player_id]
        calls_ = calls[player_id]
        factor[player_id] = round(agg / calls_, 2) if calls_ else float('inf')
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

    return dict(hand_counts)

def track_preflop_action(df, player_dict, target_action):
    """
    Returns a dictionary of player names to the number of hands in which they performed the target_action preflop.
    A hand is only counted once per player, even if the player performs the action multiple times in that hand.
    """
    from collections import defaultdict
    import re
    
    action_counts = defaultdict(set)  # player_id -> set of hand_ids
    current_hand_id = None
    preflop_section = False  # Flag to track if we're in the preflop section
    players_already_counted = set()
    
    for entry in df['entry']:
        entry = entry.strip()
        
        # Detect end of a hand (which appears first in the log)
        if entry.startswith("-- ending hand"):
            match = re.search(r'#(\d+)', entry)
            if match:
                current_hand_id = int(match.group(1))
                players_already_counted.clear()
                preflop_section = False
        
        # Detect the flop (which marks the start of preflop section when reading in reverse)
        elif "Flop:" in entry and current_hand_id is not None:
            preflop_section = True
            
        # Detect start of a hand (which ends the preflop section when reading in reverse)
        elif entry.startswith("-- starting hand"):
            preflop_section = False
            current_hand_id = None
        
        # Process preflop actions
        elif preflop_section and current_hand_id is not None:
            if target_action in entry:
                # Extract player ID using regex
                match = re.search(r'"([^"]+ @ ([^"]+))"', entry)
                if match:
                    pid = match.group(2)  # Just get the ID part
                    if pid not in players_already_counted:
                        action_counts[pid].add(current_hand_id)
                        players_already_counted.add(pid)
    
    # Convert to counts and map to player names
    return {
        player_dict.get(pid, pid): len(hand_ids)
        for pid, hand_ids in action_counts.items()
    }



def track_preflop_calls(df, player_dict):
    return track_preflop_action(df, player_dict, 'calls')

def track_preflop_raises(df, player_dict):
    return track_preflop_action(df, player_dict, 'raises')


def track_preflop_action_no_flop(df, player_dict, target_action):
    """
    Tracks preflop actions in hands that end before the flop.
    Returns a dictionary of player names to the number of hands in which they performed the target_action preflop.
    """
    from collections import defaultdict
    import re

    action_counts = defaultdict(set)
    current_hand_id = None
    hand_lines = []
    hand_has_flop = False
    players_already_counted = set()

    for entry in df['entry']:
        entry = entry.strip()

        # Start of a new hand
        if entry.startswith("-- starting hand"):
            # Process the previous hand if it ended preflop (i.e., no flop)
            if not hand_has_flop and current_hand_id is not None:
                for line in hand_lines:
                    if target_action in line:
                        match = re.search(r'"([^"]+ @ ([^"]+))"', line)
                        if match:
                            pid = match.group(2)
                            if pid not in players_already_counted:
                                action_counts[pid].add(current_hand_id)
                                players_already_counted.add(pid)
            # Reset for the next hand
            match = re.search(r'#(\d+)', entry)
            current_hand_id = int(match.group(1)) if match else None
            hand_lines = []
            hand_has_flop = False
            players_already_counted.clear()

        # End of hand doesn't trigger anything directly (start triggers processing of last hand)

        elif "Flop:" in entry:
            hand_has_flop = True

        elif current_hand_id is not None:
            hand_lines.append(entry)

    return {
        player_dict.get(pid, pid): len(hand_ids)
        for pid, hand_ids in action_counts.items()
    }

def track_pfr_noflop(df, player_dict):
    return track_preflop_action_no_flop(df, player_dict, 'raises')
def track_calls_noflop(df, player_dict):
    return track_preflop_action_no_flop(df, player_dict, 'calls')



#yessss okay it's working, either add the merged function or just combine the functions to avoid copy-paste.
#RAISES ARE CORRECT
#BUT CALLS ARE BEING SLIGHTLY OVERCOUNTED!! WHY???