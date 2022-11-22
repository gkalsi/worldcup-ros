"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import codes
import json
import sys
import os.path
from operator import itemgetter

import pprint

MAX_POINTS = 9
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHT_PURPLE = '\033[94m'
PURPLE = '\033[95m'
BOLD = '\033[1m'
END = '\033[0m'

ROOT_DATA_DIR='data'        # Data files are contained in `./data/<country-year>/...`
GROUPS_FILE='groups.json'
MATCHES_FILE='matches.json'

def check_input_files(matches, groups):
    # Make sure no country appears more than once in the groups file.
    group_set = set()
    for members in groups.values():
        for member in members:
            if member in group_set:
                print("%s appears more than once in group file" % (member),
                      file=sys.stderr)
                return False
            group_set.add(member)
    
    # Make sure that every match is played by somebody who belogns to a group.
    for match in matches:
        for team in match.keys():
            if team not in group_set:
                print("%s plays a match but does not belong to a group" % team,
                      file=sys.stderr)
                return False
        if len(match) != 2:
            print("Only two teams may participate in a match", file=sys.stderr)
            return False

        team1, team2 = match.keys()
        score1, score2 = match[team1], match[team2]

        if score1 == -1 or score2 == -1:
            if score1 != score2:
                print("%s and %s only one team has a recorded score?" % (team1, team2),
                      file=sys.stderr)
                return False

        # Make sure that teams only play against other teams in their own groups
        for group in groups.values():
            if (team1 in group) != (team2 in group):
                print("%s and %s play against each other but aren't in the same group?"
                      % (team1, team2), file=sys.stderr)
                return False                    

    return True


def match_has_been_played(match):
    score1, score2 = match.values()
    if score1 == -1 or score2 == -1:
        if score1 == score2:
            return False
        else:
            raise("Malformed match")
    return True


def generate_participants(groups):
    participants = []
    for members in groups.values():
        for member in members:
            participants.append(member)
    return participants
            

def compute_points(matches, participants):
    points = dict.fromkeys(participants, 0)
    for match in matches:
        if not match_has_been_played(match):
            continue

        team1, team2 = match.keys()
        score1, score2 = match[team1], match[team2]

        if score1 > score2:
            points[team1] += 3
        elif score2 > score1:
            points[team2] += 3
        else:
            points[team1] += 1
            points[team2] += 1
    return points
 

def compute_goal_differences(matches, participants):
    goal_differences = dict.fromkeys(participants, 0)

    for match in matches:
        if not match_has_been_played(match):
            continue

        team1, team2 = match.keys()
        score1, score2 = match[team1], match[team2]

        goal_differences[team1] += (score1 - score2)
        goal_differences[team2] += (score2 - score1)

    return goal_differences


def find_cut(ordered_standings, start):
    for i in range(start, len(ordered_standings) - 1):
        if ordered_standings[i][1] > ordered_standings[i+1][1]:
            return i + 1
    return len(ordered_standings)


def print_results(group_standings, goal_differences, winpath, args):
    ordered = []
    for team, score in group_standings.items():
        ordered.append((team, score))

    ordered.sort(key=itemgetter(1))
    ordered = ordered[::-1]

    alpha_ordered = list(ordered)
    alpha_ordered.sort(key=itemgetter(0))

    # Teams [0:fst_cut] are at the front of the group
    # Teams [fst_cut:snd_cut] are in second place
    fst_cut = find_cut(ordered, 0)
    snd_cut = find_cut(ordered, fst_cut)

    adv_thresh = MAX_POINTS + 1  # Advancement is certain
    gd_thresh = MAX_POINTS + 1   # Advancement decided by goal difference
    # If more than 2 teams are tied for first place, print them all in purple 
    # otherwise print all first place teams in green.
    if fst_cut > 2:
        adv_thresh = MAX_POINTS + 1
        if fst_cut < len(ordered):
            gd_thresh = ordered[fst_cut][1]
        else:
            gd_thresh = -1
    else:
        adv_thresh = ordered[fst_cut][1]

    if snd_cut == 2:
        adv_thresh = ordered[snd_cut][1]
    elif snd_cut > 2 and fst_cut == 1:
        if snd_cut < len(ordered):
            gd_thresh = ordered[snd_cut][1]
        else:
            gd_thresh = -1

    if args.winpath:
        print("\t%s" % ", ".join(winpath))

    for team, score in alpha_ordered:
        if args.fullnames:
            print_name = codes.Names[team]
        else:
            print_name = team

        if score > adv_thresh:
            print("\t%s%14s%s (%d)     " % (GREEN, print_name, END, score), end='')
        elif score > gd_thresh:
            print("\t%s%14s%s (%d, %2d) " % (PURPLE, print_name, END, score, goal_differences[team]), end='')
        else:
            print("\t%14s (%d)     " % (print_name, score), end='')
    print("")


