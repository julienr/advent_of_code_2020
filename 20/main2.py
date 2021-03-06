import sys
import numpy as np
import collections
import math
tiles = open('input').read().split('\n\n')

def data_to_str(arr):
    return '\n'.join(''.join(r) for r in arr)

def rotate(data, angle, flip):
    if not flip:
        data = data
    elif flip:
        data = data[:, ::-1]

    if angle == 0:
        data = data
    elif angle == 90:
        data = np.transpose(data, (1, 0))[:, ::-1]
    elif angle == 180:
        data = data[::-1, ::-1]
    elif angle == 270:
        data = np.transpose(data, (1, 0))
    else:
        raise RuntimeError('Error')
    return data


class Tile:
    def __init__(self, data, id):
        self.data = data
        self.id = id
        #self.borders = [
            #''.join(self.data[:,0]),
            #''.join(self.data[:,-1]),
            #''.join(self.data[0, :]),
            #''.join(self.data[-1, :]),
        #]

    def __str__(self):
        return 'id=%s\n%s\n' % (self.id, data_to_str(self.data))

    def __repr__(self):
        return 'Tile(id=%s)' % (self.id)

    def rotated(self, angle, flip):
        data = rotate(self.data, angle, flip)
        return Tile(data, self.id)

    def border_left(self):
        return ''.join(self.data[:, 0])

    def border_right(self):
        return ''.join(self.data[:, -1])

    def border_top(self):
        return ''.join(self.data[0, :])

    def border_bottom(self):
        return ''.join(self.data[-1, :])


def make_tile(s):
    lines = s.split('\n')
    title = lines[0].strip()
    assert title.startswith('Tile ')
    id = int(title[4:-1])

    data = np.array([list(l) for l in lines[1:] if len(l) > 0])
    return Tile(data, id)

tiles = list(map(make_tile, tiles))
#print('\n'.join('%s' % t for t in tiles))

print('%d tiles' % len(tiles))
size = int(math.sqrt(len(tiles)))
print('size=%d' % size)
#print(tiles[0].data)
#print(tiles[0].borders)

if False:
    print(tiles[0].rotated(angle=0))
    print(tiles[0].rotated(angle=90))
    print(tiles[0].rotated(angle=180))
    print(tiles[0].rotated(angle=270))

