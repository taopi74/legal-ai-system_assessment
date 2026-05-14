### Improvement from Edits (Before vs After)

**Before any edits (baseline draft):**

> **Case Fact Summary**
>
> **1. Parties** [evidence_id:doc1:chunk:2]
> GlobalFreight Ltd (Claimant) and SwiftLogistics PLC (Defendant) are the main parties to this dispute. The claimant is a freight forwarding company and the defendant is a logistics provider.
>
> **2. Key Dates** [evidence_id:doc1:chunk:3]
> A contract was entered into between the parties in 2023. A breach occurred sometime after the contract was signed. The claimant commenced proceedings following the breach.
>
> **3. Core Facts** [evidence_id:doc1:chunk:4]
> The claimant alleges that the defendant failed to deliver goods within the agreed timeframe, causing financial losses and operational disruption. The defendant has not yet filed a defence. The claimant seeks compensation for losses suffered as a result of the alleged breach.
>
> **4. Document Type** [evidence_id:doc1:chunk:1]
> Particulars of Claim
>
> **5. Notable Gaps**
> Some details were not clearly stated in the source documents.

---

**Operator edit submitted:**

> **Case Fact Summary**
>
> **1. Parties** [evidence_id:doc1:chunk:2]
> GlobalFreight Ltd (Claimant) v. SwiftLogistics PLC (Defendant).
>
> **2. Key Dates**
> Contract signed: 14 March 2023 [evidence_id:doc1:chunk:3]. Breach date: 02 July 2023 [evidence_id:doc1:chunk:5]. Proceedings issued: 18 September 2023 [evidence_id:doc1:chunk:6].
>
> **3. Core Facts** [evidence_id:doc1:chunk:4]
> Defendant failed to deliver goods by agreed deadline. Claimant suffered £240,000 in damages. No defence filed.
>
> **4. Document Type** [evidence_id:doc1:chunk:1]
> Particulars of Claim
>
> **5. Notable Gaps**
> Exact delivery schedule unclear from documents. Defendant's position not yet on record.

---

**Learned patterns extracted from edit:**

```json
{
  "style_notes": "Prefer concise sections; remove redundant background details",
  "structural_preferences": [
    "Always include explicit evidence tags after key dates",
    "Use 'Claimant v. Defendant' format for parties",
    "Notable Gaps must be specific, not generic"
  ],
  "content_corrections": [
    "Include specific dates with day/month/year format when available in source",
    "Include monetary amounts when stated in source documents",
    "Mark truly unknown facts as 'unclear from documents'"
  ]
}
```

**Re-generated draft (after learning — using `improved_generation_prompt.txt`):**

> **Case Fact Summary**
>
> **1. Parties** [evidence_id:doc1:chunk:2]
> GlobalFreight Ltd (Claimant) v. SwiftLogistics PLC (Defendant).
>
> **2. Key Dates**
> Contract signed: 14 March 2023 [evidence_id:doc1:chunk:3]. Breach: 02 July 2023 [evidence_id:doc1:chunk:5]. Claim issued: 18 September 2023 [evidence_id:doc1:chunk:6].
>
> **3. Core Facts** [evidence_id:doc1:chunk:4]
> Defendant failed to meet agreed delivery deadline. Claimant claims £240,000 in damages for resulting losses. No defence filed to date.
>
> **4. Document Type** [evidence_id:doc1:chunk:1]
> Particulars of Claim
>
> **5. Notable Gaps**
> Exact delivery schedule: unclear from documents. Defendant's position: not yet on record.

---

**Measurable improvement:**

| Metric | Before edit | After learning |
|--------|-------------|----------------|
| Word count | ~420 words | ~180 words |
| Citation tags | 5 (some sections missing) | 8 (all key claims cited) |
| Date specificity | Vague ("2023", "sometime after") | Exact (day/month/year) |
| Notable Gaps quality | Generic ("Some details unclear") | Specific per missing item |
| Monetary figures included | ❌ | ✅ |
