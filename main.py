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

import sys
from operator import itemgetter

# Participants
RUSSIA = "Russia"
BELGIUM = "Belgium"
GERMANY = "Germany"
ENGLAND = "England"
SPAIN = "Spain"
POLAND = "Poland"
ICELAND = "Iceland"
SERBIA = "Serbia"
FRANCE = "France"
PORTUGAL = "Portugal"
SWITZERLAND = "Switzerland"
CROATIA = "Croatia"
SWEDEN = "Sweden"
DENMARK = "Denmark"
IRAN = "Iran"
SOUTH_KOREA = "South Korea"
JAPAN = "Japan"
SAUDI_ARABIA = "Saudi Arabia"
AUSTRALIA = "Australia"
NIGERIA = "Nigeria"
EGYPT = "Egypt"
SENEGAL = "Senegal"
TUNISIA = "Tunisia"
MOROCCO = "Morocco"
MEXICO = "Mexico"
COSTA_RICA = "Costa Rica"
PANAMA = "Panama"
BRAZIL = "Brazil"
URUGUAY = "Uruguay"
ARGENTINA = "Argentina"
COLOMBIA = "Colombia"
PERU = "Peru"

GROUP_A = "Group A"
GROUP_B = "Group B"
GROUP_C = "Group C"
GROUP_D = "Group D"
GROUP_E = "Group E"
GROUP_F = "Group F"
GROUP_G = "Group G"
GROUP_H = "Group H"

MAX_POINTS = 9

# Groups
GROUPS = {
    GROUP_A: {
        "Members": [RUSSIA, URUGUAY, SAUDI_ARABIA, EGYPT],
        "Standings": {RUSSIA: 6, URUGUAY: 6, SAUDI_ARABIA: 0, EGYPT: 0},
        "Matches": [
            (SAUDI_ARABIA, EGYPT),
            (URUGUAY, RUSSIA)
        ]
    },
    GROUP_B: {
        "Members": [SPAIN, PORTUGAL, IRAN, MOROCCO],
        "Standings": {SPAIN: 4, PORTUGAL: 4, IRAN: 3, MOROCCO: 0},
        "Matches": [
            (IRAN, PORTUGAL),
            (SPAIN, MOROCCO)
        ]
    },
    GROUP_C: {
        "Members": [FRANCE, DENMARK, AUSTRALIA, PERU],
        "Standings": {FRANCE: 6, DENMARK: 4, AUSTRALIA: 1, PERU: 0},
        "Matches": [
            (AUSTRALIA, PERU),
            (DENMARK, FRANCE)
        ]
    },
    GROUP_D: {
        "Members": [CROATIA, ARGENTINA, NIGERIA, ICELAND],
        "Standings": {CROATIA: 6, ARGENTINA: 1, NIGERIA: 3, ICELAND: 1},
        "Matches": [
            (NIGERIA, ARGENTINA),
            (ICELAND, CROATIA)
        ]
    },
    GROUP_E: {
        "Members": [SWITZERLAND, BRAZIL, SERBIA, COSTA_RICA],
        "Standings": {SWITZERLAND: 4, BRAZIL: 4, SERBIA: 3, COSTA_RICA: 0},
        "Matches": [
            (SWITZERLAND, COSTA_RICA),
            (SERBIA, BRAZIL)
        ]
    },
    GROUP_F: {
        "Members": [MEXICO, GERMANY, SWEDEN, SOUTH_KOREA],
        "Standings": {MEXICO: 3, GERMANY: 0, SWEDEN: 3, SOUTH_KOREA: 0},
        "Matches": [
            (SOUTH_KOREA, MEXICO),
            (GERMANY, SWEDEN),
            (MEXICO, SWEDEN),
            (SOUTH_KOREA, GERMANY)
        ]
    },
    GROUP_G: {
        "Members": [ENGLAND, BELGIUM, TUNISIA, PANAMA],
        "Standings": {ENGLAND: 3, BELGIUM: 3, TUNISIA: 0, PANAMA: 0},
        "Matches": [
            (BELGIUM, TUNISIA),
            (ENGLAND, PANAMA),
            (ENGLAND, BELGIUM),
            (PANAMA, TUNISIA)
        ]
    },
    GROUP_H: {
        "Members": [JAPAN, SENEGAL, COLOMBIA, POLAND],
        "Standings": {JAPAN: 3, SENEGAL: 3, COLOMBIA: 0, POLAND: 0},
        "Matches": [
            (JAPAN, SENEGAL),
            (POLAND, COLOMBIA),
            (SENEGAL, COLOMBIA),
            (JAPAN, POLAND)
        ]
    }
}

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHT_PURPLE = '\033[94m'
PURPLE = '\033[95m'
BOLD = '\033[1m'
END = '\033[0m'


def unplayed_matches_are_valid(unplayed_matches):
    teams = set()

    for match in unplayed_matches:
        # Each match has two participants
        if len(match) != 2:
            return False

        teams.add(match[0])
        teams.add(match[1])

    # There are at most 4 teams in a group
    return len(teams) <= 4


def group_standings_are_valid(group_standings):
    if len(group_standings) != 4:
        return False


def find_cut(ordered_standings, start):
    for i in range(start, len(ordered_standings) - 1):
        if ordered_standings[i][1] > ordered_standings[i+1][1]:
            return i + 1
    return len(ordered_standings)


def print_results(group_standings):
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
    # If more than 2 teams are tied for first place, print them all in yellow
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
    else:
        gd_thresh = MAX_POINTS + 1

    for team, score in alpha_ordered:
        if score > adv_thresh:
            print("%s%14s%s (%d) " % (GREEN, team, END, score), end='')
        elif score > gd_thresh:
            print("%s%14s%s (%d) " % (YELLOW, team, END, score), end='')
        else:
            print("%14s (%d) " % (team, score), end='')
    print("")


def compute_outcomes_recursive(group_standings, unplayed_matches):
    if len(unplayed_matches) == 0:
        # Ran all simulations, print the outcomes
        print_results(group_standings)
        return

    t1, t2 = unplayed_matches[0]

    # T1 wins
    group_standings[t1] += 3
    compute_outcomes_recursive(group_standings, unplayed_matches[1:])
    group_standings[t1] -= 3

    # T2 wins
    group_standings[t2] += 3
    compute_outcomes_recursive(group_standings, unplayed_matches[1:])
    group_standings[t2] -= 3

    # Both teams tie
    group_standings[t1] += 1
    group_standings[t2] += 1
    compute_outcomes_recursive(group_standings, unplayed_matches[1:])
    group_standings[t1] -= 1
    group_standings[t2] -= 1


def compute_outcomes(group_standings, unplayed_matches):
    if not unplayed_matches_are_valid(unplayed_matches):
        return False

    if not group_standings_are_valid(group_standings):
        return False

def main():
  for group in sorted(GROUPS.keys()):
      print("\n%s%s%s" % (BOLD, group.upper(), END))
      print("Games:")
      for match in GROUPS[group]["Matches"]:
        print("\t%s vs. %s" % (match[0], match[1]))
      print("Possible Outcomes:")
      compute_outcomes_recursive(
          GROUPS[group]["Standings"], GROUPS[group]["Matches"])


if __name__ == "__main__":
  main()