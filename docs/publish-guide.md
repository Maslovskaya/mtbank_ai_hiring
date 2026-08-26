# Инструкция по публикации репо

## 1. Создать репо на GitHub

```bash
# Через GitHub CLI
gh repo create mtbank-ai-hiring --public --description "MTBank AI Engineer — тестовое задание"

# Или вручную на github.com/new
```

## 2. Запушить

```bash
cd mtbank-ai-hiring
git init
git add .
git commit -m "feat: initial test assignment for AI Engineer vacancy"
git branch -M main
git remote add origin https://github.com/YOUR_ORG/mtbank-ai-hiring.git
git push -u origin main
```

## 3. Настроить репо

В Settings → General:
- ✅ Issues — включить (кандидаты сдают через Issue)
- ❌ Wiki — выключить
- ❌ Projects — выключить

В Settings → Pages: отключить (не нужен)

## 4. Добавить Topics для поиска

```
mtbank, ai, llm, openwebui, speech-recognition, hiring
```

## 5. Ссылка для кандидатов

```
https://github.com/YOUR_ORG/mtbank-ai-hiring
```

Вставьте эту ссылку в письмо кандидатам и в docx-документ вместо описания ТЗ.
