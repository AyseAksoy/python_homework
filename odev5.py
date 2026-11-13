shape = int(input('Are you looking for a quadrilateral(1) or a triangle(2)? Enter 1 or 2.'))
if not(shape == 1 or shape == 2):
    print('Enter 1 or 2.')

if shape == 1:
    print('You must enter 4 edges.')
    edge1=int(input('Enter the first edge:'))
    if not(edge1 > 0):
        print('Edge must take positive values!')
    else:
        edge2=int(input('Enter the second edge:'))
        if not(edge2 > 0):
            print('Edge must take positive values!')
        else:
            edge3=int(input('Enter the third edge:'))
            if not(edge3 > 0):
                print('Edge must take positive values!')
            else:
                edge4=int(input('Enter the fourth edge:'))
                if not(edge4 > 0):
                    print('Edge must take positive values!')
                elif edge1 == edge2 == edge3 == edge4:
                    print('This is a square.')
                elif (edge1==edge2 and edge3==edge4) or (edge1==edge3 and edge2==edge4) or (edge1==edge4 and edge3==edge2):
                    print('This is a rectangle.')
                else:
                    print('This is a regular quadrilateral.')
                

    if shape == 2:
        print('You must enter 3 edges')
        edge_1= int(input('Enter the first edge:'))
        if not(edge_1 > 0):
            print('Edge must take positive values!')
            edge_2= int(input('Enter the second edge:'))
            if not(edge_2 > 0):
               print('Edge must take positive values!')
            else:
                edge_3= int(input('Enter the first edge:'))
                if not(edge_3 > 0):
                    print('Edge must take positive values!')
                elif edge_1 == edge_2 == edge_3:
                    print('This is an equilateral triangle.')
                elif edge_1 == edge_2 and abs(edge_1 - edge_2) < edge_3 < edge_1 +edge_2:
                    print('This is an isosceles triangle.')
                elif edge_1 == edge_3 and abs(edge_1 - edge_3) < edge_2 < edge_1 +edge_3:
                    print('This is an isosceles triangle.')
                elif edge_3 == edge_2 and abs(edge_3 - edge_2) < edge_1 < edge_2 +edge_3:
                    print('This is an isosceles triangle.')
                elif edge_1 != edge_2 and edge_2 != edge_3 and edge_1 != edge_3 and abs(edge_1 - edge_2) < edge_3 < edge_1 +edge_2:
                    print('This is a normal triangle.')
                else:
                    print('You cannot form a triangle.')








            
