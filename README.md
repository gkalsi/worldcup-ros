# World Cup - Round of 16

Visualize possible outcomes of the group stage at the World cup to decide who qualifies for the round of 16.

Previously this repsository was called `russia-2018` but has since
been generalized for the Qatar 2022 world cup.

## Input Files
All input data is stored as JSON data in the `data` directory.
Each subdirectory contains 2 files:
 + `groups.json` which lists the groups in the group stage
 + `matches.json` which lists all the matches that are either yet to be played or have been played.

A match that has not been played should have both teams' score listed as -1.

## Usage
```
python3 ./outcomes.py     # Runs with default arguments

python3 ./outcomes.py -h  # Help with options 
```

This will output a table as follows:
```
GROUP A
Matches:
	SAU vs. EGY
	URY vs. RUS
Possible Outcomes:
           EGY (0)     	           RUS (6)     	           SAU (3)     	           URY (9)     
           EGY (0)     	           RUS (9)     	           SAU (3)     	           URY (6)     
           EGY (0)     	           RUS (7)     	           SAU (3)     	           URY (7)
...
```
for each of the groups.

Matches denotes matches that are still yet to be played and Possible Outcomes lists which teams will advance given every possible match outcome.

Teams highlighted in green advance to the round of 16 in a given scenario. Teams highlighted in purple will be decided by goal difference. Teams in white will not advance.

The number in parentheses denotes the number of points each team has accumulated in a given scenario. If a team's advancement is decided by goal difference, the goal difference is also listed in parens next to the points. 

Passing `--fullnames` as an argument lists full country names instead of 3 letter country codes.

Passing `--winpath` as an argument will show the path of wins and losses required to realize each scenario.

passing `--group <LETTER>` will only print results for a particular group.
