import tkinter as tk              # tkinter is Python's built-in library for creating windows and buttons
from tkinter import ttk           # ttk provides the table (Treeview) used for the transaction history
import json                       # json is used to save the users' data to a file and read it back
import os                         # os is used for file paths and for creating random salts
import sys                        # sys is used to find the program's folder when it runs as an .exe
import hashlib                    # hashlib is used to hash PINs and security answers
from datetime import datetime, date

# ======================= SETTINGS =======================
# Changing a value here changes the rule everywhere in the program.
MAX_ATTEMPTS = 3                  # wrong PINs (or wrong security answers) allowed before locking
DAILY_WITHDRAW_LIMIT = 5000       # maximum amount (TL) one user can withdraw per day
MAX_DEPOSIT = 50000               # maximum amount (TL) per single deposit
BANKNOTE = 10                     # withdrawals must be a multiple of this value (the ATM only has 10 TL notes)
PIN_LENGTH = 4                    # PINs must have exactly this many digits


# ======================= DATA FILE LOCATION =======================
def is_writable(folder):
    """Returns True if a file can be created in the given folder."""
    test_file = os.path.join(folder, '.write_test')
    try:
        with open(test_file, 'w') as file:
            file.write('ok')
        os.remove(test_file)
        return True
    except OSError:
        return False


def find_data_folder():
    """Chooses where users.json is stored.
    Normally it is next to the program (or the .exe). If that folder is read-only
    (for example C:\\Program Files), a 'PythonBankATM' folder in the user's home folder is used instead."""
    if getattr(sys, 'frozen', False):                       # True when running as an .exe (PyInstaller)
        program_folder = os.path.dirname(sys.executable)
    else:                                                   # running as a normal .py file
        program_folder = os.path.dirname(os.path.abspath(__file__))

    if is_writable(program_folder):
        return program_folder

    backup_folder = os.path.join(os.path.expanduser('~'), 'PythonBankATM')
    try:
        os.makedirs(backup_folder, exist_ok=True)
        return backup_folder
    except OSError:
        return program_folder                               # nothing is writable; save_users() will show a warning


DATA_FILE = os.path.join(find_data_folder(), 'users.json')


# ======================= SECURITY HELPERS =======================
def hash_secret(secret, salt):
    """Turns a PIN or an answer into a hash. A hash cannot be turned back into the original text.
    The salt is a random value per user, so two users with the same PIN get different hashes."""
    return hashlib.pbkdf2_hmac('sha256', secret.encode('utf-8'), bytes.fromhex(salt), 100000).hex()


def normalize(text):
    """Prepares text for comparison: removes extra spaces and makes it lowercase.
    'İ' and 'I' are replaced first so Turkish letters are lowercased correctly."""
    return text.strip().replace('İ', 'i').replace('I', 'ı').lower()


def check_pin(account, pin):
    """Returns True if the given PIN matches the account's stored PIN hash."""
    return hash_secret(pin, account['salt']) == account['pin_hash']


# ======================= DEFAULT USERS =======================
# Used only when an account does not exist in users.json yet (for example on the first run).
# These demo PINs and answers are written here in plain text only to create the accounts;
# users.json stores nothing but their hashes.
DEFAULT_USERS = {
    'Ayşe':   {'pin': '1234', 'balance': 1000,
               'question': 'What was the name of your first pet?', 'answer': 'pamuk'},
    'Mehmet': {'pin': '4567', 'balance': 2500,
               'question': 'In which city were you born?', 'answer': 'ankara'},
    'Zeynep': {'pin': '8080', 'balance': 500,
               'question': 'What is your favourite colour?', 'answer': 'turuncu'},
}


