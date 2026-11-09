# Опросник: Потребление стримингового видео (Тема №29)

Публичная ссылка после деплоя будет вида:

```
https://ВАШЕ-ИМЯ-ПРИЛОЖЕНИЯ.streamlit.app/#potreblenie-strimingovogo-video
```

## Как получить ссылку (Streamlit Community Cloud)

### 1. Загрузите код на GitHub

1. Создайте **публичный** репозиторий на GitHub (например `streaming-survey-app`).
2. Загрузите в него файлы:
   - `app.py`
   - `requirements.txt`
   - `.gitignore`
   - этот `README.md`

Не загружайте `serviceAccountKey.json`!

### 2. Задеплойте на Streamlit Cloud

1. Зайдите на https://share.streamlit.io/
2. Войдите через GitHub.
3. Нажмите **New app**.
4. Выберите ваш репозиторий, ветку `main`, файл `app.py`.
5. Нажмите **Deploy**.

Через 1–2 минуты появится ссылка вида:
`https://streaming-survey-app-xxxxx.streamlit.app`

### 3. (Рекомендуется) Подключите Firebase через Secrets

1. В настройках приложения на Streamlit Cloud → **Settings → Secrets**.
2. Вставьте содержимое вашего `serviceAccountKey.json` в таком виде:

```toml
[firebase]
type = "service_account"
project_id = "ваш-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "firebase-adminsdk-...@....iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
universe_domain = "googleapis.com"
```

3. Сохраните — приложение перезапустится и начнёт писать в Firestore.

### 4. Ссылка для отчёта / защиты

После деплоя скопируйте URL и добавьте якорь:

```
https://ВАШЕ-ПРИЛОЖЕНИЕ.streamlit.app/#potreblenie-strimingovogo-video
```

Эту ссылку можно вставить в отчёт, дневник и презентацию.
