'''
-GAME BOARD-

Contains classes and functions responsible for rendering the Andantino hex board
'''

from tkinter import *
import numpy as np

class HexaCanvas(Canvas):
    def __init__(self, master, *args, **kwargs):
        Canvas.__init__(self, master, *args, **kwargs)
        self.hexaSize = 20

    def setHexaSize(self, number):
        self.hexaSize = number

    def create_hexagon(self, x, y, color = "gray60", fill="blue", color1=None, color2=None, color3=None, color4=None, color5=None, color6=None):
        size = self.hexaSize
        dx = (size**2 - (size/2)**2)**0.5

        point1 = (x+dx, y+size/2)
        point2 = (x+dx, y-size/2)
        point3 = (x   , y-size  )
        point4 = (x-dx, y-size/2)
        point5 = (x-dx, y+size/2)
        point6 = (x   , y+size  )

        if color1 == None:
            color1 = color
        if color2 == None:
            color2 = color
        if color3 == None:
            color3 = color
        if color4 == None:
            color4 = color
        if color5 == None:
            color5 = color
        if color6 == None:
            color6 = color

        self.create_line(point1, point2, fill=color1, width=2)
        self.create_line(point2, point3, fill=color2, width=2)
        self.create_line(point3, point4, fill=color3, width=2)
        self.create_line(point4, point5, fill=color4, width=2)
        self.create_line(point5, point6, fill=color5, width=2)
        self.create_line(point6, point1, fill=color6, width=2)

        if fill != None:
            self.create_polygon(point1, point2, point3, point4, point5, point6, fill=fill)

class HexagonalGrid(HexaCanvas):
    def __init__(self, master, scale, grid_width, grid_height, *args, **kwargs):

        dx     = (scale**2 - (scale/2.0)**2)**0.5
        width  = 2 * dx * grid_width + dx
        height = 1.5 * scale * grid_height + 0.5 * scale

        HexaCanvas.__init__(self, master, background='silver', width=width, height=height, *args, **kwargs)
        self.setHexaSize(scale)

    def setCell(self, xCell, yCell, *args, **kwargs ):
        size = self.hexaSize
        dx = (size**2 - (size/2)**2)**0.5
        pix_x = dx + 2*dx*xCell
        if yCell%2 ==1 :
            pix_x += dx
        pix_y = size + yCell*1.5*size
        self.create_hexagon(pix_x, pix_y, *args, **kwargs)
################################################################################

def getCoordinates(board_state, player_colors):
    p1_color = player_colors[0]
    p2_color = player_colors[1]

    p1_pieces = np.argwhere(board_state == 1)
    p2_pieces = np.argwhere(board_state == 2)
    empty_cells = np.argwhere(board_state == 0)

    state_dict = {p1_color:p1_pieces, p2_color:p2_pieces, 'dark green':empty_cells}

    return state_dict


def render_default(hex_grid):
    def_color = 'gray'
    # Render default board
    f=0
    for j in range(0,5):
        for i in range(5-j,5+10+j):
            hex_grid.setCell(i,1+j+f, fill=def_color)
        for i in range(5-j,5+10+j+1):
            hex_grid.setCell(i,1+1+j+f, fill=def_color)
        f += 1
    f=0
    for j in range(0,5):
        for i in range(1+j,19-j):
            hex_grid.setCell(i,11+j+f, fill=def_color)
        if j!=4:
            for i in range(1+j+1,19-j):
                hex_grid.setCell(i,11+1+j+f, fill=def_color)
        f += 1
    hex_grid.setCell(10,10, fill='black')



def render(board_state, player_colors):
    '''
    board_state = [(plyr1 move, plyr1 color), (plyr2 move, plyr2 color), ... ]
    plyr move = [x,y]
    '''
    tk = Tk()

    hex_grid = HexagonalGrid(tk, scale=20, grid_width=21, grid_height=21)
    hex_grid.grid(row=0, column=0, padx=5, pady=5)

    def correct_quit(tk):
        tk.destroy()
        tk.quit()

    next_ = Button(tk, text = "-next-", command = lambda:correct_quit(tk))
    next_.grid(row=1, column=0)

    #-----------------------------------------
    # Render board state
    if board_state.shape == (20,20):
        state_dict = getCoordinates(board_state, player_colors)

        for color, coords in state_dict.items():
            for coord in coords:
                #print("Coord: ",coord)
                hex_grid.setCell(coord[0], coord[1], fill=color)

    tk.mainloop()
