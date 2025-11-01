import time
from typing import Tuple

# Core Mancala game logic (no pygame)
class Mancala:
    SOUTH_PITS = list(range(0, 6))
    SOUTH_STORE = 13
    NORTH_PITS = list(range(7, 13))
    NORTH_STORE = 6

    def __init__(self, arr=None):
        self.a = list(arr) if arr is not None else [4,4,4,4,4,4,0, 4,4,4,4,4,4,0]

    def copy(self): return Mancala(self.a)

    @staticmethod
    def opposite(idx:int)->int: return 12 - idx

    def is_terminal(self)->bool:
        return sum(self.a[0:6]) == 0 or sum(self.a[7:13]) == 0

    def finalize_if_terminal(self):
        if sum(self.a[0:6]) == 0:
            self.a[Mancala.NORTH_STORE] += sum(self.a[7:13])
            for i in range(7,13): self.a[i] = 0
        elif sum(self.a[7:13]) == 0:
            self.a[Mancala.SOUTH_STORE] += sum(self.a[0:6])
            for i in range(0,6): self.a[i] = 0

    def legal_moves(self, north_turn: bool):
        pits = Mancala.NORTH_PITS if north_turn else Mancala.SOUTH_PITS
        return [i for i in pits if self.a[i] > 0]

    def move(self, pit:int, draw_step=None, north_turn:bool=False, step_delay_ms:int=0)->bool:
        """
        Make a move from 'pit'. Return True if player gets an extra turn.
        Draw callback is invoked AFTER each single seed is dropped.
        This core implementation doesn't depend on pygame; uses time.sleep for delays.
        """
        stones = self.a[pit]
        self.a[pit] = 0
        idx = pit

        while stones > 0:
            i = idx
            if i > 6:
                i += 1             
                i = i % 14
                if i == 6:
                    continue
                else:
                    self.a[i % 14] += 1
                    idx = i
                stones -= 1
            else:
                i += 1
                i = i % 14
                if i == 13:
                    continue
                else:
                    self.a[i % 14] += 1
                    idx = i
                stones -= 1

            if draw_step:
                draw_step(idx)
                if step_delay_ms > 0:
                    time.sleep(step_delay_ms/1000.0)

        # Capture: last stone in empty own pit captures opposite
        repeat = False
        if north_turn:
            if idx in Mancala.NORTH_PITS and self.a[idx] == 1:
                opp = Mancala.opposite(idx)
                if self.a[opp] > 0:
                    self.a[Mancala.NORTH_STORE] += self.a[opp] + 1
                    self.a[idx] = 0; self.a[opp] = 0
            if idx == Mancala.NORTH_STORE:
                repeat = True
        else:
            if idx in Mancala.SOUTH_PITS and self.a[idx] == 1:
                opp = Mancala.opposite(idx)
                if self.a[opp] > 0:
                    self.a[Mancala.SOUTH_STORE] += self.a[opp] + 1
                    self.a[idx] = 0; self.a[opp] = 0
            if idx == Mancala.SOUTH_STORE:
                repeat = True

        self.finalize_if_terminal()
        return repeat


def evaluate(s:Mancala)->int:
    south_store = s.a[Mancala.SOUTH_STORE]
    north_store = s.a[Mancala.NORTH_STORE]
    south_side = sum(s.a[0:6])
    north_side = sum(s.a[7:13])
    return (north_store - south_store) * 100 + int((north_side - south_side) * 10)

INF = 10**9

def alphabeta(state:Mancala, depth:int, alpha:int, beta:int, north_to_move:bool)->Tuple[int,int]:
    if depth==0 or state.is_terminal(): return evaluate(state), -1
    moves = state.legal_moves(north_to_move)
    if not moves: return evaluate(state), -1
    best_move = moves[0]

    if north_to_move:
        value = -INF
        for m in moves:
            s2 = state.copy()
            rep = s2.move(m, None, True)
            next_depth = depth if rep else depth-1
            next_player = True if rep else False
            val,_ = alphabeta(s2, next_depth, alpha, beta, next_player)
            if val > value:
                value, best_move = val, m
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value, best_move
    else:
        value = INF
        for m in moves:
            s2 = state.copy()
            rep = s2.move(m, None, False)
            next_depth = depth if rep else depth-1
            next_player = False if rep else True
            val,_ = alphabeta(s2, next_depth, alpha, beta, next_player)
            if val < value:
                value, best_move = val, m
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value, best_move
'''mancala_core.py ends here'''