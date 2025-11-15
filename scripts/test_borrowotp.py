from django import setup
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','Student_Resource_Exchange.settings')
setup()
from products.models import BorrowOTP
from registration.models import User
b = BorrowOTP.objects.first()
u = User.objects.first()
print('BorrowOTP exists:', bool(b))
print('registration.User exists:', bool(u))
if b and u:
    try:
        b.verified_by = u
        b.save()
        print('Saved BorrowOTP with registration.User as verified_by — OK')
    except Exception as e:
        print('Error saving BorrowOTP:', e)
else:
    print('No BorrowOTP or no registration.User to test; nothing to save')
