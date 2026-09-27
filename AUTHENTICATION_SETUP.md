# AccessRoute Authentication

The dashboard is now protected by a login screen with two roles:

- User
- Maintainer

## Demo accounts

- User: `user@accessroute.local` / `ChangeMe123!`
- Maintainer: `maintainer@accessroute.local` / `ChangeMe123!`

Change these credentials before deployment. User records are stored in `users.json` with PBKDF2-SHA256 password hashes. The current implementation uses in-memory access tokens, so production deployment should replace this with a persistent session/JWT provider and HTTPS.

## Run

Backend:
```bash
cd Navigation
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Frontend:
```bash
cd Navigation/frontend
npm install
npm run dev
```

The dashboard is not rendered until a successful login is completed. Signing out clears the browser token and returns to the login screen.
