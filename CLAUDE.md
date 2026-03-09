# CLAUDE.md

## Project Overview

LangGraph agent projects trying out new features and examples in different folders such as:

- LangGraph Ollama integration
- LangGraph LiteLLM integration
- LangGraph multi-agent example
- LangGraph HITL example

The purpose of this repository is to create minimal, working reference implementations of different patterns and features.

This repository is not intended to contain production-grade systems.

---

## Core Philosophy

This project follows a strict MVP-first development approach.

Rules:

- start with the smallest working implementation
- avoid unnecessary abstractions
- add complexity only after the previous version works
- each phase must run successfully before moving forward
- never implement future phases early

---

## Absolute Rules (Prevent Overengineering)

Claude must not introduce the following unless explicitly requested:

- design patterns (factory, strategy, dependency injection)
- abstract base classes
- plugin systems
- generic utilities
- complex config frameworks
- premature optimization
- large folder hierarchies
- unnecessary classes

Prefer:

- simple functions
- minimal files
- direct implementation
- readable code

---

## Project Goal

Build a LangGraph backend application that processes uploaded health reports.

Pipeline:

1. upload report
2. remove PII
3. parse health report
4. convert parsed data to markdown
5. store processed data in vector database
6. allow querying of stored documents

Input reports may contain:

- unstructured text
- tables
- mixed formatting

---

## Target System Architecture

3-tier architecture

Interface  
→ Chainlit

Backend  
→ LangGraph

Database  
→ in-memory storage initially

Future storage  
→ Qdrant vector database

---

## Development Phases

### Phase 1 — Hello World

Goal: verify LangGraph setup.

Requirements:

- single Python file
- minimal dependencies
- one node only
- prints "hello world"
- spaghetti code allowed
- no folders
- no abstractions

Stop after this phase.

---

### Phase 2 — Basic Graph

Goal: create a minimal working pipeline.

Add nodes:

- upload node
- PII removal node
- parse node

Rules:

- keep minimal files
- nodes implemented as simple functions
- avoid abstractions

Add:

- basic config variables
- environment variable usage

---

### Phase 3 — Refactor

Only begin after Phase 2 runs successfully.

Refactor into structure:

src/
  graph/
  nodes/
  utils/

Add:

- telemetry
- improved prompts
- basic logging

---

### Phase 4 — Vector Storage

Add:

- Qdrant integration
- embedding model
- document chunking

Optimization allowed in this phase.

Examples:

- chunking strategy
- ef parameters
- searchParams tuning

---

## LangGraph Guidelines

Use StateGraph pattern.

Rules:

- one node = one feature
- nodes implemented as simple Python functions
- avoid class-based nodes
- avoid abstractions until refactor phase

Example nodes:

- upload_node
- pii_node
- parse_node
- index_node

---

## Tech Stack

Preferred stack:

- LangGraph
- LiteLLM
- DeepSeek models
- Chainlit

Rules:

- max tokens per invocation: 500
- use LiteLLM rate limiting

---

## Project Structure (After Refactor Phase)

src/
  graph/
  nodes/
  utils/

tests/

Tests are optional until Phase 3.

---

## Setup Rules

Always:

- use uv
- use uv pip
- create and activate .venv
- refer only to latest official documentation

Environment variables may be copied from:

~/.env/.env

---

## Makefile

All frequently used commands must be added to a Makefile.

Examples:

make run  
make test  
make lint

---

## Coding Guidelines

Prioritize:

- readability
- simple functions
- clear docstrings

Avoid:

- clever code
- complex abstractions
- unnecessary engineering

---

## Agentic AI Projects

Preferred frameworks:

1. LangGraph
2. Google ADK

LangGraph is the default choice.

---

## Completion Rule

After completing a development phase:

1. ensure the code runs successfully
2. do not implement the next phase
3. stop and wait for user confirmation before continuing

---

## Development Workflow

Rules:

- implement only the current phase
- do not design for future phases
- verify the phase runs before moving forward
- commit after each successful phase
