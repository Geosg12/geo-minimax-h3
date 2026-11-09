
#!/usr/bin/env bash
set -euo pipefail

COMFYUI_DIR=/workspace/runpod-slim/ComfyUI

if [ ! -f "$COMFYUI_DIR/main.py" ]; then
    echo '[GEO] ERRO: ComfyUI nao foi inicializado pelo RunPod.' >&2
    exit 1
fi

mkdir -p "$COMFYUI_DIR/user/default/workflows"
cp -f /opt/geo/workflows/*.json "$COMFYUI_DIR/user/default/workflows/"

python3 /opt/geo/instalar-modelos.py --models-dir "$COMFYUI_DIR/models"

echo '[GEO] INSTALACAO CONCLUIDA. Iniciando ComfyUI 8188.'
