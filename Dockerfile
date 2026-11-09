
# GEO MiniMax H3 - ambiente independente
FROM runpod/comfyui:cuda12.8

ARG COMFYUI_VERSION=v0.37.0

RUN set -eux; \
    mkdir -p /tmp/geo-comfy; \
    curl -fsSL --retry 5 \
      "https://github.com/Comfy-Org/ComfyUI/archive/refs/tags/${COMFYUI_VERSION}.tar.gz" \
      -o /tmp/geo-comfy.tgz; \
    tar -xzf /tmp/geo-comfy.tgz \
      --strip-components=1 -C /tmp/geo-comfy; \
    rsync -a --delete \
      --exclude=/models \
      --exclude=/custom_nodes \
      --exclude=/user \
      --exclude=/input \
      --exclude=/output \
      /tmp/geo-comfy/ /opt/comfyui-baked/; \
    rm -rf /tmp/geo-comfy /tmp/geo-comfy.tgz

RUN set -eux; \
    grep -Ev '^(torch|torchvision|torchaudio)([[:space:]\[<>=!~;#]|$)' \
      /opt/comfyui-baked/requirements.txt \
      > /tmp/geo-requirements.txt; \
    python3 -m pip install --no-cache-dir \
      --break-system-packages \
      -r /tmp/geo-requirements.txt; \
    rm /tmp/geo-requirements.txt

COPY instalar-modelos.py modelos.json /opt/geo/
COPY workflows/ /opt/geo/workflows/
COPY bootstrap-geo.sh /opt/geo/bootstrap-geo.sh

RUN chmod +x /opt/geo/bootstrap-geo.sh

RUN python3 - <<'PYINJECT'
from pathlib import Path
p = Path('/start.sh')
s = p.read_text()
needle = 'echo "Starting ComfyUI with args: $FIXED_ARGS"'
assert s.count(needle) == 1, 'Inicializador mudou'
s = s.replace(
    needle,
    '/opt/geo/bootstrap-geo.sh\n' + needle
)
p.write_text(s)
PYINJECT
