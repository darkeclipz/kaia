# How to compute the desired villager distribution

Think of it as building a **target mix** in two layers:

1. **Flow layer (ongoing costs):** “How many vills do I need on each resource to *sustain* my planned production?”
2. **Stockpile layer (one-off / near-term purchases):** “How many extra vills do I need to *catch up* to afford upcoming things within a horizon?”

Then you add them and cap to your vill count.

## 1) Flow layer (ongoing costs) → vill floor per resource

If you have recurring spends like “2-stable knights” (120F + 150G every 30s), convert that into **burn per second**:

* food burn = 120 / 30 = **4.0 food/s**
* gold burn = 150 / 30 = **5.0 gold/s**

General:

[
burn[r] = \sum_i \frac{cost_i[r]}{period_i}
]

Given gather rate per vill:

[
rate[r] = \text{gather_rate}[r]
]

You need at least:

[
v_flow[r] = \lceil burn[r] / rate[r] \rceil
]

This gives a **minimum** vill allocation that prevents the production plan from slowly starving.

### Farm reseed as a flow cost (wood)

A farmer periodically spends 60 wood to reseed. The expected wood burn per farmer is:

* time to empty a farm ≈ `farm_capacity / food_rate_per_vill` seconds
* wood burn per second per farmer ≈ `60 / (farm_capacity / food_rate)` = `60 * food_rate / farm_capacity`

So if you have `F` farmers:

[
burn_wood_reseed \approx F \cdot 60 \cdot \frac{food_rate}{farm_capacity}
]

Then:

[
v_{flow}[wood] \gets v_{flow}[wood] + \left\lceil \frac{burn_wood_reseed}{rate[wood]} \right\rceil
]

This is why wood doesn’t collapse when you go heavy farms.

## 2) Stockpile layer (upcoming purchases) → extra villagers for catch-up

Let’s define a short horizon, say `H = 120s`.

Compute what you want to be able to pay in that horizon (your “shopping list”):

[
target[r] = \text{sum of planned costs in next H seconds}
]

Deficit is:

[
deficit[r] = \max(0, target[r] - current[r])
]

Now ask: “How many villagers on resource `r` would collect that deficit by time H?”

[
v_{stock}[r] = \left\lceil \frac{deficit[r]}{rate[r] \cdot H} \right\rceil
]

These are *extra* villagers beyond the flow layer.

## 3) Combine and normalize to total villagers

Start with:

[
v[r] = v_{flow}[r]
]

Let `remaining = total_vills - sum(v[r])`.

Then allocate `remaining` to cover the largest deficits using `v_stock[r]`, and finally dump leftovers into “best” resources.

This is what your greedy policy was doing already—just with the missing “flow floor” and reseed pressure added.

# “Large deficits” concern: won’t it send *everyone* to one resource?

It can, if you let it. And sometimes that’s actually correct (e.g., you’re 200 food short of clicking Feudal right now—food is king). But if you do it naïvely you get bad behavior:

* you starve wood → no houses/farms
* you starve gold → production stalls
* you never recover

So good policies add **controls**:

## A) Flow layer is a hard minimum

Even if you have a giant food deficit, you still keep the villagers required to sustain ongoing production (and reseeds).

That alone prevents “everyone to food”.

## B) Cap how many villagers can be pulled at once

In an RTS AI, you also add *execution friction*: you don’t instantly retask 30 vills. You might cap to e.g. 5 per 10 seconds.

That keeps it stable and realistic.

## C) Use a “time-to-afford” rule instead of raw deficit size

Instead of sorting by `deficit[r]`, sort by **how urgent** it is:

[
time_to_afford[r] \approx \frac{deficit[r]}{assigned[r] \cdot rate[r] + \epsilon}
]

And prioritize the resource that most reduces time to next critical purchase.

## D) Put a minimum on wood and food anyway

Even without ongoing production, you often want:

* minimum wood for houses/farms
* minimum food for villager creation

So you can enforce “baseline floors” like:

* at least 2 on wood in Dark Age
* at least 6 on food early, etc.
  (or make these dynamic: based on how soon you’ll hit pop cap, how many farmers you have, etc.)

## A concrete “decision tick” recipe 

Every N seconds (e.g. 5 seconds):

1. **Compute rates** (including upgrades/civ bonuses)
2. **Compute burn rates** from production goals + reseed estimate
3. Convert burn → `v_flow[r]`
4. Compute `target costs` for the next `H` seconds (your build/tech/unit goals)
5. Convert deficits → `v_stock[r]`
6. Allocate villagers:

   * start with `v_flow`
   * allocate remaining to satisfy `v_stock` (largest urgency first)
   * dump remainder into best weighted resource
7. Apply a retask cap (e.g., only move 3 villagers this tick)