def new_account(pin, balance, question, answer):
    """Creates a complete account dictionary with hashed PIN and answer.
      salt            -> random value used when hashing this user's PIN and answer
      pin_hash        -> hash of the 4-digit PIN
      answer_hash     -> hash of the security answer (used by 'Forgot PIN?')
      card_blocked    -> True once the card is blocked
      wrong_attempts  -> consecutive wrong PINs on the login screen
      reset_attempts  -> consecutive wrong security answers
      withdrawn_today / withdraw_date -> used for the daily withdrawal limit"""
    salt = os.urandom(16).hex()
    return {
        'salt': salt,
        'pin_hash': hash_secret(pin, salt),
        'security_question': question,
        'answer_hash': hash_secret(normalize(answer), salt),
        'balance': balance,
        'history': [],
        'card_blocked': False,
        'wrong_attempts': 0,
        'reset_attempts': 0,
        'withdrawn_today': 0,
        'withdraw_date': '',
    }


def upgrade_account(name, account):
    """Brings an account saved by an older version of this program up to date,
    so an existing users.json keeps working (old plain-text PINs are hashed here)."""
    default = DEFAULT_USERS.get(name)

    if 'salt' not in account:
        account['salt'] = os.urandom(16).hex()

    if 'pin' in account:                                    # old version: PIN stored in plain text
        account['pin_hash'] = hash_secret(account.pop('pin'), account['salt'])
    if 'pin_hash' not in account and default:
        account['pin_hash'] = hash_secret(default['pin'], account['salt'])

    if 'answer_hash' not in account:
        if default:
            account['security_question'] = default['question']
            account['answer_hash'] = hash_secret(normalize(default['answer']), account['salt'])
        else:
            account['security_question'] = ''
            account['answer_hash'] = None                   # no question set -> 'Forgot PIN?' is not available

    # Fill in any missing fields with their starting values
    account.setdefault('balance', 0)
    account.setdefault('history', [])
    account.setdefault('card_blocked', False)
    account.setdefault('wrong_attempts', 0)
    account.setdefault('reset_attempts', 0)
    account.setdefault('withdrawn_today', 0)
    account.setdefault('withdraw_date', '')

    # Old history entries were plain text; convert them to the new table format
    for i, entry in enumerate(account['history']):
        if isinstance(entry, str):
            account['history'][i] = {'date': '-', 'type': entry, 'amount': '', 'balance': ''}


# ======================= LOAD AND SAVE =======================
def load_users():
    """Reads the users' data from users.json. Missing or damaged files never crash the program:
    any account that cannot be loaded is created again from DEFAULT_USERS."""
    data = None
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = None                                     # damaged or unreadable file
    if not isinstance(data, dict):
        data = {}

    for name, info in DEFAULT_USERS.items():                # create default accounts that are missing
        if name not in data:
            data[name] = new_account(info['pin'], info['balance'], info['question'], info['answer'])
    for name, account in data.items():                      # update accounts from older versions
        upgrade_account(name, account)
    return data


def save_users():
    """Writes all users' data to users.json and returns True if it worked.
    The data is first written to a temporary file and then renamed, so a crash in the middle
    of saving can never leave a half-written (damaged) users.json behind.
    If saving fails, a warning is shown at the top of the window instead of crashing."""
    temp_file = DATA_FILE + '.tmp'
    try:
        with open(temp_file, 'w', encoding='utf-8') as file:
            # ensure_ascii=False keeps Turkish letters (e.g. "Ayşe") readable; indent=4 makes the file tidy
            json.dump(users, file, ensure_ascii=False, indent=4)
        os.replace(temp_file, DATA_FILE)
        warning_label.config(text='')
        return True
    except OSError:
        warning_label.config(text='Warning: your changes could not be saved to the disk.')
        return False


users = load_users()      # load the saved data when the program starts


# ======================= ACCOUNT HELPERS =======================
def find_user(typed_name):
    """Finds a username without caring about upper/lower case ('ayşe' -> 'Ayşe').
    Returns the real username, or None if it does not exist."""
    for name in users:
        if normalize(name) == normalize(typed_name):
            return name
    return None


def add_history(account, kind, amount=''):
    """Adds one row to the account's transaction history, with the current date and time."""
    account['history'].append({
        'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'type': kind,
        'amount': amount,
        'balance': '{} TL'.format(account['balance']),
    })


