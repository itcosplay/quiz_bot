from key_value_db import KeyValueDB, KeyValueObject

#initialize the key-value
# key_value_db = KeyValueDB("Greet=Hello World,Project=KeyValueDB", True, '=', ',', False)
questions_db = KeyValueDB()

questions_db.add('В каком году началась куликовская битва?', '1930')
#get an object
# print(key_value_db.get("Greet"))

#remove an object
# key_value_db.remove("Greet")

#add an object
# key_value_db.add("What", "i don't know what to write here")
print(questions_db.get('В каком году началась куликовская битва?'))
#print all the objects
# for kvo in key_value_db:
#     print(kvo)