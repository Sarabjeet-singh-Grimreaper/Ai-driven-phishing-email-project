FROM node:18-alpine

WORKDIR /app

COPY package.json pnpm-lock.yaml* package-lock.json* ./

RUN npm install

COPY . .

# Set env to point to Docker network service gateway by default
ENV NEXT_PUBLIC_API_URL=http://localhost:8000

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "start"]
