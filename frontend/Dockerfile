FROM node:20-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Открываем порт
EXPOSE 5173

# Команда запуска dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]