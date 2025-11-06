class Character:
    def __init__(self, name, health):
        self.name = name
        self.health = health
    
    def profile(self):
        return f'Имя:{self.name} Здоровье: {self.health}'
class Warrior(Character):
    def atack(self):
        return 'Атака'
    
class Mage(Character):
    def atack(self):
        return 'Магия!'
    
class Archer(Character):
    def atack(self):
        return 'Лучники!'
    
character = Character('Леон', 4000)
warrior = Warrior('Леон', 4000)
mage = Mage('Леон', 4000)
archer = Archer('Леон', 4000)
character.profile()
warrior.atack()
mage.atack()
archer.atack()

class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        return
    
class Rectangle(Shape):

    def area(a):
        return a * a
    
class Circle(Shape):
    def area(r):
        return 3.14 * (r ** 2)
    
shape = Shape('Фигура')
rectangle = Rectangle
circle = Circle
print(rectangle.area(3))
print(circle.area(4))

