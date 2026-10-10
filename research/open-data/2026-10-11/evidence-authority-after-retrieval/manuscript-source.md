---
title: "Evidence Authority After Retrieval: A Control-Surface Framework for RAG and Agentic Systems"
author: "Huseyin Buldurgan, LatentAtlas"
date: "2026-07-07"
version: "0.2"
status: "Zenodo-ready working paper draft"
license_candidate: "CC BY 4.0, to be confirmed before publication"
language: "eng"
---

# Evidence Authority After Retrieval

## A Control-Surface Framework for RAG and Agentic Systems

Huseyin Buldurgan, LatentAtlas  
huseyin@latentatlas.ai  
Version 0.2  
2026-07-07

## Abstract

A prior LatentAtlas methodology preprint argued that relevance is not authority: a retrieved source may be topically correct while still being insufficient for action, publication, identity resolution, or customer-facing use. Building on that result, this paper develops the post-preprint thesis that evidence authority is an operating control surface between retrieval and downstream use. The proposed layer receives candidate sources from retrieval, binds them to an explicit claim and use context, tests provenance, freshness, identity scope, contradiction state, source role, support axes, and intended use, and returns a controlled lane before generation, action, or publication proceeds. The paper introduces a minimal evidence authority packet, separates retrieval, qualification, generation, action, and audit planes, and argues that review, learning, and release-readiness must remain governed states rather than implicit permission. The contribution is a design framework for RAG and agentic systems that makes retrieved context operationally usable without allowing similarity scores, plausible grounding, or post-hoc review labels to become unexamined authority.

## Keywords

retrieval-augmented generation; RAG; evidence authority; control surface; provenance; AI governance; decision systems; auditability; agentic systems; customer-facing AI

## 1. Introduction

RAG has made it easier for AI systems to find relevant material. The harder problem is deciding what that material is allowed to support.

The first LatentAtlas preprint, "Relevance Is Not Authority," treated this as a measurable benchmark problem. It defined boundary layers, failure categories, and a sealed benchmark surface for authority confusion in commercial LLM APIs. That work established the core thesis: topical relevance, semantic similarity, and retrieved context do not automatically grant evidence support, action readiness, publish safety, or customer-facing authority.

This paper starts after that result and asks what operating boundary a production system needs once relevance and authority have been separated.

The answer proposed here is an evidence authority control surface. The term "control surface" is deliberate. The problem is not only evaluation, and it is not only retrieval. It is the operational boundary between candidate context and the system behavior that follows: answer generation, classification, escalation, workflow action, or public communication.

In practice, the question is not just:

> Did retrieval find something relevant?

It is:

> Given this claim, this source, this use context, this freshness state, this provenance, and this contradiction environment, what is the system allowed to do next?

That question should be explicit, auditable, and separated from both retrieval ranking and language generation.

## 2. Prior Result and New Question

The earlier methodology preprint establishes the empirical and categorical problem: models and retrieval systems can confuse relevance with authority, and the confusion appears in repeatable forms.

Here, that result becomes a systems design question:

1. If relevance is only candidate generation, what should qualify the candidate?
2. If evidence support is not action permission, where should action permission be checked?
3. If internal truth is not customer-facing truth, where should publication authority be enforced?
4. If review is required, how do we prevent review from silently becoming permission?
5. If a claim is later questioned, what artifact explains why the system allowed, blocked, verified, or reviewed it?

The practical contribution is an operating boundary for systems that already accept the relevance-versus-authority distinction.

## 3. Post-Preprint Thesis Extensions

After the first preprint, the stronger thesis is no longer only "relevance is not authority." The stronger thesis is that authority must become a governed system state before AI output can safely move downstream.

The post-preprint work adds six design claims.

### 3.1 Evidence Authority Is an Operating Contract

Authority cannot live only in an explanatory paragraph after an answer is generated. It needs a contract before the answer, action, or publication step. The contract should define what input is allowed, what source metadata is required, what lane can be returned, and what downstream behavior each lane permits.

### 3.2 Candidate Generation Must Not Mutate Truth

Retrieval can produce candidate evidence, but candidate generation should not update production truth, publish customer-facing output, or silently expand the evidence surface. This matters because a retrieval layer can become operationally dangerous when it is treated as both source discovery and source approval.

### 3.3 Proof Requires Support Axes, Not Just Source Count

More sources are not automatically stronger evidence. Multiple weak, duplicated, same-origin, or generic sources can create an illusion of consensus. A stronger evidence packet should ask which support axes are covered: the claim subject, the approval or decision condition, and traceability back to a source that can be inspected.

### 3.4 Review Is a Controlled State

Review-needed and context-needed outputs must not be coerced into allow decisions. This is a separate thesis from the original relevance claim. The original failure was semantic overreach; the later operating failure is state leakage, where an ambiguous lane quietly behaves like permission.

### 3.5 Learning Is a Proposal Layer

Systems should learn from reviewed outcomes, but learning should first create proposals, hard negatives, calibration candidates, or shadow-policy tests. It should not directly mutate production rules, customer-facing output, memory, or policy. This preserves improvement without allowing the system to rewrite its own authority boundary.

