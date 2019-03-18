# retention-backend

## Installation

#### 1. Создание экземпляра Cloud SQL
Для хранения событый необходимо созданить эксзепляр Cloud SQL c типом СУБД PostgreSQL

1.1. Открыть окно мониторинга Cloud SQL в консоле Google Cloud и выбрать "Создать экземпляр"

1.2. Выбрать PostgreSQL верссии 9.6 в качесве типа СУБД

1.3. Ввести идентификатор базы, пароль для пользователя *postgres* и регион, после подтвердить создание экземпляра Cloud SQL

1.4. В созданном экзепляре Cloud SQL создать базу данных во вкладке *Базы Данных*

Установить в качестве названия БД значение **retention**.

 *В случае использования своего имени БД необходимо заменить значение переменно CLOUDSQL_DATABASE в файле config.py на соотвутвующее*

1.5. Для создания таблицы необходимо выполнить в консоли Google Cloud слеюущие команды:
```
gcloud sql connect retention --user=postgres
```
*В случае использования своего имени БД использовать его вместо retention*

Далее скопировать в консоль и выполнить команды из файла *src/resources/setup.sql*

#### 2. Конфигурация параметров сервиса

В данном блоке представлена информация о конфигурации сервиса перед деплоем в AppEngine

1.1. Конирование репозитория в Google Cloud
```
git clone https://github.com/Paulymorph/retention-backend.git
```
1.2. Настрока соединения с Cloud SQL из AppEngine

1.2.1. Установка строки соединения с объектом Cloud SQL

Необходимо ввести в файле *app.yaml* строку соединения с объектом Cloud SQL, получаемую на странице монитринга Cloud SQL в переменную *cloud_sql_instances*, например
```
beta_settings:
  cloud_sql_instances: "my-team-project-217908:europe-west1:retention"
```

1.2.2. Соединение с БД

В файле *config.py* необходимо ввести данные для соединения с БД:

```
PROJECT_ID = 'my-team-project-217908'       // Идентификатор проекта Google Cloud
CLOUDSQL_USER = 'postgres'                  // Имя пользователя БД
CLOUDSQL_PASSWORD = '...'                   // Пароль пользователя БД
CLOUDSQL_DATABASE = 'retention'             // Имя БД
CLOUDSQL_CONNECTION_NAME = 'my-team-project-217908:europe-west1:retention' // Строка соединения с объектом Cloud SQL
```

#### 3. Деплой сервиса в App Engine

Для деплоя приложения необходимо перерейти в папку с сконфигурированным приложением и выполнить команду деплоя

```
cd retention-backend
gcloud app deploy
```