"""База данных, чтение/запись"""
import sqlite3
import time


class FDataBase:
    """Взаимодействие с БД"""

    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    # ################ Добавляем ################

    def addPost(self, text):
        """Добавляет новость"""
        try:
            # берём дату, время и приводим дату в понятный вид
            current_time = time.time()
            local_time = time.localtime(current_time)
            formatted_day = time.strftime("%Y-%m-%d ", local_time)
            formatted_time = time.strftime("  %H:%M", local_time)
            dt_split = formatted_day.split(' ')[0]
            dt_revers = '-'.join(dt_split.split('-')[::-1])+formatted_time
            # делаем запрос на добавление
            self.__cur.execute("INSERT INTO news VALUES(NULL, ?, ?, 'files/default-image.jpg')",
                               (text, dt_revers))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления '+str(e))
            credits()
        return True

    def addPic(self, text):
        """Добавляет работу (картину)"""
        try:
            # берём дату, время и приводим дату в понятный вид
            current_time = time.time()
            local_time = time.localtime(current_time)
            formatted_day = time.strftime("%Y-%m-%d ", local_time)
            formatted_time = time.strftime("  %H:%M:%S", local_time)
            dt_split = formatted_day.split(' ')[0]
            dt_revers = '-'.join(dt_split.split('-')[::-1])+formatted_time
            # делаем запрос на добавление
            self.__cur.execute("INSERT INTO pictures VALUES(NULL, ?, ?, 'files/default-image.jpg')",
                               (text, dt_revers))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления '+str(e))
            credits()
        return True

    # ################ Редактируем ################

    def editPost(self, text, post_id):
        """Редактирование новости"""
        try:
            self.__cur.execute("UPDATE news SET text = ? WHERE post_id = ?", (text, post_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка обновления '+str(e))
            credits()
        return True

    def editPostImage(self, img_path_cut, post_id):
        """Редактирование/добавление картинки к новости"""
        if not img_path_cut:
            return False
        try:
            new_path = img_path_cut.replace('\\', '/')
            self.__cur.execute(f"UPDATE news SET img = ? WHERE post_id = ?", (new_path, post_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления фото "+str(e))
            return False
        return True

    def deletePost(self, post_id):
        """Удаление новости"""
        try:
            self.__cur.execute("DELETE FROM news WHERE post_id = ?", (post_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка удаления '+str(e))
            credits()
        return True

    def editPic(self, text, pic_id):
        """Редактирование описания картины"""
        try:
            self.__cur.execute("UPDATE pictures SET text = ? WHERE pic_id = ?", (text, pic_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка редактирования ' + str(e))
            credits()
        return True

    def editPicImage(self, img_path_cut, pic_id):
        """Редактирование картины (путь к файлу)"""
        if not img_path_cut:
            return False
        try:
            new_path = img_path_cut.replace('\\', '/')
            self.__cur.execute(f"UPDATE pictures SET img = ? WHERE pic_id = ?", (new_path, pic_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления файла "+str(e))
            return False
        return True

    def deletePic(self, pic_id):
        """Удаление записи с картиной из БД"""
        try:
            self.__cur.execute("DELETE FROM pictures WHERE pic_id = ?", (pic_id,))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка удаления '+str(e))
            credits()
        return True

    def editAbout(self, description):
        """Редактирование раздела о себе"""
        try:
            self.__cur.execute("UPDATE siteinfo SET description = ?",
                               (description,))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка редактирования ' + str(e))
            credits()
        return True

    def editPhoto(self, photo):
        """Редактирование/добавление фотографии художника"""
        if not photo:
            return False
        try:
            bin_photo = sqlite3.Binary(photo)
            self.__cur.execute(f"UPDATE siteinfo SET photo = ?", (bin_photo,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления фото "+str(e))
            return False
        return True

    def editContacts(self, email_new, phone_new):
        """Редактирование контактов"""
        try:
            self.__cur.execute("UPDATE siteinfo SET email = ?, phone = ?",
                               (email_new, phone_new))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка редактирования ' + str(e))
            credits()
        return True

    def editPsw(self, user_id, pswrd):
        """Обновляет пароль"""
        try:
            self.__cur.execute(f"UPDATE users SET psw = ? WHERE user_id = {user_id}", (pswrd,))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка записи данных профиля ' + str(e))
        return True

    # ################ Получаем ################

    def getNews(self):
        """Берет статьи из БД"""
        try:
            self.__cur.execute(f"SELECT post_id, text, dt, img FROM news ORDER BY dt DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return []

    def getPost(self, post_id):
        """Берет статью из БД"""
        try:
            self.__cur.execute(f"SELECT post_id, text, dt, img FROM news WHERE post_id = ?", (post_id,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))

    def lastPostId(self):
        """Крайняя запись (post id)"""
        try:
            self.__cur.execute(f"SELECT MAX(post_id) FROM news")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def lastPostImg(self):
        """Крайняя запись (путь к новостной картинке)"""
        try:
            self.__cur.execute(f"SELECT MAX(post_id), img FROM news")
            res = self.__cur.fetchone()[1]
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def getPictures(self):
        """Берет все работы из БД"""
        try:
            self.__cur.execute(f"SELECT pic_id, text, dt, img FROM pictures ORDER BY dt DESC")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения картин ' + str(e))
        return []

    def getPic(self, pic_id):
        """Берет описание картине из БД"""
        try:
            self.__cur.execute(f"SELECT pic_id, text, img FROM pictures WHERE pic_id = ?", (pic_id,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))

    def lastPicId(self):
        """Крайняя запись (pic id)"""
        try:
            self.__cur.execute(f"SELECT MAX(pic_id) FROM pictures")
            res = self.__cur.fetchone()[0]
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def lastPicImg(self):
        """Крайняя запись (путь к картине)"""
        try:
            self.__cur.execute(f"SELECT MAX(pic_id), img FROM pictures")
            res = self.__cur.fetchone()[1]
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def getAbout(self):
        """Берет информацию о художнике из БД"""
        try:
            self.__cur.execute(f"SELECT photo, description FROM siteinfo")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def getContacts(self):
        """Берет информацию о себе (о художнике) из БД"""
        try:
            self.__cur.execute(f"SELECT email, phone FROM siteinfo LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных ' + str(e))
        return True

    def getLogin(self, user_id):
        """Берет логин из БД"""
        try:
            self.__cur.execute(f"SELECT name FROM profile WHERE user_id = {user_id}")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print('Ошибка получения данных профиля ' + str(e))
        return True

    # ################ Авторизуемся ################

    def getUser(self, user_id):
        """Авторизация. Пользователь"""
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE user_id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных '+str(e))
        return False

    def getUserByName(self, name):
        """Авторизация, проверка наличия пользователя"""
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE name = '{name}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print('Пользователь не найден')
                return False
            return res
        except sqlite3.Error as e:
            print('Ошибка получения данных '+str(e))
        return False

    def verifyExt(self, filename):
        """Проверка на *.PNG, *.JPG, *.JPEG"""
        ext = filename.rsplit('.', 1)[1]
        if ext == 'png' or ext == 'PNG' or ext == 'jpg' or ext == 'JPG' \
                or ext == 'jpeg' or ext == 'JPEG' or ext == 'bmp' or ext == 'BMP':
            return True
        return False
