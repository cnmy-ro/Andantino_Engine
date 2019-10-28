'''
-ENGINE UTILITIES-

Bulky and less frequently used utility functions for the engine
'''

__author__ = "Chinmay Rao (i6218054)"

def buildNeighborhoodDict():
    ''' Return neighbourhood of all the cells on the board '''
    ''' Return type: Dictionary '''
    nbhood_dict = {}

    f=0
    for j in range(0,5):
        for i in range(5-j,5+10+j):
            #hex_grid.setCell(i,1+j+f, fill=def_color)
            k = 1+j+f
            nbhood_dict[(i,k)] = [(i,k-1),(i-1,k),(i,k+1),(i+1,k+1),(i+1,k),(i+1,k-1)] ##

        for i in range(5-j,5+10+j+1):
            #hex_grid.setCell(i,1+1+j+f, fill=def_color)
            k = 1+1+j+f
            nbhood_dict[(i,k)] =[(i-1,k-1),(i-1,k),(i-1,k+1),(i,k+1),(i+1,k),(i,k-1)]
        f += 1
    f=0
    for j in range(0,5):
        for i in range(1+j,19-j):
            #hex_grid.setCell(i,11+j+f, fill=def_color)
            k = 11+j+f
            nbhood_dict[(i,k)] = [(i,k-1),(i-1,k),(i,k+1),(i+1,k+1),(i+1,k),(i+1,k-1)]
        if j!=4:
            for i in range(1+j+1,19-j):
                #hex_grid.setCell(i,11+1+j+f, fill=def_color)
                k = 11+1+j+f
                nbhood_dict[(i,k)] = [(i-1,k-1),(i-1,k),(i-1,k+1),(i,k+1),(i+1,k),(i,k-1)]
        f += 1

    # -- Edge and corner adjustments --
    # Top edge
    for i in range(5,15):
        nbhood_dict[(i,1)] = [(i-1,1),(i,2),(i+1,2),(i+1,1)]
    # Top-left edge
    f=1
    for i in range(5,0,-1):
        nbhood_dict[(i,f)] = [(i,f+1),(i+1,f+1),(i+1,f),(i+1,f-1)]
        f += 1
        nbhood_dict[(i,f)] = [(i-1,f+1),(i,f+1),(i+1,f),(i,f-1)]
        f += 1
    # Bottom-left edge
    f=10
    for i in range(1,6):
        nbhood_dict[(i,f)] = [(i,f+1),(i+1,f),(i,f-1),(i-1,f-1)]
        f += 1
        nbhood_dict[(i,f)] = [(i+1,f+1),(i+1,f),(i+1,f-1),(i,f-1)]
        f += 1
    # Bottom edge
    for i in range(5,15):
        nbhood_dict[(i,19)] = [(i-1,19),(i,18),(i+1,18),(i+1,19)]
    # Bottom-right edge
    f=18
    for i in range(15,19):
        nbhood_dict[(i,f)] = [(i-1,f+1),(i-1,f),(i-1,f-1),(i,f-1)]
        f -= 1
        nbhood_dict[(i,f)] = [(i,f+1),(i-1,f),(i,f-1),(i+1,f-1)]
        f -= 1
    # Top-right edge
    f=2
    for i in range(15,19):
        nbhood_dict[(i,f)] = [(i-1,f-1),(i-1,f),(i-1,f+1),(i,f+1)]
        f += 1
        nbhood_dict[(i,f)] = [(i,f-1),(i-1,f),(i,f+1),(i+1,f+1)]
        f += 1
    # Corners
    nbhood_dict[(5,1)] = [(5,2),(6,2),(6,1)]
    nbhood_dict[(1,10)] = [(1,9),(2,10),(1,11)]
    nbhood_dict[(5,19)] = [(5,18),(6,18),(6,19)]
    nbhood_dict[(14,19)] = [(13,19),(14,18),(15,18)]
    nbhood_dict[(19,10)] = [(18,9),(18,10),(18,11)]
    nbhood_dict[(14,1)] = [(13,1),(14,2),(15,2)]

    return nbhood_dict