### 3.6 Release Readiness Requires Negative Controls

A green run is not enough. The system also needs proof that it fails when it should fail: stale artifacts, malformed packets, unexpected fields, weak evidence, public-output leaks, missing reason-code coverage, or incomplete readiness inputs should block or route to review. A release gate is credible only when its negative controls are visible.

These extensions shift the argument from a benchmark thesis to a system thesis. The first paper established that authority confusion exists. The post-preprint claim is that authority must be represented as packet shape, lane state, verification gate, release control, and audit trail.

## 4. From Retrieval Pipeline to Decision Boundary

A conventional RAG pipeline is often drawn as a linear path:

```text
ingest -> retrieve -> generate -> deliver
```

That path is too compressed for systems where the answer can affect a customer, record, workflow, financial decision, legal interpretation, or public statement.

The safer architecture separates five planes:

| Plane | Role | Main risk if collapsed |
| --- | --- | --- |
| Retrieval plane | Finds candidate material | Similarity becomes proof |
| Qualification plane | Tests whether candidates can support the claim | Related context becomes evidence |
| Generation plane | Produces text, classification, or proposed action | Fluent output hides weak evidence |
| Action/publication plane | Decides whether output can affect a system or audience | Internal support becomes external authority |
| Audit plane | Preserves why the lane was chosen | Later review cannot reconstruct the decision |

The evidence authority layer lives primarily in the qualification plane, but it must be visible to the action and audit planes. If it is hidden inside a prompt, a reranker, or an unstructured answer explanation, the boundary will be difficult to verify and easy to bypass.

## 5. The Evidence Authority Control Surface

An evidence authority control surface is the interface between retrieved context and downstream use. It should not replace the retriever, vector database, search index, or language model. It should constrain what those systems are allowed to support.

The control surface has four responsibilities.

### 5.1 Bind the Claim

The system must know what claim is being supported. A candidate source can be useful for one claim and useless for another. "The policy mentions refund windows" is different from "this customer should be denied a refund today."

### 5.2 Bind the Use Context

The system must know what the claim will be used for. Internal orientation, analyst review, automated action, public communication, and direct customer response require different evidence bars.

### 5.3 Qualify Candidate Evidence

The system must test whether candidate evidence is specific, current, provenance-backed, identity-aligned, non-contradicted, and appropriate for the requested use.

### 5.4 Return a Controlled Lane

The result should not be a vague confidence score. It should be a lane with a reason: allow, verify, review, or block. Only an allow lane for the requested use should permit downstream generation, action, or publication without additional intervention.

## 6. Minimal Evidence Authority Packet

The development detail missing from many RAG discussions is the packet shape. If the system cannot represent the claim, use context, source status, and lane separately, it cannot reliably enforce the boundary.

A minimal public-safe packet can be described without exposing private implementation details:

| Field | Purpose |
| --- | --- |
| `claim` | The proposition, answer, classification, or action being considered |
| `requested_use` | The intended use: orientation, decision support, action, publication, or customer response |
| `candidate_sources` | The retrieved sources or records being considered |
| `source_role` | Whether a source is policy, evidence, example, glossary, internal note, public statement, or other role |
| `identity_scope` | Whether the source concerns the same entity, a comparable entity, or only the same topic |
| `support_axes` | Which proof axes are covered: claim subject, approval condition, traceability, or domain-specific equivalents |
| `provenance_state` | Whether origin, owner, lineage, and approval state are known |
| `freshness_state` | Whether the source is current, expired, future-effective, superseded, or review-overdue |
| `contradiction_state` | Whether conflicting sources exist and whether they override the candidate |
| `sensitivity_state` | Whether the source can be used internally, publicly, or customer-facing |
| `lane` | The resulting state: allow, verify, review, or block |
| `reason_code` | A compact explanation of why the lane was chosen |
| `audit_reference` | The trace needed to inspect the decision later |

This packet is not meant to be a universal standard. It is a minimum control shape. Different domains can add fields, but removing these distinctions tends to recreate the original failure: retrieved context becomes unexamined authority.

## 7. Why a Score Is Not Enough

Many production systems already have scores: retrieval similarity, reranker score, model confidence, answer-quality score, moderation score, or human rating. These are useful, but they do not answer the authority question by themselves.

A single score cannot distinguish:

- a related source from an identity-matched source;
- an old source from a current source;
- an internal source from a customer-facing source;
- evidence support from action permission;
- an ambiguous case from an allowed case;
- a contradicted candidate from an uncontested candidate.

Evidence authority therefore should return a structured lane, not only a scalar. Scores can inform the lane, but they should not replace it.

## 8. Review Is a State, Not Permission

Review is often treated as a safe fallback. In many systems, however, review is only a label attached to an output that continues moving through the workflow. That is not review; it is delayed ambiguity.

A review-needed lane should mean:

1. The requested authority has not been granted.
2. The next step is controlled.
3. The reason for review is visible.
4. Any override is attributable.
5. The original candidate evidence and claim remain inspectable.

This matters because review and allow are operationally different states. A system that says "review needed" while still drafting, sending, publishing, suppressing, updating, or escalating has not preserved the boundary.

## 9. Governance Without Broad Data Collection

Evidence authority does not require broad raw-corpus access as a first step. In early evaluation, a safer pattern is to work with minimized source excerpts, masked claim packets, synthetic hard negatives, or customer-controlled infrastructure.

This matters for both security and measurement. Asking for broad tenant data before the purpose, retention period, access controls, masking approach, and third-party exposure are clear can create avoidable risk. It can also obscure the evaluation target. The first question is not "Can we ingest everything?" It is "Can the system preserve the authority boundary on a bounded set of representative claims and sources?"

If live customer data is later required, it should enter through a separate review path that covers purpose limitation, minimization, access control, retention, redaction, logging, transfer boundaries, and vendor review expectations. Evidence handling is part of evidence authority.

## 10. Evaluation Implications

Evaluation should test the boundary, not only answer quality. A useful evidence-authority evaluation set should include high-similarity negatives, stale sources, related-but-not-identical entities, internal-only sources, contradicted candidates, malformed evidence, review-needed cases, and clean valid allows.

The purpose is to measure boundary behavior under pressure. A test set made only of obviously irrelevant documents will flatter the system. The meaningful cases are those where retrieval looks successful but authority is missing or incomplete.

Three reporting principles follow:

1. Report false evidence allows separately from ordinary wrong answers.
2. Report review-needed cases separately from blocked cases.
3. Report valid-allow preservation separately from safety improvement.

Without this separation, an apparently safer system may simply be over-blocking, and an apparently accurate system may still be letting unsupported evidence through.

## 11. Relationship to Vector Databases and Rerankers

This framework is compatible with vector databases, keyword search, hybrid retrieval, rerankers, and enterprise search. It assigns retrieval infrastructure a bounded role in the larger decision system.

The distinction is narrower:

> Retrieval infrastructure finds candidates. Evidence authority decides what candidates may support.

That distinction is useful because it allows the retrieval layer to improve without giving it responsibility it cannot reliably carry alone. A stronger retriever may improve recall and ranking. It still needs a separate control surface before retrieved material is used for action, publication, or customer-facing output.

## 12. Scope of the Framework

The framework is scoped as follows:

- Evidence authority improves control over evidence use; it is not a guarantee of truth.
- Human review remains a controlled lane, not a universal requirement for every RAG output.
- Vector databases and rerankers remain useful candidate-generation infrastructure.
- Domain-specific professional approval processes remain external to the framework.
- Domain policy and source metadata determine how the framework is instantiated.
- Initial evaluation can use minimized source excerpts, masked claim packets, synthetic hard negatives, or customer-controlled infrastructure.
- The earlier benchmark motivates the framework; engagement-specific proof still requires scoped domain evaluation.
- Learning proposals, review labels, and release artifacts are governance inputs, not production authorization by themselves.

Evidence authority is a control framework. It improves how a system handles retrieved context, but it does not remove the need for domain policy, source governance, security review, and human accountability where those are required.

## 13. Practical Implications

For product teams, evidence authority changes the requirement from "show sources" to "show what the sources are allowed to support."

For engineering teams, it argues for a modular boundary: retrieval output should become a candidate packet, not direct prompt fuel. Generation should consume only the authority lane it is permitted to use.

For governance teams, it creates an audit surface. A later reviewer can inspect the claim, candidate source, source role, freshness state, contradiction state, lane, and reason code rather than reconstructing the decision from a generated answer.

For customer-facing teams, it separates internal support from customer-safe communication. A source can help an internal operator without being suitable for direct customer delivery.

## 14. Conclusion

The first problem in RAG was finding relevant context. The next problem is deciding what that context is allowed to do.

The earlier LatentAtlas preprint established the relevance-versus-authority failure mode as a benchmarkable problem. This paper proposes the operating layer that follows from that finding: an evidence authority control surface between retrieval and downstream use.

That layer should bind the claim, bind the use context, qualify candidate evidence, return a controlled lane, and preserve an audit trail. Its purpose is not to replace retrieval or language generation. Its purpose is to prevent retrieved context from silently becoming decision authority.

## References

Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S., and Kiela, D. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." arXiv:2005.11401. https://arxiv.org/abs/2005.11401

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., Zhang, Y., Narayanan, D., Wu, Y., Kumar, A., Newman, B., Yuan, B., Yan, B., Zhang, C., Manning, C. D., Re, C., and others. (2022). "Holistic Evaluation of Language Models." arXiv:2211.09110. https://arxiv.org/abs/2211.09110

National Institute of Standards and Technology. (2023). "Artificial Intelligence Risk Management Framework (AI RMF 1.0)." NIST AI 100-1. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf

World Wide Web Consortium. (2013). "PROV-O: The PROV Ontology." W3C Recommendation. https://www.w3.org/TR/prov-o/

Buldurgan, H. (2026). "Relevance Is Not Authority: A Sealed Boundary Benchmark of Decision-Confusion in Commercial LLM APIs." LatentAtlas methodology preprint. DOI: 10.5281/zenodo.20161629. https://doi.org/10.5281/zenodo.20161629
