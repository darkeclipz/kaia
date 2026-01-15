# Step-by-step plan for a deadline-first gatherer-% controller (fastest timings)

#### 0) Decide what you’re controlling

* Outputs each update: `p_food, p_wood, p_gold, p_stone` (integers, sum=100).
* Update cadence: every 5–10 seconds (15s is usually too slow).
* Stability: use either **smoothing** (`alpha=0.30`) or a **max step** (±3%) per update.

## A) Maintain the state you need

#### 1) Read current state

At each update tick, collect:

* `t_now`
* `stock[r]` for each resource
* `vills_total`
* current gatherer percents `p_prev[r]` (sum=100)

#### 2) Maintain “in-progress” timers

Whenever you start something with fixed duration (age-up, tech, etc.), store:

* `research_name`
* `t_end = t_start + duration`

This makes **fixed deadlines** possible.

## B) Build the deadline list

You generate a small list (1–3 items) of “must afford by time t” constraints.

#### 3) Define two deadline types

* **Fixed deadline:** you know `t_deadline` exactly (because something is already running, or because a previous event time is known).
* **Estimated deadline:** you don’t know it yet, so you compute an “earliest click estimate” and treat that as a rolling deadline.

#### 4) If research is running → produce fixed deadlines

Example for fastest Paladin:

* If Imperial is running and ends at `t_imp_end`:

  * deadline 1: at `t_imp_end` must afford **Cavalier cost**
  * deadline 2: at `t_imp_end + cav_time` must afford **Paladin cost**

Similarly for earlier steps:

* If Feudal is running, deadline might be “have wood for Stable+Blacksmith ready by Feudal end”.

Keep it to the **next one or two** steps; more tends to over-steer.

#### 5) If nothing is running → produce estimated deadlines

Compute the *earliest possible* time you could click the next key thing.

To estimate: first compute current income:

* `income[r] = vills_total * (p_prev[r]/100) * rate[r]`

Then for a candidate purchase (e.g. Castle click costs):

* `deficit[r] = max(0, cost[r] - stock[r])`
* `tta = max(deficit[r]/income[r])` over required resources
* `t_click_est = t_now + tta`
* If there are prereq buildings, add build time: `t_click_est += build_time_est`

Use that `t_click_est` as the deadline for the click.

## C) Convert deadlines into required income (extra burn)

#### 6) Convert each deadline into required per-second rates

For each deadline `(t_d, cost)` and each resource:

* `dt = max(1, t_d - t_now)`
* `remaining = max(0, cost[r] - stock[r])`
* `req_rate[r] = remaining / dt`

#### 7) Combine multiple deadlines safely

Don’t sum (it overcounts). Use:

* `extra_burn[r] = max(req_rate[r] across deadlines)`

This means “meet the tightest requirement”.

## D) Add continuous drains (true flow)

#### 8) Compute base burn (ongoing)

Include things that truly behave like a per-second drain:

* villager production food/sec (TCs × 50 / 25)
* unit production plans (if you want constant production)
* farm reseed burn (wood/sec)

Farm reseed burn:

* estimate farmers = `round(vills_total * p_prev["food"]/100)`
* `burn_reseed_wood = farmers * 60 * (food_rate_per_farmer / farm_capacity)`
* add into `base_burn["wood"]`

#### 9) Total burn

* `burn_total[r] = base_burn[r] + extra_burn[r]`

## E) Convert to vill requirements and then to target percentages

#### 10) Convert burn_total into a vill “floor”

For each resource:

* `v_flow[r] = ceil(burn_total[r] / rate[r])`

This is the minimum allocation that should hit your deadline(s) and cover continuous drains.

#### 11) Feasibility check (important)

If `sum(v_flow) > vills_total`, the deadline is impossible right now.
Action:

* drop to “estimated deadline” mode (or just accept it’s infeasible and let it converge).
  Practical: if infeasible, keep the **most important** deadline only (usually the soonest one), recompute.

#### 12) Optional buffers using v_stock (only for liquidity)

In deadline-first, `v_stock` is not for tech costs. It’s for small safety buffers:

* `buffer_wood` (houses/farms): e.g. 200
* `buffer_food` (vill production): e.g. 100

Compute:

* `deficit_buf[r] = max(0, buffer[r] - stock[r])`
* `v_stock[r] = ceil(deficit_buf[r] / (rate[r] * H))` with `H=120`

Then combine:

* `weight[r] = v_flow[r] + v_stock[r]`

(If you don’t want buffers, set `v_stock=0` and `weight=v_flow`.)

#### 13) Convert weights → integer percents that sum to 100

Use “largest remainder”:

* base percent `p_raw[r] = floor(100 * weight[r] / sumW)`
* distribute leftover points to largest remainders until sum=100

## F) Stabilize (smoothing or capped movement)

#### 14) Smooth (alpha=0.30) OR cap changes

Smoothing:

* `p_new[r] = round(0.70*p_prev[r] + 0.30*p_raw[r])`

Then fix sum to 100:

* `diff = 100 - sum(p_new)`
* add `diff` to the most urgent resource (or food as default)

Alternative (often better): cap to ±3%:

* `delta = clamp(p_raw[r]-p_prev[r], -3, +3)`
* `p_new[r] = p_prev[r] + delta`
* fix sum to 100

#### 15) Apply

Set SN gatherer percents to `p_new`.

## G) How this enforces “have resources by time t”

Because at each tick it enforces:

[
income[r] \ge \frac{cost[r]-stock[r]}{t_d-t}
]

So if feasible, your stock evolves to meet the deadline. If not feasible, the feasibility check forces you to relax into an estimated deadline.

If you want the fastest-paladin chain as concrete deadlines, the usual ones to generate are:

* before/while Imperial is running: `(t_imp_end, Cavalier cost)`, `(t_imp_end+80, Paladin cost)`
* before Imperial is clicked: estimated click time for Imp (from TTA + prereq build time) → `(t_imp_click_est, Imp cost)` and optionally `(t_imp_click_est, prereq building wood)`
