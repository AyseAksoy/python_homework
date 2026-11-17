import tkinter as tk    # tkinter is Python's built-in library for creating windows and buttons

# ======================= USERS =======================
# Each username is a key; its value is another dictionary holding that user's account data.
#   pin            -> the user's 4-digit PIN (stored as a string so leading zeros are kept)
#   balance        -> current account balance in TL
#   history        -> list of completed transactions
#   card_blocked   -> True once the card is blocked; the user can no longer log in
#   wrong_attempts -> number of consecutive wrong PIN entries for this user
users = {
    'Ayşe':   {'pin': '1234', 'balance': 1000, 'history': [], 'card_blocked': False, 'wrong_attempts': 0},
    'Mehmet': {'pin': '4567', 'balance': 2500, 'history': [], 'card_blocked': False, 'wrong_attempts': 0},
    'Zeynep': {'pin': '8080', 'balance': 500,  'history': [], 'card_blocked': False, 'wrong_attempts': 0},
}

# ======================= COLORS AND FONTS =======================
# Keeping colors in variables makes it easy to change the whole look from one place.
NAVY = '#0f2747'        # window background
WHITE = '#ffffff'       # main screen card
BLUE = '#1e6fd9'        # primary buttons
GRAY = '#6b7280'        # secondary buttons and descriptions
GREEN = '#1b873f'       # success messages
RED = '#c62828'         # error messages
TEXT = '#1b1b1b'        # regular text

FONT = 'Segoe UI'       # default Windows font; other systems use a similar fallback

# ======================= SESSION STATE =======================
# These variables are shared by several screens, so they are defined at the top level.
current_user = None     # username of the person currently logged in (None = nobody)
right_to_access = 3     # remaining login attempts on the login screen
pin_attempts = 3        # remaining attempts when entering the current PIN to change it

# ======================= MAIN WINDOW =======================
window = tk.Tk()                         # create the main application window
window.title('Python Bank ATM')          # text shown in the window's title bar
window.geometry('500x660')               # window size: width x height (in pixels)
window.resizable(False, False)           # prevent the user from resizing the window
window.configure(bg=NAVY)                # set the background color

# Bank name shown at the top of every screen
header = tk.Label(window, text='PYTHON BANK', font=(FONT, 22, 'bold'), bg=NAVY, fg=WHITE, pady=18)
header.pack()

# "content" is the white card in the middle. Every screen draws its widgets inside it.
content = tk.Frame(window, bg=WHITE, padx=28, pady=24)
content.pack(fill='both', expand=True, padx=22, pady=(0, 22))


# ======================= HELPER FUNCTIONS =======================
# Small functions that create common widgets, so the screen functions stay short and readable.

def clear():
    """Removes everything from the screen before a new screen is drawn."""
    for widget in content.winfo_children():
        widget.destroy()
    window.unbind('<Return>')            # remove the Enter key action of the previous screen


def add_title(text):
    """Adds a large bold title to the current screen."""
    tk.Label(content, text=text, font=(FONT, 17, 'bold'), bg=WHITE, fg=TEXT).pack(anchor='w')


def add_text(text, color=GRAY, size=10):
    """Adds a paragraph of text. wraplength moves long lines to the next line automatically."""
    tk.Label(content, text=text, font=(FONT, size), bg=WHITE, fg=color,
             justify='left', wraplength=380).pack(anchor='w', pady=(4, 0))


def add_entry(label, hidden=False):
    """Adds a label and a text box below it, and returns the text box.
    If hidden is True, typed characters are shown as dots (used for PINs)."""
    tk.Label(content, text=label, font=(FONT, 10, 'bold'), bg=WHITE, fg=TEXT).pack(anchor='w', pady=(14, 2))
    entry = tk.Entry(content, font=(FONT, 13), relief='solid', bd=1, show='•' if hidden else '')
    entry.pack(fill='x', ipady=6)
    return entry


def add_message(text='', color=RED):
    """Adds a label for feedback messages and returns it,
    so its text can be changed later with message.config(text=...)."""
    message = tk.Label(content, text=text, font=(FONT, 10, 'bold'), bg=WHITE, fg=color,
                       justify='left', wraplength=380)
    message.pack(anchor='w', pady=(10, 0))
    return message


def make_button(parent, text, command, color=BLUE):
    """Creates a flat, colored button. 'command' is the function that runs when it is clicked."""
    return tk.Button(parent, text=text, command=command, font=(FONT, 11, 'bold'),
                     bg=color, fg=WHITE, activebackground=NAVY, activeforeground=WHITE,
                     relief='flat', cursor='hand2', pady=10)


