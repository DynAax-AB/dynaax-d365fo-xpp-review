# Reading X++ in a diff

> **Draft: Nurlin to review.**

F&O stores X++ code and metadata as XML files, one per element. A pull
request diff shows changes to those files.

## Where things are

The path tells you the package, the model and the element type:

```text
Metadata/<Package>/<Model>/<ElementType>/<ElementName>.xml
```

In some repositories the folder is called something else (for example `src/`
or the package name at the top), but the `<Model>/<ElementType>/` part is
the same.

| Folder | What it is | Rules to think of |
|---|---|---|
| `AxClass` | A class, including CoC extension classes and event handler classes | COC, EVT, DAT, TTS, BAT, BP |
| `AxTable`, `AxTableExtension` | A new table, or fields, indexes and field groups added to a standard one | EXT-04, DAT-09, BP-01 |
| `AxForm`, `AxFormExtension` | A form, or changes to a standard form | UI, EXT |
| `AxMenuItemDisplay`, `AxMenuItemAction`, `AxMenuItemOutput` | Menu items | SEC-01, LBL-01 |
| `AxSecurityPrivilege`, `AxSecurityDuty`, `AxSecurityRole` and their `...Extension` folders | Security | SEC |
| `AxDataEntityView` | Data entities | SEC-03 |
| `AxEdt`, `AxEnum`, `AxEnumExtension` | Types and enums | EXT-04, BP-01 |
| `AxLabelFile` | Label files. The text is in `LabelResources/<language>/<Name>.<language>.label.txt`, one `LabelId=Text` per line | LBL |
| `Descriptor/<Model>.xml` | The model descriptor, including which models it references | EXT-01 |

If the model folder is a Microsoft model (`ApplicationSuite`,
`ApplicationPlatform`, `ApplicationFoundation`, `Directory` and so on) and
the element isn't an extension, the change is overlayering (EXT-01).

## Where the code is

Inside an `AxClass` file, the class declaration and each method are in CDATA
blocks:

```xml
<AxClass xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
	<Name>CONExpireRatingsService</Name>
	<SourceCode>
		<Declaration><![CDATA[
final class CONExpireRatingsService extends SysOperationServiceBase
{
}
]]></Declaration>
		<Methods>
			<Method>
				<Name>process</Name>
				<Source><![CDATA[
    public void process(CONExpireRatingsContract _contract)
    {
        ...
    }
]]></Source>
			</Method>
		</Methods>
	</SourceCode>
</AxClass>
```

Tables, forms and their extensions can carry methods the same way, alongside
their properties (`<Label>`, `<HelpText>`, `<DataMethod>` and so on).

## Reading tips

- Lines starting with `+` are added and `-` removed. Review the added lines;
  use the removed ones to understand what changed.
- A new file (`new file mode`) means the whole element is new. Check its
  name, prefix, labels and, for menu items, its security.
- A diff shows only a few lines around each change. If you need the rest of
  the method to judge a rule (for example, whether `ttscommit` comes later),
  say so or ask for the whole file.
- Text in `Label` and `HelpText` properties should start with `@` (a label
  reference). Anything else is hard-coded text (LBL-01).
- Visual Studio project files (`.rnrproj`) and build files rarely need
  review. Mention them only if they add a model reference.