if False:
    tile = Tile(np.array([
        ['1', "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]), '42')
    print(tile)

    for angle in [0, 90, 180, 270]:
        for flip in [True, False]:
            print('\nangle=%s, flip=%s' % (angle, flip))
            print(tile.rotated(angle=angle, flip=flip))

    sys.exit()

all_tiles = []
for t in tiles:
    for angle in [0, 90, 180, 270]:
        for flip in [True, False]:
            all_tiles.append(t.rotated(angle=angle, flip=flip))


def find_possible_tile(border_left, border_top, border_right, border_bottom,
                       exclude_ids):
    candidates = []
    for t in all_tiles:
        if t.id in exclude_ids:
            continue
        if border_left and border_left != t.border_left():
            continue
        if border_right and border_right != t.border_right():
            continue
        if border_top and border_top != t.border_top():
            continue
        if border_bottom and border_bottom != t.border_bottom():
            continue
        candidates.append(t)
    if len(candidates) == 0:
        return None
    else:
        assert len(candidates) == 1, '%d' % len(candidates)
        return candidates[0]


def find_arrangement(starting_tile):
    image = np.zeros((size, size), dtype=np.object)
    image[:] = None
    used_ids = set([])
    for i in range(size):
        for j in range(size):
            if i == j == 0:
                image[i, j] = starting_tile
                used_ids.add(starting_tile.id)
            else:
                border_left = border_top = border_right = border_bottom = None
                if i > 0 and image[i-1, j] is not None:
                    border_top = image[i-1, j].border_bottom()
                if i < size - 1 and image[i+1, j] is not None:
                    border_bottom = image[i+1, j].border_top()
                if j > 0 and image[i, j-1] is not None:
                    border_left = image[i, j-1].border_right()
                if j < size - 1 and image[i, j+1] is not None:
                    border_right = image[i, j+1].border_left()
                t = find_possible_tile(border_left, border_top, border_right,
                        border_bottom, used_ids)
                if t is None:
                    return None
                image[i, j] = t
                used_ids.add(t.id)
    return image


def solution_id(image):
    return image[0, 0].id * image[-1, 0].id * image[-1, -1].id * image[0, -1].id


image = None
for starting_tile in all_tiles:
    solution = find_arrangement(starting_tile)
    if solution is not None:
        print('found solution id=%s' % solution_id(solution))
        #print(solution)
        image = solution

def image_to_str(image):
    rows = []
    for i in range(image.shape[0]):
        for ti in range(image[i][0].data.shape[0]):
            rs = ' '.join(''.join(r.data[ti]) for r in image[i, :])
            rows.append(rs)
        rows.append('')
    return '\n'.join(rows)

print(image)
print(image_to_str(image))
print(solution_id(image))

def make_final_image(image):
    final_size = size * (image[0][0].data.shape[0] - 2)
    final_image = np.zeros(
        (final_size, final_size), dtype='<U1')
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            off = image[0][0].data.shape[0] - 2
            final_image[i * off:(i + 1) * off, j * off: (j + 1) * off] =\
                image[i, j].data[1:-1, 1:-1]
    return final_image


def print_final_image(image):
    print('\n'.join(''.join(row) for row in image))

final_image = make_final_image(image)


MONSTER="""
                  # 
#    ##    ##    ###
 #  #  #  #  #  #   
"""
MONSTER = np.array([list(r) for r in MONSTER.split('\n') if r.strip() != ''])
print('MONSTER ', MONSTER)

def search_monster(image, draw=False):
    sea_monsters = []
    for i in range(0, image.shape[0] - MONSTER.shape[0]):
        for j in range(0, image.shape[1] - MONSTER.shape[1]):
            def _find():
                coords = []
                for mi in range(MONSTER.shape[0]):
                    for mj in range(MONSTER.shape[1]):
                        if MONSTER[mi, mj] == ' ':
                            continue
                        else:
                            if image[i + mi, j + mj] != '#':
                                return False, []
                            coords.append((i + mi, j + mj))
                return True, coords
            found, coords = _find()
            if found:
                sea_monsters.append(coords)

    if draw:
        vimg = image.copy()
        for coords in sea_monsters:
            for c in coords:
                vimg[c[0], c[1]] = 'O'
        print('\nMONSTERS')
        print_final_image(vimg)

    return sea_monsters

sea_monsters = []
for angle in [0, 90, 180, 270]:
    found = False
    for flip in [True, False]:
#for angle in [180]:
    #for flip in [True]:
        print('\nangle=%s, flip=%s' % (angle, flip))
        tmp = rotate(final_image, angle, flip)
        print_final_image(tmp)
        sea_monsters = search_monster(tmp, draw=False)
        if len(sea_monsters) > 0:
            found = True
            break
    if found:
        break

print('%d monsters' % len(sea_monsters))
vimg = tmp.copy()
for coords in sea_monsters:
    for c in coords:
        vimg[c[0], c[1]] = '.'
print('\nMONSTERS')

hash_count = np.count_nonzero(vimg == '#')
print('hash count: %d' % hash_count)


#border_to_tiles = collections.defaultdict(lambda: [])
#for t in tiles:
    #for b in t.borders:
        #border_to_tiles[b].append(t)

#tiles_n_outer = collections.defaultdict(lambda: 0)
#for border, tiles_list in border_to_tiles.items():
    #if len(tiles_list) == 1:
        #for t in tiles_list:
            #tiles_n_outer[t] += 1

#for t, n_outer in tiles_n_outer.items():
    #print(t.id, n_outer)
#print(len(tiles_n_outer.keys()))