def add_button(text, command, color=BLUE):
    """Creates a full-width button and places it on the current screen."""
    make_button(content, text, command, color).pack(fill='x', pady=(10, 0))


# ======================= LOGIN SCREEN =======================
def show_login(message='', color=RED):
    """Shows the login screen. Every new customer starts here with 3 fresh attempts."""
    global current_user, right_to_access
    current_user = None                  # nobody is logged in on this screen
    right_to_access = 3                  # reset attempts for the new customer
    clear()

    add_title('Welcome')
    add_text('Please log in to your account.\n'
             'You have 3 attempts; your card will be blocked upon the 3rd incorrect entry.')
    username_entry = add_entry('Username')
    pin_entry = add_entry('PIN', hidden=True)
    msg = add_message(message, color)    # shows messages such as "Goodbye!" or errors

    def login():
        """Runs when the 'Log In' button (or the Enter key) is pressed."""
        global current_user, right_to_access
        username = username_entry.get()  # read what the user typed
        pin = pin_entry.get()
        pin_entry.delete(0, 'end')       # always clear the PIN box after an attempt

        # A blocked card is rejected before the PIN is even checked
        if username in users and users[username]['card_blocked']:
            msg.config(text='Your card has been blocked; you cannot log in. Please contact your bank.', fg=RED)
            return

        # Case 1: the username does not exist
        if username not in users:
            right_to_access -= 1
            text = 'Your username is incorrect.'

        # Case 2: the username exists but the PIN is wrong
        elif users[username]['pin'] != pin:
            users[username]['wrong_attempts'] += 1           # wrong attempts are counted per user
            remaining = 3 - users[username]['wrong_attempts']
            right_to_access -= 1
            if remaining == 0:                                # 3rd wrong PIN for this user -> block the card
                users[username]['card_blocked'] = True
                right_to_access = 3
                username_entry.delete(0, 'end')
                msg.config(text='Your PIN is incorrect. Your card has been blocked; you cannot log in.', fg=RED)
                return
            text = 'Your PIN is incorrect. {} attempts left.'.format(remaining)

        # Case 3: username and PIN are both correct
        else:
            users[username]['wrong_attempts'] = 0             # a successful login resets the counter
            current_user = username
            show_menu('Logging in to your account...', GREEN)
            return

        # Too many failed attempts on this screen (e.g. unknown usernames): start over, nobody is blocked
        if right_to_access == 0:
            right_to_access = 3
            username_entry.delete(0, 'end')
            text = 'Too many incorrect attempts. Please start again.'

        msg.config(text=text, fg=RED)

    add_button('Log In', login)
    add_button('Shut Down ATM', window.destroy, GRAY)         # window.destroy closes the program
    window.bind('<Return>', lambda event: login())            # pressing Enter also logs in
    username_entry.focus()                                    # place the cursor in the username box


# ======================= MAIN MENU =======================
def show_menu(message='', color=GREEN):
    """Shows the current balance and the six operation buttons."""
    clear()
    account = users[current_user]        # shortcut to the logged-in user's data

    add_title('Welcome, {}'.format(current_user))

    # Light blue box that displays the current balance
    balance_box = tk.Frame(content, bg='#eef3fb', padx=16, pady=12)
    balance_box.pack(fill='x', pady=(12, 6))
    tk.Label(balance_box, text='Current balance', font=(FONT, 10), bg='#eef3fb', fg=GRAY).pack(anchor='w')
    tk.Label(balance_box, text='{} TL'.format(account['balance']), font=(FONT, 24, 'bold'),
             bg='#eef3fb', fg=NAVY).pack(anchor='w')

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

    add_message(message, color)          # result of the last operation (green = success)


# ======================= 1) BALANCE INQUIRY =======================
def balance_inquiry():
    """Records the inquiry in the history and shows the balance as a message."""
    account = users[current_user]
    account['history'].append('Balance inquiry       (Balance: {} TL)'.format(account['balance']))
    show_menu('Your balance is {} TL.'.format(account['balance']))


