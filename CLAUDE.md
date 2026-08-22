# VLM-GroundBench

## Goal

Build a reproducible research benchmark for evaluating multimodal
vision-language models on natural-language visual grounding.

## Core Research Questions

RQ1:
How accurately can different VLMs localize objects described in natural language?

RQ2:
Does model specialization for visual grounding improve localization accuracy?

RQ3:
How does prompt complexity affect grounding performance?

RQ4:
Does model scale improve grounding performance?

RQ5:
What is the tradeoff between accuracy, latency and computational cost?

## Models

- Qwen2.5-VL-7B
- Llama 3.2 11B Vision
- Llama 3.2 90B Vision
- Cosmos Reason
- Nemotron 3 Nano Omni

## Core Metrics

- IoU
- mAP
- Precision
- Recall
- F1
- Hallucination rate
- Mean inference latency
- Token usage / API cost where available

## Rules

1. Never modify ground-truth annotations automatically.
2. Never change benchmark prompts after results are collected.
3. Every experiment must have a reproducible configuration.
4. Save raw model outputs.
5. Separate raw outputs from derived metrics.
6. Never manually alter evaluation results.
7. All reported metrics must be reproducible from raw outputs.
8. Cite external claims in research documentation.
9. Distinguish model capability from prompt engineering.
10. Do not cherry-pick successful examples.

## Research Integrity

The benchmark protocol must be frozen before final evaluation.
