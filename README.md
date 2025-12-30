# AI Document Intelligence

Production-ready AI system for extracting, validating, and reasoning over business documents using LLMs.

## Problem
Businesses process large volumes of invoices and logistics documents manually, leading to errors, delays, and inconsistent validation.

## Solution
This project provides an end-to-end document intelligence pipeline that:
- Extracts structured data from documents using LLMs
- Validates data against business rules
- Assigns confidence scores to extracted fields
- Persists results for auditing and downstream systems

## Architecture (High-Level)
- TypeScript API Gateway
- Python FastAPI AI Service
- LLM Extraction Engine
- Rule-based Validation Engine
- PostgreSQL Persistence Layer

## Features (MVP)
- PDF/document upload
- Schema-guided data extraction
- Validation & inconsistency detection
- Confidence scoring
- Structured JSON output

## Tech Stack
- Python (FastAPI)
- TypeScript (Node.js)
- PostgreSQL
- LLM APIs
- Docker

## Status
🚧 MVP in progress
