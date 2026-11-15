starting_sallary=(input("Enter the starting salary: "))
while not starting_sallary.isdigit() or int(starting_sallary) == 0:
    print('Invalid input. Please enter a positive number.')
    starting_sallary=input('Enter the starting salary: ')
starting_sallary = int(starting_sallary)

total_cost=1000000
semi_annual_raise=0.07
r=0.04
portion_down_payment=0.25
down_payment=total_cost*portion_down_payment
epsilon=100                                              # acceptable margin of error        

                                                         # bounds for the bisection search (high is 10000 for a precision of 0.0001)
low = 0
high = 10000
steps = 0

                                                         # check whether the down payment can be reached even by saving 100% of the salary
max_savings = 0
temp_salary = starting_sallary
for month in range(1, 37):
    max_savings += (temp_salary / 12) + (max_savings * r / 12)
    if month % 6 == 0:
        temp_salary += temp_salary * semi_annual_raise

if max_savings < down_payment - epsilon:
    print("It is not possible to pay the down payment in three years.")
else:                                                    # keep searching until a suitable savings rate is found
    while low <= high:
        steps += 1
        guess = (low + high) // 2                        # integer division: guess is always a whole number between 0 and 10000
        rate = guess / 10000
        current_savings = 0
        temp_salary = starting_sallary                   # calculate the savings over 36 months
        for month in range(1, 37):
            current_savings += (temp_salary / 12) * rate + (current_savings * r / 12)
            if month % 6 == 0:
                temp_salary += temp_salary * semi_annual_raise

                                                         # check the margin of error and narrow the search range
        if abs(current_savings - down_payment) <= epsilon: 
            print("Best savings rate: ", rate)           # abs() returns the absolute value
            print("Steps in bisection search: ", steps)
            break
        elif current_savings < down_payment:
            low = guess + 1
        else:
            high = guess - 1
    else:                                                # runs only if the loop ends without break (no rate found within epsilon)
        print("No savings rate could be found within the acceptable margin of error.")

input('\nPress Enter to exit...')