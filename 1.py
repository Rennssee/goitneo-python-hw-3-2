from datetime import datetime, timedelta
from collections import UserDict, defaultdict

# Field classes
class Field:
    def __init__(self, value):
        self.value = value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, phone):
        if self.validate(phone):
            super().__init__(phone)
        else:
            raise ValueError("Invalid phone format")

    @staticmethod
    def validate(phone):
        return len(phone) == 10 and phone.isdigit()

class Birthday(Field):
    def __init__(self, date):
        if self.validate(date):
            parsed_date = datetime.strptime(date, "%d.%m.%Y")
            super().__init__(parsed_date)
        else:
            raise ValueError("Invalid birthday format")

    @staticmethod
    def validate(date):
        try:
            datetime.strptime(date, "%d.%m.%Y")
            return True
        except ValueError:
            return False

# Record and AddressBook classes
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        p = Phone(phone)
        self.phones.append(p)

    def add_birthday(self, date):
        self.birthday = Birthday(date)

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_birthdays_per_week(self):
        today = datetime.today().date()
        birthdays = defaultdict(list)

        for record in self.data.values():
            if record.birthday:
                name = record.name.value
                birthday = record.birthday.value.date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday.replace(year=today.year + 1)

                delta_days = (birthday_this_year - today).days

                if delta_days < 7:
                    weekday_num = birthday_this_year.weekday()
                    if weekday_num in [5, 6]:
                        weekday = "Monday"
                    else:
                        weekday = birthday_this_year.strftime("%A")
                    birthdays[weekday].append(name)

        return birthdays

# Bot functions
def read_customer_input(user_input):
    cmd, *args = user_input.split()
    return cmd.lower(), args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as e:
            return str(e)
    return inner

@input_error
def add_contact_safely(args, book):
    name, phone = args
    if name not in book:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        raise KeyError("Contact already exists.")

@input_error
def change_contact_safely(args, book):
    name, phone = args
    if name in book:
        record = book[name]
        record.phones[0].value = phone
        return "Contact updated."
    else:
        raise KeyError("Contact not found.")

@input_error
def get_phone_safely(args, book):
    name = args[0]
    if name in book:
        return book[name].phones[0].value
    else:
        raise KeyError("Contact not found.")

@input_error
def add_birthday_safely(args, book):
    name, date = args
    if name in book:
        book[name].add_birthday(date)
        return "Birthday added."
    else:
        raise KeyError("Contact not found.")

@input_error
def show_birthday_safely(args, book):
    name = args[0]
    if name in book and book[name].birthday:
        return book[name].birthday.value.strftime("%d.%m.%Y")
    else:
        raise KeyError("Contact or birthday not found.")

def show_all_contacts(book):
    if not book:
        return "No contacts stored."
    return "\n".join(f"{name}: {record.phones[0].value}" for name, record in book.data.items())

def show_birthdays_next_week(book):
    birthdays = book.get_birthdays_per_week()
    if not birthdays:
        return "No birthdays next week."
    return "\n".join(f"{weekday}: {', '.join(names)}" for weekday, names in birthdays.items())

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = read_customer_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact_safely(args, book))
        elif command == "change":
            print(change_contact_safely(args, book))
        elif command == "phone":
            print(get_phone_safely(args, book))
        elif command == "all":
            print(show_all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday_safely(args, book))
        elif command == "show-birthday":
            print(show_birthday_safely(args, book))
        elif command == "birthdays":
            print(show_birthdays_next_week(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
