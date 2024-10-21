# tetris on python with curses library
# by DoggeKey
#
#

# begin
#
# importing librates
import curses,random

# initializating screen window
Screen = curses.initscr()
screen = curses.newwin(25,32) # 32x25

# set rules for curses
curses.curs_set(False) # remove cursor
curses.noecho() # no echo input
curses.cbreak() # no need enter key
screen.nodelay(True) # no waiting input
screen.keypad(True) # allow arrows

# classes
#
# game field class
class Background:

	def __init__(self, ln, flr, field):
		"""create game field"""
		self.field = field[:]
		self.LINE = ln[:]
		self.FLOOR = flr[:]
		self.cache = list()

	def check_field(self, scr):
		"""clear rows in field"""
		ceil = []
		for i in range(20):
			row = 0
			# count blocks in row
			for j in range(10):
				if self.field[i][j] == True:
					row += 1
			# add full riw ti ceil
			if row == 10:
				ceil.append(i)
		# delete ceils
		for i in ceil:
			for k in range(i, 1, -1):
				for j in range(10):
					self.field[k][j] = self.field[k-1][j]
		# update screen
		for i in ceil:
			self.update(4, scr)
			self.update(9, scr)
			self.update(13, scr)
			self.update(18, scr)
		# give scores
		achive = (0, 1, 5, 10, 50)
		return achive[len(ceil)]
		
	def update(self, y, scr):
		"""draw field screen part"""
		for i in range(-3, 3):
			# testing cache
			if not(y + i in self.cache):
				if (y + i >= 0) and (y + i < 20):
					# draw empty line
					scr.addstr(y + i, 0, self.LINE, curses.color_pair(1))
					# draw blocks
					for j in range(10):
						if self.field[y + i][j] == True:
							scr.addstr(y + i, j*2 + 2, "[]", curses.color_pair(1))
				elif y + i == 20:
					# draw floor
					scr.addstr(y + i, 0, self.FLOOR, curses.color_pair(1))
				# add y to chache
				self.cache.append(y + i)

	def clear_cache(self):
		"""clearing cache"""
		self.cache = list()

# game figure class
class Figure:
	
	def __init__(self, blocks):
		"""create figure"""
		self.blocks = blocks
		# finding borders
		left = 0
		right = 0
		down = 0
		up = 0
		for block in self.blocks:
			if block[0] > right:
				right = block[0]
			if block[0] <= left:
				left = block[0]
			if block[1] > down:
				down = block[1]
		self.borders = (-left, 9-right, 19-down)

	def get(self):
		"""get figure blocks"""
		ret = list()
		for i in range(4):
			ret.append([])
			for j in range(2):
				ret[i].append(self.blocks[i][j])
		return ret

	def get_borders(self):
		"""get figure borders"""
		ret = list()
		for i in range(3):
			ret.append(self.borders[i])
		return ret

	def rotate(self, x, y, bg):
		"""totate figure 90 degrees in clockwise"""
		# initializating local variables
		attempt = self.get()
		left = 0
		right = 0
		down = 0
		up = 0
		cannot_rotate = False
		
		# rotate clone
		for i in range(4):
			buffer = attempt[i][0]
			attempt[i][0] = -attempt[i][1]
			attempt[i][1] = buffer
			
		    # define borders
			if attempt[i][0] > right:
				right = attempt[i][0]
			if attempt[i][0] <= left:
				left = attempt[i][0]
			if attempt[i][1] > down:
				down = attempt[i][1]
			at_borders = (-left, 9-right, 19-down)
		
		# check condition for each block
		for i in range(4):
			if (x < at_borders[0]) or (x > at_borders[1]) or (y > at_borders[2]) or (self.check_one(x + attempt[i][0], y + attempt[i][1], bg) == True):
				cannot_rotate = True
        # accept rotation
		if cannot_rotate == False:
			self.blocks = attempt
			self.borders = at_borders


	def on_floor(self, y, x, bg):
		"""convert figure to blocks on field"""
		for block in self.blocks:
			bg.field[y + block[1]][x + block[0]] = True

	def check(self, x, y, bg):
		"""check blocks collision"""
		for block in self.blocks:
			if bg.field[y + block[1]][x + block[0]] == True:
				return True
		return False
	def check_one(self, x, y, bg):
		"""check collision in current position"""
		if bg.field[y][x] == True:
			return True
		return False

	def draw(self, x, y, scr, bg):
		"""draw current figure"""
		# update background
		for block in self.blocks:
				bg.update(y + block[1], scr)
		bg.clear_cache()
		# draw new blocks
		for block in self.blocks:
				scr.addstr(y + block[1], x*2 + block[0]*2 + 2, "[]", curses.color_pair(1))