def remaining_daily_limit(account):
    """Returns how much the user can still withdraw today.
    When a new day starts, the amount withdrawn so far is reset to 0."""
    today = date.today().isoformat()
    if account['withdraw_date'] != today:
        account['withdraw_date'] = today
        account['withdrawn_today'] = 0
    return DAILY_WITHDRAW_LIMIT - account['withdrawn_today']


def valid_new_pin(new_pin, account=None):
    """Returns an error message if the new PIN is not acceptable, or None if it is fine."""
    if not new_pin.isdecimal() or len(new_pin) != PIN_LENGTH:
        return 'Your new PIN must be exactly {} digits.'.format(PIN_LENGTH)
    if account is not None and check_pin(account, new_pin):
        return 'Your new PIN must be different from your current PIN.'
    return None


# ======================= COLORS AND FONTS =======================
NAVY = '#0f2747'        # window background
WHITE = '#ffffff'       # main screen card
BLUE = '#1e6fd9'        # primary buttons
GRAY = '#6b7280'        # secondary buttons and descriptions
GREEN = '#1b873f'       # success messages
RED = '#c62828'         # error messages
YELLOW = '#ffd54f'      # save warning
TEXT = '#1b1b1b'        # regular text
LIGHT = '#eef3fb'       # light blue boxes

FONT = 'Segoe UI'       # default Windows font; other systems use a similar fallback

# ======================= SESSION STATE =======================
current_user = None                 # username of the person currently logged in (None = nobody)
right_to_access = MAX_ATTEMPTS      # remaining login attempts on the login screen
pin_attempts = MAX_ATTEMPTS         # remaining attempts when entering the current PIN to change it

# ======================= MAIN WINDOW =======================
window = tk.Tk()                         # create the main application window
window.title('Python Bank ATM')          # text shown in the window's title bar
window.geometry('520x720')               # window size: width x height (in pixels)
window.resizable(False, False)           # prevent the user from resizing the window
window.configure(bg=NAVY)

header = tk.Label(window, text='PYTHON BANK', font=(FONT, 22, 'bold'), bg=NAVY, fg=WHITE, pady=14)
header.pack()

# Shown only when the data could not be saved (see save_users)
warning_label = tk.Label(window, text='', font=(FONT, 9, 'bold'), bg=NAVY, fg=YELLOW)
warning_label.pack()

# "content" is the white card in the middle. Every screen draws its widgets inside it.
content = tk.Frame(window, bg=WHITE, padx=28, pady=22)
content.pack(fill='both', expand=True, padx=22, pady=(4, 22))

# Style for the transaction history table
style = ttk.Style()
style.configure('History.Treeview', font=(FONT, 9), rowheight=24)
style.configure('History.Treeview.Heading', font=(FONT, 9, 'bold'))


# ======================= WIDGET HELPERS =======================
def clear():
    """Removes everything from the screen before a new screen is drawn."""
    for widget in content.winfo_children():
        widget.destroy()
    window.unbind('<Return>')            # remove the Enter key action of the previous screen


def add_title(text):
    tk.Label(content, text=text, font=(FONT, 17, 'bold'), bg=WHITE, fg=TEXT).pack(anchor='w')


def add_text(text, color=GRAY, size=10, bold=False):
    """Adds a paragraph of text. wraplength moves long lines to the next line automatically."""
    tk.Label(content, text=text, font=(FONT, size, 'bold' if bold else 'normal'), bg=WHITE, fg=color,
             justify='left', wraplength=400).pack(anchor='w', pady=(4, 0))


def add_entry(label, hidden=False):
    """Adds a label and a text box below it, and returns the text box.
    If hidden is True, typed characters are shown as dots (used for PINs)."""
    tk.Label(content, text=label, font=(FONT, 10, 'bold'), bg=WHITE, fg=TEXT).pack(anchor='w', pady=(12, 2))
    entry = tk.Entry(content, font=(FONT, 13), relief='solid', bd=1, show='•' if hidden else '')
    entry.pack(fill='x', ipady=5)
    return entry


def add_message(text='', color=RED):
    """Adds a label for feedback messages and returns it, so its text can be changed later."""
    message = tk.Label(content, text=text, font=(FONT, 10, 'bold'), bg=WHITE, fg=color,
                       justify='left', wraplength=400)
    message.pack(anchor='w', pady=(10, 0))
    return message


