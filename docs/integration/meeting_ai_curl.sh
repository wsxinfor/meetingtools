#!/usr/bin/env bash
# meeting-ai → local-asr-service  curl integration example
# Usage: bash meeting_ai_curl.sh <audio_file.mp3>
set -euo pipefail

BASE_URL="${ASR_BASE_URL:-http://localhost:18080/api}"
API_KEY="${ASR_API_KEY:-asr_your_key_here}"
AUDIO_FILE="${1:?Usage: $0 <audio_file>}"

echo "=== Step 1: Upload audio ==="
UPLOAD_RESP=$(curl -s -X POST "${BASE_URL}/v1/transcriptions" \
  -H "Authorization: Bearer ${API_KEY}" \
  -F "file=@${AUDIO_FILE}" \
  -F "language=zh" \
  -F "enable_vad=true" \
  -F "enable_punctuation=true" \
  -F "enable_diarization=false" \
  -F "enable_filler_removal=false"
)
echo "$UPLOAD_RESP" | python3 -m json.tool

TASK_ID=$(echo "$UPLOAD_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['task_id'])")
echo "Task ID: $TASK_ID"

echo ""
echo "=== Step 2: Poll until done (every 5s) ==="
while true; do
  STATUS_RESP=$(curl -s "${BASE_URL}/v1/transcriptions/${TASK_ID}" \
    -H "Authorization: Bearer ${API_KEY}")

  STATUS=$(echo "$STATUS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['status'])")
  PROGRESS=$(echo "$STATUS_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['progress'])")
  echo "  status=${STATUS}  progress=${PROGRESS}%"

  case "$STATUS" in
    done)      break ;;
    failed)    echo "ERROR: Task failed"; echo "$STATUS_RESP" | python3 -m json.tool; exit 1 ;;
    cancelled) echo "ERROR: Task was cancelled"; exit 1 ;;
  esac
  sleep 5
done

echo ""
echo "=== Step 3: Fetch structured result ==="
curl -s "${BASE_URL}/v1/transcriptions/${TASK_ID}/result" \
  -H "Authorization: Bearer ${API_KEY}" \
  | python3 -m json.tool

echo ""
echo "=== Step 4: Download export files ==="
for FMT in json txt srt vtt; do
  OUT="${TASK_ID}.${FMT}"
  curl -s -o "$OUT" \
    "${BASE_URL}/v1/transcriptions/${TASK_ID}/download?format=${FMT}" \
    -H "Authorization: Bearer ${API_KEY}"
  echo "  Saved: $OUT"
done

echo ""
echo "Done."
