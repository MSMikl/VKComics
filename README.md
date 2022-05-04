# VKComics

Скрипт для опубликования на странице ВКонтакте случайного комикса с сайта [https://xkcd.com/](https://xkcd.com/)

## Первоначальная настройка

Для использования скрипта необходимо:

1. Создать собственное приложение ВКонтакте [здесь](https://vk.com/editapp?act=create). После чего сохранить ID приложения со вкладки "Настройки".
2. Получить ключ пользователя, следуя [инструкции](https://vk.com/dev/implicit_flow_user). Параметр **scope** необходим следующий `photos,groups,wall,offline`

Полученный ключ пользователя необходимо записать в файл `.env` в папке со скриптом в формате

    ACCESS_TOKEN = fdjgv35487gpehvjinfgsdh493u65hong3

Также в `.env` следует записать id пользователя и id группы, в которую планируется публиковать посты и текущую версию API Вконтакте

    GROUP_ID = 1234
    USER_ID = 5678
	VERSION = 5.131
    
## Использование

    main.py

При запуске скрипт случайным образом выбирает один из комиксов xkcd, скачивает его и публикует в группу ВКонтакте. После публикации файл удаляется.

В случае успешного выполнения скрипта выводится соответствующее сообщение. В случае неудачи на одном из этапов сообщение об этом также выводится в консоль.