################################################################################

def getAltBoardState(board_state):
    ''' Return a transformed board state with alternate coord system (ABCD-1234) '''
    ''' Returned dictionary format: {(A,1):0,(A,2):0,...}'''

    alt_board_state = {}
    A_idx1 = ['A','C','E','G','I']
    for a in range(len(A_idx1)):
        f=1
        for i in range(5+2*a,0+a,-1):
            alt_board_state[(A_idx1[a],f)] = board_state[i,f]
            f += 1
            alt_board_state[(A_idx1[a],f)] = board_state[i,f]
            f += 1
    A_idx2 = ['B','D','F','H','J']
    for a in range(len(A_idx2)):
        f=1
        for i in range(6+2*a,1+a,-1):
            alt_board_state[(A_idx2[a],f)] = board_state[i,f]
            f += 1
            alt_board_state[(A_idx2[a],f)] = board_state[i,f]
            f += 1
        alt_board_state[(A_idx2[a],f)] = board_state[i-1,f]
    A_idx3 = ['K','M','O','Q','S']
    for a in range(len(A_idx3)):
        f=1+2*a
        for i in range(15+a,6+2*a,-1):
            f += 1
            alt_board_state[(A_idx3[a],f)] = board_state[i,f]
            if i!= 15+a:
                f += 1
                alt_board_state[(A_idx3[a],f)] = board_state[i,f]
        alt_board_state[(A_idx3[a],f+1)] = board_state[i-1,f+1]
    A_idx3 = ['L','N','P','R']
    for a in range(len(A_idx3)):
        f=2+2*a
        for i in range(15+a,7+2*a,-1):
            f += 1
            alt_board_state[(A_idx3[a],f)] = board_state[i,f]
            f += 1
            alt_board_state[(A_idx3[a],f)] = board_state[i,f]
        alt_board_state[(A_idx3[a],f+1)] = board_state[i-1,f+1]

    return alt_board_state

################################################################################
'''                     Board coordinate mapping functions                   '''
################################################################################

def getAltToDefMapping():
    ''' Alternate to Default coordinate mapping'''
    ''' Return type: Dictionary '''
    alt_to_def = {}
    A_idx1 = ['A','C','E','G','I']
    for a in range(len(A_idx1)):
        f=1
        for i in range(5+2*a,0+a,-1):
            alt_to_def[(A_idx1[a],f)] = (i,f)
            f += 1
            alt_to_def[(A_idx1[a],f)] = (i,f)
            f += 1
    A_idx2 = ['B','D','F','H','J']
    for a in range(len(A_idx2)):
        f=1
        for i in range(6+2*a,1+a,-1):
            alt_to_def[(A_idx2[a],f)] = (i,f)
            f += 1
            alt_to_def[(A_idx2[a],f)] = (i,f)
            f += 1
        alt_to_def[(A_idx2[a],f)] = (i-1,f)
    A_idx3 = ['K','M','O','Q','S']
    for a in range(len(A_idx3)):
        f=1+2*a
        for i in range(15+a,6+2*a,-1):
            f += 1
            alt_to_def[(A_idx3[a],f)] = (i,f)
            if i!= 15+a:
                f += 1
                alt_to_def[(A_idx3[a],f)] = (i,f)
        alt_to_def[(A_idx3[a],f+1)] = (i-1,f+1)
    A_idx3 = ['L','N','P','R']
    for a in range(len(A_idx3)):
        f=2+2*a
        for i in range(15+a,7+2*a,-1):
            f += 1
            alt_to_def[(A_idx3[a],f)] = (i,f)
            f += 1
            alt_to_def[(A_idx3[a],f)] = (i,f)
        alt_to_def[(A_idx3[a],f+1)] = (i-1,f+1)

    return alt_to_def

def getDefToAltMapping(alt_to_def_mapping):
    ''' Default to Alternate coordinate mapping'''
    ''' Return type: Dictionary'''
    def_to_alt_mapping = {}
    for key, val in alt_to_def_mapping.items():
        def_to_alt_mapping[val] = key
    return def_to_alt_mapping
