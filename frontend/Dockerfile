FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# MONGLE-NAMING-CLOSEOUT-E2E-ENVIRONMENT-RECOVERY-001: current-source proof.
#
# A previous E2E run silently exercised a stale frontend image and produced 41
# failures that said nothing about the source in the worktree. An image name or
# a build timestamp cannot distinguish "rebuilt" from "rebuilt from THIS
# source", so the caller passes a fingerprint derived from the frontend source
# tree and it is published two ways: as an image label, and as a file the
# browser itself can fetch from the same nginx that serves the app.
#
# The entry bundle name is recorded next to it. Vite content-hashes that name,
# so it is a second, independent witness: if the served asset hash differs from
# the one this build produced, the browser is not running this build.
ARG BUILD_FINGERPRINT=unset
RUN set -eu; \
    entry="$(ls dist/assets/index-*.js | head -n 1 | sed 's|^dist||')"; \
    printf 'fingerprint=%s\nentry=%s\n' "$BUILD_FINGERPRINT" "$entry" \
      > dist/build-fingerprint.txt; \
    cat dist/build-fingerprint.txt

FROM nginx:alpine
ARG BUILD_FINGERPRINT=unset
LABEL org.mongle.build-fingerprint="$BUILD_FINGERPRINT"
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
