#!/usr/bin/env python3

from curses import wrapper
import curses
import random
import os
import sys
import itertools

LETTER_Q_ASCII_CODE = 113

HANGMANPICS = [
    [
        "  +---+",
        "  |   |",
        "      |",
        "      |",
        "      |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        "      |",
        "      |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        "  |   |",
        "      |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        " /|   |",
        "      |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        " /|\  |",
        "      |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        " /|\  |",
        " /    |",
        "      |",
        "=========",
    ],
    [
        "  +---+",
        "  |   |",
        "  O   |",
        " /|\  |",
        " / \  |",
        "      |",
        "=========",
    ],
]


class Hangman:
    words = []
    word = None
    letters = set()
    attempt = 0

    def __init__(self, wordlist=None, *args, **kwargs):
        if wordlist:
            self.words = self.load_wordlist(wordlist)

    def random_word(self, min_length=4, max_length=60):
        if not self.words:
            return None

        words = [word for word in self.words if min_length < len(word) < max_length]

        return random.choice(words).strip()

    def load_wordlist(self, wordlist):
        with open(wordlist) as handle:
            self.words = handle.readlines()

        return self.words

    def draw_hangman(self, screen, height, width, position_y, position_x):
        box1 = curses.newwin(height, width, position_y, position_x)
        box1.box()
        box1.bkgd(" ", curses.color_pair(4) | curses.A_BOLD)

        height, width = box1.getmaxyx()

        for index, t in enumerate(HANGMANPICS[self.attempt]):
            max_height = max(1, len(HANGMANPICS[self.attempt]))
            max_width = max([len(t) for t in HANGMANPICS[self.attempt]])

            box1.addstr(
                ((height // 2) - (max_height // 2)) + index,
                (width // 2) - (max_width // 2),
                str(t),
                curses.color_pair(4),
            )

        screen.refresh()
        box1.refresh()

    def draw_letters(self, screen, height, width, position_y, position_x):
        box1 = curses.newwin(height, width, position_y, position_x)
        box1.box()
        box1.bkgd(" ", curses.color_pair(4))

        height, width = box1.getmaxyx()

        box1.addstr(
            1, 2, 'Welcome to hangman.  Press "q" at anytime to quit out of the game.'
        )
        box1.addstr(
            2,
            2,
            "You have {chances} chance(s) left to solve the puzzle before you lose.".format(
                chances=len(HANGMANPICS) - self.attempt
            ),
        )

        box1.addstr(
            4,
            2,
            "You've chosen the following letters: {letters}".format(
                letters=" ".join(self.letters)
            ),
        )

        found_letters = set(self.word) & self.letters

        revealed_letters = {
            letter for letter in list(self.word) if letter in found_letters
        }

        masked_word = " ".join(
            [letter in revealed_letters and letter or "_" for letter in list(self.word)]
        )

        box1.addstr(
            6,
            2,
            "Your word so far is ({masked_word}): {word}".format(
                masked_word=masked_word, word=" ".join(revealed_letters)
            ),
        )

        screen.refresh()
        box1.refresh()

    def winner(self):
        # Check if we're a winner
        if len((set(self.word) ^ self.letters) & set(self.word)) == 0:
            return True

        return False

    def run(self, stdscr):
        def game(stdscr):
            cursor_x = 0
            cursor_y = 0

            stdscr = curses.initscr()

            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
            curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)

            height, width = stdscr.getmaxyx()

            stdscr.clear()

            key = 0

            winner = False
            last_characters = []

            bh, bw = 20, 20

            self.word = self.random_word()

            self.draw_hangman(stdscr, bh, bw, 1, 1)
            self.draw_letters(stdscr, bh, width - (bw + 4), 1, bw + 2)

            # Keep playing while the user hasn't hit the key 'q' or they haven't
            # exceeded the number of hangman rounds/attempts

            while all([key != LETTER_Q_ASCII_CODE, self.attempt < len(HANGMANPICS)]):
                self.draw_hangman(stdscr, bh, bw, 1, 1)
                self.draw_letters(stdscr, bh, width - (bw + 4), 1, bw + 2)

                key = stdscr.getch()

                if any([ord("a") <= key <= ord("z"), ord("A") <= key <= ord("Z")]):
                    # Check if the value entered matches one of the characters
                    # in random word, if so, add it the set
                    character = chr(key)

                    if character not in self.word:
                        self.attempt += 1

                    self.letters.add(character)

                winner = self.winner()

                if winner:
                    break

            stdscr.clear()

            if winner:
                message = 'Congratulations, you solved the word "{word}" in {attempt} attempt(s)'.format(
                    word=self.word, attempt=self.attempt
                )

            else:
                message = 'You failed to guess the word "{word}" after {attempt} attempts'.format(
                    word=self.word, attempt=self.attempt
                )

            exit_message = "Press any key to exit, the game is over..."

            stdscr.addstr(height // 2, (width // 2) - (len(message) // 2), message)

            stdscr.addstr(
                (height // 2) + 2, (width // 2) - (len(exit_message) // 2), exit_message
            )

            stdscr.refresh()
            stdscr.getch()

        return game(stdscr)


if __name__ == "__main__":
    hangman = Hangman("words.txt")
    wrapper(hangman.run)
