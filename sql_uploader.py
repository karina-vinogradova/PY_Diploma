from pprint import pprint
import sqlalchemy

class SqlUploader():

    def __init__(self):
        
        #Подключение к базе данных
        user = 'testuser'
        password = '1111'
        database = 'testbase'

        engine = sqlalchemy.create_engine(f'postgresql://{user}:{password}@localhost:5432/{database}')
        self.connection = engine.connect()

    def create_table(self, owner_id):
        self.connection.execute(f"""CREATE TABLE IF NOT EXISTS user{owner_id} (id integer primary key);""")
        self.connection.execute(f"""CREATE TABLE IF NOT EXISTS user{owner_id}_photos (
                                        link text,
                                        user{owner_id}_id integer not null references user{owner_id}(id));""")

    def check_id_in_base(self, owner_id, user_id):
        list_of_id = self.connection.execute(f"""SELECT id FROM user{owner_id};""").fetchall()
        for id in list_of_id:
            if id[0] == user_id:
                return True
        else:
            return False

    def upload_id_to_table(self, owner_id, user_id):
        if not self.check_id_in_base(owner_id, user_id):
            self.connection.execute(f"""INSERT INTO user{owner_id} VALUES ({user_id});""")

    def upload_photo_to_table(self, owner_id, user_id, photo_link: str):
        self.connection.execute(f"""INSERT INTO user{owner_id}_photos VALUES ('{photo_link}', {user_id});""")
                   
