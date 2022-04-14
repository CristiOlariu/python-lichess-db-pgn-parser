import bz2
from fast_parsing_lib import write_partial_result, read_games, read_opening_map

if __name__ == '__main__':
    from time import time
    from game_counts import game_counts
    import sys

    # size at which a new output file to be created
    chunk_size = eval(sys.argv[1])
    output_folder = sys.argv[2]
    fn = sys.argv[3]  # filename of input file

    print(fn)

    games = []
    total_games = game_counts.get(fn, 100_000_000)

    opening_map = read_opening_map("./openings_map.txt")

    # with open(fn, "r") as game_file:  # TODO: check if file is raw or compressed, and choose the correct file opener
    with bz2.open(fn, "rt") as game_file:
        start_time = time()
        counter = 0
        result_file_counter = 0
        _chunk_st = time()
        for game in read_games(game_file, opening_map):

            if game:
                games.append(game + '\n')
                counter += 1

            if (counter % chunk_size) == 0:
                speed = counter/(time()-start_time)
                print(
                    f"{fn}\nProcessed: took {time()-_chunk_st:.2f} sec -- {counter} at speed: {speed:.2f} games/second")
                print(
                    f"{fn}\nEstimated time remaining: {((total_games-counter)/speed)/3600:.2f} hours")
                _st = time()
                write_partial_result(
                    fn, output_folder, games, result_file_counter)
                print(f"{fn}\nWriting gz took: {time()-_st:.2f} secs")
                games = list()
                result_file_counter += 1
                _chunk_st = time()

        write_partial_result(fn, output_folder, games, result_file_counter)
        game_file.close()

    print(f"Finished {fn}.\nTook: {time()-start_time} seconds.\nProcessed: {counter} at speed: {counter/(time()-start_time):.2f} games/second")
