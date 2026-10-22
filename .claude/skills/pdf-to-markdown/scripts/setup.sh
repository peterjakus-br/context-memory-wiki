#!/usr/bin/env bash
# One-time (per machine / per cloud container) setup for the pdf-to-markdown skill.
#
# Creates an isolated venv OUTSIDE the repo, installs CPU-only PyTorch and
# IBM Docling, and pre-downloads the three models the converter needs
# (layout, TableFormer, CodeFormula). Idempotent: re-running is a no-op
# unless something is missing.
#
#   bash .claude/skills/pdf-to-markdown/scripts/setup.sh
#
# Override locations with PDF2MD_HOME (default ~/.cache/pdf-to-markdown).
# Fresh install: ~2 GB of wheels + ~0.7 GB of model weights, a few minutes.
set -euo pipefail

PDF2MD_HOME="${PDF2MD_HOME:-$HOME/.cache/pdf-to-markdown}"
VENV="$PDF2MD_HOME/venv"
MODELS="$PDF2MD_HOME/models"
PY="$VENV/bin/python"
DOCLING_SPEC="${DOCLING_SPEC:-docling>=2.140,<3}"

mkdir -p "$PDF2MD_HOME"

if [ ! -x "$PY" ]; then
  echo "[setup] creating venv at $VENV"
  python3 -m venv "$VENV"
  "$PY" -m pip install --quiet --upgrade pip
fi

if ! "$PY" -c "import torch" 2>/dev/null; then
  echo "[setup] installing CPU-only torch (avoids multi-GB CUDA wheels)"
  "$PY" -m pip install --quiet torch torchvision --index-url https://download.pytorch.org/whl/cpu
fi

if ! "$PY" -c "import docling" 2>/dev/null; then
  echo "[setup] installing $DOCLING_SPEC"
  "$PY" -m pip install --quiet "$DOCLING_SPEC"
fi

if [ ! -d "$MODELS" ] || [ -z "$(ls -A "$MODELS" 2>/dev/null)" ]; then
  echo "[setup] downloading models (layout, tableformer, code_formula) to $MODELS"
  "$VENV/bin/docling-tools" models download layout tableformer code_formula --output-dir "$MODELS" >/dev/null
fi

"$PY" - <<'EOF'
import docling, torch
print(f"[setup] ok: docling {docling.__version__}, torch {torch.__version__}")
EOF
echo "[setup] venv:   $VENV"
echo "[setup] models: $MODELS"
