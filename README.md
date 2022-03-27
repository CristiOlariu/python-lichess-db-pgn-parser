# Desciption

This repo is parsing and transforming chess games from the lichess database (https://database.lichess.org/) from the pgn format to another custom 1-liner format, more suitable at being ingested by machines to extract insights, e.g. via Spark.

# Requirements

Python 3.8 and above.

No external libraries are needed, the idea is to be able to parse the pgn games with built-in libraries, and not rely on generic pgn parsers which will have to use some regex at some point to deal with the "too" flexible pgn standard, however the lichess db exports are more "clean" and thus can be parsed without regex.

# Transforms what to what?

Sample input:

```
[Event "Rated Rapid game"]
[Site "https://lichess.org/mAEz2AcC"]
[Date "2018.12.31"]
[Round "-"]
[White "AliKhaled"]
[Black "ifospor"]
[Result "0-1"]
[UTCDate "2018.12.31"]
[UTCTime "23:00:01"]
[WhiteElo "1702"]
[BlackElo "1628"]
[WhiteRatingDiff "-13"]
[BlackRatingDiff "+13"]
[ECO "C45"]
[Opening "Scotch Game: Haxo Gambit"]
[TimeControl "600+0"]
[Termination "Normal"]

1. e4 { [%eval 0.12] [%clk 0:10:00] } 1... e5 { [%eval 0.37] [%clk 0:10:00] } 2. Nf3 { [%eval 0.23] [%clk 0:09:58] } 2... Nc6 { [%eval 0.15] [%clk 0:09:59] } 3. Bc4 { [%eval 0.1] [%clk 0:09:56] } 3... Bc5 { [%eval 0.24] [%clk 0:09:56] } 4. d4 { [%eval -0.16] [%clk 0:09:48] } 4... exd4 { [%eval 0.0] [%clk 0:09:53] } 5. c3 { [%eval 0.0] [%clk 0:09:46] } 5... Nf6 { [%eval 0.14] [%clk 0:09:44] } 6. Bg5? { [%eval -0.86] [%clk 0:09:37] } 6... O-O? { [%eval 0.3] [%clk 0:09:41] } 7. e5? { [%eval -0.86] [%clk 0:09:11] } 7... Re8? { [%eval 0.64] [%clk 0:09:19] } 8. Bxf6?? { [%eval -2.88] [%clk 0:08:25] } 8... Qxf6 { [%eval -2.83] [%clk 0:09:13] } 9. O-O { [%eval -3.04] [%clk 0:08:23] } 9... Nxe5 { [%eval -2.67] [%clk 0:09:10] } 10. Re1?? { [%eval -8.32] [%clk 0:07:45] } 10... Nxf3+ { [%eval -8.1] [%clk 0:09:05] } 11. gxf3 { [%eval -8.14] [%clk 0:07:44] } 11... Rxe1+ { [%eval -8.21] [%clk 0:09:04] } 12. Qxe1 { [%eval -8.12] [%clk 0:07:42] } 12... dxc3?? { [%eval -4.33] [%clk 0:08:49] } 13. Qe8+?! { [%eval -5.28] [%clk 0:07:25] } 13... Bf8 { [%eval -5.38] [%clk 0:08:46] } 14. Nxc3 { [%eval -5.4] [%clk 0:07:22] } 14... Qxf3? { [%eval -3.35] [%clk 0:08:33] } 15. h3? { [%eval -5.12] [%clk 0:05:43] } 15... d6?! { [%eval -4.43] [%clk 0:07:47] } 16. Nd5?? { [%eval -10.3] [%clk 0:03:46] } 16... Bxh3 { [%eval -10.02] [%clk 0:07:02] } 17. Ne7+ { [%eval -18.8] [%clk 0:02:27] } 17... Kh8 { [%eval -18.43] [%clk 0:06:58] } 18. Ng6+?! { [%eval #-9] [%clk 0:01:44] } 18... hxg6?! { [%eval -24.37] [%clk 0:06:45] } 0-1
```

to

```
mAEz2AcC│20181231│82801│B│N│N│Y│Y│36│C45014│600+0│AliKhaled│1702│-13││ifospor│1628│+13││e4 e5 Nf3 Nc6 Bc4 Bc5 d4 exd4 c3 Nf6 Bg5? O-O? e5? Re8? Bxf6?? Qxf6 O-O Nxe5 Re1?? Nxf3+ gxf3 Rxe1+ Qxe1 dxc3?? Qe8+?! Bf8 Nxc3 Qxf3? h3? d6?! Nd5?? Bxh3 Ne7+ Kh8 Ng6+?! hxg6?!│0.12 0.37 0.23 0.15 0.1 0.24 -0.16 0.0 0.0 0.14 -0.86 0.3 -0.86 0.64 -2.88 -2.83 -3.04 -2.67 -8.32 -8.1 -8.14 -8.21 -8.12 -4.33 -5.28 -5.38 -5.4 -3.35 -5.12 -4.43 -10.3 -10.02 -18.8 -18.43 #-9 -24.37│600 600 598 599 596 596 588 593 586 584 577 581 551 559 505 553 503 550 465 545 464 544 462 529 445 526 442 513 343 467 226 422 147 418 104 405
```

with the following field meaning, separated by "│" (ASCII 179):
```
 1. id: 
    game id - the unique game id as provided by lichess. Add this id to the path, e.g. https://lichess.org/GAME_ID and the original game from lichess will be retrieved.

 2. date: 
    date, without the original periods (".") to save some space in the output files (maybe...)

 3. time: 
    reformated "HH:MM:SS" to the second of the day, so a number from 0 corresponding to 00:00:00 up to 86399 which corresponds to 23:59:59. 
    
    Rationale for this: save time when using Spark or other big data processing frameworks, when searching for time-related insights, such as worst 24 hours in move accuracy.

 4. result: 
    'W' --> '1-0'
    'B' --> '0-1'
    'D' --> '1/2-1/2'
    or '*' if there is no termination (abandoned games, etc.)
 
 5. termination: 
    'N' --> 'Normal'
    'T' --> 'Time forfeit'
    'A' --> 'Abandoned'
    'U' --> 'Unterminated'
    'R' --> 'Rules infraction'
    or '*' if the game termination could not be established

 6. mate: 
    flag with "Y" or "N" indicating if the game ended in mate. It's not a pgn field, added here for faster future queries.

 7. hasEval:
    flag with "Y" or "N" indicating if the game has game engine evaluation

 8. hasClock:
    flag with "Y" or "N" indicating if the game has remaining time on the clock for each player.

 9. nbMoves:
    total number of moves. It's not a pgn field, added here for faster future queries.

10. eco:
    the opening ECO (Encyclopedia of Chess Openings) code. 
    
    This field has been extended to comprise also the Opening field, so that "A04" and "Reti Opening" have become "A04006", so the 6th A04 opening. There is an opening map, mapping all these various 3-letter ECO codes and the Opening field to a 6-letter code in openings_map.txt. 

    Rationale for this: the ECO code is not sufficient to uniquely categorize each chess opening, hence the need to clarification coming from the Opening field. However the Opening field is text, meaning it can be of any length, and is also prone to duplicates due to different spelling, e.g. Réti and Reti.

    After parsing all games from lichess up to Feb 2022, a mapping was extracted that should, in theory, cover all possible chess ECO and Openings, based on the 3,099,534,127 parsed games.

11. tc: 
    time control, as per the original pgn format.

12. wname:
    white's name

13. welo:
    white's elo

14. welodiff:
    white's elo diff after the game concluded, i.e. how many elo points have been lost or won

15. wtitle:
    white's title (e.g. GM)

16: bname:
    black's name

17: belo:
    black's elo

18: belodiff:
    black's elo diff after the game concluded, i.e. how many elo points have been lost or won

19: btitle:
    black's title (e.g. GM)

20. moves: 
    a space-separated list of moves from the game, preserving NAG's if the game was analysed (e.g. ?? means a blunder, etc.). These standard games always start from move one - pgn supports starting from any move if an initial position other than default is provided via a FEN - however, lichess exports full games from move 1.

    The first item in the list is white's move, then the second is black's move and so on, alternating.

    Can be empty if there were no moves performed.

21. evals: 
    a space-separated list of evaluations, if the games was analyzed with a game engine.

    The first element in the list is the evaluation after white's move, the second item is the evaluation after black's move, and so on, alternating.

    Slight change: if a game ended in mate, an '#' is appended as last evaluation in order for the length of the moves, evals and locks to be the same, or else evals would be 1 short.

22. clocks:
    a space-separated list of remaining time on the clock.

    The first element in the list is the remaining time after white's move, the second item is the remaining time after black's move, and so on, alternating.

    The original format is H:MM:SS which was tranformed into total seconds, e.g. 0:10:00 was transformed to 600.

    Rationale: subsequent queries are faster in integer values than string formats such as H:MM:SS, right ? :D
    
```

# How to run

Place pgn.gz2 files from lichess in the main folder of this repo (test it with smaller files, e.g. from 2013 as the more recent ones are large.)

The program expects 2 parameters:

- chunk size: lichess exports are 1 file per month, but that'snot great for parallel parsing, so this reformatter can chunk the data so it contains a specific number of games per chunk. The chunks will be in gz. Why gz ... is supported by Spark, good compression, fast decompression on the fly.

- pgn file, as bz2 archive - lichess exports are bz2.

Example:
```
$ python3 main.py 100_000 lichess_db_standard_rated_2019-01.pgn.bz2
```

Where 100_000 is the chunk size, and lichess_db_standard_rated_2019-01.pgn.bz2 is the pgn archive to be parsed.

# Optional

The fast_parsing_lib.py file can be made as cython module, which will be faster than the python object file.

To do that, the setup.py script can be used:

```
python3 setup.py build_ext --inplace
```

Nothing else need to be done, the main.py works the same, and will pick the lib from the cython files, however with the setup.py fails, might be from missing cython or other libraries that are not mandatory for main.py to work.
