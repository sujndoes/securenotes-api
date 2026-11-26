# Security policy

This is a portfolio project I built to learn how to secure an API. It is not a hosted service, and no real user data is stored in it. This page says how to report a problem, which security choices were deliberate, and what the code does not protect against.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting: open the Security tab of this repository and choose "Report a vulnerability". If that option is missing, open an issue titled "Security report" with no technical details, and I will contact you there to arrange a private channel.

Please include the request you sent, what you expected, and what happened instead. I maintain this alone, so replies can take a while. Only the latest commit on `main` is supported.

## Deliberate choices

CORS is off. The API has no browser frontend, so no other origin is allowed to call it from a browser. A future frontend would need an explicit list of allowed origins, and a wildcard combined with credentials would not be acceptable.

The interactive docs (`/docs`, `/redoc` and `/openapi.json`) are disabled unless `ENVIRONMENT` is set to `development`. The setting defaults to `production`, so a deployment that forgets it keeps the docs closed.

Request bodies over 1 MB are rejected by the Caddy proxy with a 413 before they reach the app. The limit lives in the `Caddyfile`, so anything that connects to uvicorn directly on port 8000 skips it. The app checks field lengths on its own as well: passwords must be 12 to 255 characters, note titles up to 255, and note bodies up to 10,000.

Login returns the same 401 message for an unknown email and for a wrong password. An unknown email also runs one password hash check against a dummy hash, so response time does not reveal which emails have accounts. On my laptop, a known email took 200.5 ms and an unknown one 7.9 ms before that fix. After it, they took 152.5 ms and 161.2 ms.

A user who asks for someone else's note gets a 404, not a 403, so the response does not confirm the note exists. Every notes query filters on the owner taken from the token, and a request body cannot set an owner.

Emails are lowercased and stripped of spaces before lookup and before saving, so differently capitalized addresses are the same account.

`/register` and `/login` allow 5 requests per minute per client IP, counted separately for each route. The counters are held in memory, so a restart resets them.

Every response the app produces carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer` and `Cache-Control: no-store`. Responses that Caddy produces itself, such as the 413, do not carry them.

## Secrets

`SECRET_KEY` is required, has no default, and must be at least 32 characters, or the app refuses to start. Generate one with:

```
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The key lives in `.env`, which `.gitignore` excludes. `.env.example` lists the variable names with placeholder values only. CI uses a throwaway key that protects nothing, and Gitleaks scans the full git history on every push and pull request. If a real key ever reaches the repository, replace the key first and clean the history second.

## Logging

Failed logins are logged with the reason, the email and the client IP. Passwords and tokens must never be written to a log. Log lines go to the console, and nothing stores or ships them, so there is no retention policy. Email addresses and IPs are personal data, and a real deployment would need a retention rule for them.

Behind Caddy, the client IP comes from the `X-Forwarded-For` header, which Caddy sets itself and overwrites if a client sends one. Uvicorn trusts that header from `127.0.0.1`, so anything that reaches port 8000 directly can forge its address in the logs and in the rate limiter. For that reason port 8000 must stay unreachable from outside the machine.

## Running it safely

Uvicorn should listen on `127.0.0.1` only and run with `--forwarded-allow-ips=127.0.0.1`. The `--no-server-header` flag hides the `Server: uvicorn` header, which otherwise names the software. Only Caddy faces the network, on 443 plus 80 for the redirect, and a firewall blocks 8000.

Local HTTPS uses Caddy's own certificate authority, which `caddy trust` installs into the Windows trust store. Its private key sits in the Caddy folder under `AppData`, so use it only on your own machine and remove it with `caddy untrust` when you are done. A real deployment would use a public authority such as Let's Encrypt, which Caddy can handle automatically.

## Automated checks

GitHub Actions runs these on every push and pull request: the test suite (30 tests, including ones that confirm one user cannot read, edit or delete another user's notes), `pip-audit` on the pinned dependencies, Bandit on the `app` folder, and Gitleaks on the repository history. Dependabot is off, so a pin that turns vulnerable later shows up only the next time CI runs.

To run the same checks locally:

```
python -m pytest
pip-audit -r requirements.txt
bandit -r app
```

## Known limits

Access tokens last 15 minutes. There are no refresh tokens, no logout and no revocation, so a stolen token works until it expires. Tokens are signed with HS256 and one shared secret, so anyone who gets the key can mint tokens for any user.

The rate limit is per IP address, so an attacker with many addresses gets around it, and a real user who mistypes the password five times waits a minute. Registering a taken email returns 409, which confirms that the address has an account, and only the rate limit slows that down.

Notes are stored as plain text in an unencrypted SQLite file, so anyone who can read the file can read the notes. There is no email verification, password reset, multi-factor login or account lockout. The full list, with the reasoning for each item, is in [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).
