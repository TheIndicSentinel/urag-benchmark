# Commit SHA map (identity rewrite, 2026-10-14)

History was rewritten once, before anything was published, to replace the local author identity with a GitHub noreply identity. Trees, author dates, commit dates and messages are unchanged (verified commit-by-commit). Earlier documents that cite a short SHA refer to the *old* column.

| Old SHA | New SHA | Subject |
|---|---|---|
| 0493185 | 4535876 | Add deterministic baseline CLI, synthetic corpus, cases C1-C4, plan docs |
| 297d659 | 2f2da87 | Add customer outreach plan, interview guide, evidence log template |
| f47bf58 | e3c49a5 | Pre-register adversarial cases C5-C11 (data + expectations) before execution |
| e939540 | a2ce8d8 | Improve evaluator (non-interference oracle, recall, coverage/risk, splits); record run 1 |
| a12e079 | e03ac01 | Fix fail-open approval state and change relevance; record run 2 and results |
| 7766986 | 6ec3874 | Pre-register C12/C13 held-out env-handling cases and prefilter hypothesis; run 3 |
| 8ad25f9 | 1e5976b | Fix conflict-status overwrite, off-service history, env handling; add prefilter option and |
| 1016538 | 8351525 | Pre-register gates, arms and sample thresholds before public-data evaluation |
| 6321d5b | 434bd3c | Adopt plan v6 and log decisions D5-D9 |
| 8055c70 | d466de4 | Add source survey: candidate public sources, licences and ground-truth rules |
| b677421 | 6db4288 | Add comparison arms N0/N1 and single-check ablations to the runner |
| 97193f0 | 1c01753 | Pre-register C15/C16 (change-environment scoping) before the fix |
| c3f3900 | 8cfa321 | Scope change correlation by environment; record runs 6-7 |
| c9ff97a | 03dfa21 | Register generator config and Amendment 1 before any ingestion; record licence verificatio |
| 3d46244 | 021bc62 | Add S1 (Kubernetes docs) generator and pointer-only cases; Amendment 2 |
| 9aa2b7b | 970794c | Amendment 3: version-unknown policy and public-case outcome taxonomy (before arm A code/ru |
| e9f2aa5 | 0b48a2f | Amendment 4: sensitivity metric and retrieval diagnostics (before full dev run); version d |
| ff5ecba | a7e1d0e | Record first S1 dev run with ablations; document validity problems found |
| 43e425f | 6f416e3 | Amendment 5: support windows, lineage rule and F1 redesign (config v2), before regeneratio |
| 979e4d9 | e843dd5 | Regenerate S1 cases under config v2 (support windows, F1 redesign); lineage rule in arm A |
| 0db43a2 | 4c6f82f | Record v2 dev results: checks now separate under ablation |
| 42ae4a9 | b02067a | Generalize generator (docs_gen, S1/S2); generate S2 PostgreSQL cases; multi-source runner |
| e2e9b84 | de40e3d | Amendment 6: A2 ranked-alternatives variant and metadata-filter control (before code) |
| 581bc9e | b84f355 | Implement A2 / metadata-prefilter variants; record v3 dev results (N1P matches A2P on F1/F |
| 67a1363 | 7e3fe4b | Amendments 7 and 8 (G2 procedure with fail-open/closed controls; sufficiency definition; F |
| 5ff8e06 | 796dcd1 | F4 twins from F1 only (Amendment 8.4); sufficiency, closed-filter and lifecycle-unknown se |
| 0b3d916 | 06424b3 | Add G2 degradation runner, lead query style, sufficiency/closed-filter variants (code for  |
| 0ecb440 | e46e20d | Make G2 runner resumable; add G2 aggregation (matched coverage per Amendment 7) |
| 3dd7131 | e4c8faf | Record v4 dev results: sufficiency and query-style sensitivity |
| 7b19230 | 85f0f39 | Reorder G2 arms for index reuse; record decisions D13-D17 |
| 7839f76 | a9c5fe9 | Amendment 9: primary query style, pre-stated reframe rule, thesis wording; plan status not |
| b017ed9 | 7790b3d | Record G2 determinism spot check |
