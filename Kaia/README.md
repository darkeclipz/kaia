# Kaia Custom AI (AoE2)

Kaia is a custom AOE2 bot that should close the difficulty gap a bit vs. the default AI. The default AI tends to be really boring on lower settings and quickly ramps up and becomes overwhelming. Kaia aims to be fun opponent to play against, while also keeping the game chill to play!

## Todo
 * Research missing tech.
 * ~~Research unit upgrades only when there are a mininum number of units of it (e.g. 8).~~
 * Research last tech at university.
 * Build bombardment towers.
 * Test good attack group combo for different difficulties.
 * ~~Build watch towers towards the enemy, instead of a random position around the town.~~
 * Find and protect relics in the case it is not possible to send a monk before the enemy team does. Basically if they reach the castle age and a relic has been located, send a scout cavalry to that position. Scout cavalry is quick enough to kill the monk before they are being converted.
 * ~~FIX: Scout doesn't explore the enemy town, so TSA doesn't work.~~
 * ~~FIX: Camp size for trees is not updated dynamically, so it gets stuck making a lumber camp.~~
 * Identify enemy forces. Move the scout to the enemy at some point to see which units they are making as a first attack. We can train counter units in that case. Depending on that we need to either build an archery range or stables. Specifically, we need to know if they build a barrack, archery range or stable in the feudal age.
 * Use scouts to harass the enemy at the start of a game at the 8th minute (berry time). Stand in range of the TC and attack a villager to have them garrison in the TC. Then run away so they come out again. Repeat this until the scout is dead. Run away if we are being attacked. 
 * ~~Update `g-XXX-resources` to only include gold and stone that is reachable within half of the map size. This is to prevent "suicide building missions" to build a mining camp next to the enemy base.~~
 * Build a siege workshop in the center of the map once we start attacking, if it is training any siege units.
 * ~~Place a lumber camp next to the last lumber camp that has been placed. This is to ensure that we minimize the distance that the villagers have to walk.~~
 * Retreat units if they are in range of an enemy castle.
 * Retreat units that have low HP.
 * If we are not attacking, don't allow units to go outside of `sn-maximum-town-size`.
 * Retreat based on how many enemies we see instead of a fixed time interval.
 * Stay near castle and towers if we are defending.
 * Stay away from castles and towers if we are attacking.
 * Use a priority system for building, training units, and research.

## Findings

1. `resource-found` doesn't trigger for gold if the gold mine is further away then the `sn-mining-camp-max-distance` in the dark age. Once the feudal age is reached, the distance increases and it is detected. You would expect `resource-found` to return `true` once a scout has found the gold, but that is not the case.
2. `up-get-fact military-population any-enemy g-x` doesn't work, because it only counts the population for the current player. There is no `up-` variant available that counts enemy units this way. Use `up-find-remote` and keep track of the enemy units that way.
3. Farms don't get up and running if `sn-maximum-food-drop-distance` is too small.
4. Research loom before hunting boars (if applicable).
5. Playing a normal game with low resources needs like 6 barracks, archery ranges, or stables to be able to quickly produce unit. With only 3 of them the resources stack up because they don't train fast enough. Perhaps even build 9 of them in late imperial?

## Game parameters

Note that the game should be started with the following parameters: 

```
SKIPINTRO DEBUGSPEEDS AIDEBUGGING LOGSYSTEMS=AIScript VERBOSELOGGING AISCRIPTPROFILING CONSTANTLOGGING
```

 * Use `+` and `-` to change the game speed, or whatever hotkeys have been set up.
 * Set a breakpoint with `(fe-break-point 1 == 1 -1)`.

## Logs

Logs produced by the game can be found here (Linux): 