# ======================= 2-3) WITHDRAWAL / DEPOSIT =======================
def show_amount(kind):
    """One screen for both operations. kind is either 'withdraw' or 'deposit'."""
    clear()
    account = users[current_user]

    # Title and description depend on the operation
    if kind == 'withdraw':
        add_title('Withdrawal')
        add_text('Enter the amount of money you wish to withdraw.')
    else:
        add_title('Deposit')
        add_text('How much money would you like to deposit into your account?')

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
        amount = amount_entry.get()

        # Only positive whole numbers are accepted (letters, decimals, negatives and 0 are rejected)
        if not amount.isdigit() or int(amount) == 0:
            msg.config(text='You have entered an invalid number; please try again.')
            return
        amount = int(amount)             # convert text to a number before doing math

        if kind == 'withdraw':
            # Check the balance first; only withdraw if there is enough money
            if amount > account['balance']:
                msg.config(text='Insufficient balance. Your balance is {} TL.'.format(account['balance']))
                return
            account['balance'] -= amount
            account['history'].append('Withdrawal: -{} TL  (Balance: {} TL)'.format(amount, account['balance']))
            show_menu('Your new balance is {} TL.'.format(account['balance']))
        else:
            account['balance'] += amount
            account['history'].append('Deposit:    +{} TL  (Balance: {} TL)'.format(amount, account['balance']))
            show_menu('Current balance in your account is {} TL.'.format(account['balance']))

    add_button('Confirm', confirm)
    add_button('Back to Menu', lambda: show_menu(), GRAY)
    window.bind('<Return>', lambda event: confirm())          # Enter key confirms
    amount_entry.focus()


# ======================= 4) CHANGE PIN =======================
# Changing the PIN has two steps:
#   Step 1 (show_pin_change): verify the current PIN (3 attempts)
#   Step 2 (show_new_pin):    enter and save the new PIN
def show_pin_change():
    """Step 1: asks for the current PIN. 3 wrong entries block the card."""
    global pin_attempts
    pin_attempts = 3
    clear()
    account = users[current_user]

    add_title('Change PIN')
    add_text('Enter your current PIN to continue.')
    current_entry = add_entry('Current PIN', hidden=True)
    msg = add_message()

    def check_current():
        global pin_attempts
        if current_entry.get() == account['pin']:            # correct PIN -> go to step 2
            show_new_pin()
            return
        current_entry.delete(0, 'end')
        pin_attempts -= 1
        if pin_attempts == 0:                                 # 3 wrong entries -> block card and log out
            account['card_blocked'] = True
            show_login('Too many incorrect attempts. Your card has been blocked. Please take your card.')
            return
        msg.config(text='Your PIN is incorrect. {} attempts left.'.format(pin_attempts))

    add_button('Continue', check_current)
    add_button('Cancel', lambda: show_menu('PIN change cancelled.', GRAY), GRAY)
    window.bind('<Return>', lambda event: check_current())
    current_entry.focus()


def show_new_pin():
    """Step 2: asks for the new PIN and saves it if it is valid."""
    clear()
    account = users[current_user]

    add_title('Change PIN')
    add_text('You can change your PIN.')
    new_entry = add_entry('New 4-digit PIN', hidden=True)
    msg = add_message()

    def save():
        new_pin = new_entry.get()
        # The new PIN must be exactly 4 digits and different from the current one
        if not new_pin.isdecimal() or len(new_pin) != 4 or new_pin == account['pin']:
            new_entry.delete(0, 'end')
            msg.config(text='Your new PIN must be exactly 4 digits and different from your current PIN.')
            return
        account['pin'] = new_pin
        account['history'].append('PIN changed')              # the PIN itself is never written to the history
        show_menu('Your PIN has been changed.')

    add_button('Save New PIN', save)
    add_button('Cancel', lambda: show_menu('PIN change cancelled.', GRAY), GRAY)
    window.bind('<Return>', lambda event: save())
    new_entry.focus()


# ======================= 5) TRANSACTION HISTORY =======================
def show_history():
    """Lists all transactions of the logged-in user in a scrollable box."""
    clear()
    history = users[current_user]['history']

    add_title('Transaction History')

    if len(history) == 0:
        add_text('You have no transactions yet.', TEXT, 11)
    else:
        # A Listbox with a scrollbar, so long histories can be scrolled
        box = tk.Frame(content, bg=WHITE)
        box.pack(fill='both', expand=True, pady=(12, 0))
        scrollbar = tk.Scrollbar(box)
        scrollbar.pack(side='right', fill='y')
        listbox = tk.Listbox(box, font=('Consolas', 10), relief='solid', bd=1,
                             yscrollcommand=scrollbar.set, activestyle='none')
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=listbox.yview)               # connect the scrollbar to the list

        # Add each transaction with a line number: "1. ...", "2. ...", ...
        count = 1
        for transaction in history:
            listbox.insert('end', ' {}. {}'.format(count, transaction))
            count += 1

    add_button('Back to Menu', lambda: show_menu(), GRAY)


# ======================= 6) EXIT =======================
def exit_account():
    """Logs the user out and returns to the login screen for the next customer.
    Account data (balance, history, PIN) is kept in the 'users' dictionary."""
    show_login('Your transaction has been completed. Goodbye!', GREEN)


# ======================= START THE PROGRAM =======================
show_login()           # the first screen is the login screen
window.mainloop()      # keeps the window open and waits for clicks and key presses
