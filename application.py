"""Веб-проект Арт-Студия Юрия Пономарёва. Main File."""

import os
import os.path
import sqlite3
from config import ADMIN, SECRET_KEY
from FDataBase import FDataBase
from UserLogin import UserLogin
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import Flask, render_template, request, g, flash, abort, redirect, url_for, make_response
from werkzeug.datastructures import MultiDict
import hashlib

# Конфигурация
DEBUG = True   # не забываем выключить
app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'database.db')))
MAX_CONTENT_LENGTH = 10240 * 1024  # максимальный размер в байтах, 10Мб

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # вызывает страницу, если юзер не авторизован


@login_manager.user_loader
def load_user(user_id):
    """Создаёт право на просмотр только залогиненым юзерам из БД"""
    return UserLogin().fromDB(user_id, dbase)


def connect_db():
    """Соединение с БД"""
    conn = sqlite3.connect(app.config['DATABASE'])  # путь к БД
    conn.row_factory = sqlite3.Row  # выдача данных из БД в виде словаря
    return conn


def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('crt_tbls.sql', mode='r') as f:
        db.cursor().executescript(f.read())  # запускает скрипты из файла
    db.commit()
    db.close()


def get_db():
    """Соединение с БД, если оно не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()


dbase = None
# кнопки, которые будут видны только пользователю
prf_btn = '<a href="/profile"><b>[👨🏻‍🎨]</b></a>'
ext_btn = '<a href="/logout"><b>[→</b></a>'


@app.before_request
def before_request():
    """Устанавливает соединение с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)


# ################## Главная страница. Новости. Добавление, Редактирование. Удаление ##################


@app.route("/")
def index():
    """Главная страница"""
    news = dbase.getNews()
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('indexadmin.html', news=news, prf_btn=prf_btn, ext_btn=ext_btn)
    else:
        return render_template('index.html', news=news)


@app.route('/showpreview/post_<int:post_id>')
def showpreview(post_id):
    """Отображает картину по id."""
    img_bin = dbase.getPost(post_id)['img']
    if not img_bin:
        return ""
    if img_bin:
        post_img = make_response(img_bin)
        post_img.headers['Content-Type'] = 'image'
        return post_img


@app.route("/addpost", methods=['POST', 'GET'])
@login_required
def addpost():
    """Добавить новость"""
    if request.method == 'POST':
        if len(request.form['text']) == 0:
            flash("Введите текст", "success")
            pass
        else:
            dbase.addPost(request.form['text'])
            last_id = int(dbase.lastPostId())
            return redirect(url_for('addpostimg', last_id=last_id))
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('addpost.html', prf_btn=prf_btn, ext_btn=ext_btn)


@app.route("/addpostimg/post_<int:last_id>", methods=['POST', 'GET'])
@login_required
def addpostimg(last_id):
    """Добавить картинку в новый пост"""
    img = dbase.lastPostImg()
    last_id = dbase.lastPostId()
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('addpostimg.html', prf_btn=prf_btn, ext_btn=ext_btn, img=img, last_id=last_id)


@app.route("/editpost/post_<int:post_id>", methods=['POST', 'GET'])
@login_required
def editpost(post_id):
    """Редактировать новость"""
    text = dbase.getPost(post_id)['text']
    img = dbase.getPost(post_id)['img']
    if request.method == 'POST':
        dbase.editPost(request.form['text'], post_id)
        return redirect('/')
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('editpost.html', prf_btn=prf_btn, ext_btn=ext_btn,
                               text=text, img=img, post_id=post_id)


@app.route('/uploadimage/post_<int:post_id>', methods=['POST', 'GET'])
@login_required
def uploadimage(post_id):
    """Загрузка картинки к новости"""
    if request.method == 'POST':
        file = request.files['file']
        if file and dbase.verifyExt(file.filename):  # проверяем расширение файла
            try:
                image = file.read()
                res = dbase.editPostImage(image, post_id=post_id)
                if not res:
                    pass
            except FileNotFoundError as e:
                print("Ошибка чтения файла: " + str(e))
        else:
            pass
    return redirect(request.referrer)  # переход на предыдущую страницу


@app.route("/deletepost/post_<int:post_id>")
@login_required
def deletepost(post_id):
    """Удалить новость"""
    dbase.deletePost(post_id)
    return redirect('/')


