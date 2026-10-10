#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

OPENAI_MODEL_DEFAULT="gpt-5.5"
ANTHROPIC_MODEL_DEFAULT="claude-opus-4-7"
COHERE_MODEL_DEFAULT="command-a-reasoning-08-2025"
VOYAGE_RERANK_MODEL_DEFAULT="rerank-2.5"

read_secret() {
  local label="$1"
  local var_name="$2"
  local value=""
  while true; do
    printf "%s: " "$label"
    IFS= read -r -s value
    printf "\n"
    if [[ -n "$value" ]]; then
      printf -v "$var_name" "%s" "$value"
      break
    fi
    printf "Bos gecilemez. Tekrar gir.\n"
  done
}

printf "\nLatentAtlas Concept Boundary API smoke benchmark\n"
printf "Case count: %s\n" "${LATENTATLAS_SMOKE_LIMIT:-10}"
printf "OpenAI decision model: %s\n" "${OPENAI_MODEL:-$OPENAI_MODEL_DEFAULT}"
printf "Anthropic decision model: %s\n" "${ANTHROPIC_MODEL:-$ANTHROPIC_MODEL_DEFAULT}"
printf "Cohere decision model: %s\n" "${COHERE_MODEL:-$COHERE_MODEL_DEFAULT}"
printf "Voyage rerank model: %s\n\n" "${VOYAGE_RERANK_MODEL:-$VOYAGE_RERANK_MODEL_DEFAULT}"
printf "Not: OpenAI/Anthropic/Cohere karar uretir. Voyage rerank/relevance olcer; embedding/generation modeli degildir.\n"
printf "Key degerleri ekranda gosterilmeyecek ve artifact dosyalarina yazilmayacak.\n\n"

read_secret "OpenAI API key" OPENAI_API_KEY
read_secret "Anthropic API key" ANTHROPIC_API_KEY
read_secret "Cohere API key" COHERE_API_KEY
read_secret "Voyage API key" VOYAGE_API_KEY

export OPENAI_API_KEY
export ANTHROPIC_API_KEY
export COHERE_API_KEY
export VOYAGE_API_KEY
export OPENAI_MODEL="${OPENAI_MODEL:-$OPENAI_MODEL_DEFAULT}"
export ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-$ANTHROPIC_MODEL_DEFAULT}"
export COHERE_MODEL="${COHERE_MODEL:-$COHERE_MODEL_DEFAULT}"
export VOYAGE_RERANK_MODEL="${VOYAGE_RERANK_MODEL:-$VOYAGE_RERANK_MODEL_DEFAULT}"

RUN_ARGS=(--limit "${LATENTATLAS_SMOKE_LIMIT:-10}" --confirm-third-party)
if [[ "${1:-}" == "--full" ]]; then
  RUN_ARGS=(--full --resume --confirm-third-party)
  shift
fi

printf "\nBenchmark basliyor...\n"
PYTHONDONTWRITEBYTECODE=1 python3 research/concept_boundary_engine/run_real_llm_boundary_benchmark.py "${RUN_ARGS[@]}" "$@"
printf "\nBitti. Run manifest: outputs/latentatlas/concept_boundary_real_llm_runs/manifest.json\n"
