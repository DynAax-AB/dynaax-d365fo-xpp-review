# X++ review rules

> **Draft: Nurlin to review.** Rules marked `REVIEW` need confirming by an
> experienced F&O technical lead.

Each rule has an ID to quote in findings, a severity, what to look for in a
diff, why it matters and the fix. Severities are explained in
`severity-and-verdict.md`. Code examples use the made-up prefix `CON`.

Report a rule only when the change breaks it. Don't report standard
Microsoft code that the change didn't touch.

---

## 1. Extensions, not overlayering (EXT)

Source: [Customize through extension and overlayering](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/customization-overlayering-extensions),
[Naming guidelines for extensions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/naming-guidelines-extensions)

### EXT-01 No overlayering of Microsoft or ISV models

**Severity:** Blocker

**Look for:** a changed file under a Microsoft model folder (ApplicationSuite,
ApplicationPlatform, ApplicationFoundation, Directory and so on) or an ISV
model, that isn't an extension element (`AxTableExtension`,
`AxFormExtension` and so on) in the team's own model. Also a model descriptor
that marks a Microsoft model as customized.

**Why it matters:** Microsoft's models are sealed against overlayering. Even
where a model still allows it, every update has to be merged by hand, and the
change can be lost or break the next update.

**Fix:** move the change into the team's own model as an extension: a table
or form extension, a Chain of Command class, an event handler or a delegate
subscription. If no extension point exists, ask Microsoft for one through an
extensibility request.

### EXT-02 Don't copy a standard element to change it

**Severity:** Major

**Look for:** a new form, class or table that is a near copy of a standard one
(same methods, a prefixed name), and menu items pointed at the copy.

**Why it matters:** the copy doesn't get Microsoft's fixes and new features.
Standard code that calls the original still calls the original.

**Fix:** extend the original. Copy only when the process is truly different,
and say why in the pull request.

### EXT-03 Name extension elements and classes the standard way

**Severity:** Minor

**Look for:** extension elements not named `<Element>.<Prefix>Extension`
(for example `CustTable.CONExtension`), and extension classes not named
`<Element><Prefix>_Extension` (for example `CustTableCON_Extension`).

**Why it matters:** clear names show at a glance what is extended and by whom,
and avoid name clashes with other models extending the same element.

**Fix:** rename to the standard pattern.

### EXT-04 Prefix what you add to standard elements

**Severity:** Major

**Look for:** new fields, indexes, field groups, enum values or methods on
standard tables, forms or enums without the model prefix, such as a field
called `DeliveryNote` on `SalesTable`.

**Why it matters:** if Microsoft later adds an element with the same name, the
build breaks or the two silently mix up.

**Fix:** add the prefix, for example `CONDeliveryNote`.

### EXT-05 Don't use internal, non-hookable or obsolete APIs

**Severity:** Major

**Look for:** calls to methods marked `[Internal]`, wrappers or handlers on
methods marked `[Hookable(false)]` or `[Wrappable(false)]`, and calls to
methods with `SysObsoleteAttribute`.

**Why it matters:** Microsoft can change or remove these in any update without
notice. Obsolete methods are already planned for removal.

**Fix:** use the public replacement the obsolete message names, or a
supported extension point.

Source: [Deprecation of methods and metadata elements](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/migration-upgrade/deprecation-deletion-apis)

---

## 2. Chain of Command (COC)

Source: [Method wrapping and Chain of Command](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/method-wrapping-coc)

### COC-01 Always call next, at the top level of the method

**Severity:** Blocker

**Look for:** a wrapper method where `next` is inside an `if`, a loop, a
`switch`, after a `return`, or missing. Only methods marked `[Replaceable]`
may skip `next`.

**Why it matters:** the standard logic, and every other extension in the
chain, doesn't run. The compiler rejects most of these cases, so the change
may not build at all.

**Fix:** call `next` once, at the top level, and put the condition around
your own logic instead.

```xpp
// Before
public boolean validateWrite()
{
    boolean ret;
    if (this.CONDeliveryNote)
    {
        ret = next validateWrite();
    }
    return ret;
}

// After
public boolean validateWrite()
{
    boolean ret = next validateWrite();
    if (ret && !this.CONDeliveryNote)
    {
        ret = checkFailed("@CON:DeliveryNoteRequired");
    }
    return ret;
}
```

