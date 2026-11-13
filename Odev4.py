midterm_grade1 = int(input('Enter your first midterm grade:'))
midterm_grade2 = int(input('Enter your second midterm grade:'))
final_exam_grade = int(input('Enter your final exam grade:'))

if not(0 <= midterm_grade1 <= 100 and 0 <= midterm_grade2 <= 100 and 0 <= final_exam_grade <= 100 ):
    print('Your note cannot be calculated! Grades must be between 0 and 100.')
else:
    total_note= midterm_grade1 * 0.30 + midterm_grade2 * 0.30 +final_exam_grade * 0.40

    if 100 >= total_note >= 90:
        print('Your note is AA.')
    elif 90 > total_note >= 85:
        print('Your note is BA.')
    elif 85 > total_note >= 80:
        print('Your note is BB.')
    elif 80 > total_note >= 75:
        print('Your note is CB.')
    elif 75 > total_note >= 70:
        print('Your note is CC.')
    elif 70 > total_note >= 65:
        print('Your note is DC.')
    elif 65 > total_note >= 60:
        print('Your note is DD.')
    elif 60 > total_note >= 55:
        print('Your note is FD.')
    elif total_note < 55:
        print('Your note is FF.')
