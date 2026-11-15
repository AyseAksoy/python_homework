print('Please log in to your account. Be careful, you have 3 attempts before you are locked out.')
user_name= 'Ayşe'
password = '123'
right_to_access = 0

while True:
    user_name_system = input('Enter your username:')
    password_system = input('ENter your password:')
    if (user_name != user_name_system and password != password_system ):
        print('Your password and user name are incorrect.')
        right_to_access += 1
    elif (user_name == user_name_system and password != password_system):
        print('Your username is correct but your password is incorrect.')
        right_to_access += 1
    elif (user_name != user_name_system and password == password_system ):
        print('Your username is incorrect but your password is true.')
        right_to_access += 1
    else:
        print('You can log in to your account.')
        break

    if(right_to_access == 3):
        print('Your access attempts have been exhausted; you are now exiting the program.')
        break
    
input('\nPress Enter to exit...')