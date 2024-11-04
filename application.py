from webapp import app as application , update_database

if __name__ == "__main__":
    update_database()
    application.run()