def make_button(parent, text, command, color=BLUE):
    """Creates a flat, colored button. 'command' is the function that runs when it is clicked."""
    return tk.Button(parent, text=text, command=command, font=(FONT, 11, 'bold'),
                     bg=color, fg=WHITE, activebackground=NAVY, activeforeground=WHITE,
                     relief='flat', cursor='hand2', pady=9)


def add_button(text, command, color=BLUE):
    """Creates a full-width button and places it on the current screen."""
    make_button(content, text, command, color).pack(fill='x', pady=(10, 0))


def add_link(text, command):
    """Creates a small text-style button (used for 'Forgot PIN?')."""
    tk.Button(content, text=text, command=command, font=(FONT, 10, 'underline'), bg=WHITE, fg=BLUE,
              activebackground=WHITE, activeforeground=NAVY, relief='flat', bd=0, highlightthickness=0,
              cursor='hand2').pack(anchor='e', pady=(8, 0))


# ======================= LOGIN SCREEN =======================
def show_login(message='', color=RED):
    """Shows the login screen. Every new customer starts here with fresh attempts."""
    global current_user, right_to_access
    current_user = None
    right_to_access = MAX_ATTEMPTS
    clear()

    add_title('Welcome')
    add_text('Please log in to your account.\n'
             'You have {0} attempts; your card will be blocked upon the {0}rd incorrect entry.'.format(MAX_ATTEMPTS))
    username_entry = add_entry('Username')
    pin_entry = add_entry('PIN', hidden=True)
    msg = add_message(message, color)

    def login():
        """Runs when the 'Log In' button (or the Enter key) is pressed."""
        global current_user, right_to_access
        username = find_user(username_entry.get())         # None if the username does not exist
        pin = pin_entry.get()
        pin_entry.delete(0, 'end')                          # always clear the PIN box after an attempt

        # A blocked card is rejected before the PIN is even checked
        if username is not None and users[username]['card_blocked']:
            msg.config(text='Your card has been blocked; you cannot log in. '
                            'Use "Forgot PIN?" or contact your bank.', fg=RED)
            return

        # Case 1: the username does not exist
        if username is None:
            right_to_access -= 1
            text = 'Your username is incorrect.'

        # Case 2: the username exists but the PIN is wrong
        elif not check_pin(users[username], pin):
            account = users[username]
            account['wrong_attempts'] += 1                  # wrong attempts are counted per user
            remaining = MAX_ATTEMPTS - account['wrong_attempts']
            right_to_access -= 1
            if remaining <= 0:                              # 3rd wrong PIN for this user -> block the card
                account['card_blocked'] = True
                save_users()
                right_to_access = MAX_ATTEMPTS
                username_entry.delete(0, 'end')
                msg.config(text='Your PIN is incorrect. Your card has been blocked; you cannot log in.', fg=RED)
                return
            save_users()                                    # remember the wrong attempt count
            text = 'Your PIN is incorrect. {} attempts left.'.format(remaining)

        # Case 3: username and PIN are both correct
        else:
            users[username]['wrong_attempts'] = 0           # a successful login resets the counter
            save_users()
            current_user = username
            show_menu('Logging in to your account...', GREEN)
            return

        # Too many failed attempts on this screen (e.g. unknown usernames): start over, nobody is blocked
        if right_to_access == 0:
            right_to_access = MAX_ATTEMPTS
            username_entry.delete(0, 'end')
            text = 'Too many incorrect attempts. Please start again.'

        msg.config(text=text, fg=RED)

    add_button('Log In', login)
    add_link('Forgot PIN?', show_forgot_username)
    add_button('Shut Down ATM', window.destroy, GRAY)       # window.destroy closes the program
    window.bind('<Return>', lambda event: login())          # pressing Enter also logs in
    username_entry.focus()


