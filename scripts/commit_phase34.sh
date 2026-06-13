#!/bin/bash
set -e
cd /mnt/c/AgriFlow_OS/AgriFlow_Main
git add -A
echo "=== Git Status ==="
git status --short
git commit -m "feat(billing): Phase 3.4 PDF generation + mobile share sheet integration"
echo "=== COMMIT DONE ==="
git push origin stabilization-v1 2>&1 || echo "Push skipped (network)"