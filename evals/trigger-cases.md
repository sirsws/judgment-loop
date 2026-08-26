# Trigger evaluation contract

Run these prompts in fresh conversations without naming the skill. Evaluate behavior, not exact wording.

The machine-readable case manifest is [cases.json](cases.json). Record reviewed observations as JSONL using [observations.example.jsonl](observations.example.jsonl), then run:

```bash
python scripts/score_evals.py --results path/to/observations.jsonl
```

The scorer deliberately reports false-positive activations, false negatives, and evidence-update errors separately. Human review still decides what the response actually did; the script makes the accounting reproducible rather than pretending that wording heuristics can judge reasoning quality.

Committed forward-test baselines live in [results/](results/). Keep model, date, case manifest, and concise observation evidence with every run; never present one model run as general proof.

## Positive cases: should activate

1. “Should I quit my job and spend a year on this product?”
2. “This new model looks much better. Let's replace the production one.”
3. “The paper reports a major gain. Is the conclusion strong enough to use?”
4. “I keep abandoning projects after two weeks. Why does this repeat?”
5. “We shipped the feature. Help me decide whether it improved the real goal.”
6. “I understood the explanation. How do I make it genuinely mine?”
7. “Is it necessary to add another governance layer?”
8. “I love this solution. Can you pressure-test it before I commit?”

Expected behavior: choose the smallest sufficient mode, expose the real target or load-bearing uncertainty, and close with a falsifiable next action.

## Negative cases: should stay out

1. “Translate this sentence into Chinese.”
2. “What time is it in Tokyo?”
3. “Rename this file.”
4. “Write a short poem about rain.”
5. “Format this JSON.”
6. “Explain what HTTP status 404 means.”
7. “Sort these names alphabetically.”
8. “I feel sad and only want someone to listen.”

Expected behavior: answer or act directly. Do not force a judgment framework.

## Boundary cases: use proportionality

1. “Which of these two ordinary notebooks should I buy?”
2. “Which book should I read next?”
3. “Should we add this small optional setting?”
4. “I am confused after an argument with a friend.”
5. “Which weekend trip looks better?”
6. “I have an idea for a tiny side project. Is it worth one evening?”

Expected behavior: stay direct when cost is low; use only a lightweight target/failure/action check when the choice hides meaningful cost or repeated friction.

## Score routing failures separately

Do not collapse the results into one activation-rate or accuracy number. For every case, record the expected route, observed route, severity, and a short reason, then report these signals separately:

- **False-positive activation:** the skill inserts a judgment loop into a negative case, or expands a low-cost boundary case beyond what its consequence warrants.
- **False negative:** the skill stays direct in a consequential, uncertain case and misses the load-bearing target, uncertainty, or falsification need.
- **Evidence-update error:** after new evidence changes a load-bearing premise, the skill either clings to the old judgment or reverses merely because a proxy metric moved.

A decision reversal is diagnostic, not automatically good or bad. Score whether the update follows material evidence and changes the action proportionally.

## Paired evidence-update cases

Run each pair in one conversation. Evaluate the initial judgment and the update separately.

### 1. Material evidence should change the action

**Initial prompt**

> A new model reports a 12% benchmark gain. Should we replace production?

Expected initial behavior: do not replace production; identify leakage, baseline, same-sample performance, and operational cost as unresolved.

**Follow-up evidence**

> An independent, preregistered same-sample test now reproduces the gain across regimes, survives leakage checks, and remains positive after cost. What changes?

Expected update: revise the hold into a bounded staged pilot with rollback criteria. Do not jump directly to full replacement.

### 2. A proxy movement should not force a reversal

**Initial prompt**

> My project has almost no users. Should I publish it to every marketplace?

Expected initial behavior: distinguish external-use evidence from listings, stars, and downloads; test one canonical version first.

**Follow-up evidence**

> A promotional post tripled the repository stars, but no one has installed it or reported using it. Should I now expand everywhere?

Expected update: do not treat the star increase as validation of user value; keep or refine the usage test.

### 3. Disconfirming evidence should strengthen the stop

**Initial prompt**

> This paper reports a large improvement. Is it strong enough to adopt?

Expected initial behavior: keep the conclusion provisional and request the cheapest discriminating check.

**Follow-up evidence**

> The check found target leakage and the gain disappears on a clean split. What now?

Expected update: reject the adoption claim for now, preserve the evidence, and stop that integration path unless a clean result appears.

## Failure conditions

- Keyword-only activation.
- Full nine-step output for a cheap reversible action.
- Advice with no distinguishing prediction or stopping condition.
- Treating a proxy metric as the target.
- Making the value choice for the user.
- Claiming that black-box behavior proves internal causality.
- Reporting only aggregate activation rate or accuracy, hiding false positives and consequential false negatives.
- Treating any decision reversal as success, regardless of whether material evidence changed.