# ======================= FORGOT PIN =======================
# Resetting a forgotten PIN has two steps:
#   Step 1 (show_forgot_username): the user enters their username
#   Step 2 (show_forgot_question): the user answers their security question and chooses a new PIN
# A successful reset also unblocks the card. 3 wrong answers lock the reset for that user.
def show_forgot_username():
    clear()
    add_title('Forgot PIN')
    add_text('Enter your username. You will be asked your security question.')
    username_entry = add_entry('Username')
    msg = add_message()

    def next_step():
        username = find_user(username_entry.get())
        if username is None:
            msg.config(text='Your username is incorrect.')
            return
        account = users[username]
        if account['answer_hash'] is None:
            msg.config(text='No security question is set for this account. Please contact your bank.')
            return
        if account['reset_attempts'] >= MAX_ATTEMPTS:
            msg.config(text='PIN reset is locked because of too many incorrect answers. Please contact your bank.')
            return
        show_forgot_question(username)

    add_button('Next', next_step)
    add_button('Back to Login', lambda: show_login(), GRAY)
    window.bind('<Return>', lambda event: next_step())
    username_entry.focus()


def show_forgot_question(username):
    clear()
    account = users[username]

    add_title('Forgot PIN')
    add_text('Security question for {}:'.format(username))
    add_text(account['security_question'], TEXT, 11, bold=True)
    answer_entry = add_entry('Your answer')
    new_entry = add_entry('New {}-digit PIN'.format(PIN_LENGTH), hidden=True)
    confirm_entry = add_entry('Confirm new PIN', hidden=True)
    msg = add_message()

    def reset_pin():
        # 1) Check the security answer
        if hash_secret(normalize(answer_entry.get()), account['salt']) != account['answer_hash']:
            account['reset_attempts'] += 1
            save_users()
            remaining = MAX_ATTEMPTS - account['reset_attempts']
            if remaining <= 0:
                show_login('Too many incorrect answers. PIN reset is locked; please contact your bank.')
                return
            answer_entry.delete(0, 'end')
            msg.config(text='Your answer is incorrect. {} attempts left.'.format(remaining))
            return

        # 2) Check the new PIN
        error = valid_new_pin(new_entry.get())
        if error is None and new_entry.get() != confirm_entry.get():
            error = 'The PINs do not match.'
        if error is not None:
            new_entry.delete(0, 'end')
            confirm_entry.delete(0, 'end')
            msg.config(text=error)
            return

        # 3) Save the new PIN and unblock the card
        account['pin_hash'] = hash_secret(new_entry.get(), account['salt'])
        account['card_blocked'] = False
        account['wrong_attempts'] = 0
        account['reset_attempts'] = 0
        add_history(account, 'PIN reset')
        save_users()
        show_login('Your PIN has been reset. You can now log in with your new PIN.', GREEN)

    add_button('Reset PIN', reset_pin)
    add_button('Cancel', lambda: show_login(), GRAY)
    window.bind('<Return>', lambda event: reset_pin())
    answer_entry.focus()