### COC-02 Extension classes are final, attributed and named _Extension

**Severity:** Major

**Look for:** an `[ExtensionOf(...)]` class that isn't `final`, whose name
doesn't end in `_Extension`, or that uses a string instead of `classStr`,
`tableStr`, `formStr`, `formDataSourceStr`, `formDataFieldStr` or
`formControlStr` (data entities use `tableStr`).

**Why it matters:** the compiler requires `final` and the `_Extension`
suffix. The `*Str` functions make the compiler check the element name.

**Fix:** add `final`, rename the class, and use the right `*Str` function.

### COC-03 Same signature, without default values

**Severity:** Major

**Look for:** a wrapper whose parameters differ from the original, or that
repeats a default value (`str _message = "Hi"`).

**Why it matters:** the wrapper must match the original's signature, and
must leave out default parameter values. Otherwise it doesn't compile.

**Fix:** copy the signature and remove the default values.

### COC-04 One extension class per element per model

**Severity:** Minor

<!-- REVIEW: team convention, not a compiler rule. Confirm it is how you want reviews to treat it. -->

**Look for:** a second `[ExtensionOf]` class for an element that the same
model already extends.

**Why it matters:** wrappers for one element spread over several classes are
hard to find and easy to duplicate.

**Fix:** move the new methods into the existing extension class for that
element.

### COC-05 Put your logic after next unless it must run first

**Severity:** Minor

**Look for:** logic before `next` that changes parameters, buffer fields or
state that the standard method then uses.

**Why it matters:** code before `next` changes what the standard logic sees,
which is easy to get wrong and hard to debug when Microsoft changes the
method.

**Fix:** move it after `next`, or add a comment saying why it has to run
first.

### COC-06 Use the intended extension point

**Severity:** Minor

**Look for:** a wrapper that only overrides a return value or sets a value
when the method offers a delegate, an `EventHandlerResult` or a
`[Replaceable]` hook for that purpose.

**Why it matters:** the intended hook is the supported contract and is less
likely to change.

**Fix:** subscribe to the delegate, or use the hook Microsoft provides.

Source: [Respond using EventHandlerResult](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/respond-event-handler-result)

### COC-07 next inside try/catch doesn't hide standard errors

**Severity:** Major

**Look for:** `next` inside a `try` whose `catch` doesn't rethrow, logs
nothing, or turns an error into a silent `return`.

**Why it matters:** from Platform update 21, `next` may sit inside
`try`/`catch`/`finally` for cleanup. But a `catch` that swallows the
exception hides standard validation and posting errors from the user.

**Fix:** use `finally` for cleanup, and rethrow (`throw;`) after any logging
in the `catch`.

---

## 3. Event handlers (EVT)

Source: [Events and delegates](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-events),
[Table record lifecycle events](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/subscribe-table-events)

### EVT-01 Prefer Chain of Command to pre and post handlers on methods

**Severity:** Minor

**Look for:** new `[PreHandlerFor]` or `[PostHandlerFor]` handlers on a
method that could be wrapped.

**Why it matters:** CoC can use protected members and the return value
directly, and keeps the extension in one class per element.

**Fix:** move the logic to a CoC wrapper. Keep handlers for data events and
delegates.

### EVT-02 Data event handlers return results through the event args

**Severity:** Major

**Look for:** `onValidatedField`, `onValidatedWrite` or `onValidatedDelete`
handlers that throw an error or show a message without setting the result.

**Why it matters:** the caller reads the result from the event args. If the
handler throws, users get an error instead of a normal validation message,
and other handlers don't run.

**Fix:** set the result on `ValidateEventArgs` (`parmValidateResult(false)`)
after `checkFailed`.

### EVT-03 Subscribe to delegates where Microsoft provides them

**Severity:** Minor

**Look for:** a wrapper or handler around a method that already raises a
delegate for this purpose.

**Why it matters:** delegates are the stable hook. They also work across
models without a hard reference.

**Fix:** subscribe to the delegate with `[SubscribesTo]`.

Source: [Delegates](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/extensibility/extensible-code-delegates)

### EVT-04 Handler classes hold handlers only and use compile-time names

**Severity:** Minor

**Look for:** handler attributes with plain strings instead of `classStr`,
`tableStr`, `formStr` and `delegateStr`, and business logic mixed into the
handler class.

**Why it matters:** with plain strings, a renamed element isn't caught at
compile time. Logic in handler classes is hard to reuse and test.

**Fix:** use the `*Str` functions, and move logic to a separate class the
handler calls.

---

## 4. Data access and performance (DAT)

Source: [X++ data selection and manipulation](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-data/xpp-data-home-page),
[Set-based to record-by-record conversion](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-data/xpp-data-perf)

### DAT-01 Use firstonly when one record is enough

**Severity:** Minor

**Look for:** a `select` (not `while select`) that uses only the first
record, without `firstonly`.

**Why it matters:** without `firstonly`, the database may prepare a full
result set the code never reads.

**Fix:** add `firstonly`, or call the table's `find` method.

### DAT-02 Select only the fields you need from wide tables

**Severity:** Minor

**Look for:** `while select` over a wide table (`CustTable`, `SalesLine`,
`InventTrans` and similar) that uses one or two fields.

**Why it matters:** every field is read and sent to the AOS for every row.

**Fix:** add a field list. Then check no later code reads a field that wasn't
selected; it would be empty.

### DAT-03 Use set-based statements instead of row-by-row loops

**Severity:** Major

**Look for:** a `while select forupdate` loop that only sets fields and calls
`update()`, or a loop that only calls `insert()` or `delete()`.

**Why it matters:** row by row means one database call per record. On large
tables a job that could take seconds takes hours, and holds locks longer.

**Fix:** use `update_recordset`, `insert_recordset` or `delete_from`, or
`RecordInsertList` when each row needs calculated values.

```xpp
// After
ttsbegin;
update_recordset rating
    setting Status = CONRatingStatus::Expired
    where rating.Status == CONRatingStatus::Active
       && rating.RatingDate < _cutOff;
ttscommit;
```

### DAT-04 Know when set-based falls back to row by row

**Severity:** Major

**Look for:** set-based statements on tables that override `insert`,
`update` or `delete`, have the database log or alerts on, or have delete
actions. Also any `skipDataMethods(true)`, `skipDatabaseLog(true)`,
`skipEvents(true)` or `skipDeleteActions(true)`.

**Why it matters:** in those cases F&O quietly runs the statement row by row.
The `skip...` calls make it set-based again, but also skip the logic, logging
or alerts, which may be wrong for that table.

**Fix:** if the table's own logic must run, accept row by row. If skipping is
correct, keep the `skip...` call with a comment saying why.

### DAT-05 No select inside a loop

**Severity:** Major

**Look for:** a `select` or `find()` inside a `while select` loop, on a table
that could be joined.

**Why it matters:** one extra query per row. A 10,000-row loop makes 10,001
database calls.

**Fix:** join the table in the `while select`, or use `exists join` or
`notexists join` when you only need to know a record exists.

### DAT-06 Select forupdate in the same transaction that updates

**Severity:** Blocker

<!-- REVIEW: Learn's example shows a select in one transaction and the update in another. Confirm a select at level 0 with the update inside ttsbegin fails the same way. -->

**Look for:** `select forupdate` or `while select forupdate` outside the
`ttsbegin` that later calls `update()` or `delete()` on that buffer. Also
`forupdate` on records that are never updated (Minor).

**Why it matters:** F&O checks that a record is updated at the same
transaction level it was selected at. Otherwise the update fails at run time.

**Fix:** put the select inside the transaction, or reread the record inside
it. Remove `forupdate` where nothing is updated.

Source: [Transaction integrity](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-data/xpp-transaction)

### DAT-07 Don't bypass table logic with doInsert, doUpdate or doDelete

**Severity:** Major

**Look for:** `doInsert()`, `doUpdate()` or `doDelete()` in business logic.

**Why it matters:** they skip the table's `insert`, `update` or `delete`
methods and every extension of them, so related data and validations can be
missed.

**Fix:** call `insert()`, `update()` or `delete()`. If skipping is the
point, for example in a data upgrade script, add a comment saying so.

### DAT-08 Make cross-company queries explicit

**Severity:** Major

<!-- REVIEW: confirm the changecompany buffer point matches current behaviour. -->

**Look for:** code that should read several legal entities but has no
`crossCompany`, and `changecompany` blocks that reuse a buffer declared
outside the block.

**Why it matters:** without `crossCompany`, a query reads only the current
company. A buffer used inside `changecompany` needs to be reset
(`buffer = null`) or it can keep the old company's data.

**Fix:** add `crossCompany` (with a container of companies if needed), and
reset buffers inside `changecompany`.

### DAT-09 Where clauses on large tables match an index

**Severity:** Major

**Look for:** new queries on large transaction tables filtered on fields that
aren't in any index the diff shows, and `like "*text"` with a leading
wildcard.

**Why it matters:** the database has to scan the whole table, which gets
slower as data grows and can block other users.

**Fix:** filter on indexed fields, or add a prefixed index in a table
extension. If you can't see the indexes, raise it as a Question.

---

## 5. Transactions (TTS)

Source: [Transaction integrity](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-data/xpp-transaction),
[X++ exception handling](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-exceptions)

### TTS-01 Every ttsbegin has a matching ttscommit on every path

**Severity:** Blocker

**Look for:** a `return`, `break` or `continue` between `ttsbegin` and
`ttscommit`, or a branch that skips `ttscommit`.

**Why it matters:** an unbalanced transaction fails at run time, and the
user's work in that call is rolled back.

**Fix:** check conditions before `ttsbegin`, or restructure so every path
reaches `ttscommit`. Use an exception to stop.

### TTS-02 No user interaction inside a transaction

**Severity:** Blocker

**Look for:** `Box::`, dialogs, `Dialog`, form opening or anything that waits
for the user between `ttsbegin` and `ttscommit`.

**Why it matters:** the transaction holds database locks while the user
reads the message. Other users and batch jobs wait or deadlock. In batch it
can't work at all.

**Fix:** ask the user before `ttsbegin`, then run the transaction.

### TTS-03 Keep transactions short

**Severity:** Major

**Look for:** web service calls, file reads or writes, or long calculations
inside a transaction; or one transaction per row in a loop when the whole
update should succeed or fail together.

**Why it matters:** long transactions hold locks and block others. A
transaction per row can leave a job half done if it fails midway.

**Fix:** do slow work before the transaction. Decide whether the whole update
belongs in one transaction and say so.

### TTS-04 Catch blocks inside a transaction don't catch most errors

**Severity:** Major

**Look for:** a `try`/`catch` inside `ttsbegin`/`ttscommit` that expects to
handle errors there.

**Why it matters:** an exception inside a transaction cancels the
transaction, and a `catch` inside it doesn't run (except for `UpdateConflict`
and `DuplicateKeyException` caught by name). The first `catch` outside the
transaction handles it instead, so the code doesn't do what it seems to.

**Fix:** put the `try`/`catch` around the whole transaction.

### TTS-05 Retry update conflicts and deadlocks only at level 0, with a limit

**Severity:** Major

**Look for:** `retry` on `Exception::UpdateConflict` or `Exception::Deadlock`
without checking `appl.ttsLevel() == 0`, or without a retry limit.

**Why it matters:** retrying inside an outer transaction can't work, and a
retry with no limit can loop forever.

**Fix:**

```xpp
catch (Exception::UpdateConflict)
{
    if (appl.ttsLevel() == 0 && xSession::currentRetryCount() < 5)
    {
        retry;
    }
    throw Exception::UpdateConflictNotRecovered;
}
```

---

## 6. Labels and hard-coded values (LBL)

Source: [Create localizable labels](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/user-interface/create-localizable-labels-client)

### LBL-01 All user-facing text uses labels

**Severity:** Major

**Look for:** text in quotes passed to `info`, `warning`, `error`,
`checkFailed`, `throw error`, `Box::`, dialog captions, and `Label` or
`HelpText` properties in element XML that aren't `@...` label references.

**Why it matters:** hard-coded text can't be translated, and changing it
needs a code deployment.

**Fix:** add the text to the model's label file and use the label ID, for
example `"@CON:DeliveryNoteRequired"`.

### LBL-02 Build messages with strFmt and placeholders

**Severity:** Minor

**Look for:** messages built by joining strings with `+`.

**Why it matters:** word order differs between languages, so joined pieces
can't be translated properly.

**Fix:** one label with `%1`, `%2` placeholders, and `strFmt("@CON:...",
value1, value2)`.

### LBL-03 No hard-coded companies, users, paths, URLs or accounts

**Severity:** Major

