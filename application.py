import os
from flask import url_for
import models
import routes

application = app = routes.app

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            full_name='Admin',
            email='admin@admin.com',
            password='password',
            mobile_no='9999999999',
            admin=True
        )
    except ValueError:
        pass
    application.run(debug = True, host='0.0.0.0', threaded=True)
