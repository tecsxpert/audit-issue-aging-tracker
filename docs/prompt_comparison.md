# Prompt Comparison

## Version Summary
| Endpoint | Previous Prompt | Optimized Prompt |
|---|---|---|
| `/describe` | Free-form explanation | Fixed sections: Summary, Why It Matters, Likely Impact, Immediate Review Steps |
| `/recommend` | Generic bullet recommendations | Five structured bullets with priority, owner, action, and validation |
| `/generate-report` | Basic report sections | Complete audit report with evidence retention and hallucination guardrails |

## Improvements
| Improvement | Benefit |
|---|---|
| "Use only the audit issue provided" | Reduces unsupported assumptions |
| Explicit section labels | Improves structure score and downstream readability |
| Owner and validation fields | Improves actionability and audit closure quality |
| Evidence to retain | Makes report output more useful for compliance review |
| Security/compliance audience | Keeps responses aligned with project domain |

## Prompt Version
Current production prompt version:

```text
v2.0-quality-reviewed
```

Defined in:

```text
services/prompt_manager.py
```