```
~/.steam/debian-installation/steamapps/compatdata/813780/pfx/drive_c/users/steamuser/Games/Age of Empires 2 DE/logs`
```

## Resources
 
 * **Scripting encyclopedia:** https://airef.github.io/index.html
 * **AI Scripters forum:** https://forums.aiscripters.com/viewforum.php?f=8
 * **AOECompanion:** https://aoecompanion.com/
 * **AI Scripting Steam Tutorial:** https://steamcommunity.com/sharedfiles/filedetails/?id=1238296169
 * **Three ways to get AI to attack:** https://forums.ageofempires.com/t/three-ways-to-get-the-ai-to-attack/205476
 * **Discussion about attack groups:** https://aok.heavengames.com/cgi-bin/forums/display.cgi?action=st&fn=28&tn=39123
 * **TSA:** https://aok.heavengames.com/university/other/town-size-attack/
 * **Difficulty parameters (hard-coded AI limits based on difficulty):** https://airef.github.io/commands/commands-details.html#difficulty
   * Specifically the time it takes to train a villager on easy is 33 seconds vs. only 25 seconds when the difficulty is set to extreme.
 * **Object data:** https://airef.github.io/parameters/parameters-details.html#ObjectData

## UP commands

 * Send units to a specific point: https://airef.github.io/commands/commands-details.html#up-target-point
 * Find a resource on the map: https://airef.github.io/commands/commands-details.html#up-find-resource
 * Filter on distance within target point: https://airef.github.io/commands/commands-details.html#up-filter-distance
 * Object data: https://airef.github.io/parameters/parameters-details.html#ObjectData
 * Find enemy units: https://airef.github.io/commands/commands-details.html#up-find-remote
 * Attack units with local vs remote: https://airef.github.io/commands/commands-details.html#up-target-objects
 * Set target object from search result: https://airef.github.io/commands/commands-details.html#up-set-target-object
 * Only select units within 10 tiles from target point: https://airef.github.io/commands/commands-details.html#up-filter-distance


## Boar hunting

A list of useful strategic numbers used for boar hunting:

 * https://airef.github.io/strategic-numbers/sn-details.html#sn-boar-lure-destination
 * https://airef.github.io/strategic-numbers/sn-details.html#sn-enable-boar-hunting
 * https://airef.github.io/strategic-numbers/sn-details.html#sn-minimum-number-hunters
 * https://airef.github.io/strategic-numbers/sn-details.html#sn-minimum-boar-hunt-group-size
 * https://airef.github.io/strategic-numbers/sn-details.html#sn-minimum-boar-lure-group-size
 * https://airef.github.io/strategic-numbers/sn-details.html#sn-maximum-hunt-drop-distance

## Villager task scheduling system

We need a system that assigns tasks to villagers based on how many villagers we have instead of setting resource percentages.
This is currently being handled by setting resource percentages, which works for the time being. This means that this system doesn't have a really high priority for now.

### Task plan

```
1   SHEEP
2   SHEEP
3   SHEEP
4   SHEEP
5   SHEEP 
6   SHEEP
7   WOOD
8   WOOD
...
```

## Building priority system

We need a system that makes it possible to execute various build orders dynamically. To do so, the concept of a _building priority score_ is introduced:

 * There is a `g-current-priority-score` goal that represents the current priority score that we are at.
 * A building is constructed once a certain priority score has been reached.
 * Every villager increases the priority score by 1.
 * The priority score is also increased for each stage of research we are in. Each stage gives 500 points, so a large population (>= 100) can't practically overflow it into the next stage (unless you train 500 villagers...).
 * Only the early houses are included, at some point the houses are constructed once there is not enough headroom left. 
 * The building priority can get a maximum value of 5000 once the post-imperial age is reached with a population of 500.
 * Note to only include villagers into the score!

|Stage|Points|
|---|---|
|Dark age|0|
|Feudal pending|500|
|Feudal age|1000|
|Castle pending|1500|
|Castle age|2000|
|Imperial pending|2500|
|Imperial age|3000|
|Imperial age (post)|3500|

### Build plan

This is an example of a build plan.

```
3       HOUSE
3       HOUSE
10      LUMBERCAMP
13      HOUSE
13      MILL
18      HOUSE
22      MINING-CAMP-GOLD
518     FARM
518     FARM
518     FARM
518     FARM
518     FARM
518     FARM
1000    AUTO-HOUSE
1000    AUTO-FARM
1000    BLACKSMITH
1000    MARKET
1500    FARM
1500    FARM
1500    FARM
1500    FARM
2000    TOWN-CENTER
2000    TOWN-CENTER
2565    TOWN-CENTER
```

Since there is no way to index a goal dynamically, we will use a different approach.

First we define a bunch of house goals. We don't need hundreds of them, because the build order is only used for the first 30 villagers or so. After that the default AI takes over.

```
g-build-house0 = 3
g-build-house1 = 3
g-build-house2 = 13
g-build-house3 = 13
g-build-house4 = 9999
g-build-house5 = 9999
g-build-house6 = 9999
g-build-house7 = 9999
g-build-house8 = 9999
g-build-house9 = 9999
g-auto-housing = 1000
```

Testing to see if we need to build a house could look something like this:

```
(defrule
(or (up-compare-goal g-current-building-priority g:>= g-build-house0)
(or (up-compare-goal g-current-building-priority g:>= g-build-house1)
(or (up-compare-goal g-current-building-priority g:>= g-build-house2)
(or (up-compare-goal g-current-building-priority g:>= g-build-house3)
(or (up-compare-goal g-current-building-priority g:>= g-build-house4)
(or (up-compare-goal g-current-building-priority g:>= g-build-house5)
(or (up-compare-goal g-current-building-priority g:>= g-build-house6)
(or (up-compare-goal g-current-building-priority g:>= g-build-house7)
    (up-compare-goal g-current-building-priority g:>= g-build-house8))))))))))
    (can-build house)
    (up-pending-objects c: house c:== 0)
    =>
    (build house)
)
```

## Technology priority system

This is pretty similar to the building priority system. There is a goal `g-current-technology-priority` to indicate where we are at. The age research still gives `+500` priority, same as with the buildings.

~~However, instead of using villagers, we will use the number of technologies researched. This gives us an order in which we can research technologies.~~

### Research plan

```
23      FEUDAL-AGE
1025    LOOM
1025    CASTLE-AGE
1500    DOUBLE-BIT-AXE
2025    BOW-SAW
2025    GOLD-MINING
3000    CAVALIER
3000    PALADIN
```

Hmmm, we do want to be able to start researching a technology once a certian civilian population size has been reached. But we also want to be able to define prerequisite technologies...

* We want to order the technologies based on which one goes first.
* We want to "block" researching a technology based on how many civilians we have or in which age we are.

This leads to the following design:

 * Each technology has an order goal `g-research-order-dark-age`, `...`.
 * Each technology has a priority goal `g-research-priority-dark-age`, `...`.
 * Starting research increases the order goal by 1.
 * The priority goal is the same as the building priority system: `priority = age-status + civ. pop`.
 * Any technology that doesn't depend on the number of villagers has a priority of 0.
 * A technology can be forced to be researched by settings its priority to `g-current-priority-score`.

## Enemy unit estimation

Estimate enemy forces so we can train counter units and attack/retreat more aggressively instead of relying on a timer.


### Data limits

The AI scripting engine of AOE2 DE has the following data limitations:

 * Rules: 10,000
 * Elements per rule: 16 in UP, 32 in DE
 * Goals: 1 to 16,000
 * Strategic Numbers: 0 to 511
 * Timers: 1 to 50
 * Defconst values: -32768 to 32767 or a text string
 * Goal and SN values: -2,147,483,648 to 2,147,483,647
 * Flag values: powers of 2 from 1 to 2,147,483,648
 * DUC Local Search list length: 240
 * DUC Remote Search list length: 40
 * Taunts: 255
 * Characters per line: 255
 * Nested File Load Commands: 10 files deep
 * Nested #load-if Commands: 50 (might be lower, somewhere in the 30s)
 * Doctrine: 1
