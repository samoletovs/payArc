# payArc

Payment gateway research experiment — secure, API-first payment infrastructure

> Lab experiment under [NauroLabs](https://naurolabs.com).
> Hosted at: https://<not deployed yet>

## Quick start
```bash
npm install
npm run dev
```

## Structure
- `src/` — frontend code
- `api/` — Azure Functions API (created on first feature)
- `infrastructure/main.bicep` — Azure resources (SWA + monitoring)
- `.github/workflows/` — CI/CD via the shared SWA deploy template

## NauroLabs conventions
- Golden path: see [.github/PLATFORM.md](../.github/PLATFORM.md)
- Project lifecycle: hypothesis → MVP → measure → iterate or kill
- AI-native: ask "what if AI did 90% of this?" before designing

## Hypothesis
_Fill in what experiment this project is testing._