# ======================= MAIN MENU =======================
def show_menu(message='', color=GREEN):
    """Shows the current balance and the six operation buttons."""
    clear()
    account = users[current_user]        # shortcut to the logged-in user's data

    add_title('Welcome, {}'.format(current_user))

    # Light blue box that displays the current balance and today's remaining withdrawal limit
    balance_box = tk.Frame(content, bg=LIGHT, padx=16, pady=10)
    balance_box.pack(fill='x', pady=(10, 6))
    tk.Label(balance_box, text='Current balance', font=(FONT, 10), bg=LIGHT, fg=GRAY).pack(anchor='w')
    tk.Label(balance_box, text='{} TL'.format(account['balance']), font=(FONT, 24, 'bold'),
             bg=LIGHT, fg=NAVY).pack(anchor='w')
    tk.Label(balance_box, text='Daily withdrawal limit left: {} TL'.format(remaining_daily_limit(account)),
             font=(FONT, 9), bg=LIGHT, fg=GRAY).pack(anchor='w')

    add_text('Which operation would you like to perform?', TEXT, 11)

    # A grid with 2 equal-width columns for the menu buttons
    grid = tk.Frame(content, bg=WHITE)
    grid.pack(fill='x', pady=(8, 0))
    grid.columnconfigure(0, weight=1)
    grid.columnconfigure(1, weight=1)

    # Each item: (button text, function to run, button color)
    # lambda is used when the function needs an argument, e.g. show_amount('withdraw')
    buttons = [
        ('Balance Inquiry', balance_inquiry, BLUE),
        ('Withdrawal', lambda: show_amount('withdraw'), BLUE),
        ('Deposit', lambda: show_amount('deposit'), BLUE),
        ('Change PIN', show_pin_change, BLUE),
        ('Transaction History', show_history, BLUE),
        ('Exit', exit_account, RED),
    ]
    # i // 2 gives the row (0, 0, 1, 1, 2, 2) and i % 2 gives the column (0, 1, 0, 1, 0, 1)
    for i, (text, command, btn_color) in enumerate(buttons):
        make_button(grid, text, command, btn_color).grid(row=i // 2, column=i % 2, sticky='ew', padx=4, pady=4)

    add_message(message, color)


# ======================= 1) BALANCE INQUIRY =======================
def balance_inquiry():
    account = users[current_user]
    add_history(account, 'Balance inquiry')
    save_users()
    show_menu('Your balance is {} TL.'.format(account['balance']))


# ======================= 2-3) WITHDRAWAL / DEPOSIT =======================
def show_amount(kind):
    """One screen for both operations. kind is either 'withdraw' or 'deposit'."""
    clear()
    account = users[current_user]

    if kind == 'withdraw':
        add_title('Withdrawal')
        add_text('Enter the amount of money you wish to withdraw.\n'
                 'Amounts must be a multiple of {} TL. Daily limit left: {} TL.'
                 .format(BANKNOTE, remaining_daily_limit(account)))
    else:
        add_title('Deposit')
        add_text('How much money would you like to deposit into your account?\n'
                 'Maximum {} TL per deposit.'.format(MAX_DEPOSIT))

    amount_entry = add_entry('Amount (TL)')

    # Quick amount buttons that fill the text box with a preset value
    quick = tk.Frame(content, bg=WHITE)
    quick.pack(fill='x', pady=(10, 0))
    for i, value in enumerate([100, 200, 500, 1000]):
        quick.columnconfigure(i, weight=1)

        # v=value stores the current value; without it, every button would use the last value (1000)
        def fill(v=value):
            amount_entry.delete(0, 'end')
            amount_entry.insert(0, str(v))

        make_button(quick, '{} TL'.format(value), fill, GRAY).grid(row=0, column=i, sticky='ew', padx=3)

    msg = add_message()

    def confirm():
        """Validates the amount and completes the operation."""
        amount = amount_entry.get().strip()

        # Only positive whole numbers made of the digits 0-9 are accepted
        if not amount.isdecimal() or int(amount) == 0:
            msg.config(text='You have entered an invalid number; please try again.')
            return
        amount = int(amount)             # convert text to a number before doing math

        if kind == 'withdraw':
            if amount % BANKNOTE != 0:                      # % gives the remainder of a division
                msg.config(text='Please enter a multiple of {} TL.'.format(BANKNOTE))
                return
            if amount > account['balance']:
                msg.config(text='Insufficient balance. Your balance is {} TL.'.format(account['balance']))
                return
            limit_left = remaining_daily_limit(account)
            if amount > limit_left:
                msg.config(text='Daily withdrawal limit exceeded. You can withdraw up to {} TL more today.'
                           .format(limit_left))
                return
            account['balance'] -= amount
            account['withdrawn_today'] += amount
            add_history(account, 'Withdrawal', '-{} TL'.format(amount))
            save_users()
            show_menu('Your new balance is {} TL.'.format(account['balance']))
        else:
            if amount > MAX_DEPOSIT:
                msg.config(text='You can deposit at most {} TL at a time.'.format(MAX_DEPOSIT))
                return
            account['balance'] += amount
            add_history(account, 'Deposit', '+{} TL'.format(amount))
            save_users()
            show_menu('Current balance in your account is {} TL.'.format(account['balance']))

    add_button('Confirm', confirm)
    add_button('Back to Menu', lambda: show_menu(), GRAY)
    window.bind('<Return>', lambda event: confirm())
    amount_entry.focus()


# ======================= 4) CHANGE PIN =======================
# Changing the PIN has two steps:
#   Step 1 (show_pin_change): verify the current PIN (3 attempts, then the card is blocked)
#   Step 2 (show_new_pin):    enter, confirm and save the new PIN
def show_pin_change():
    global pin_attempts
    pin_attempts = MAX_ATTEMPTS
    clear()
    account = users[current_user]

    add_title('Change PIN')
    add_text('Enter your current PIN to continue.')
    current_entry = add_entry('Current PIN', hidden=True)
    msg = add_message()

    def check_current():
        global pin_attempts
        if check_pin(account, current_entry.get()):        # correct PIN -> go to step 2
            show_new_pin()
            return
        current_entry.delete(0, 'end')
        pin_attempts -= 1
        if pin_attempts == 0:                               # 3 wrong entries -> block card and log out
            account['card_blocked'] = True
            save_users()
            show_login('Too many incorrect attempts. Your card has been blocked. Please take your card.')
            return
        msg.config(text='Your PIN is incorrect. {} attempts left.'.format(pin_attempts))

    add_button('Continue', check_current)
    add_button('Cancel', lambda: show_menu('PIN change cancelled.', GRAY), GRAY)
    window.bind('<Return>', lambda event: check_current())
    current_entry.focus()


def show_new_pin():
    clear()
    account = users[current_user]

    add_title('Change PIN')
    add_text('You can change your PIN.')
    new_entry = add_entry('New {}-digit PIN'.format(PIN_LENGTH), hidden=True)
    confirm_entry = add_entry('Confirm new PIN', hidden=True)
    msg = add_message()

    def save():
        error = valid_new_pin(new_entry.get(), account)
        if error is None and new_entry.get() != confirm_entry.get():
            error = 'The PINs do not match.'
        if error is not None:
            new_entry.delete(0, 'end')
            confirm_entry.delete(0, 'end')
            msg.config(text=error)
            return
        account['pin_hash'] = hash_secret(new_entry.get(), account['salt'])
        add_history(account, 'PIN changed')                 # the PIN itself is never written anywhere
        save_users()
        show_menu('Your PIN has been changed.')

    add_button('Save New PIN', save)
    add_button('Cancel', lambda: show_menu('PIN change cancelled.', GRAY), GRAY)
    window.bind('<Return>', lambda event: save())
    new_entry.focus()


# ======================= 5) TRANSACTION HISTORY =======================
def show_history():
    """Shows the logged-in user's transactions in a table, newest first."""
    clear()
    history = users[current_user]['history']

    add_title('Transaction History')

    if len(history) == 0:
        add_text('You have no transactions yet.', TEXT, 11)
    else:
        box = tk.Frame(content, bg=WHITE)
        box.pack(fill='both', expand=True, pady=(12, 0))

        columns = ('date', 'type', 'amount', 'balance')
        table = ttk.Treeview(box, columns=columns, show='headings', style='History.Treeview')
        headings = {'date': ('Date', 118), 'type': ('Transaction', 112), 'amount': ('Amount', 74),
                    'balance': ('Balance', 82)}
        for column, (title, width) in headings.items():
            table.heading(column, text=title)
            table.column(column, width=width, anchor='w')

        scrollbar = ttk.Scrollbar(box, orient='vertical', command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        table.pack(side='left', fill='both', expand=True)

        for entry in reversed(history):                     # reversed -> newest transaction at the top
            table.insert('', 'end', values=(entry['date'], entry['type'], entry['amount'], entry['balance']))

    add_button('Back to Menu', lambda: show_menu(), GRAY)


# ======================= 6) EXIT =======================
def exit_account():
    """Logs the user out and returns to the login screen for the next customer."""
    show_login('Your transaction has been completed. Goodbye!', GREEN)


# ======================= START THE PROGRAM =======================
save_users()           # create (or update) users.json, e.g. hash PINs saved by an older version
show_login()           # the first screen is the login screen
window.mainloop()      # keeps the window open and waits for clicks and key presses
