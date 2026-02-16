class Employee:
    def __init__(self, person, name, base_salary, percent = 0):
        self.name = name
        self.base_salary = float(base_salary)
        self.person = person
        self.percent = float(percent)

    def check(self):
        if self.person == "Manager":
            return self.base_salary * (1 + self.percent/100)
        elif self.person == "Developer":
            return self.base_salary + (self.percent) * 500
        else:
            return self.base_salary

    def total_salary(self):
        return self.base_salary
    

        
data = input().split()

if len(data) == 4:
    person, name, base_salary, percent = data
else:
    person, name, base_salary = data
    percent = 0

p = Employee(person, name, base_salary, percent)

print(f"Name: {name}, Total: {p.check():.2f}")