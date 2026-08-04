# GROE v6.1 cache hotfix

This patch prevents an older browser bundle from remaining visible after a successful Render deployment.

Changes:

- The browser shell now loads versioned assets: `app.v6.1.js` and `styles.v6.1.css`.
- FastAPI sends `Cache-Control: no-store` for the browser shell and static assets during beta.
- The page includes the build marker `data-groe-build="v6.1"`.
- The JavaScript console prints `GROE build v6.1 loaded`.

The v6 client-feedback functionality is unchanged; this patch only ensures that the deployed v6 interface is actually loaded.
