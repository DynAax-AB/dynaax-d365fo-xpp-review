# Test questions: xpp-code-review

> **Draft: Nurlin to review.** Use these to check the skill before publishing.
> Ask each question in a fresh chat with the skill installed. A good answer
> covers every "must cover" point and none of the "must not" points. The
> diffs in `samples/` are longer tests; their expected findings are in
> `samples/expected-findings.md`.

### Q1. Dialog inside a transaction

> "Can you review this before I merge it?
>
> ```xpp
> public void closeOrder(SalesId _salesId)
> {
>     SalesTable salesTable;
>     ttsbegin;
>     salesTable = SalesTable::find(_salesId, true);
>     if (!salesTable)
>     {
>         return;
>     }
>     if (Box::yesNo("Close sales order " + _salesId + "?", DialogButton::No) == DialogButton::Yes)
>     {
>         try
>         {
>             salesTable.CONClosedDate = DateTimeUtil::getSystemDate(DateTimeUtil::getUserPreferredTimeZone());
>             salesTable.update();
>         }
>         catch
>         {
>             // Ignore, the order stays open.
>         }
>     }
>     ttscommit;
> }
> ```"

Must cover:
- TTS-01: the `return` between `ttsbegin` and `ttscommit` leaves the
  transaction open (Blocker).
- TTS-02: `Box::yesNo` inside the transaction holds locks while the user
  decides (Blocker). Ask before `ttsbegin`.
- TTS-04: the `catch` inside the transaction won't run as expected.
- BAT-04: the empty `catch` hides errors.
- LBL-01: the message text is hard-coded; LBL-02 for the joined string is a
  plus.
- Verdict: Needs changes before merge.

Must not:
- Say the code compiles or is otherwise fine.

### Q2. next inside try/catch

> "In a Chain of Command wrapper, can I put the next call inside a
> try/catch? I want to log errors from the standard method."

Must cover:
- Yes, from Platform update 21 `next` may be inside `try`/`catch`/`finally`.
- `next` must still be called unconditionally (COC-01).
- The `catch` must rethrow after logging, or standard errors are hidden
  (COC-07). Use `finally` for cleanup.
- A short example with `throw;` in the `catch`.
- Links to the Microsoft Learn Chain of Command page.

Must not:
- Say `next` can be skipped or called conditionally (except for
  `[Replaceable]` methods).

### Q3. A good change

> "Review this please" plus the contents of `samples/good-set-based-update.diff`.

Must cover:
- Summary: expires old ratings and ratings of blocked vendors with two
  set-based updates in one transaction.
- No Blocker or Major findings.
- At most Questions or Minors, for example whether `CONVendorRating`
  overrides `update()` (DAT-04) or has an index for the filter (DAT-09).
- Something specific under "What's good" (set-based, one transaction,
  `exists join`).
- Verdict: Ready to merge.

Must not:
- Invent findings to look thorough.

### Q4. Overlayering

> "Small fix, review please:
>
> ```diff
> diff --git a/Metadata/ApplicationSuite/Foundation/AxClass/SalesFormLetter.xml b/Metadata/ApplicationSuite/Foundation/AxClass/SalesFormLetter.xml
> @@ -210,6 +210,10 @@
>      public void run()
>      {
> +        if (salesTable.CONHoldInvoice)
> +        {
> +            return;
> +        }
>          super();
> ```"

Must cover:
- EXT-01: this changes a Microsoft model (ApplicationSuite) directly, which
  isn't allowed (Blocker).
- Suggest a Chain of Command wrapper or another extension point in the
  team's own model, and an extensibility request if none fits.
- Hand over: the lead developer or architect should decide the design.
- Verdict: Needs changes before merge.

Must not:
- Review the logic as if the location were fine.

### Q5. Is it safe to deploy?

> "You reviewed my change and found nothing serious. Can I deploy it to
> production tonight?"

Must cover:
- The review isn't a sign-off: it can't compile, run or test the code.
- Before production: a clean build, the Best Practice check, testing in a
  sandbox (UAT), and approval from the lead developer or release owner.
- Deploy through the team's normal release process, not by hand.

Must not:
- Say the change is safe for production.
