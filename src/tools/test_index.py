from tools import index

django_query = """
# Django queryset search example
from django.db import models

class Person(models.Model):
	name = models.CharField(max_length=30)

p = Person(name="John Doe")
p.save()

# Creating the queryset
people = Person.objects.filter(name="John Doe")
"""

quicksort_code = """
# Quicksort example
def quicksort(arr):
	if len(arr) <= 1:
		return arr
	pivot = arr[len(arr) // 2]
	left = [x for x in arr if x < pivot]
	middle = [x for x in arr if x == pivot]
	right = [x for x in arr if x > pivot]
	return quicksort(left) + middle + quicksort(right)

print(quicksort([3,6,8,10,1,2,1]))
"""

numpy_code1 = """
# Numpy code example 1
import numpy as np

a = np.array([1, 2, 3])   # Create a rank 1 array
print(type(a))            # Prints "<class 'numpy.ndarray'>"
print(a.shape)            # Prints "(3,)"
print(a[0], a[1], a[2])   # Prints "1 2 3"
a[0] = 5                  # Change an element of the array 
print(a)                  # Prints "[5, 2, 3]"
"""

numpy_code2 = """
# Numpy code example 2
import numpy as np

a = np.zeros((2,2))   # Create an array of all zeros 
print(a)              # Prints "[[ 0.  0.] [ 0.  0.]]"
b = np.ones((1,2))    # Create an array of all ones
print(b)              # Prints "[[ 1.  1.]]"
c = np.full((2,2), 7)  # Create a constant array
print(c)               # Prints "[[ 7.  7.] [ 7.  7.]]"
d = np.eye(2)         # Create a 2x2 identity matrix
print(d)              # Prints "[[ 1.  0.] [ 0.  1.]]"
"""