def __generate_possible_outcomes_recursive(matches_remaining, match_idx, points, goal_differences, win_path, args):
    if len(matches_remaining) == match_idx:
        print_results(points, goal_differences, win_path, args)
        return

    match = matches_remaining[match_idx]
    team1, team2 = match.keys()

    if args.fullnames:
        print1, print2 = codes.Names[team1], codes.Names[team2]
    else:
        print1, print2 = team1, team2

    points[team1] += 3
    win_path.append("%s beats %s" % (print1, print2))
    __generate_possible_outcomes_recursive(matches_remaining, match_idx + 1, points, goal_differences, win_path, args)
    points[team1] -= 3
    win_path.pop()

    points[team2] += 3
    win_path.append("%s beats %s" % (print2, print1))
    __generate_possible_outcomes_recursive(matches_remaining, match_idx + 1, points, goal_differences, win_path, args)
    points[team2] -= 3
    win_path.pop()
    
    points[team1] += 1
    points[team2] += 1
    win_path.append("%s ties %s" % (print1, print2))
    __generate_possible_outcomes_recursive(matches_remaining, match_idx + 1, points, goal_differences, win_path, args)
    points[team1] -= 1
    points[team2] -= 1
    win_path.pop()    
    

def get_unplayed_group_matches(matches, groups, target_group):
    unplayed_group_matches = []
    members = groups[target_group]
    for match in matches:
        if match_has_been_played(match):
            continue
        team1, team2 = match.keys()
        if team1 in members:
            unplayed_group_matches.append(match)
    return unplayed_group_matches


def generate_possible_outcomes(matches, groups, points, target_group, goal_differences, args):
    possible_outcomes = []
    members = groups[target_group]
    group_points = dict.fromkeys(members, 0)
    for member in members:
        group_points[member] = points[member]

    group_matches_remaining = get_unplayed_group_matches(matches, groups, target_group)
    
    win_path = []
    __generate_possible_outcomes_recursive(group_matches_remaining, 0, group_points, goal_differences, win_path, args)
        
        
def main():
    parser = argparse.ArgumentParser(description='Print information about the world cup')

    parser.add_argument('--data', '-d', default='qatar-2022',
                        help='name of the subdirectory under ./data/ to consider')
    parser.add_argument('--fullnames', '-f', action='store_true',
                        help='print full country names instead of ISO country codes')
    # TODO(gkalsi): Implement nocolour
    parser.add_argument('--nocolour', '-c', action='store_true',
                        help='Do not colourize output, use text to convey semantics')
    parser.add_argument('--winpath', '-w', action='store_true',
                        help='Show the path taken to achieve each outcome')
    parser.add_argument('--group', '-G', help='json file containing group data')

    args = parser.parse_args()

    matches_path = os.path.join(ROOT_DATA_DIR, args.data, MATCHES_FILE)
    with open(matches_path, 'r') as matches_file:
        matches = json.load(matches_file)

    groups_path = os.path.join(ROOT_DATA_DIR, args.data, GROUPS_FILE)
    with open(groups_path, 'r') as groups_file:
        groups = json.load(groups_file)

    # Make sure that every match is played by a country in a group.
    # In other words, make sure the groups file and the matches files
    # are consistent.
    if not check_input_files(matches, groups):
        print("Input sanity check failed", file=sys.stderr)
        sys.exit(-1)

    participants = generate_participants(groups)

    points = compute_points(matches, participants)

    goal_differences = compute_goal_differences(matches, participants)

    target_groups = []
    if args.group:
        target_groups.append(str.upper(args.group))
    else:
        target_groups = sorted(groups.keys())


    for group in target_groups:
        print("\n%sGROUP %s%s" % (BOLD, group.upper(), END))
        print("Matches:")
        unplayed_matches = get_unplayed_group_matches(matches, groups, group)
        for match in unplayed_matches:
            team1, team2 = match.keys()
            if args.fullnames:
                team1 = codes.Names[team1]
                team2 = codes.Names[team2]
            print("\t%s vs. %s" % (team1, team2))

        print("Possible Outcomes:")
        generate_possible_outcomes(matches, groups, points, group, goal_differences, args)


if __name__ == "__main__":
    main()