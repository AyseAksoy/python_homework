import random
import string

WORDLIST_FILENAME = "words.txt"


def load_words():
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    
    Depending on the size of the word list, this function may
    take a while to finish.
    """
    print("Loading word list from file...")
                                                                                           # inFile: file
    inFile = open(WORDLIST_FILENAME, 'r')
                                                                                           # line: string
    line = inFile.readline()
                                                                                           # wordlist: list of strings
    wordlist = line.split()
    print("  ", len(wordlist), "words loaded.")
    return wordlist



def choose_word(wordlist):
    """
    wordlist (list): list of words (strings)
    
    Returns a word from wordlist at random
    """
    return random.choice(wordlist)


                                                                                           # Load the list of words into the variable wordlist
                                                                                           # so that it can be accessed from anywhere in the program
wordlist = load_words()


def is_word_guessed(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing; assumes all letters are
      lowercase
    letters_guessed: list (of letters), which letters have been guessed so far;
      assumes that all letters are lowercase
    returns: boolean, True if all the letters of secret_word are in letters_guessed;
      False otherwise
    '''
    for letter in secret_word:
        if letter not in letters_guessed:
            return False
    return True



def get_guessed_word(secret_word, letters_guessed):
    '''
    secret_word: string, the word the user is guessing
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string, comprised of letters, underscores (_), and spaces that represents
      which letters in secret_word have been guessed so far.
    '''
    result = ''
    for letter in secret_word:
        if letter in letters_guessed:
           result += letter
        else:
            result += '_ '
    return result



def get_available_letters(letters_guessed):
    '''
    letters_guessed: list (of letters), which letters have been guessed so far
    returns: string (of letters), comprised of letters that represents which letters have not
      yet been guessed.
    '''
    result= ''
    for letter in string.ascii_lowercase:
        if letter not in letters_guessed:
            result += letter
    return result
    
    

def hangman(secret_word):
    '''
    secret_word: string, the secret word to guess.
    
    Starts up an interactive game of Hangman.
    
    * At the start of the game, let the user know how many 
      letters the secret_word contains and how many guesses s/he starts with.
      
    * The user should start with 6 guesses

    * Before each round, you should display to the user how many guesses
      s/he has left and the letters that the user has not yet guessed.
    
    * Ask the user to supply one guess per round. Remember to make
      sure that the user puts in a letter!
    
    * The user should receive feedback immediately after each guess 
      about whether their guess appears in the computer's word.

    * After each guess, you should display to the user the 
      partially guessed word so far.
    
    Follows the other limitations detailed in the problem write-up.
    '''
    guesses_remaining = 6
    warnings_remaining = 3
    letters_guessed = []

    print('Welcome to the game Hangman!')
    print('I am thinking of a word that is', len(secret_word), 'letters long.')
    print('You have', warnings_remaining, 'warnings left.')
    print('-------------')

    while guesses_remaining > 0 and not is_word_guessed(secret_word, letters_guessed):
        print('You have', guesses_remaining, 'guesses left.')
        print('Available letters:', get_available_letters(letters_guessed))
        guess = input('Please guess a letter: ').lower()

        if not guess.isalpha():                                    # CASE 1: input is not a letter
            if warnings_remaining > 0:                             #   if the user still has warnings
                warnings_remaining -= 1                            #   lose one warning
                print('Oops! That is not a valid letter. You have', warnings_remaining, 'warnings left:', get_guessed_word(secret_word, letters_guessed))
            else:                                                  #   if no warnings are left
                guesses_remaining -= 1                             #   lose one guess
                print('Oops! That is not a valid letter. You have no warnings left so you lose one guess:', get_guessed_word(secret_word, letters_guessed))

        elif guess in letters_guessed:                             # CASE 2: letter was already guessed
            if warnings_remaining > 0:
                warnings_remaining -= 1
                print("Oops! You've already guessed that letter. You have", warnings_remaining, 'warnings left:', get_guessed_word(secret_word, letters_guessed))
            else:
                guesses_remaining -= 1
                print("Oops! You've already guessed that letter. You have no warnings left so you lose one guess:", get_guessed_word(secret_word, letters_guessed))

        else:                                                      # CASE 3: a new valid letter
            letters_guessed.append(guess)                          #   add it to the guessed letters
            if guess in secret_word:                               #   if the letter is in the word
                print('Good guess:', get_guessed_word(secret_word, letters_guessed))
            else:                                                  #   if the letter is not in the word
                if guess in 'aeiou':                               #   vowel: lose two guesses
                    guesses_remaining -= 2
                else:                                              #   consonant: lose one guess
                    guesses_remaining -= 1
                print('Oops! That letter is not in my word:', get_guessed_word(secret_word, letters_guessed))
        print('------------')

    if is_word_guessed(secret_word, letters_guessed):              # the user found the word
        print('Congratulations, you won!')
        score = guesses_remaining * len(set(secret_word))          # score = guesses left * unique letters
        print('Your total score for this game is:', score)
    else:                                                          # the user ran out of guesses
        print('Sorry, you ran out of guesses. The word was', secret_word)
   


def match_with_gaps(my_word, other_word):
    '''
    my_word: string with _ characters, current guess of secret word
    other_word: string, regular English word
    returns: boolean, True if all the actual letters of my_word match the 
        corresponding letters of other_word, or the letter is the special symbol
        _ , and my_word and other_word are of the same length;
        False otherwise: 
    '''
    my_word = my_word.replace(' ', '')                             # remove spaces: "a_ _ le" -> "a__le"

    if len(my_word) != len(other_word):                            # if the lengths are different
        return False                                               # they cannot be the same word

    for i in range(len(my_word)):                                  # check each position one by one (i = index)
        if my_word[i] != '_':                                      # if there is a LETTER in my_word and it is not the same as in other_word
            if my_word[i] != other_word[i]:
                return False                                       # it does not match
        else:                                                      # if there is a _ in my_word
            if other_word[i] in my_word:                           # and that letter is already revealed in my_word
                return False                                       # it does not match

    return True                                                    # no mismatch found in any position



def show_possible_matches(my_word):
    '''
    my_word: string with _ characters, current guess of secret word
    returns: nothing, but should print out every word in wordlist that matches my_word
             Keep in mind that in hangman when a letter is guessed, all the positions
             at which that letter occurs in the secret word are revealed.
             Therefore, the hidden letter(_ ) cannot be one of the letters in the word
             that has already been revealed.

    '''
    result = ''                                                     # start with an empty string
    for word in wordlist:                                           # check every word in the word list
        if match_with_gaps(my_word, word):                          # if the word matches my_word
            result += word + ' '                                    # add it to the result with a space
    if result == '':                                                # if no word was added
        print('No matches found')
    else:
        print(result)



def hangman_with_hints(secret_word):
    '''
    secret_word: string, the secret word to guess.
    
    Starts up an interactive game of Hangman.
    
    * At the start of the game, let the user know how many 
      letters the secret_word contains and how many guesses s/he starts with.
      
    * The user should start with 6 guesses
    
    * Before each round, you should display to the user how many guesses
      s/he has left and the letters that the user has not yet guessed.
    
    * Ask the user to supply one guess per round. Make sure to check that the user guesses a letter
      
    * The user should receive feedback immediately after each guess 
      about whether their guess appears in the computer's word.

    * After each guess, you should display to the user the 
      partially guessed word so far.
      
    * If the guess is the symbol *, print out all words in wordlist that
      matches the current guessed word. 
    
    Follows the other limitations detailed in the problem write-up.
    '''
    guesses_remaining = 6
    warnings_remaining = 3
    letters_guessed = []

    print('Welcome to the game Hangman!')
    print('I am thinking of a word that is', len(secret_word), 'letters long.')
    print('You have', warnings_remaining, 'warnings left.')
    print('-------------')

    while guesses_remaining > 0 and not is_word_guessed(secret_word, letters_guessed):
        print('You have', guesses_remaining, 'guesses left.')
        print('Available letters:', get_available_letters(letters_guessed))
        guess = input('Please guess a letter: ').lower()

        if guess == '*':                                           # NEW CASE: the user asks for a hint
            print('Possible word matches are:')
            show_possible_matches(get_guessed_word(secret_word, letters_guessed))

        elif not guess.isalpha():                                  # CASE 1: input is not a letter
            if warnings_remaining > 0:
                warnings_remaining -= 1
                print('Oops! That is not a valid letter. You have', warnings_remaining, 'warnings left:', get_guessed_word(secret_word, letters_guessed))
            else:
                guesses_remaining -= 1
                print('Oops! That is not a valid letter. You have no warnings left so you lose one guess:', get_guessed_word(secret_word, letters_guessed))

        elif guess in letters_guessed:                             # CASE 2: letter was already guessed
            if warnings_remaining > 0:
                warnings_remaining -= 1
                print("Oops! You've already guessed that letter. You have", warnings_remaining, 'warnings left:', get_guessed_word(secret_word, letters_guessed))
            else:
                guesses_remaining -= 1
                print("Oops! You've already guessed that letter. You have no warnings left so you lose one guess:", get_guessed_word(secret_word, letters_guessed))

        else:                                                      # CASE 3: a new valid letter
            letters_guessed.append(guess)
            if guess in secret_word:
                print('Good guess:', get_guessed_word(secret_word, letters_guessed))
            else:
                if guess in 'aeiou':                               # vowel: lose two guesses
                    guesses_remaining -= 2
                else:                                              # consonant: lose one guess
                    guesses_remaining -= 1
                print('Oops! That letter is not in my word:', get_guessed_word(secret_word, letters_guessed))
        print('------------')

    if is_word_guessed(secret_word, letters_guessed):              # the user found the word
        print('Congratulations, you won!')
        score = guesses_remaining * len(set(secret_word))          # score = guesses left * unique letters
        print('Your total score for this game is:', score)
    else:                                                          # the user ran out of guesses
        print('Sorry, you ran out of guesses. The word was', secret_word)


if __name__ == "__main__":
    secret_word = choose_word(wordlist)
    hangman_with_hints(secret_word)
    input('\nPress Enter to exit...')