import random
import math

class MAB:
    def __init__(self, limit):
        self.p = min(1, random.random() * limit)
    
    def pull(self):
        return 0 if random.random() > self.p else 1

mabs = [MAB(0.5) for _ in range(2)]
mabs += [MAB(10) for _ in range(1)] # sure win
mabs += [MAB(0.1) for _ in range(2)]

class node:
    def __init__(self, state, parent = None):
        self.parent = parent
        self.state = state
        self.plays = 0
        self.wins = 0
        self.children = []

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

    def mab(self):
        return self.state[0]
    
    def pulls(self):
        return self.state[1]

    def terminal(self):
        return self.pulls() == MAX_PULLS

    def add_play(self, win):
        self.plays += 1
        if win: self.wins += 1

    def ucb1(self, plays):
        return self.wins / self.plays + math.sqrt(2 * math.log(plays) / self.plays)

    def value(self):
        return mabs[self.mab()].pull() + (self.parent.value() if self.parent != None else 0)

MAX_PULLS = 20
EPOCHS = 100000

root = node((0,0))
threshold = 8

def win(value):
    return value > threshold

def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def playout(state, value):
    _, pulls = state
    value += mabs[state[0]].pull()
    for i in range(MAX_PULLS - pulls - 1):
        value += random.choice(mabs).pull()
    return value

probs = [x.p for x in mabs]
print(list(enumerate(probs)))

for _ in range(EPOCHS):
    # selection
    at = root
    while len(at.children) == len(mabs) and not at.terminal():
        stats = [child.ucb1(at.plays) for child in at.children]
        at = at.children[argmax(stats)]
    if at.terminal():
        print("reached tree end")
        break
    left = list(range(len(mabs)))

    # expansion
    for c in at.children:
        left.remove(c.mab())
    next_pull = random.choice(left)
    next_state = (next_pull, at.pulls() + 1)
    next_node = node(next_state)
    at.add_child(next_node)

    # simulation
    is_win = win(playout(next_state, at.value()))

    # backpropagation
    at = next_node
    while at != None:
        at.add_play(is_win)
        at = at.parent


test = 1000
rand = 0
mcts = 0

for _ in range(test):
    run = 0
    for _ in range(MAX_PULLS):
        run += random.choice(mabs).pull()
    rand += win(run)
rand /= test

print("Random result:", rand)

for _ in range(test):
    at = root
    while len(at.children) == len(mabs) and not at.terminal():
        stats = [child.ucb1(root.plays) for child in at.children]
        at = at.children[argmax(stats)]
    if at.terminal():
        add = at.value()
    else:
        add = playout((random.choice(range(len(mabs))), at.pulls() + 1), at.value())
    mcts += win(add)

mcts /= test
print("MCTS result:", mcts)

