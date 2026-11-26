# Approved example

This worked example shows every principle in SKILL.md working together:

- It starts from a die, which the reader already understands.
- Outcome, sample space and event are each used in plain words, then named in bold.
- Each axiom gets a sentence on why it must be true.
- The "or" rule lets the natural wrong instinct (just add them) fail on a real example before the formula fixes it.
- The text sets up the Venn diagram with a question and then tells the reader what to look at in it.
- The answer is checked by listing faces.
- The Your turn asks the reader to do the key step (find the overlap) themselves.

---

## 3. Outcomes, events and the axioms

Before you can say how likely something is, you need to be clear about what *could* happen. So we'll start with a single die, because you already know everything about it.

When you roll a die, exactly one face lands on top. Probability calls each of those possible results an **outcome**. A die has six outcomes: 1, 2, 3, 4, 5 and 6. Put every outcome together and you have the **sample space**, which is just a name for "the full list of things that could happen". For one die, the sample space is {1, 2, 3, 4, 5, 6}.

Most of the time, though, you don't care about one exact face. You care about something broader, like "did I roll an even number?". Three faces answer yes to that question: 2, 4 and 6. A group of outcomes like this is called an **event**. So "roll an even number" is the event {2, 4, 6}, and it happens whenever any one of those three faces comes up.

Now you can measure how likely an event is. On a fair die every face has the same chance, so all that matters is how many faces belong to the event. Three of the six faces are even, so the probability of rolling an even number is 3 out of 6, or 1/2. That's the whole recipe whenever the outcomes are equally likely: count the outcomes in the event, then divide by the total number of outcomes.

### The rules every probability obeys

The lecture gives four rules, called axioms. Every probability in this module follows them, so it's worth seeing why each one makes sense instead of memorising it.

```latex
0 \le P(A) \le 1 \qquad P(\text{True}) = 1 \qquad P(\text{False}) = 0
```

The first rule says a probability always sits between 0 and 1. That falls straight out of the recipe above. An event can't contain fewer than zero faces, and it can't contain more faces than the die has. So the fraction can never drop below 0 or rise above 1.

The next two rules pin down the two ends of that scale. Something certain to happen, such as "the die shows a number from 1 to 6", has probability 1, because every outcome counts. Something that can't happen, such as "the die shows a 7", has probability 0, because no outcome counts. Every other event sits somewhere in between.

### The fourth rule: "or"

The fourth rule is the only one that needs real thought. It tells you the chance that at least one of two events happens:

```latex
P(A \text{ or } B) = P(A) + P(B) - P(A \text{ and } B)
```

Your first instinct is probably to just add the two probabilities. To see why that goes wrong, try it on an example.

Say event A is "the roll is even", which is the faces {2, 4, 6}. Event B is "the roll is more than 3", which is the faces {4, 5, 6}. Each event has three faces, so P(A) = 3/6 and P(B) = 3/6. Adding them gives 6/6, which would mean "A or B" is certain. But it clearly isn't: if you roll a 1 or a 3, neither event happens.

The picture below shows what went wrong.

*[Diagram: one die's six faces in a sample-space box, with two overlapping ellipses for A (even) and B (more than 3); faces 4 and 6 highlighted in the overlap. Title: "4 and 6 are in both sets, so P(A) + P(B) counts them twice".]*

Look at the faces 4 and 6. They're even *and* more than 3, so they sit inside both circles. When you added P(A) and P(B), you counted them once for A and then again for B. The answer came out too big because two faces were counted twice.

The fix is to take the double count back off. The overlap, "A and B", contains 2 faces, so P(A and B) = 2/6. Subtract it once:

```latex
P(A \text{ or } B) = \frac{3}{6} + \frac{3}{6} - \frac{2}{6} = \frac{4}{6}
```

You can check this by listing the faces where A or B happens: 2, 4, 5 and 6. That's four faces out of six, so the formula gives the right answer.

So the rule is just a way of not counting the overlap twice. When two events have no overlap at all, such as "roll a 1" and "roll a 6", P(A and B) is 0, and then you really can just add them.

**Your turn.** Roll one die. Let A be "roll a 1 or a 2" and B be "roll an odd number". Before you touch the formula, write down which faces are in both events. Then work out P(A or B), and check your answer by listing the faces. The answer is in section 10.

If you'd like to see this in motion, [Seeing Theory: Compound probability](https://seeing-theory.brown.edu/compound-probability/index.html) lets you drag overlapping sets around. [Basic probability](https://seeing-theory.brown.edu/basic-probability/index.html) on the same site shows coin flips settling towards one half the more you flip.
