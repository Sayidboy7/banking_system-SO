from Bank import *
from models import *
from Bank import views


if __name__ == '__main__':
	with app.app_context():
		db.create_all()
	app.run(debug=True, host='0.0.0.0', port=3030)
