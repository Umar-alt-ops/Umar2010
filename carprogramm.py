import sqlite3
conn = sqlite3.connect('rental.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS cars (
id INTEGER PRIMARY KEY AUTOINCREMENT,
brand TEXT,
model TEXT,
year INTEGER,
available BOOLEAN
)
''')

conn.commit()

cursor.execute('''
CREATE TABLE IF NOT EXISTS rents (
id INTEGER PRIMARY KEY AUTOINCREMENT,
customer_name TEXT,
car_id INTEGER,
days INTEGER,
total_price REAL,
FOREIGN KEY (car_id) REFERENCES cars(id)
)
''')

conn.commit()

class Car:
    def __init__(self, brand, model, year, available=True):
        self.brand = brand
        self.model = model 
        self.year = year 
        self.available = available

    def mark_unavailable(self):
        self.available = False
    def mark_available(self):
        self.available = True
    
class RentalService:
    def add_car(self, car: Car):
        try:
            cursor.execute(
                "INSERT INTO cars (brand, model, year, available) VALUES (?, ?, ?, ?)",
                (car.brand, car.model, car.year, car.available)
            )
            conn.commit()
            print(f"Машина {car.brand} {car.model} добавлена.")
        except Exception as e:
            print("Ошибка при добавлении машины:", e)
    
    def show_all_cars(self):
        cursor.execute("SELECT * FROM cars")
        cursor.fetchall()
        if not cursor.fetchall():
            print("Список машин пуст.")
            return
        for car in cursor.fetchall():
            if car[4]:
             print("Доступно")
            else:
             print("Занята")
            print(f"{car[0]} | {car[1]} {car[2]} ({car[3]}) | {cursor.fetchall()}")
        
    def show_available_cars(self):
        cursor.execute("SELECT * FROM cars WHERE available=1")
        cars = cursor.fetchall()
        if not cars:
            print('Свободных машин нет')
        
        for car in cars:
            print(print(f"{car[0]} | {car[1]} {car[2]} ({car[3]}) | Доступна"))
            
    def rent_car(self, customer_name, car_id, days, daily_price):
        try:
            cursor.execute("SELECT available, brand, model FROM cars WHERE id=?", (car_id))
            car = cursor.fetchall()
            if not car:
                print("Машина с таким номером не найдена.")
                return
            if not car[0]:
                print("Машина уже арендована.")
                return
            total_price = days * daily_price
            cursor.execute(
                "INSERT INTO rents (customer_name, car_id, days, total_price) VALUES (?, ?, ?, ?)",
                (customer_name, car_id, days, total_price)
            )
            cursor.execute(
                "UPDATE cars SET available=0 WHERE id=?",
                (car_id)
            )
            conn.commit()
            print(f"{customer_name} арендовал {car[1]} {car[2]} на {days} дней. Цена: {total_price}")
        except Exception as car:
            print("Ошибка при аренде машины:", car)

     
    def return_car(self, car_id):
        try:
            cursor.execute("SELECT brand, model, available FROM cars WHERE id=?", (car_id,))
            car = cursor.fetchall()
            if not car:
                print("Машина с таким ID не найдена.")
                return
            if car[2]:
                print("Машина уже свободна.")
                return
            cursor.execute("UPDATE cars SET available=1 WHERE id=?", (car_id,))
            conn.commit()
            print(f"Машина {car[0]} {car[1]} возвращена и теперь доступна.")
        except Exception as car2:
            print('Ошибка:', car2)

    def delete_car(self, car_id):
        try:
            cursor.execute("SELECT brand, model FROM cars WHERE id=?", (car_id,))
            car = cursor.fetchall()
            if not car:
                print("Машина с таким ID не найдена.")
                return
            cursor.execute("DELETE FROM cars WHERE id=?", (car_id,))
            conn.commit()
            print(f"Машина {car[0]} {car[1]} удалена из базы.")
        except Exception as car3:
            print("Ошибка при удалении машины:", car3)

    def show_all_rents(self):
        try:
            cursor.execute("""SELECT r.id, r.customer_name, c.brand, c.model, r.total_price, r.days
            FROM rents r
            """)
            rents = cursor.fetchall()
            if not rents:
                print("Записей об аренде нет.")
                return
            for rent in rents:
                print(f"ID: {rent[0]} | Клиент: {rent[1]} | Машина: {rent[2]} {rent[3]} | Дней: {rent[5]} | Цена: {rent[4]}")
        except Exception as car4:
            print("Ошибка при выводе аренд:", car4)

    def car():
       service = RentalService()
       while True:
        print("""
1. Добавить машину
2. Показать все машины
3. Показать доступные машины
4. Арендовать машину
5. Вернуть машину
6. Удалить машину
7. Показать все аренды
8. Выйти
        """)
        choice = input("Выберите действие: ")

        if choice == "1":
            brand = input("Марка: ")
            model = input("Модель: ")
            year = int(input("Год: "))
            car = Car(brand, model, year)
            service.add_car(car)
        elif choice == "2":
            service.show_all_cars()
        elif choice == "3":
            service.show_available_cars()
        elif choice == "4":
            customer = input("Имя клиента: ")
            car_id = int(input("ID машины: "))
            days = int(input("Количество дней: "))
            daily_price = float(input("Цена в день: "))
            service.rent_car(customer, car_id, days, daily_price)
        elif choice == "5":
            car_id = int(input("ID машины для возврата: "))
            service.return_car(car_id)
        elif choice == "6":
            car_id = int(input("ID машины для удаления: "))
            service.delete_car(car_id)
        elif choice == "7":
            service.show_all_rents()
        elif choice == "8":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

print(RentalService.car())
