# Kaia Custom AI (AoE2)

Kaia is a custom AOE2 bot that should close the difficulty gap a bit vs. the default AI. The default AI tends to be really boring on lower settings and quickly ramps up and becomes overwhelming. Kaia aims to be fun opponent to play against, while also keeping the game chill to play!

## Resources
 
 * **Scripting encyclopedia:** https://airef.github.io/index.html
 * **AI Scripters forum:** https://forums.aiscripters.com/viewforum.php?f=8
 * **AOECompanion:** https://aoecompanion.com/
 * **AI Scripting Steam Tutorial:** https://steamcommunity.com/sharedfiles/filedetails/?id=1238296169
 * **Three ways to get AI to attack:** https://forums.ageofempires.com/t/three-ways-to-get-the-ai-to-attack/205476
 * **Discussion about attack groups:** https://aok.heavengames.com/cgi-bin/forums/display.cgi?action=st&fn=28&tn=39123

## TODO
 * Research missing tech
 * Research unit upgrades only when there is a unit
 * Research last tech at university
 * Build bombardment towers
 * Test good attack group combo for different difficulties
 * Add light cavalry and exploring with 2 or even 3 cavals, instead of the current fixed 1
 * Add flags for building and military lines, e.g. `g-build-barracks`, `g-build-archery-range`, `g-build-stable`, `g-build-siege-workshop`.

## Notes about strategic numbers

### Attack behaviour

#### (10, 25, 50)

```
(set-strategic-number sn-number-attack-groups 10)
(set-strategic-number sn-minimum-attack-group-size 28)
(set-strategic-number sn-maximum-attack-group-size 50)
```

#### Adding a new unit to train

 * Create the training flag `g_train_XXX` in `main`.
 * Add `train\XXX` and only train the unit if `g_train_XXX` is `yes`.
 * Add the unit to the correct types in `technology\has` to receive automatic upgrades.
 * Set the training flag to `yes` to train it.