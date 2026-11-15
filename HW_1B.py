total_cost=(input("Enter the total cost of your dream house: "))
while not total_cost.isdigit() or int(total_cost) == 0:
	print('Invalid input. Please enter a positive number.')
	total_cost=input("Enter the total cost of your dream house: ")
total_cost = int(total_cost)

current_savings = 0

salary=input("Enter the starting annual salary: ")
while not salary.isdigit() or int(salary) == 0:
	print("Invalid input. Please enter a positive number.")
	salary =input("Enter starting annual salary: ")
salary = int(salary)

semi_annual_raise=input("Enter the semi-annual raise, as a decimal: ").replace(',','.')
while not semi_annual_raise.replace('.', '', 1).isdigit() or not (0 <= float(semi_annual_raise) <= 1):
	print('Invalid input. Please enter a value between 0 and 1.')
	semi_annual_raise =input('Enter the semi-annual raise, as a decimal: ').replace(',','.')
semi_annual_raise = float(semi_annual_raise)

portion_down_payment = 0.25
down_payment = total_cost * portion_down_payment

portion_saved = (input("Enter the percent of your salary to save, as a decimal: ")).replace(',','.') 
while not portion_saved.replace('.', '', 1).isdigit() or not (0 < float(portion_saved) <= 1):
	print('Invalid input. Please enter a value between 0 and 1.')
	portion_saved =input('Enter the percent of your salary to save, as a decimal: ').replace(',','.')
portion_saved = float(portion_saved)

monthly_saved = (salary / 12 ) * portion_saved
r = 0.04  # annual return on current savings
month = 0

while current_savings < down_payment:
	current_savings += monthly_saved + (current_savings * r / 12)
	month += 1
	if month % 6 == 0:
		salary += salary * semi_annual_raise
		monthly_saved = (salary / 12 ) * portion_saved

print("Number of months: ", month)

input('\nPress Enter to exit...')