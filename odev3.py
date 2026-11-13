height=float(input('Enter your height:'))
weight=float(input('Enter your weight:'))
body_mass_index= weight/height ** 2

if body_mass_index< 18.5 :
    print('You are thin.')
elif 18.5 <= body_mass_index < 25 :
    print('You are normal.')
elif 25 <= body_mass_index < 30 :
    print('You are owerweight.')
else:
    print('You are obese.')



number_1=int(input('Enter a number:'))
number_2=int(input('Enter a number:'))
number_3=int(input('Enter a number:'))

if number_1 == number_2 == number_3:
    print('All numbers are equal to each other.')
else:
    if number_1 >= number_2 >= number_3 or number_1 >= number_3 >= number_2:
        print('The biggest number is {}'.format(number_1)) 
    elif number_2 >= number_1 >= number_3 or number_2 >= number_3 >= number_1:
        print('The biggest number is {}'.format(number_2)) 
    else:
        print('The biggest number is {}'.format(number_3))

    if number_1 <= number_2 <= number_3 or number_1 <= number_3 <= number_2:
        print('The smallest number is {}'.format(number_1))
    elif number_2 <= number_1 <= number_3 or number_2 <= number_3 <= number_1:
        print('The smallest number is {}'.format(number_1))
    else:
        print('The smallest number is {}'.format(number_3))