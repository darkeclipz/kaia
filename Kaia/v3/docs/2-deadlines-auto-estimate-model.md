# Step-by-step plan for the scalable “2 deadlines + auto-estimate” model

This is the version where strategies **only set two cost bundles + a time flag** (fixed or auto), and the controller does the rest.

## 1) Decide your deadline time conventions

Use a single integer/flag per deadline time:

* `t >= 0` → fixed absolute deadline time (seconds)
* `t == -1` → auto: `t_est = now + TTA(cost)`
* `t == -2` → auto with phase gate: `t_est = max(gate_time, now + TTA(cost))`

`gate_time` is **one value per phase**, set by your strategy (e.g. Feudal end, Castle end, etc.).

## 2) What your strategy sets (per phase)

For each phase (e.g. “Feudal started”, “Castle started”, “Imperial started”), strategy writes:

* Deadline 1:

  * `deadline1_t` (fixed or -1/-2)
  * `deadline1_cost = {food, wood, gold, stone}`

* Deadline 2:

  * `deadline2_t`
  * `deadline2_cost`

* Phase gate:

  * `gate_time` (absolute time). This is used only when a deadline time is `-2`.

That’s it. No custom estimation logic in strategy.

Example mapping you wanted:

* Feudal started:

  * D1 fixed at `t_feudal_end`: cost = wood for 2 feudal buildings
  * D2 `-2`: cost = Castle age click cost, gate = `t_feudal_end + slack`
* Castle started:

  * D1 fixed at `t_castle_end`: cost = wood for Stable (or extra stable)
  * D2 `-2`: cost = Imperial click cost, gate = `t_castle_end + slack`
* Imperial started:

  * D1 fixed at `t_imp_end`: cost = Cavalier
  * D2 fixed at `t_imp_end + cav_time`: cost = Paladin

“slack” can be a constant like 40–60s if you don’t want to model building times.

## 3) Each update tick: read current game state

Controller reads:

* `now`
* `stock[r]` for each resource
* `vills_total`
* current gatherer percents `p_prev[r]`
* gather rates per vill `rate_per_vill[r]` (res/sec)
* whether vill production is active (not aging up), TC count, etc.
* farm capacity + food rate per farmer (for reseed)

## 4) Compute current income from percents

```python
income[r] = vills_total * (p_prev[r] / 100) * rate_per_vill[r]
```

## 5) Implement the generic TTA function

For a cost bundle:

```python
def TTA(cost):
    deficit[r] = max(0, cost[r] - stock[r])
    return max(deficit[r] / max(eps, income[r]) for r with deficit>0)
```

## 6) Resolve the two deadlines into actual times

For each deadline i:

* If `t_i >= 0`: `t_eff = t_i`
* If `t_i == -1`: `t_eff = now + TTA(cost_i)`
* If `t_i == -2`: `t_eff = max(gate_time, now + TTA(cost_i))`

If a deadline is “inactive”, set its time to `now` or its cost to all zeros.

## 7) Convert deadlines into required income rates (“deadline burn”)

For each deadline i:

```python
dt = max(1, t_eff - now)
remaining[r] = max(0, cost_i[r] - stock[r])
req_rate_i[r] = remaining[r] / dt
```

Combine the two deadlines per resource safely:

```python
deadline_burn[r] = max(req_rate_1[r], req_rate_2[r])
```

(Use max so you don’t double-count overlapping plans.)

## 8) Compute base continuous burn (“base_burn”)

This is the stuff that behaves like a real per-second drain:

* Villager production:

```python
if not researching_age_up:
    base_burn["food"] += town_centers * 50 / 25
```

* Farm reseed (expected):

```python
farmers = round(vills_total * p_prev["food"] / 100)
base_burn["wood"] += farmers * 60 * (food_rate_per_farmer / farm_capacity)
```

* Unit production you intend to sustain right now (e.g. 2-stable knights):

```python
base_burn["food"] += stables_active * 60 / 30
base_burn["gold"] += stables_active * 75 / 30
```

(Only include production you’re actually committing to in the current phase.)

## 9) Total burn and convert to `v_flow`

```python
burn_total[r] = base_burn[r] + deadline_burn[r]
v_flow[r] = ceil(burn_total[r] / rate_per_vill[r])
```

Optional feasibility check:

* If `sum(v_flow) > vills_total`, keep only Deadline1 (or relax Deadline2 to `-1`), then recompute.

## 10) Optional: small buffer `v_stock` (liquidity only)

You can keep this very small or omit it entirely.

Example buffers:

```python
buffer = {"wood": 200, "food": 100, "gold": 0, "stone": 0}
deficit_buf[r] = max(0, buffer[r] - stock[r])
v_stock[r] = ceil(deficit_buf[r] / (rate_per_vill[r] * H))   # H=120
```

Then:

```python
weight[r] = v_flow[r] + v_stock[r]
```

If you want maximum simplicity: `weight = v_flow`.

## 11) Convert weights → target percentages (sum to 100)

Use largest remainder:

* `p_raw[r] = floor(100 * weight[r] / sumW)`
* distribute leftover points to largest remainders until sum=100

## 12) Stabilize

Either:

### Smoothing (alpha=0.30)

```python
p_new[r] = round(0.70*p_prev[r] + 0.30*p_raw[r])
fix diff so sum=100
```

or

### Capped movement (±3% per tick)

```python
p_new[r] = p_prev[r] + clamp(p_raw[r]-p_prev[r], -3, +3)
fix diff so sum=100
```

## 13) Apply

Set gatherer percentages to `p_new`.

### Summary of what scales well

* Strategies only change 2 cost bundles + 2 time flags + 1 gate time.
* Controller handles all math: TTA, deadline burn, flow, percent rounding, smoothing/cap.
* Fixed deadlines are used when known; otherwise `-2` auto-estimates with a simple gate so it never predicts “before Feudal ends”, etc.
