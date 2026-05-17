FROM node:20

WORKDIR /blockchain

COPY package.json package-lock.json ./
RUN npm install

COPY . .

# Use Ganache for persistence
CMD ["npx", "ganache", "--wallet.deterministic", "--database.dbPath", "/blockchain_data", "--server.host", "0.0.0.0"]
