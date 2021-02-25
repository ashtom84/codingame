############################
# large room for improvement
############################

import sys

class Space:
    def __init__(self, l, c, start=(-1,-1), end=(-1,-1), T1=(-1,-1), T2=(-1,-1), space=[]):
        self.l = l
        self.c = c
        self.start = start
        self.end = end
        self.T1 = T1
        self.T2 = T2
        self.space = space

    def add_row_to_space(self, row):
        self.space.append([s for s in row])

    def set_bounds(self, st, ed):
        self.start = st
        self.end = ed

    def set_teleport(self, t1, t2):
        self.T1 = t1
        self.T2 = t2

    def find_indexes(self, row, s):
        idxs = []
        for i in range(len(row)):
            if row[i] == s:
                idxs.append(i)
        return idxs

    def update_Ts(self, T1, T2, i):
        Ts = self.find_indexes(row, "T")
        if len(Ts) == 1:
            if T1 == (-1, -1):
                T1 = (i, Ts[0])
            else:
                T2 = (i, Ts[0])
        elif len(Ts) == 2:
            k, l = Ts
            T1, T2 = (i, k), (i, l)
        return T1, T2

    def find_index(self, row, s):
        for i in range(len(row)):
            if row[i] == s:
                return i
        return -1

    def update_bounds(self, bound, row, symbol):
        if bound == (-1,-1):
            idx = self.find_index(row, symbol)
            if idx != -1:
                return (i, idx)
            else:
                return (-1, -1)
        else:
            return bound

class Bender:
    def __init__(self, px, py, direction="SOUTH", inverter=0, beer=0, teleported=False, brokenwalls=0, visited={}, step=0, walk={}):
        self.px = px
        self.py = py
        self.direction = direction
        self.inverter = inverter
        self.beer = beer
        self.brokenwalls = brokenwalls
        self.visited = visited
        self.step = step
        self.walk = walk
        self.priorities = { # by inverter % 2
            0: ["SOUTH", "EAST", "NORTH", "WEST"],
            1: ["WEST", "NORTH", "EAST", "SOUTH"],
        }
        self.barriers = { # by beer % 2
            0: ["X", "#"],
            1: ["#"]
        }
        self.teleported = teleported

    def get_state(self, px=None, py=None, direction=None):
        if px is None:
            px = self.px
        if py is None:
            py = self.py
        if direction is None:
            direction = self.direction
        return (px, py, direction, self.inverter, self.beer, self.teleported, self.brokenwalls)

    def update_step(self):
        self.step += 1

    def update_visited(self):
        self.visited[self.get_state()] = self.visited.get(self.get_state(), 0) + 1
    
    def set_direction(self, new_dir):
        self.direction = new_dir
    
    def set_position(self, new_px, new_py):
        self.px = new_px
        self.py = new_py

    def set_to_modifier(self, modifier):
        dir_map = {
            "N": "NORTH", "E": "EAST", "S": "SOUTH", "W": "WEST"
        }
        self.direction = dir_map[modifier]

    def add_to_walk(self):
        self.walk[(self.step, self.px, self.py)] = self.get_state()

    def check_for_loop(self):
        k = self.step
        while k > 1:
            k -= 1
            if (k, self.px, self.py) in self.walk.keys():
                if self.walk[(k, self.px, self.py)] == self.walk[(self.step, self.px, self.py)]:
                    return k, self.px, self.py
        return -1, self.px, self.py

    def next_step_new_direction(self, dir_):
        x, y, br = self.px, self.py, self.barriers[self.beer]
        l, c, sp = space.l, space.c, space.space
        if dir_ == "SOUTH":
            return ((x+1, y), "SOUTH") if x+1 < l and sp[x+1][y] not in br else (-1, -1)
        elif dir_ == "EAST":
            return ((x, y+1), "EAST") if y+1 < c and sp[x][y+1] not in br else (-1, -1)
        elif dir_ == "NORTH":
            return ((x-1, y), "NORTH") if x-1 > 0 and sp[x-1][y] not in br else (-1, -1)
        elif dir_ == "WEST":
            return ((x, y-1), "WEST") if y-1 > 0 and sp[x][y-1] not in br else (-1, -1)

    def next_step(self, space):
        return self.next_step_new_direction(self.direction)

    def broken_wall(self):
        self.brokenwalls += 1
        self.visited = {}

    def step_in_space(self, space):
        # one more step
        self.update_step()
        # parameters
        i, j = self.px, self.py
        s = space.space[i][j]
        if s == "I":
            self.inverter = (self.inverter + 1) % 2
        if s == "B":
            self.beer = (self.beer + 1) % 2
        if s == "T" and not self.teleported:
            self.teleported = True
            if (i, j) == space.T1:
                next_x, next_y = space.T2
            else:
                next_x, next_y = space.T1
            return self.step, self.direction, next_x, next_y
        if s != "T" and self.teleported:
            self.teleported = False
        if s == "X" and self.beer:
            space.space[i][j] = ""
            self.broken_wall()
        if s in ["N", "E", "S", "W"]:
            self.set_to_modifier(s)

        # update visited map        
        self.update_visited()

        next_ = self.next_step(space)
        # barrier encountered
        if next_ == (-1, -1):
            k, prior = 0, self.priorities[self.inverter]
            while k < len(prior) and next_ == (-1, -1):
                next_ = self.next_step_new_direction(prior[k])
                k += 1
        (next_x, next_y), next_dir = next_

        # update the walk, check for loops
        self.add_to_walk()
        last_step, last_px, last_py = self.check_for_loop()
        if last_step != -1:
            last_dir = "LOOP"
            return last_step, last_dir, last_px, last_py
        else:
            return self.step, next_dir, next_x, next_y
        return self.step, next_dir, next_x, next_y


l, c = [int(i) for i in input().split()]
space = Space(l, c)

for i in range(l):
    row = input()
    # check if start/end have been found and update
    space.set_bounds(space.update_bounds(space.start, row, "@"), 
                        space.update_bounds(space.end, row, "$"))
    # check if T1/T2 have been found and update
    t1, t2 = space.update_Ts(space.T1, space.T2, i)
    space.set_teleport(t1, t2)
    # add the current row
    space.add_row_to_space(row)
print(space.start, space.end, space.T1, space.T2, file=sys.stderr, flush=True)
print(space.space, file=sys.stderr, flush=True)

x, y = space.start
bender = Bender(x, y)

pos, directions = space.space[x][y], []
cpt = 0
while pos != "$":
    cur_step, cur_dir, next_x, next_y = bender.step_in_space(space)
    if cur_dir == "LOOP":
        directions = ["LOOP"]
        break
    pos = space.space[next_x][next_y]
    bender.set_direction(cur_dir)
    bender.set_position(next_x, next_y)
    if not (pos == "T" and bender.teleported):
        directions.append(cur_dir)
for direction in directions:
    print(direction)
