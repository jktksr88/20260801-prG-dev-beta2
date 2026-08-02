# Frontend development source

This folder contains the original React + TypeScript + Vite development source.

Render does **not** run npm or Vite. The production browser files are committed under:

`backend/app/static/`

That deliberate single-runtime setup prevents npm package or frontend build failures during Render deployment. Changes made in this development folder must be reflected in the committed static frontend before release.
