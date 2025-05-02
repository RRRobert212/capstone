#matrix.py
#uses data collected from stats.py to assemble a matrix on which we can perform data analysis / prediction

import pandas as pd
from poker_analysis import stats
from poker_analysis import parser

pd.set_option('display.max_columns', None)

# (Optional) Also show all rows
pd.set_option('display.max_rows', None)


def constructMatrix(filepath):

    #----------------------------------------------#
    #load the log
    df = parser.load_log(filepath)
    myDict = parser.create_player_dict(df)


    #----------------------------------------------#
    #constructing dictionaries from stats functions

    #action counts
    totalCalls = stats.get_action_counts(df, "calls", myDict)
    totalFolds = stats.get_action_counts(df, 'folds', myDict, min_words=3)
    totalRaises = stats.get_action_counts(df, 'raises', myDict)
    totalBets = stats.get_action_counts(df, 'bets', myDict)

    #preflop actions
    preflopRaises = stats.get_preflop_actions(df, myDict, 'raises')
    preflopCalls = stats.get_preflop_actions(df, myDict, 'calls')
    preflopFolds = stats.get_preflop_actions(df, myDict, 'folds')

    #critical stats
    vpip = stats.calc_VPIP(df, myDict)
    pfr = stats.calc_PFR(df, myDict)
    agressionFactor = stats.calc_aggression_factor(totalBets, totalRaises, totalCalls, myDict)

    #number of hands played
    hands = stats.track_player_presence(df, myDict)

    #other stats
    numberOfShows = stats.count_shows(df, myDict)
    numberOfStands = stats.count_stands(df, myDict)

    #----------------------------------------------#
    #Profit/Loss calculations, structure of the log makes this complicated
    #key stats are netProfit and profitYesOrNo

    #profitstats
    takenProfit = stats.get_quit_or_stand_stacks_all(df, myDict)
    remainingProfit = stats.get_final_player_stacks(df, myDict)
    extraProfit = stats.get_quit_or_stand_stacks_after_final(df, myDict)
    grossProfit = stats.calculate_gross_profits(myDict, takenProfit, remainingProfit, extraProfit)

    #buyin stats
    joinedBuyIn = stats.get_joined_buy_ins(df, myDict)
    adminUpdatedBuyIn = stats.get_admin_updates_after_game_start(df, myDict)
    trueBuyIn = stats.calculate_final_buyin(myDict, joinedBuyIn, adminUpdatedBuyIn)

    #results
    netProfit = stats.calculate_net_profit(myDict, grossProfit, trueBuyIn)

    #----------------------------------------------#
    #constructing matrices from dicts
    #exactly the same except one has net profit as last column and one indicates whether or not a player profited in last column
    allDictsProfitAmount = [
        ("Total Calls", totalCalls),
        ("Total Folds", totalFolds),
        ("Total Raises", totalRaises),
        ("Total Bets", totalBets),
        ("Total Hands", hands),
        ("Preflop Calls", preflopCalls),
        ("Preflop Raises", preflopRaises),
        ("Preflop Folds", preflopFolds),
        ("VPIP", vpip),
        ("PFR", pfr),
        ("Agression Factor", agressionFactor),
        ("Number of Shows", numberOfShows),
        ("Number of Stands", numberOfStands),
        ("Net Profit", netProfit)
    ]


    
    matrixAmount = pd.DataFrame()
    for name, stat_dict in allDictsProfitAmount:
        stat_series = pd.Series(stat_dict, name = name)
        matrixAmount = pd.concat([matrixAmount, stat_series], axis = 1)

    matrixAmount = matrixAmount.fillna(0)

    return matrixAmount