# ################### Каталог с картинами. Добавление, Редактирование. Удаление ###################


@app.route("/catalog")
def catalog():
    """Каталог работ (картин)"""
    pictures = dbase.getPictures()
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('catalogadmin.html', pictures=pictures, prf_btn=prf_btn, ext_btn=ext_btn)
    else:
        return render_template('catalog.html', pictures=pictures)


@app.route('/showpicture/pic_<int:pic_id>')
def showpicture(pic_id):
    """Отображает картину по id."""
    pic_bin = dbase.getPic(pic_id)['img']
    if not pic_bin:
        return ""
    if pic_bin:
        pic_img = make_response(pic_bin)
        pic_img.headers['Content-Type'] = 'image'
        return pic_img


@app.route("/picplug", methods=['POST', 'GET'])
@login_required
def picplug():
    """Заглушка, создаёт пустую запись с id перед добавлением картины"""
    dbase.addPic('')
    last_id = int(dbase.lastPicId())
    return redirect(url_for('addpicimg', last_id=last_id))


@app.route("/addpicimg/pic_<int:last_id>", methods=['POST', 'GET'])
def addpicimg(last_id):
    """Добавить картину"""
    img = dbase.lastPicImg()
    if request.method == 'POST':
        return redirect(url_for('addpictext', last_id=last_id))
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('addpicimg.html', prf_btn=prf_btn, ext_btn=ext_btn, img=img, last_id=last_id)


@app.route('/uploadpicture/pic_<int:pic_id>', methods=['POST', 'GET'])
@login_required
def uploadpicture(pic_id):
    """Загрузка картины"""
    if request.method == 'POST':
        file = request.files['file']
        if file and dbase.verifyExt(file.filename):  # проверяем расширение файла
            try:
                image = file.read()
                res = dbase.editPicImage(image, pic_id=pic_id)
                if not res:
                    pass
            except FileNotFoundError as e:
                print("Ошибка чтения файла: " + str(e))
        else:
            pass
    return redirect(request.referrer)  # переход на предыдущую страницу


@app.route("/addpictext/pic_<int:last_id>", methods=['POST', 'GET'])
@login_required
def addpictext(last_id):
    """Добавить название картины (год, цена и т.д.)"""
    if request.method == 'POST':
        last_id = int(dbase.lastPicId())
        dbase.editPic(request.form['text'], last_id)
        return redirect('/catalog')
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('addpictext.html', prf_btn=prf_btn, ext_btn=ext_btn)


@app.route("/editpicture/pic_<int:pic_id>", methods=['POST', 'GET'])
def editpicture(pic_id):
    """Редактировать работу"""
    text = dbase.getPic(pic_id)['text']
    img = dbase.getPic(pic_id)['img']
    if request.method == 'POST':
        dbase.editPic(request.form['text'], pic_id=pic_id)
        return redirect('/catalog')
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('editpicture.html', prf_btn=prf_btn, ext_btn=ext_btn,
                               text=text, img=img, pic_id=pic_id)


@app.route("/deletepicture/pic_<int:pic_id>")
@login_required
def deletepicture(pic_id):
    """Удалить работу"""
    dbase.deletePic(pic_id)
    return redirect('/catalog')


@app.route("/deletepiclastid")
@login_required
def deletepiclastid():
    """Удалить работу, которую начал добавлять"""
    last_id = int(dbase.lastPicId())
    dbase.deletePic(last_id)
    return redirect('/catalog')


# ################### Раздел о себе. Редактирование ####################


@app.route("/about")
def about():
    """Информация о себе (о художнике)"""
    edit_btn = '<button class="edit-button"><a href="/editabout"><b>Редактировать</b></a></button>'
    description = dbase.getAbout()['description']
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('about.html', description=description,
                               prf_btn=prf_btn, ext_btn=ext_btn, edit_btn=edit_btn)
    elif current_user.is_authenticated and current_user.getName() != ADMIN:
        return render_template('about.html', description=description,
                               prf_btn=prf_btn, ext_btn=ext_btn)
    else:
        return render_template('about.html', description=description)


