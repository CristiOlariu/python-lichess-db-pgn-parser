import os
from typing import Dict

SEP = '│'  # ASCII 179


def read_opening_map(fn: str) -> Dict:
    opening_map = {}
    with open(fn, 'r') as f:
        for opening in f:
            opening_map[opening[7:-1]] = opening[:6]
    return opening_map


def _proc_game_result(result):
    return {
        '1-0': 'W',
        '0-1': 'B',
        '1/2-1/2': 'D'
    }.get(result, '*')


def _process_game_termination(termination):
    return {
        'Normal': 'N',
        'Time forfeit': 'T',
        'Abandoned': 'A',
        'Unterminated': 'U',
        'Rules infraction': 'R',
    }.get(termination, "*")


def _process_date(date):
    return date[:4] + date[5:7] + date[8:]


def _process_time(time):
    return str(int(time[:2])*3600 + int(time[3:5])*60 + int(time[6:]))
    # return f"{time[:2]}{time[3:5]}{time[6:]}"

def extract_headers(headers, opening_map=None):
    site = headers.get('Site', None)
    g_id = site.split("/")[-1] if site else ''
    # g_date = headers.get('UTCDate', '').replace('.', '')
    # g_date = _process_date(headers.get('UTCDate', ''))
    g_date = headers.get('UTCDate', '')
    g_time = headers.get('UTCTime', '')
    g_timesecs = _process_time(headers.get('UTCTime', ''))
    g_result = _proc_game_result(headers.get('Result', ''))
    g_eco = opening_map.get(f"{headers.get('ECO', '')}{SEP}{headers.get('Opening', '')}",
                            "?") if opening_map else headers.get('ECO', '')
    g_termination = _process_game_termination(headers.get('Termination', ''))
    g_tc = headers.get('TimeControl', '')

    g_wname = headers.get('White', '').replace(SEP, '')
    g_welo = headers.get('WhiteElo', '')
    g_welodiff = headers.get('WhiteRatingDiff', '')
    g_wtitle = headers.get('WhiteTitle', '')

    g_bname = headers.get('Black', '').replace(SEP, '')
    g_belo = headers.get('BlackElo', '')
    g_belodiff = headers.get('BlackRatingDiff', '')
    g_btitle = headers.get('BlackTitle', '')

    return g_id, g_date, g_time, g_timesecs, g_result, g_eco, g_termination, g_tc, g_wname, g_welo, g_welodiff, g_wtitle, g_bname, g_belo, g_belodiff, g_btitle


# def extract_clk(clks):
    # result = list()
    # for clk in clks:
    #     h, m, s = int(clk[0]), int(clk[2:4]), int(clk[5:])
    #     # h, m, s = int(h), int(m), int(s)
    #     result.append(h*3600 + m*60 + s)
    # return map(str, result)

def extract_clk(clk):
    if len(clk) == 7:
        return str(3600 * int(clk[0]) + 60 * int(clk[2:4]) + int(clk[5:]))
    else:
        h, m, s = clk.split(':')
        h, m, s = int(h), int(m), int(s)
        return str(h*3600 + m*60 + s)


def read_games(game_file, opening_map=None):
    line = game_file.readline()
    blank_lines = 0
    headers = {}
    moves = []
    clocks = []
    evals = []
    while line:
        # print(line)
        # a comment line: add to the headers dict
        if line[0] == "[":
            line = line[1:-3]
            (tag, val) = line.split(' "')
            headers[tag] = val

        # line starts with a digit: beginning or continuing of move chunks; works also if moves are on multiple lines
        if line[0] in "123456789":
            # print(line)
            line = line.split(" ")
            nextIsEval = False
            nextIsClock = False
            # print(line)
            for l in line:
                # if this is clk
                if nextIsClock:
                    nextIsClock = False
                    clocks.append(l[:-1])  # remove the ] from end of line
                    # continue

                # if this is eval
                elif nextIsEval:
                    nextIsEval = False
                    evals.append(l[:-1])  # remove the ] from end of line
                    # continue

                # match moves: all pawn moves, big piece moves, and castles
                elif l[0] in "abcdefghNBQRKO":
                    moves.append(l)

                # check if next is clock: if so, go to the next element and get clock value
                elif l[:5] == "[%clk":
                    nextIsClock = True
                    # continue

                # check if next is eval: if so, go to the next element and get evaluation value
                elif l[:6] == "[%eval":
                    nextIsEval = True
                    # continue

        # if empty line, increase counter
        if line[0] == "\n":
            blank_lines += 1

        # at two empty lines, a game ends: yield all parsed info
        if blank_lines == 2:
            g_id, g_date, g_time, g_timesecs, g_result, g_eco, g_termination, g_tc, g_wname, g_welo, g_welodiff, g_wtitle, g_bname, g_belo, g_belodiff, g_btitle = extract_headers(
                headers, opening_map)
            g_moves = " ".join(moves)
            g_mate = "N"
            if g_moves:
                if g_moves[-1] == "#":
                    g_mate = "Y"

            g_nbMoves = str(len(moves))
            g_hasEval = "Y" if len(evals) else "N"
            g_clocks = " ".join(map(extract_clk, clocks))
            g_hasClock = "Y" if len(clocks) else "N"

            g_evals = " ".join(evals)
            if (g_mate == 'Y') & (g_hasEval == 'Y'):
                # g_evals += f' #{g_mate}'
                g_evals += f' #'

            result = SEP.join([
                g_id,
                g_date,
                g_time,
                g_timesecs,
                g_result,
                g_termination,
                g_mate,
                g_hasEval,
                g_hasClock,
                g_nbMoves,
                g_eco,
                g_tc,
                g_wname,
                g_welo,
                g_welodiff,
                g_wtitle,
                g_bname,
                g_belo,
                g_belodiff,
                g_btitle,
                g_moves,
                g_evals,
                g_clocks
            ])

            # RESETS
            blank_lines = 0
            headers = dict()
            moves = list()
            clocks = list()
            evals = list()
            yield result

        line = game_file.readline()


def write_partial_result(fn, output_folder, games, result_file_counter):
    fn = fn.split("/")[-1]  # TODO: extract filename using the Path lib
    fn = fn+f'.part_{result_file_counter:06}.cri'
    with open(output_folder + fn, 'w') as result_file:
        result_file.writelines(games)
        result_file.close()
    os.system(f"gzip -f {output_folder}{fn}")
