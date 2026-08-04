# Deploy GROE v8 — Simple Procedure

No new Git branch is required. Render keeps the last successful deployment live when a new deployment fails, so upload this tested release directly to `main`.

## GitHub

1. Extract `GROE-Client-Feedback-v8-FULL.zip` on your computer.
2. Open the GitHub repository and select branch `main`.
3. Choose **Add file → Upload files**.
4. Drag all extracted files and folders into the repository root.
5. Allow GitHub to replace files with the same names.
6. Commit with: `Deploy complete GROE client feedback v8`.
7. Confirm these files exist on `main`:
   - `backend/app/static/index.html`
   - `backend/app/static/assets/app.v8.1.js`
   - `backend/app/static/assets/styles.v8.1.css`
   - `backend/app/weather/indonesia_locations.py`

## Render

1. Wait for the automatic deployment from `main`.
2. If it does not start, choose **Manual Deploy → Deploy latest commit**.
3. Use **Clear build cache & deploy** only when Render selected the correct new commit but still serves an older build.
4. Do not create separate frontend/backend services and do not change Root Directory, Build Command, Start Command or Publish Directory.

## Proof that the correct release is live

Open:

```text
https://groe-fullstack-beta.onrender.com/api/v1/build
```

Expected:

```json
{"service":"groe","build":"8.1.0"}
```

Then open:

```text
https://groe-fullstack-beta.onrender.com/assets/app.v8.1.js
```

It must return JavaScript rather than 404. The website footer must show `Beta build 8.1.0`.

## Optional AI diary

The diary works without an AI key. To enable AI-supported advice, add `OPENAI_API_KEY` under the existing Render web service's **Environment** page, then save and deploy. Never upload the key to GitHub.
