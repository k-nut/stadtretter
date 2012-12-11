#!/usr/bin/env python

from main import db
from main import Action

db.create_all()

new_user = Action("knut", "war toll", "", 52.14, 10.00)
second   = Action("Peter", "ist nett", "", 52.11, 10.00)
db.session.add(new_user)
db.session.add(second)
db.session.commit()

print(Action.query.all())
print(Action.query.filter(Action.lat.between(52.10, 52.12), Action.lon.between(9.00, 9.00)).all())
