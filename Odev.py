number_1= int(input('Enter a number: '))
number_2= int(input('Enter a number: '))
number_3= int(input('Enter a number: '))
print(' {}*{}*{} result is {} '.format(number_1,number_2,number_3,number_1*number_2*number_3))

height= float(input('Enter a height:'))
weight= float(input('Enter your weight:'))
print('Your size index is {}'.format(weight/(height*height)))

expense=int(input('How much fuel does your vehicle consume per kilometer?'))
km=int(input('How many kilometers does your vehicle travel?'))
payment=expense*km
print('Total fee you need to pay is {} TL'.format(payment)) 
