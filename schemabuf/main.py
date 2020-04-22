import schemabuf.schema.builder as schema


Name = schema.StructBuilder()\
  .field('first_name', 0x1, schema.model.String)\
  .field('middle', 0x2, schema.model.String)\
  .field('last_name', 0x3, schema.model.String)\
  .build()


Person = schema.StructBuilder()\
  .field('name', 0x1, Name)\
  .field('email', 0x2, schema.model.String)\
  .field('age', 0x3, schema.model.Float)\
  .field('age_days', 0x4, schema.model.Double)\
  .field('active', 0x5, schema.model.Boolean)\
  .build()


Contacts = schema.StructBuilder()\
  .field('people', 0x1, schema.model.List(Person))\
  .build()


def main():
  people = [Person.create()]
  for i in range(5):
    name = Name.create()
    name.first_name = 'No{}'.format(i)
    name.last_name = 'Person'
    person = Person.create()
    person.name = name
    person.email = 'person{}@test.com'.format(i)
    person.age = 15.0 + i * 3
    person.age_days = person.age * 356.25
    person.active = i == 0
    people.append(person)
  
  contacts = Contacts.create()
  contacts.people = people

  # print(contacts)
  print(Contacts.serialise_value(contacts))
  serialised = Contacts.serialise(contacts)
  print(serialised)
  print(Contacts.deserialise(serialised))



if __name__ == '__main__':
  main()
