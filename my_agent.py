__author__ = "<hayden Knox>"
__organization__ = "COSC343/AIML402, University of Otago"
__email__ = "<hknox67@gmail.com>"

from collections import Counter
import pandas as pd


class WordleAgent():
    """
        A class that encapsulates the code dictating the
        behaviour of the Wordle playing agent

        ...

        Attributes
        ----------
        dictionary : list
            a list of valid words for the game
        letter : list
            a list containing valid characters in the game
        word_length : int
            the number of letters per guess word
        num_guesses : int
            the max. number of guesses per game
        mode: str
            indicates whether the game is played in 'easy' or 'hard' mode

        Methods
        -------
        AgentFunction(percepts)
            Returns the next word guess given state of the game in percepts
        """

    def __init__(self, dictionary, letters, word_length, num_guesses, mode):
        """
        :param dictionary: a list of valid words for the game
        :param letters: a list containing valid characters in the game
        :param word_length: the number of letters per guess word
        :param num_guesses: the max. number of guesses per game
        :param mode: indicates whether the game is played in 'easy' or 'hard' mode
        """
        self.dictionary = dictionary
        self.mode = mode
        self.num_guesses = num_guesses
        self.word_length = word_length
        self.letters = letters
        self.attempts = set()
        self.examined = set()
        self.positive_count = 0
        self.difficulty = False
        if self.mode == "hard":
            self.difficulty = True
        self.set_dictionary = dictionary.copy()
        self.guess_attempt = ""
        # Removes the letters from the dictionary which do not match the criteria in the settings.py file
        self.alphabetical_frequency = Counter(" ".join(self.set_dictionary))
        # This code block removes the words in selected dictionary
        # which do not match the word length citeria
        for entry in self.set_dictionary:
            if len(entry) != self.word_length:
                self.set_dictionary.remove(entry)
        self.character_frequency = Counter()
        data = list()
        for entry in self.set_dictionary:
            data.append(self.split_words(entry))
        self.dictionary_frame = pd.DataFrame(data=data,
                                             columns=[f'character_{ch + 1}' for ch in range(word_length)])
        self.dictionary_frame['entry'] = dictionary

    def return_zero(self, examined, frame_data, wrong_indx):
        if examined[wrong_indx] not in frame_data and examined[wrong_indx] not in self.examined:
            entry = self.dictionary_frame['entry'].apply(lambda ch: examined[wrong_indx] not in ch)
            self.dictionary_frame = self.dictionary_frame[entry]

    def letter_state1(self, examined, hit_indx, frame_data):
        """
        :param examined: this is a collection of letters which the dataframe has already processed.
        :param hit_indx: Variable corresponds to the character index values within a dataframe tuple which are placed correctly
        :param frame_data: the current instance of a dataframe to be manipulated.
        :return: N/A
        """
        if examined[hit_indx] not in self.examined:
            self.examined.add(examined[hit_indx])
        frame_data[hit_indx] = examined[hit_indx]

    def letter_state_negative(self, examined, wrong_indx):
        """
        :param examined: this is a collection of dataframe tuple letters
        :param wrong_indx: ariable corresponds to the character index values within a dataframe tuple which are placed incorrectly
        :return: N/A
        """
        self.dictionary_frame = self.dictionary_frame[self.dictionary_frame[f'character_{wrong_indx + 1}'] != examined[wrong_indx]]
        entry = self.dictionary_frame['entry'].str.contains(examined[wrong_indx])
        self.dictionary_frame = self.dictionary_frame[entry]
        if examined[wrong_indx] not in self.examined:
            self.examined.add(examined[wrong_indx])

    def positive_counter(self, positive_count, letter_states):
        """
        :param positive_count: this is the letter value counter for all letters in letter state who returned from wordle a 1 value
        :param letter_states: this is a collection are the values of either 1, -1, or 0 returned from wordle.py in the previous tuple dataframe guess
        :return: the number of positive 1 values within a tuple word guess of the dataframe.
        """
        for i in letter_states:
            if i == 1:
                positive_count += 1
        return positive_count

    def split_words(self, word):
        """
        :param word: this is a single word passed from the instantiated dictionary from the wordle.py script
        :return: A list instance which divides words into their individual characters as a list.
        """
        return list(word)

    def new_guess_calculator(self, indexes):
        """
        :param indexes:
        :return: the new highest scored guess tuple value
        """
        maximum_value = 0
        current_list = self.dictionary_frame['entry']
        current_list.tolist()
        old_set = self.set_dictionary
        remaining = set(self.letters) - self.attempts
        remaining = remaining.intersection(set(''.join(current_list)))
        for ch in old_set:
            current_value = 0
            for indx in remaining:
                if indx in ch:
                    current_value += 1
            if maximum_value < current_value:
                maximum_value = current_value
                self.guess_attempt = ch
        for ch in self.guess_attempt:
            self.attempts.add(ch)
        return self.guess_attempt

    def get_tuple_score(self, word):
        score = 0
        x = 0
        for y in list(word):
            if y not in self.examined:
                score += self.character_frequency[x + 1][y]
            x += 1
        return score

    def return_word(self):
        for i in range(self.word_length):
            self.character_frequency[i + 1] = Counter(self.dictionary_frame[f'character_{i + 1}'])
        temp = list()
        for item in self.dictionary_frame['entry']:
            temp.append(self.get_tuple_score(item))
        self.dictionary_frame['word'] = temp
        self.dictionary_frame = self.dictionary_frame.sort_values(by='word', ascending=False)

        return self.dictionary_frame

    def eliminate_tupple(self, examined, letter_states, frame_data):
        """
        :param examined: these are characters which have been iterated through by the data frame comprising of characters of previous guesses.
        :param letter_states: These are the numeric values of tuple words returned from the wordle.py program.
        :param frame_data: this is the newly instanciated data frame before any further modifications are made to decrease the dataframe volume.
        :return: N/A
        """
        hit_indx = 0
        miss_indx = 0
        wrong_indx = 0
        for letter_val in letter_states:
            if letter_val == 1:
                self.letter_state1(examined, hit_indx, frame_data)
            hit_indx += 1
        for y, x in enumerate(frame_data):
            if x is not None:
                self.dictionary_frame = self.dictionary_frame[self.dictionary_frame[f'character_{y + 1}'] == x]
        for letter_val in letter_states:
            if letter_val == -1:
                self.letter_state_negative(examined, miss_indx)
            miss_indx += 1
            if letter_val == 0:
                self.return_zero(examined, frame_data, wrong_indx)
            wrong_indx += 1



    def AgentFunction(self, percepts):
        """
        :param percepts: these are the variables which are provided by the wordle.py file.
        :return: the new higest scored tuple word from the dataframe dictionary_frame
        """

        guess_counter, letter_indexes, letter_states = percepts
        self.examined = set()
        if guess_counter == 0:

            # on the agent functions first attempt at guessing the right word
            # All values are reset each time the wordle.py program executes
            self.attempts = set()
            # this list stores the examined and prior word characters as a list prom the prior declaration
            # this is so the characters are not reexamined latter on further iterations of the dataframe.
            columns = self.word_length
            self.set_dictionary = self.dictionary.copy()
            for word in self.set_dictionary:
                if len(word) != self.word_length:
                    self.set_dictionary.remove(word)
            data = list()
            for word in self.set_dictionary:
                data.append(self.split_words(word))
            self.dictionary_frame = pd.DataFrame(data=data, columns=[f'character_{ch + 1}' for ch in range(columns)])
            entry = self.dictionary_frame['entry'] = self.dictionary

        if guess_counter != 0:
            examined = list()
            frame_data = self.word_length * [None]
            for indx in letter_indexes:
                examined.append(self.letters[indx])
                if letter_states == self.word_length * [1]:
                    return " ".join(examined)

            self.eliminate_tupple(examined, letter_states, frame_data)
            if self.num_guesses - 1 > guess_counter and self.positive_counter(self.positive_count, letter_states) >= 1 and self.mode == "easy" \
                    and len(self.dictionary_frame) > 2:
                current_guess = self.new_guess_calculator(letter_states)
                if len(current_guess) == self.word_length:
                    return current_guess


        tuple = self.return_word().iloc[0]['entry']

        if self.num_guesses != guess_counter:
            self.dictionary_frame = self.dictionary_frame.loc[self.dictionary_frame["entry"] != tuple]

        for ch in tuple:
            self.attempts.add(ch)

        return tuple

