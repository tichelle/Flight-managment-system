import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from models import User

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='admin@flight.com').first()
    print('Admin found:', bool(admin))
    if admin:
        print('Role:', admin.role)
        print('Hash length:', len(admin.password_hash))
        print('Check Admin123:', admin.check_password('Admin123'))
        print('Check wrong:', admin.check_password('wrong'))
