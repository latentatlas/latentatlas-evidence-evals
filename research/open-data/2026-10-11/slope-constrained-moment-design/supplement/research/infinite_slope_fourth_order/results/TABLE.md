# Independent infinite-switch example: approximate display

Rounded displays only. Exact dyadic interval endpoints and the implicit budgets are in [certificate.json](certificate.json). These are not theta values.

| a | M(a) | δ(M(a)) | M⁴-scaled residual | Leading approximation error | Fourth-order error | Error ratio |
|---|---:|---:|---:|---:|---:|---:|
| 1/5 | 1.33119155592 | 0.266238311183 | 0.0079678446321 | 0.00253733985158 | 0.00051549331242 | 0.203162896015 |
| 1/10 | 2.53926928222 | 0.253926928222 | 0.00671419837391 | 0.000161495019229 | 8.78224405597e-06 | 0.0543808973049 |
| 1/20 | 5.01947568246 | 0.250973784123 | 0.00643811664155 | 1.01420424129e-05 | 1.40269561209e-07 | 0.0138305043007 |
| 1/50 | 12.5077726563 | 0.250155453126 | 0.00636322318748 | 2.59990357335e-07 | 5.78101596092e-10 | 0.00222355014246 |
| 1/100 | 25.0038850731 | 0.250038850731 | 0.0063526080053 | 1.62525713499e-08 | 9.04081376254e-12 | 0.000556269747594 |
| 1/200 | 50.0019423797 | 0.250009711899 | 0.00634995746572 | 1.01583533428e-09 | 1.41293894307e-13 | 0.000139091336498 |

C₂ ≈ 0.024279093400917; C₄ ≈ 0.0063490742416508.

All six sampled fourth-order errors are smaller. This table does not supply a uniform error bound between budgets. The theta weighted-majorant tail certificate is a different object, recorded separately in the certificate.
