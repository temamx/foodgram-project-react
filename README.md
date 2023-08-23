## Фудграм - это проект, в котором пользователи публикуют свои рецепты, лайкают и добавляют чужие рецепты в избранное, а также подписывают на других авторов. Попробуй и ты!

## https://temamx.hopto.org

## Автор - ваш покорный слуга feat YandexPracticum

## Стек:
* Python
* Django3
* Nginx
* PostgreSQL
* React
* Docker

## Переменные окружения
Создайте аналогичные переменные окружения из файла example.env

## Как запустить проект
git clone git@github.com:temamx/foodgram-project-react.git

docker-compose up -d --build

docker-compose exec backend python manage.py makemigrations users

docker-compose exec backend python manage.py makemigrations recipes

docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic
