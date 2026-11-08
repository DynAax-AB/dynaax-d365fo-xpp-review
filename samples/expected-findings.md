# Expected findings for the samples

> **Draft: Nurlin to review.**

The diffs in this folder are small, made-up changes to a made-up model,
`ContosoExtensions`, with the prefix `CON`. Use them to test the skill: give
the assistant one diff, ask for a review, and compare the answer with the
lists below.

- **Must find**: the review is wrong if it misses one of these.
- **May find**: fair points, but not required.
- The **verdict** must be one of those listed. For the good samples, "Merge
  after small fixes" is right when the review finds only Minors.

`tests/check_skills.py` checks that every rule ID here exists in the rules.

## bad-coc-no-next.diff

A `SalesTable` validation added through Chain of Command.

- **Verdict:** Needs changes before merge
- **Must find:** COC-01, COC-02, LBL-01
- **May find:** a Question about the `CONRequiresDeliveryNote` and
  `CONDeliveryNote` fields, which aren't in the change

## bad-row-by-row-update.diff

A method that expires old vendor ratings and ratings of blocked vendors.

- **Verdict:** Needs changes before merge
- **Must find:** DAT-06, DAT-03, DAT-05, TTS-03
- **May find:** DAT-02

## bad-dialog-in-transaction.diff

Closes a sales order after asking the user.

- **Verdict:** Needs changes before merge
- **Must find:** TTS-01, TTS-02, TTS-04, BAT-04, LBL-01
- **May find:** LBL-02

## bad-hardcoded-text-no-privilege.diff

A new vendor scorecard menu item, and a class that calls a scoring web
service.

- **Verdict:** Needs changes before merge
- **Must find:** LBL-04, LBL-03, LBL-01, SEC-01
- **May find:** BAT-05

## bad-display-method-in-grid.diff

An open balance column added to the customer list page.

- **Verdict:** Needs changes before merge
- **Must find:** UI-01, UI-02
- **May find:** a Question about how many customers the list shows

## good-coc-extension.diff

The fixed version of `bad-coc-no-next.diff`.

- **Verdict:** Ready to merge, or Merge after small fixes
- **Must find:** none (no Blocker or Major)
- **May find:** a Question about the fields, which aren't in the change

## good-set-based-update.diff

The fixed version of `bad-row-by-row-update.diff`.

- **Verdict:** Ready to merge, or Merge after small fixes
- **Must find:** none (no Blocker or Major)
- **May find:** a Question under DAT-04 about whether `CONVendorRating`
  overrides `update()`, or under DAT-09 about an index on `Status` and
  `RatingDate`

## good-sysoperation-batch.diff

A batch job (SysOperation) for expiring ratings, with a menu item, privilege,
duty and labels.

- **Verdict:** Ready to merge, or Merge after small fixes
- **Must find:** none (no Blocker or Major)
- **May find:** a Question about which role gets the `CONVendorRatingMaintain`
  duty (SEC-01)
