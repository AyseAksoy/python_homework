name = input('Enter your name: ')
while not name.isalpha():
    print('Name can only contain letters!')
    name = input('Enter your name: ')

last_name = input('Enter your last name: ')
while not last_name.isalpha():
    print('Last name can only contain letters!')
    last_name = input('Enter your last name: ')

number = int(input('Enter your number: '))

print('Your name is {} \nYour last name is {} \nYour number is {}'.format(name, last_name, number))



number1= int(input('Enter a number1:'))
number2= int(input('Enter a number2:'))
print('number1 is {}'.format(number1))
print('number2 is {}'.format(number2))
number1,number2=number2,number1 
print('new number1 is: {}'.format(number1))
print('new number2 is: {}'.format(number2))



a=int(input('Enter one of the sides of the right-angled triangle:'))
b=int(input('Enter the other side:'))
print('The length of the hypotenuse is {}'.format((a**2 + b**2)** 0.5))

