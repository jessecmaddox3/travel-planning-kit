# Security and privacy

> **TL;DR:** Default workflows are local and offline. Treat your saved trips and exports as private documents. Report bugs with invented data.

The editor binds only to `127.0.0.1`, checks the exact Host and Origin, requires a per-session action token, sends no CORS permission, and restricts browser content with a Content Security Policy. It serves only three editor assets and the explicitly selected starting document. It is not a hosted multiuser service and should not be exposed through a reverse proxy or public tunnel.

Imported JSON is validated before replacing a draft. Rendered text is escaped. Links accept only HTTP(S), with no embedded username/password. Local image reads stay within the configuration folder, reject symlink escapes and accept only bounded PNG/JPEG/WebP files. The server has no arbitrary file-write endpoint. Browser saves are explicit downloads.

An imported trip can reference images within the chosen configuration folder. Use a dedicated trip folder, rather than a broad folder containing unrelated private images. Your own image metadata is not stripped during embedding. A normal local user with access to your machine or files remains outside this tool's threat boundary.

The photo fetch command makes requests only when you run it with a supplied CSV. It follows ordinary HTTP redirects, has a 20-second request timeout and a 5 MB page limit, and preserves prior records for failed listings. Avoid untrusted URL lists. It is not designed to bypass a website's authentication or anti-bot controls.

There are no credentials, telemetry, cloud save or booking integrations. Files in `private/`, `output/`, `.env` and common build/cache folders are ignored by Git, but ignore rules are not a substitute for reviewing what you publish. Keep actual trip files outside this repository when possible.

For a security issue, use the repository's private vulnerability reporting option when available. Do not post personal itineraries, access links, addresses, booking codes or photos in a public issue. A minimal synthetic reproduction is enough to start a report.
