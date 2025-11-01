"""
Headless AI vs AI runner for testing Mancala logic and the alphabeta implementation.
Runs many games quickly without Pygame and reports win/draw statistics.
"""
from mancala_core import Mancala, alphabeta, INF

def play_game(depth_south=6, depth_north=6, verbose=False):
    state = Mancala()
    north_to_move = False

    while True:
        if state.is_terminal():
            state.finalize_if_terminal()
            ns, ss = state.a[Mancala.NORTH_STORE], state.a[Mancala.SOUTH_STORE]
            if verbose: print(f"Final {ns}-{ss}")
            if ns > ss: return 'north', ns-ss
            if ss > ns: return 'south', ss-ns
            return 'draw', 0

        depth = depth_north if north_to_move else depth_south
        _, best = alphabeta(state, depth, -INF, INF, north_to_move)
        if best == -1:
            state.finalize_if_terminal(); continue

        repeat = state.move(best, draw_step=None, north_turn=north_to_move, step_delay_ms=0)
        if not repeat:
            north_to_move = not north_to_move

def run_tournament(n=50, depth_a=6, depth_b=6):
    stats = {'north':0, 'south':0, 'draw':0}
    for i in range(n):
        winner, margin = play_game(depth_a, depth_b)
        stats[winner] += 1
    return stats

if __name__ == '__main__':
    print('Running 50 headless games (both depth=6)')
    stats = run_tournament(50, 6, 6)
    print('Results:', stats)
'''ai_vs_ai_headless.py ends here'''