@app.route("/editabout", methods=['POST', 'GET'])
@login_required
def editabout():
    """Редактировать информацию о себе"""
    description = dbase.getAbout()['description']
    if request.method == 'POST':
        dbase.editAbout(request.form['description'])
        return redirect('/about')
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('editabout.html', prf_btn=prf_btn, ext_btn=ext_btn,
                               description=description)


@app.route('/thephoto')
def thephoto():
    """Фото художника"""
    photo_bin = dbase.getAbout()['photo']
    if not photo_bin:
        return ""
    photo = make_response(photo_bin)
    photo.headers['Content-Type'] = 'image'
    return photo


@app.route('/uploadphoto', methods=['POST', 'GET'])
@login_required
def uploadphoto():
    """Загрузка фотографии"""
    if request.method == 'POST':
        file = request.files['file']
        if file and dbase.verifyExt(file.filename):  # проверяем расширение файла
            try:
                photo = file.read()
                res = dbase.editPhoto(photo)
                if not res:
                    pass
            except FileNotFoundError as e:
                print("Ошибка чтения файла: " + str(e))
        else:
            print("Изображение не добавлено")
    return redirect('/editabout')


# ################### Контактная информация. Редактирование ###################


@app.route("/contacts")
def contacts():
    """Контакты"""
    edit_btn = '<button class="edit-button"><a href="/editcontacts"' \
               'style="color: rgb(60, 60, 60);"><b>Редактировать</b></a></button>'
    email, phone = dbase.getContacts()
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('contacts.html', email=email, phone=phone,
                               prf_btn=prf_btn, ext_btn=ext_btn, edit_btn=edit_btn)
    elif current_user.is_authenticated and current_user.getName() != ADMIN:
        return render_template('contacts.html', email=email, phone=phone,
                               prf_btn=prf_btn, ext_btn=ext_btn)
    else:
        return render_template('contacts.html', phone=phone, email=email)


@app.route("/editcontacts", methods=['POST', 'GET'])
@login_required
def editcontacts():
    """Редактировать контакты"""
    email, phone = dbase.getContacts()
    if request.method == 'POST':
        dbase.editContacts(request.form['email'], request.form['phone'])
        return redirect('/contacts')
    if current_user.is_authenticated and current_user.getName() == ADMIN:
        return render_template('editcontacts.html', prf_btn=prf_btn, ext_btn=ext_btn,
                               email=email, phone=phone)


# ################### Профиль. Авторизация ###################


@app.route("/profile", methods=['POST', 'GET'])
def profile():
    """Профиль"""
    user = current_user.getName()
    if request.method == 'POST':
        if request.form['pswrd1'] == request.form['pswrd2'] and \
                len(request.form['pswrd1']) + len(request.form['pswrd2']) == 0:
            flash("Пустое поле!", "error")
        elif request.form['pswrd1'] == request.form['pswrd2']:
            pswrd = hashlib.md5(request.form['pswrd2'].encode()).hexdigest()  # хешируем пароль
            dbase.editPsw(current_user.get_id(), pswrd)
            flash("Пароль обновлён", "success")
        else:
            flash("Пароли не совпадают!", "error")
    if current_user.is_authenticated:
        return render_template('profile.html', user=user, prf_btn=prf_btn, ext_btn=ext_btn)
    else:
        return render_template('profile.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    """Авторизация"""
    form = FlaskForm()  # подключим для защиты от csrf-атак
    if current_user.is_authenticated:  # перенаправим в профиль, если юзер уже вошёл
        return redirect('/profile')
    if request.method == 'POST':
        user = dbase.getUserByName(request.form['name'])  # нашли юзера по имени в БД
        psw_form = request.form['psw']  # если юзер есть и хеш паролей совпали
        if user and user['psw'] == hashlib.md5(psw_form.encode()).hexdigest():
            # обращаемся к методу класса из нашего модуля, создаём юзера текущей сессии
            userlogin = UserLogin().create(user)
            login_user(userlogin, remember=True)  # login_user - импорт из flask_login
            # переход на запращиваемую страницу сразу после авторизации (либо в профиль, если не она найдена)
            return redirect(request.args.get('next') or '/profile')
        else:
            flash('Неверный логин/пароль!', 'error')
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    """Выход из профиля"""
    logout_user()  # logout_user - импорт из flask_login
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=DEBUG)
