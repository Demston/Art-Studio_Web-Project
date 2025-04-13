"""Сессия текущего пользователя"""

from flask_login import UserMixin


class UserLogin(UserMixin):
    """Сессия пользователя"""

    def fromDB(self, user_id, db):
        """Идентифицирует пользователя в БД"""
        self.__user = db.getUser(user_id)   # getUser из FDataBase
        return self

    def create(self, user):
        """Создаёт пользователя текущей сессии"""
        self.__user = user
        return self

    def get_id(self):
        """Возвращает id пользователя"""
        return str(self.__user['user_id']) if self.__user else "Ошибка в id"

    def getName(self):
        """Возвращает имя пользователя"""
        return self.__user['name'] if self.__user else "Без имени"

    def getEmail(self):
        """Возвращает e-mail пользователя"""
        return self.__user['email'] if self.__user else "Без e-mail"

    def is_authenticated(self):
        """Залогинен ли пользователь"""
        return True

    def is_anonymous(self):
        """Залогинен ли"""
        return False

    def is_active(self):
        """Активен ли"""
        return True
