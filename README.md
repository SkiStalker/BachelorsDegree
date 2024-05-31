# Система масштабирования вычислительных мощностей автоматизированного мониторинга топлива

Проект предназначен для развертывания в Kubernetes масштабируемой системы и контролирующего модуля, входящего в ее состав.

## Структура директорий и файлов
/app - приложение на языке python3<br/>
&emsp;/client - код генератора трафика<br/>
&emsp;/controller - код контролирующего модуля<br/>
&emsp;/server - код масштабируемой полезной нагрузки<br/>
/frontend<br/>
&emsp;/nginx - конфигурация nginx web-сервера<br/>
&emsp;/diploma - HTML и и JSX файлы для web-ui<br/>
/kubectl - .ymal файлы для развертывания системы в Kubernetes<br/>
&emsp;/controller - файлы для контролирующего модуля<br/>
&emsp;/controllerUser - файлы для системной учетной записи в Kubernetes контролирующего модуля<br/>
&emsp;/postgresql - файлы для СУБД PostgreSQL<br/>
&emsp;/prometheus- файлы для системы мониторинга Prometheus<br/>
&emsp;/serverStub - файлы для полезной нагрузки<br/>
/prometheus - конфиги системы мониторинга Prometheus<br/>
/Dockerfile - файл для сборки контролирующего модуля и web-ui<br/>
/supervisor.cond - конфигурация системы запуска контролирующего модуля и nginx

## Предварительные требования
- [Python3](https://www.python.org) версии 3.12 или выше
- [Node.js](https://nodejs.org/en) версии 20.12 или выше
- [Yarn](https://yarnpkg.com) версии 1.22 или выше
- [Docker](https://www.docker.com) версии 4.30 или выше 
- [kubectl](https://kubernetes.io/ru/docs/tasks/tools/install-kubectl) версии 1.30 или выше

## Предварительная настройка
- kubectl конфигурируется для вашего кластера
- Docker инициализируется и конфигурируется до вашего registry

## Установка dev окружения
1.  Клонируйте репозиторий:
    ```shell
    git clone https://github.com/SkiStalker/BachelorsDegree
    cd BachelorsDegree
    ```
2. Установите модуль venv в python:
    ```shell
    pip install venv
    ```
3. Создайте новое виртуальное окружение:
    ```shell
    python -m venv venv
    ```
4. Активируйте виртуальное окружение: <br/>
    Для Windows:
    ```shell
   venv\Scripts\activate.bat
    ```
   Для Linux:
   ```shell
   source venv/bin/activate
   ```
5. Установите зависимости проекта:
    ```shell
    pip install -r app/controller/src/requirements.txt
    pip install -r app/server/src/requirements.txt
    ```
6. Выйдите из виртуального окружения:
   ```shell
   deactivate
   ```
7. Перейдите в директорию с web-ui:
   ```shell
   cd ./frontend/diploma
   ```
8. Инициализируйте пакетный менеджер
   ```shell
   yarn init
   ```
9. Выход в корень проекта
   ```shell
   cd ../../
   ```
10. При отсутствии ошибок при установке все прошло успешно
    ```shell
    echo Success!!!
    ```

## Запуск приложения в тестовом режиме
### Запуск python компонента: <br/>
1. Инициализация venv<br/>
    Для Windows:
    ```shell
    venv\Scripts\activate.bat
    ```
    Для Linux:
    ```shell
    source venv/bin/activate
    ```
2. Запуск скрипта
    ```shell
    python <путь до необходимого компонента>/<имя компонента>.py
    ```

### Запуск web-ui
1. Переход в директорию web-ui
   ```shell
   cd ./frontend/diploma
   ```
2. Запуск тестовой среды
    ```shell
   yarn dev
    ```
## Сборка проекта
1. Переход в директорию web-ui
    ```shell
    cd ./frontend/diploma
    ```
2. Сборка web приложения
    ```shell
    yarn build
    ```
3. Переход в корневую директорию
    ```shell
    cd ../../
    ```
4. Сборка Docker контейнера для контролирующего модуля
    ```shell
    docker build . -f Dockerfile -t controller
    ```
5. Переход в директорию полезной нагрузки
    ```shell
    cd ./app/server
    ```
6. Сборка Docker контейнера полезной нагрузки
    ```shell
   docker build . -f Dockerfile -t server
   ```
7. Публикация в registry Docker полученных образов
    ```shell
    docker push controller
    docker push server
    ```

## Развертывание в Kubernetes
Will soon...