# constants
#
# figures
FIGURE = (
Figure([ [-1,0], [0,0], [1,0], [0,-1] ]), # T
Figure([ [-1,0], [0,0], [1,0], [1,-1] ]), # L
Figure([ [-1,0], [0,0], [1,0], [-1,-1] ]),# J
Figure([ [-1,0], [0,0], [1,0], [2,0] ]),  # I
Figure([ [-1,0], [0,0], [0,-1], [1,-1] ]),# S
Figure([ [-1,-1], [0,-1], [0,0], [1,0] ]),# Z
Figure([ [0,0], [1,0], [0,-1], [1,-1] ]), # O
)
# essential
GRAVITY = 0
GAME_OVER = False
# background
LINE = "||. . . . . . . . . . ||"
FLOOR = "||====================||"
BACKGROUND = (LINE[:]+"\n") * 20 + FLOOR[:]+"\n"
FREE_LINE = list(False for x in range(10))

# variables
#
# define classes
field = list(FREE_LINE[:] for x in range(20))
background = Background(LINE, FLOOR, field)
# essentials
stages = (10, 20, 30, 40, 50, 60, 70, 80, 90)
score = 0
old_scr = 0
time = 0
x = 3
y = 1
r = 0
placed = False
# choose new figure
selected = random.choice(FIGURE).get()
current = Figure(selected)
borders = 0

# set up
#
# create green color
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)

# clear screen to work
screen.clear()
screen.addstr(BACKGROUND, curses.color_pair(1))
screen.addstr(2, 26, "SCORE:", curses.color_pair(1))
screen.addstr(4, 26, "000000", curses.color_pair(1))

#game cycle
#
while not GAME_OVER:
	# ascending time
	time += 1
	if time%(11-GRAVITY) == 0:
		# move figure down
		if y < borders[2] and current.check(x, y + 1, background) == False:
			y += 1
		else:
			placed = True
		
	# if figure placed, take a new figure
	if placed == True:
		current.on_floor(y, x, background)
		y = 1
		x = 3
		# speed up game each 10000 points
		for i in stages:
		    if score > i:
		        GRAVITY = stages.index(i) + 1
		# score
		score += background.check_field(screen)
		# new figure
		selected = random.choice(FIGURE).get()
		current = Figure(selected)
		placed = False
		# if figure can't be placed -> end game
		if current.check(1, 3, background) == True:
			GAME_OVER = True
	
	# update borders
	borders = current.get_borders()
	
	# take input
	key = screen.getch()
	if key == curses.KEY_UP:
		current.rotate(x, y, background) # rotate
	if key == curses.KEY_DOWN and y < borders[2] and current.check(x, y + 1, background) == False:
		y += 1 # speed moving
	if key == curses.KEY_LEFT and x > borders[0] and current.check(x - 1, y, background) == False:
		x -= 1 # move left
	if key == curses.KEY_RIGHT and x < borders[1] and current.check(x + 1, y, background) == False:
		x += 1 # move right
	elif key == ord("q"):
		GAME_OVER = True # end game

	# draw figure
	current.draw(x, y, screen,background)
	# update scoreboard
	if old_scr != score:
		screen.addstr(4, 30 - len(str(score)), str(score), curses.color_pair(1))
	
	# refresh screen
	old_scr = score
	screen.refresh()
	curses.napms(50)

# end
#
curses.endwin()
print("your score:",str(score)+"00")
print("thanks for playing!")