**Look for:** literal legal entity IDs (`"USMF"`), user IDs, file paths,
URLs, main accounts, item numbers or dates in code.

**Why it matters:** the code breaks in another legal entity or environment,
and moving to production needs a code change.

**Fix:** read the value from a parameter table or a configuration form.

### LBL-04 No secrets in code

**Severity:** Blocker

**Look for:** passwords, API keys, client secrets, connection strings or
tokens in code or element XML.

**Why it matters:** everyone with access to the source can read them, they
stay in version history for good, and rotating them needs a deployment.

**Fix:** remove the secret, rotate it, and store it in Azure Key Vault.
Read it through the Key Vault parameters at run time.

Source: [Set up the Azure Key Vault client](https://learn.microsoft.com/en-us/dynamics365/finance/localizations/global/setting-up-azure-key-vault-client)

---

## 7. Security (SEC)

Source: [Role-based security](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/role-based-security),
[Security and data entities](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/data-entities/security-data-entities)

### SEC-01 Every new menu item is in a privilege, and the privilege is in a duty or role

**Severity:** Major

**Look for:** a new `AxMenuItemDisplay`, `AxMenuItemAction` or
`AxMenuItemOutput` with no `AxSecurityPrivilege` entry point for it in the
change. Then a privilege that no duty, role or extension of one includes.

**Why it matters:** without them only system administrators can use the
feature. Teams then hand out admin rights to get round it.

**Fix:** add a privilege with the menu item as an entry point, and add the
privilege to a duty (or a role extension). If they may be in another commit,
raise it as a Question.

### SEC-02 Grant the lowest access level that works

**Severity:** Major

**Look for:** privilege entry points with `Delete` or `Create` access for
forms that only show data, or one privilege that both views and maintains.

**Why it matters:** people get more access than they need, which auditors
flag and which breaks segregation of duties.

**Fix:** separate view and maintain privileges, each with the lowest access
level.

### SEC-03 Data entities have their own privileges

**Severity:** Major

**Look for:** a new public data entity, or one used for integration, with no
view and maintain privileges.

**Why it matters:** integrations then need an admin account or a role that
gives far more access than needed.

**Fix:** add view and maintain privileges for the entity, and a duty for the
integration's role.

### SEC-04 Don't bypass security checks in code

**Severity:** Blocker

<!-- REVIEW: confirm the examples to list here. -->

**Look for:** code that runs logic as another user (`runAs`), turns off
record-level security, or checks for admin rights to unlock a feature.

**Why it matters:** it gives users access their roles don't grant, outside
the security model that auditors review.

**Fix:** give access through privileges and duties. If a bypass is truly
needed, document why and have security sign it off.

---

## 8. Forms and display methods (UI)

Source: [Form styles and patterns](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/user-interface/form-styles-patterns)

<!-- REVIEW: no current Learn page covers display method caching; check the wording of UI-01. -->

### UI-01 Cache display methods shown in grids

**Severity:** Major

**Look for:** a new `display` method bound to a grid column with no
`cacheAddMethod` call in the data source `init`, and no
`[SysClientCacheDataMethodAttribute(true)]` on the method.

**Why it matters:** without caching, the method runs again for every visible
row whenever the form refreshes.

**Fix:** add `[SysClientCacheDataMethodAttribute(true)]` to the method, or
call `cacheAddMethod` in the data source `init` after `next init()`.

### UI-02 No queries inside display methods on large grids

**Severity:** Major

**Look for:** a `select`, aggregate (`sum`, `count`) or `find()` in a
`display` method used on a list page or a grid with many rows.

**Why it matters:** one query per row per refresh. Even cached, the first
load of a large grid is slow.

**Fix:** join the data in the form's data source, use a view, or add a
computed column to a view or data entity.

### UI-03 Put display and edit methods on the table

**Severity:** Minor

**Look for:** new `display` or `edit` methods on a form data source when they
only use that table's data.

**Why it matters:** methods on the table (or table extension) can be reused
by other forms, reports and entities.

**Fix:** move the method to the table or its CoC extension class.

### UI-04 Keep the data source active() method light

**Severity:** Major

**Look for:** queries, calculations or service calls added to `active()`.

**Why it matters:** `active()` runs every time the user moves to another
row, so slow code there makes the whole form feel slow.

**Fix:** do only what must change per row, such as enabling buttons. Load
anything else on demand.

---

## 9. Batch and error handling (BAT)

Source: [Batch processing overview](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/batch-processing-overview),
[Enable batch retries](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/sysadmin/retryable-batch),
[X++ exception handling](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-exceptions)

### BAT-01 Use SysOperation for new batch jobs

**Severity:** Minor

<!-- REVIEW: common practice, but Microsoft Learn's own batch class example still uses RunBaseBatch. Confirm this should be a finding. -->

**Look for:** new classes that extend `RunBase` or `RunBaseBatch`.

**Why it matters:** SysOperation keeps the dialog, parameters (data
contract) and logic (service) apart. That makes the job easier to test, to
call from other code and to extend.

**Fix:** a data contract with `[DataContractAttribute]`, a service class and
a controller extending `SysOperationServiceController`.

### BAT-02 Batch code has no user interaction

**Severity:** Major

**Look for:** `Box::`, dialogs or form calls in code that runs in batch.

**Why it matters:** there is no user in batch. The job fails or waits.

**Fix:** collect input in the dialog before the job runs, and write messages
to the Infolog.

### BAT-03 Say whether a batch job is safe to retry

**Severity:** Minor

<!-- REVIEW: confirm when you want reviewers to ask for BatchRetryable. -->

**Look for:** new batch controllers or `RunBaseBatch` classes that don't
implement `BatchRetryable`.

**Why it matters:** F&O can retry jobs after a short SQL connection error.
That's safe only if running the job twice gives the same result.

**Fix:** implement `BatchRetryable` with `isRetryable()` returning `true` when
the job is safe to run again, or `false` with a comment saying why not.

### BAT-04 No empty catch blocks

**Severity:** Major

**Look for:** `catch { }`, a `catch` with only a comment, or a `catch` that
returns without logging or rethrowing.

**Why it matters:** the error disappears. Users and support see no message,
and the data may be half updated.

**Fix:** log with a label (`error("@CON:...")`) and rethrow with `throw;`,
or handle the specific exception on purpose.

### BAT-05 Catch .NET errors and show the real message

**Severity:** Minor

**Look for:** .NET calls (`System.`, `Microsoft.`, other assemblies) without
`catch (Exception::CLRError)` or `catch (System.Exception ex)`.

**Why it matters:** the Infolog doesn't show `CLRError` exceptions by itself,
so the user sees a vague error with no cause.

**Fix:** catch the .NET exception, write its message to the Infolog, and
rethrow.

---

## 10. Naming and Best Practice warnings (BP)

Source: [X++ compile-time functions](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-ref/xpp-compile-time-functions),
[Write best practice rules](https://learn.microsoft.com/en-us/dynamics365/fin-ops-core/dev-itpro/dev-tools/author-best-practice-rules)

### BP-01 New elements use the model prefix

**Severity:** Minor

**Look for:** new tables, classes, forms, EDTs, enums, menu items or labels
without the team's prefix.

**Why it matters:** names can clash with Microsoft or ISV elements, and it's
unclear who owns the element.

**Fix:** add the prefix.

### BP-02 Fix Best Practice warnings in changed code

**Severity:** Minor

**Look for:** new `SuppressBPWarning` attributes without a justification, and
patterns BP checks usually flag (unused variables, missing labels, missing
documentation on public methods).

**Why it matters:** BP warnings catch real problems early. Suppressed ones
pile up and hide new ones.

**Fix:** fix the warning, or give the suppression a written reason.

### BP-03 No debug code or dead code

**Severity:** Major

**Look for:** `breakpoint;` statements, `info()` calls used for debugging,
and large blocks of commented-out code.

**Why it matters:** `breakpoint` stops execution where a debugger is attached,
debug messages confuse users, and commented-out code hides what the code
really does.

**Fix:** remove them. Version control keeps the old code.

### BP-04 Use compile-time functions instead of names in strings

**Severity:** Minor

**Look for:** element or field names written as strings, such as
`"CustTable"` or `"AccountNum"`, where `tableStr`, `fieldStr`, `classStr`,
`methodStr`, `formStr` or `tableNum`/`fieldNum` would work.

**Why it matters:** the compiler checks the `*Str` functions, so a rename or
typo is caught at build time instead of at run time.

**Fix:** use the matching compile-time function.
