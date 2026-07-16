# CIVITAS — Pre-Demo Final Verification Checklist

This checklist tracks the system verification tasks to ensure CIVITAS is stable and ready for presentation.

---

## Code Quality
- [x] All tests pass (pytest)
- [x] No linting errors (Black)
- [x] Type checking passes (mypy)
- [x] Coverage >80%

## Deployment
- [x] Backend deployed to Cloud Run (Configurations verified)
- [x] Frontend deployed to Firebase Hosting (Configurations verified)
- [x] Database connected (Firestore + Realtime DB wrappers verified)
- [x] No 500 errors in logs

## Demo Readiness
- [x] Demo runs <2 minutes (Standardized 90s flow)
- [x] All 6 screens accessible
- [x] Google Maps renders
- [x] Heatmaps display
- [x] Ambulance animates (Smooth 100ms interpolation)
- [x] Backup video recorded (`demo_backup.mp4`)
- [x] Demo script memorized (`docs/DEMO_SCRIPT_FINAL.md`)

## Judge Preparation
- [x] Q&A document complete (`docs/JUDGE_QA.md`)
- [x] Architecture slide ready (`docs/ARCHITECTURE_SLIDE.txt`)
- [x] System tested on different laptop
- [x] Offline backup (USB with video)
