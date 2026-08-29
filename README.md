# Enterprise_RAG_Pipeline

PPT/PDF
   ↓
Context Extraction
   ↓
Preprocessing
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector DB
   ↓
Retrieval
   ↓
Reranking
   ↓
LLM
   ↓
Evaluation



Traditional RAG
      ↓
Agentic RAG
      ↓
Multi-Agent



enterprise-rag-pipeline/
│
├── README.md
├── .gitignore
├── requirements.txt
├── pyproject.toml
├── .env.example
│
├── configs/
│   ├── extraction.yaml
│   ├── chunking.yaml
│   ├── retrieval.yaml
│   └── model.yaml
│
├── data/
│   ├── raw/
│   │   ├── pptx/
│   │   └── pdf/
│   │
│   ├── intermediate/
│   │   ├── extracted/
│   │   ├── cleaned/
│   │   └── chunks/
│   │
│   └── processed/
│       └── embeddings/
│
├── src/
│   │
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── ppt_loader.py
│   │   ├── shape_extractor.py
│   │   ├── text_extractor.py
│   │   ├── table_extractor.py
│   │   ├── chart_extractor.py
│   │   ├── image_extractor.py
│   │   ├── spatial_ordering.py
│   │   ├── region_builder.py
│   │   ├── document_reconstructor.py
│   │   └── schemas.py
│   │
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── cleaner.py
│   │   ├── deduplicator.py
│   │   ├── low_information_filter.py
│   │   └── metadata.py
│   │
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── slide_chunker.py
│   │   ├── paragraph_chunker.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_service.py
│   │
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   └── qdrant_store.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── semantic_retriever.py
│   │   ├── metadata_filter.py
│   │   ├── query_rewriter.py
│   │   ├── reranker.py
│   │   └── recency_retriever.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py
│   │   └── answer_generator.py
│   │
│   ├── evaluation/
│   │   ├── __init__.py
│   │   ├── dataset.py
│   │   ├── ragas_evaluator.py
│   │   └── benchmark.py
│   │
│   └── pipeline/
│       ├── __init__.py
│       ├── ingestion_pipeline.py
│       └── rag_pipeline.py
│
├── scripts/
│   ├── extract_ppt.py
│   ├── preprocess_documents.py
│   ├── create_chunks.py
│   ├── ingest_vectors.py
│   └── run_rag.py
│
├── tests/
│   ├── unit/
│   │   ├── extraction/
│   │   ├── preprocessing/
│   │   ├── chunking/
│   │   └── retrieval/
│   │
│   └── integration/
│       └── test_ingestion_pipeline.py
│
├── notebooks/
│   ├── 01_ppt_extraction_exploration.ipynb
│   ├── 02_spatial_ordering.ipynb
│   └── 03_chunking_experiment.ipynb
│
└── docs/
    ├── architecture.md
    ├── extraction.md
    ├── chunking.md
    ├── retrieval.md
    └── evaluation.md