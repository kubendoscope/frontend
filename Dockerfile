# Stage 1: Build the app
FROM node:current-alpine AS builder

WORKDIR /app
COPY . .

RUN npm install --legacy-peer-deps
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built files to nginx's public dir
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: replace default nginx config
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
