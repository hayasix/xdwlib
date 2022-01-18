=======
xdwfile
=======

``xdwfile`` モジュールでは、Binder および Document クラスの基底クラスである
XDWFile クラスに関連する機能を用意しています。

モジュール関数
==============

xdwfile モジュールでは、次のモジュール関数を利用できます。

``copy(input_path, output_path=None)``
    ``input_path`` で示されるファイルを単純に複製します。 ``output_path``
    は複製先のパス名です。指定しない場合は、 ``input_path`` から
    派生したパス名となります。実際に複製されたファイルのパス名を返します。

``create_sfx(input_path, output_path=None)``
    ``input_path`` で示される DocuWorks 文書またはバインダーから
    自己解凍文書 (実行形式) を生成します。 ``output_path`` は生成先の
    パス名 (指定しない場合は、 ``input_path`` と同じ) ですが、拡張子は
    指定にかかわらず ``'.exe'`` とされます。保護された DocuWorks 文書
    またはバインダーを ``input_path`` に指定することはできません。
    実際に生成された自己解凍文書のパス名を返します。

``extract_sfx(input_path, output_path=None)``
    ``input_path`` で示される自己解凍文書 (実行形式) から元の DocuWorks
    文書またはバインダーを抽出します。 ``output_path`` は抽出先のパス名
    (指定しない場合は ``input_path`` と同じ) ですが、拡張子は指定に関わらず
    ``'.xdw'`` または ``'.xbd'`` となります。実際に抽出された DocuWorks
    文書またはバインダーのパス名を返します。

``optimize(input_path, output_path=None)``
    ``input_path`` で示される DocuWorks 文書またはバインダーを最適化します。
    ``output_path`` は最適化された DocuWorks 文書またはバインダーの
    出力先のパス名です。指定しない場合は、 ``input_path`` から
    派生したパス名となります。最適化により、不要なデータが削除され、
    (DocuWorks バージョン 3 以前の) MH 圧縮されていた白黒イメージのページが
    MMR 圧縮へ変換されます。出力先の DocuWorks 文書またはバインダーは、
    インストールされている DocuWorks が対応する最新のデータ形式となります。
    保護された DocuWorks 文書またはバインダー、および署名された DocuWorks
    文書またはバインダーを ``input_path`` に指定することはできません。
    実際に出力された DocuWorks 文書またはバインダーのパス名を返します。

``protect(input_path, output_path=None, protect_type="PASSWORD", auth="NONE", **options)``
    ``input_path`` で示される DocuWorks 文書またはバインダーを保護した
    新たな  DocuWorks 文書またはバインダーを生成します。 ``output_path``
    は生成先のパス名です。指定しない場合は、 ``input_path`` から
    派生したパス名となります。 ``protect_type`` は ``'PASSWORD'``,
    ``'PASSWORD128'`` または ``'PKI'`` です (小文字でもかまいません)。
    ``auth`` は ``'NONE'``, ``'NODIALOG'`` または ``'CONDITIONAL'`` です
    (小文字でもかまいません)。実際に生成されたファイルのパス名を返します。

    ``protect_type`` が ``'PASSWORD'`` または ``'PASSWORD128'`` の場合、
    ``**options`` としてキーワード引数 ``password`` に読取用パスワード,
    ``fullaccess`` にフルアクセス用パスワード, ``comment`` に
    パスワード入力用ダイアログに表示するコメントを指定します。

    ``protect_type`` が ``'PKI'`` の場合、 ``**options`` として
    キーワード引数 ``permission`` に ``'EDIT_DOCUMENT'``,
    ``'EDIT_ANNOTATION'``, ``'PRINT'`` および ``'COPY'``
    (小文字でもかまいせん) のうち 0 個以上をカンマ ``','`` ではさんで
    列挙した文字列、 ``certificates`` に DER (RFC3280) フォーマットの
    文字列で表現された読取アクセス用証明書のシーケンス、
    ``fullaccesscerts`` に DER (RFC3280) フォーマットの文字列で表現された
    フルアクセス用証明書のシーケンスを指定します。

``protection_info(path)``
    ``path`` で示される DocuWorks 文書またはバインダーの保護状態を示す
    2 個の要素からなるタプルを返します。最初の要素は保護の方法を示し、
    その値は ``'PASSWORD'``, ``'PASSWORD128'``, ``'PKI'``, ``'STAMP'``
    または ``'CONTEXT_SERVICE'`` です (小文字でもかまいません)。
    第二の要素は文書またはバインダーについて許可されている操作を示し、
    その値は ``'EDIT_DOCUMENT'``, ``'EDIT_ANNOTATION'``, ``'PRINT'``
    および ``'COPY'`` (小文字でもかまいません) のうち 0 個以上をカンマ
    ``','`` をはさんで列挙した文字列です。

``sign(input_path, output_path=None, page=0, position=None, type="STAMP", certificate=None)``
    ``input_path`` で示される DocuWorks 文書またはバインダーに署名を
    付加した新たな DocuWorks 文書またはバインダーを生成します。
    ``output_path`` は生成先のパス名です。指定しない場合は、
    ``input_path`` から派生したパス名となります。 ``page`` は
    署名を表示するページのページ番号 (0 から始まります) です。
    ``position`` は Point オブジェクトまたは ``None`` です。 ``None`` は
    ``Point(0, 0)`` とみなされます。 ``type`` は ``'STAMP'`` または
    ``'PKI'`` です (小文字でもかまいません)。 ``certificate`` は
    ``type`` が ``'PKI'`` である場合に用いる DER (RFC3280)
    フォーマットの文字列で表現された証明書です。
    実際に生成されたファイルのパス名を返します。

``unprotect(input_path, output_path=None, auth="NONE")``
    ``input_path`` で示される DocuWorks 文書またはバインダーの保護を
    解除した新たな  DocuWorks 文書またはバインダーを生成します。
    ``output_path`` は生成先のパス名です。指定しない場合は、
    ``input_path`` から派生したパス名となります。
    ``auth`` は ``'NONE'``, ``'NODIALOG'`` または ``'CONDITIONAL'`` です
    (小文字でもかまいません)。
    実際に生成されたファイルのパス名を返します。

``xdwopen(path, readonly=False, authenticate=True, autosave=False)``
    ``path`` で示される DocuWorks 文書またはバインダーを開きます。
    ``readonly`` が ``True`` である場合は、読取専用で開きます。
    ``authenticate`` が ``True`` である場合は、保護された DocuWorks
    文書またはバインダーであっても、開くパスワードが設定されていない場合、
    パスワードキャッシュにより認証が成功した場合、および印鑑ケースが
    開いており認証が成功した場合は、開くことができます。
    ``authenticate`` が ``False`` である場合は、保護された DocuWorks
    文書またはバインダーを開くことはできません。 ``autosave`` が ``True``
    である場合は、 ``close()`` の際に自動的に ``save()`` を行います。
    開かれた DocuWorks 文書またはバインダーを Document オブジェクト
    または Binder オブジェクトで返します。

XDWFile オブジェクト
====================

XDWFile クラスは、Document クラスおよび Binder クラスの基底クラスで、DocuWorks が扱う 2 種類のファイル形式 (拡張子 ``.xdw`` および ``.xbd``) に共通する機能を扱います。

XDWFile クラスはコンテキスト管理プロトコルをサポートしており、with 文で利用できます。次のように利用します。 ::

    with Document(path).open() as doc:
        ...

または ::

    with xdwopen(path) as doc:
        ...

コンストラクタ
--------------

クラス ``XDWFile(path)``
    ``path`` は DocuWorks 文書またはバインダーを示すパス名です。
    ファイル名のうち拡張子は ``'.xdw'`` または ``'.xbd'`` でなければ
    なりません。実際に文書またはバインダーを操作するには、
    インスタンスメソッド ``open()`` を呼び出す必要があります。

インスタンス属性
----------------

``annotatable``
    文書またはバインダーへのアノテーションの追加やアノテーションの編集・
    削除が許可されている場合は ``True`` です。
    ``open()`` 後に有効な属性です。 

``attachments``
    文書またはバインダーに添付されたオリジナルデータからなる AttachmentList
    オブジェクトです。  ``open()`` 後に有効な属性です。 

``authenticate``
    文書またはバインダーを開く際に非対話の認証処理を行ったのであれば
    ``True`` です。非対話の認証処理についてはモジュール関数 ``xdwopen()``
    を参照してください。 ``open()`` 後に有効な属性です。

``binder_color``
    バインダーの場合、バインダーの色を示します。
    ``open()`` 後に有効な属性です。 

``binder_size``
    バインダーの場合、バインダーの大きさを ``'A4'``, ``'FREE'``
    などの文字列で示します。 ``open()`` 後に有効な属性です。 

``copyable``
    文書またはバインダーの複製が許可されている場合は ``True`` です。
    ``open()`` 後に有効な属性です。 

``dir``
    DocuWorks 文書またはバインダーが存在するフォルダ (ディレクトリ) です。

``documents``
    バインダーの場合、中に格納されている DocuWorks 文書の個数です。
    ``open()`` 後に有効な属性です。 

``editable``
    文書またはバインダーの編集が許可されている場合は ``True``、
    そうでない場合は ``False`` です。 ``open()`` 後に有効な属性です。 

``handle``
    XDWAPI が内部で使用するドキュメントハンドルです。
    ``open()`` 後に有効な属性です。

``name``
    文書名です。ファイル名から拡張子 (``'.'`` を含む) を除いた部分と
    同じです。

``pages``
    文書またはバインダーのページ数です。バインダーの場合は、通しでの
    総ページ数です。 ``open()`` 後に有効な属性です。 

``printable``
    文書またはバインダーの印刷が許可されている場合は ``True`` です。
    ``open()`` 後に有効な属性です。 

``properties``
    文書またはバインダーに設定されているユーザー定義プロパティの個数です。
    ``open()`` 後に有効な属性です。 

``protection``
    DocuWorks 文書またはバインダーの保護に関する 2 要素のタプルです。
    最初の要素が保護方式 (``'PASSWORD'``, ``'PASSWORD128'``, ``'PKI'``
    または ``'CONTEXT_SERVICE'``)、次の要素が許可されている操作
    (``'EDIT_DOCUMENT'``, ``'EDIT_ANNOTATION'``, ``'PRINT'`` または
    ``'COPY'`` の組み合わせをカンマ ``','`` で区切った文字列) です。

``readonly``
    文書またはバインダーを読取専用で開いたのであれば ``True`` です。
    ``open()`` 後に有効な属性です。 

``signatures``
    文書またはバインダーに付けられている署名の数です。
    ``open()`` 後に有効な属性です。 

``status``
    文書またはバインダーに付けられている署名の検証結果です。
    文書またはバインダーが開かれてからまだ署名の検証が行われていない場合は
    ``'NONE'`` になります。署名の検証が行われた場合は、署名後にその文書
    またはバインダーが編集されていれば ``'EDIT'`` 、編集されていなければ
    ``'NOEDIT'`` となります。署名の検証は行われたものの、その文書または
    バインダーの内容が破損または改竄されていた場合は ``'BAD'`` となります。
    ``open()`` 後に有効な属性です。 

``type``
    文書タイプです。 ``'DOCUMENT'`` または ``'BINDER'`` となります。

``version``
    対応する DocuWorks のバージョン番号です。
    ``open()`` 後に有効な属性です。 

インスタンスメソッド

``close()``
    文書またはバインダーを閉じます。 ``save()`` しないでこのメソッドを
    呼び出すと、 ``open()`` 後に行った操作がファイルに反映されません。

``delete_pageform(sync=False)``
    ページフォームを削除します。 ``sync`` が ``True`` である場合は、
    ``update_pageform()`` と同様にページフォームをそれぞれ削除します。

``delform(sync=False)``
    ``delete_pageform(sync)`` と同じです。

``delprop(name)``
    ``del_property(name)`` と同じです。

``del_property(name)``
    文書またはバインダーに設定されたユーザー定義のプロパティ ``name``
    を削除します。

``filename()``
    文書またはバインダーのファイル名を返します。拡張子も含まれます。

``get_property(name)``
    文書またはバインダーに設定されたユーザー定義のプロパティの値を返します。
    ``name`` が ``str`` である場合は、それをプロパティ名とみなします。
    ``name`` が ``int`` である場合は、それをプロパティの番号 (0 から始まる
    整数) とみなします。文書またはバインダーに設定されているプロパティの
    個数は、インスタンス属性 ``properties`` で参照できます。返される値は、
    ``name`` が ``int`` である場合はタプル (プロパティ名, プロパティ値)、
    ``name`` が ``str`` である場合は ``bool``, ``datetime.date`` または
    ``int`` です。

``getprop(name)``
    ``get_property(name)`` と同じです。

``get_userattr(name)``
    文書またはバインダーに設定されたユーザー属性 ``name`` の値を ``str``
    で返します。

``has_property(name)``
    文書またはバインダーに設定されたユーザ定義のプロパティ ``name`` が
    存在すれば ``True`` を、存在しなければ ``False`` を返します。

``hasprop(name)``
    ``has_property(name)`` と同じです。

``open(readonly=False, authenticate=False)``
    文書またはバインダーを開きます。 ``readonly`` が ``True`` である場合は、
    読取専用で開きます。 ``authenticate`` が ``True`` である場合は、
    非対話の認証処理を行った上で開きます。 ``self`` を返します。
    非対話の認証処理についてはモジュール関数 ``xdwopen()`` を
    参照してください。

``optimize(output_path=None)``
    モジュール関数 ``optimize()`` と同等です。 ``output_path`` が
    指定された場合は、最適化された文書またはバインダーを ``output_path``
    に書き出します。 ``output_path`` が指定されなかった場合は、
    文書またはバインダーのファイル自体を最適化されたものに置き換えます。
    文書またはバインダーがこのメソッドを呼び出した時点で ``open()``
    されていた場合は、いったん ``save()`` および ``close()`` を行い、
    次に最適化を実施して、再度 ``open()`` します。 ``output_path``
    が指定された場合に限り、実際に生成された最適化済みの文書または
    バインダーのパス名を返します。

``pageform(form)``
    文書またはバインダーに設定されたページフォーム (見出し・ページ番号)
    のうち種類が ``form`` であるものを PageForm オブジェクトで返します。
    ``form`` には ``'header'``, ``'footer'``, ``'top_image'``,
    ``'bottom_image'`` または ``'page_number'`` を指定します。

``pageform_text()``
    文書またはバインダーに設定されたページフォーム (見出し・ページ番号)
    からテキストを抽出して返します。
    ``pageform('header').text + '\v' + pageform('footer').text``
    と同じです。

``pathname()``
    文書またはバインダーのフルパス名を返します。

``protect(output_path=None, protect_type='PASSWORD', auth='NONE', **options)``
    モジュール関数 ``protect()`` と同等です。 ``output_path``
    が指定された場合は、保護された文書またはバインダーを ``output_path``
    に書き出します。 ``output_path`` が指定されなかった場合は、
    文書またはバインダーのファイル自体を保護されたものに置き換えます。
    文書またはバインダーがこのメソッドを呼び出した時点で ``open()``
    されていた場合は、いったん ``save()`` および ``close()`` を行い、
    次に保護を行って、再度 ``open()`` します。 ``output_path`` が
    指定された場合に限り、実際に生成された保護された文書または
    バインダーのパス名を返します。

``save()``
    文書またはバインダーを (上書き) 保存します。このメソッドを
    呼び出さないで ``close()`` すると、 ``open()`` 後に行った操作が
    ファイルに反映されません。

``setprop(name, value)``
    ``set_property(name, value)`` と同じです。

``set_property(name, value)``
    文書またはバインダーのユーザー定義のプロパティ ``name`` に値
    ``value`` を設定します。 ``value`` は ``bool``, ``datetime.date``,
    ``int`` または ``str`` で指定します。

``set_userattr(name, value)``
    文書またはバインダーのユーザー属性 ``name`` に値 ``value`` を設定します。
    ``value`` は ``str`` で指定します。

``sign(output_path=None, page=0, position=None, type='STAMP', certificate=None)``
    モジュール関数 ``sign()`` と同等です。 ``output_path`` が指定された
    場合は、署名された文書またはバインダーを ``output_path`` に
    書き出します。 ``output_path`` が指定されなかった場合は、
    文書またはバインダーのファイル自体を署名されたものに置き換えます。
    文書またはバインダーがこのメソッドを呼び出した時点で ``open()``
    されていた場合は、いったん ``save()`` および ``close()`` を行い、
    次に署名を行って、再度 ``open()`` します。 ``output_path`` が
    指定された場合に限り、実際に生成された署名後の文書またはバインダーの
    パス名を返します。

``signature(pos)``
    文書またはバインダーに付けられている署名のうち ``pos`` 番目
    (0 から始まる整数) のものを StampSignature または PKISignature
    オブジェクトで返します。

``unprotect(output_path=None, auth='NONE')``
    モジュール関数 ``unprotect()`` と同等です。 ``output_path`` が
    指定された場合は、保護を解除された文書またはバインダーを
    ``output_path`` に書き出します。 ``output_path`` が指定されなかった
    場合は、文書またはバインダーのファイル自体を保護解除されたものに
    置き換えます。文書またはバインダーがこのメソッドを呼び出した時点で
    ``open()`` されていた場合は、いったん ``save()`` および ``close()``
    を行い、次に保護を解除して、再度 ``open()`` します。 ``output_path``
    が指定された場合に限り、実際に生成された保護解除後の文書または
    バインダーのパス名を返します。

``update_pageform(sync=False)``
    ページフォーム (見出し・ページ番号) を更新します。 ``pageform()``
    で取得された各ページフォーム (上/下見出し、上/下画像およびページ番号)
    の属性に設定された内容に従って、ページフォームを更新します。
    ``sync`` が ``True`` であり、かつページフォームの設定先 (``self.doc``)
    が DocuWorks 文書である場合は、DocuWorks 文書がバインダー内文書で
    あったときに設定されたページフォームも合わせて更新します。 ``sync``
    が ``True`` であり、かつページフォームの設定先が DocuWorks
    バインダーである場合は、バインダー内文書すべてについて、
    それらが 単体の DocuWorks 文書であったときに設定されたページフォームも
    合わせて更新します。

``updform(sync=False)``
    ``update_pageform(sync)`` と同じです。

AttachmentList オブジェクト
===========================

AttachmentList クラスは、DocuWorks 文書またはバインダーのオリジナルデータ
(添付ファイル) 一覧を扱います。個々のオリジナルデータは、Attachment
クラスで扱います。

AttachmentList クラスは、イテレータプロトコルに対応しています。
イテレータとして使用した場合、Attachment オブジェクトを順次返します。

コンストラクタ
--------------

クラス ``AttachmentList(doc, size=None)``
    ``doc`` はオリジナルデータが属する DocuWorks 文書またはバインダー
    (Document オブジェクトまたは Binder オブジェクト) です。 ``size``
    はオリジナルデータの個数です。指定しない場合は ``doc`` が持つ
    オリジナルデータの数を自動的に取得して設定します。

インスタンス属性
----------------

``doc``
    コンストラクタに与える引数と同等です。

``size``
    コンストラクタに与える引数と同等です。

インスタンスメソッド
--------------------

``attachment(pos)``
    オリジナルデータ群の ``pos`` 番目 (0 から始まります) の
    オリジナルデータを Attachment オブジェクトとして返します。
    ``pos`` に負数を指定した場合は、末尾から数えた位置 (-1 が末尾)
    と解釈します。

``append(path)``
    ``path`` で示されるファイルをオリジナルデータとして取り込み、
    オリジナルデータ群の最後に追加します。 ``insert(-1, path)`` と同じです。

``insert(pos, path)``
    ``path`` で示されるファイルをオリジナルデータとして取り込み、
    オリジナルデータ群の ``pos`` 番目に挿入します。
    ``pos`` 番目以降にあったオリジナルデータの位置は、順次繰り下げられます。
    ``pos`` に負数を指定した場合は、末尾から数えた位置 (-1 が末尾)
    と解釈します。 

``delete(pos)``
    オリジナルデータ群の ``pos`` 番目 (0 から始まります) の
    オリジナルデータを削除します。 ``pos`` 番目よりも後ろにあった
    オリジナルデータの位置は、順次繰り上げられます。
    ``pos`` に負数を指定した場合は、末尾から数えた位置 (-1 が末尾)
    と解釈します。 

``__delitem__(pos)``
    ``delete(pos)`` と同じです。

``__getitem__(pos)``
    ``attachment(pos)`` と同じです。

Attachment オブジェクト
=======================

Attachment クラスは、DocuWorks 文書またはバインダーの個々の
オリジナルデータ (添付ファイル) を扱います。

コンストラクタ
--------------

クラス ``Attachment(doc, pos)``
    ``doc`` はオリジナルデータが属する DocuWorks 文書またはバインダー
    (Document オブジェクトまたは Binder オブジェクト) です。 ``pos`` は
    ``doc.attachments`` (AttachmentList オブジェクト) の中での
    オリジナルデータの位置です (0 から始まります)。
    ``pos`` に負数を指定することはできません。

インスタンス属性
----------------

``datetime``
    ファイルの作成日時です。 ``datetime.datetime`` オブジェクトです。

``name``
    オリジナルデータ名です。ファイル名に相当します。パス名ではありません。

``size``
    ファイルの容量です。単位はバイトです。

``text_type``
    オリジナルデータ名の格納形式です。 ``'MULTIBYTE'`` または
    ``'UNICODE'`` です。

インスタンスメソッド
--------------------

``save(path=None)``
    オリジナルデータをファイルシステム上に保存します。 ``path``
    を指定しない場合は、 ``self.name`` (またはそこから派生したパス名)
    を用います。

PageForm オブジェクト
=====================

PageForm クラスは、ページフォームを扱います。ページフォームの種類
(上見出し、上画像、下見出し、下画像およびページ番号) ごとに PageForm
オブジェクトを生成し、設定を行ったうえで、XDWFile オブジェクトの
``update_pageform()`` メソッドを呼び出すと、DocuWorks 文書または
バインダーの見出し等が更新されます。

コンストラクタ
--------------

クラス ``PageForm(doc, form)``
    PageForm クラスは、上見出し、上画像、下見出し、下画像および
    ページ番号を扱います。 ``doc`` はページフォームが属する文書または
    バインダー (Document オブジェクトまたは Binder オブジェクト) です。
    ``form`` は ``'HEADER'``, ``'TOPIMAGE'``, ``'FOOTER'``,
    ``'BOTTOMIMAGE'`` または ``'PAGENUMBER'`` です (小文字でもかまいません)。

インスタンス属性
----------------

``alignment``
    表示の水平位置です。 ``'LEFT'``, ``'CENTER'`` または ``'RIGHT'``
    で指定します (小文字でもかまいません)。

``back_color``
    背景色です。色指定についてを参照してください。

``beginning_page``
    上/下見出しの開始ページです (0 から始まります)。 ``page_range`` が
    ``'SPECIFIED'`` である場合に有効です。

``digit``
    ページ番号の桁数です。

``doc``
    ページフォームを含む DocuWorks 文書またはバインダー (Document または
    Binder オブジェクト) です。

``ending_page``
    上/見出しの開始ページです (0 から始まります)。 ``page_range`` が
    ``'SPECIFIED'`` である場合に有効です。

``font_char_set``
    テキストの属性を指定します。フォント指定についてを参照してください。

``font_name``
    テキストの属性を指定します。フォント指定についてを参照してください。

``font_pitch_and_family``
    テキストの属性を指定します。フォント指定についてを参照してください。

``font_size``
    テキストの属性を指定します。フォント指定についてを参照してください。

``font_style``
    テキストの属性を指定します。フォント指定についてを参照してください。

``fore_color``
    前景色です。色指定についてを参照してください。

``form``
    ページフォームの種類です。値は ``'HEADER'``, ``'FOOTER'``,
    ``'TOPIMAGE'``, ``'BOTTOMIMAGE'`` または ``'PAGENUMBER'`` です。

``image_file``
    上/下画像に指定する画像のパス名です。設定のみ行えます。

``left_right_margin``
    上/下見出しでの左右の余白です。単位はミリメートルです。
    1 ミリメートル未満は無視されます。

``page_range``
    ページフォームの適用範囲です。 ``'ALL'`` (小文字でもかまいません)
    で全ページが、 ``'SPECIFIED'`` (小文字でもかまいません) で
    ``beginning_page`` から ``ending_page`` までが適用範囲になります。

``starting_number``
    ページ番号の開始番号です。

``text``
    上/下見出しまたはページ番号に表示するテキストです。
    ページ番号の場合は、 ``'#'`` が実際のページ番号へ置換されます。

``top_bottom_margin``
    上見出しでの上余白、または下見出しでの下余白です。
    単位はミリメートルです。1 ミリメートル未満は無視されます。

``ver_position``
    ページ番号の表示位置です。 ``'TOP'`` または ``'BOTTOM'``
    (小文字でもかまいません) で指定します。

``zoom``
    上/下画像の表示倍率です。単位はパーセントです。
    10 以上 400 以下で指定します。1 未満は無視されます。

インスタンスメソッド
--------------------

``update(sync=False)``
    ``self.doc.update_pageform(sync)`` と同じです。

``delete(sync=False)``
    ``self.doc.delete_pageform(sync)`` と同じです。

BaseSignature オブジェクト
==========================

BaseSignature クラスは、StampSignature クラスと PKISignature クラスの
基底クラスです。

コンストラクタ
--------------

クラス ``BaseSignature(doc, pos, page, position, size, dt)``
    ``doc`` は署名が属する文書またはバインダー (Document オブジェクト
    または Binder オブジェクト) です。
    ``pos`` は ``doc`` の署名一覧の中での位置です (0 から始まります)。
    ``page`` は署名がつけられたページのページ番号です。
    ``position`` は署名の表示位置 (Point オブジェクト) です。
    ``size`` は署名の表示域の大きさ (Point オブジェクト) です。
    ``dt`` は署名日時 (``datetime.datetime`` オブジェクト) です。

インスタンス属性
----------------

コンストラクタに与える引数と同等です。

インスタンスメソッド
--------------------

``update()``
    署名の状態を取得します。その結果、 ``self.doc.status`` が更新されます。

StampSignature オブジェクト
===========================

StampSignature クラスは、DocuWorks 内蔵の電子印鑑による署名を扱います。
基底クラスは BaseSignature です。

コンストラクタ
--------------

クラス ``StampSignature(doc, pos, page, position, size, dt, stamp_name="", owner_name="", valid_until=None, memo="", status=None)``
    ``doc``, ``pos``, ``page``, ``position``, ``size``, ``dt`` は、
    BaseSignature の引数と同じです。 ``stamp_name`` は電子印鑑の名前、
    ``owner_name`` は電子印鑑の所有者として登録された名前です。
    ``valid_until`` は ``datetime.datetime`` オブジェクトで、
    有効期限の終了日時です。 ``memo`` は電子印鑑に付けられた備考です。
    ``status`` は署名の状態で、 ``'NONE'``, ``'TRUSTED'`` または
    ``'NOTRUST'`` のいずれかです。

インスタンス属性
----------------

コンストラクタに与える引数と同等です。

PKISignature オブジェクト
=========================

PKISignature クラスは、PKI (公開鍵基盤) 電子証明書による署名を扱います。
基底クラスは BaseSignature です。

コンストラクタ
--------------

クラス ``PKISignature(doc, pos, page, position, size, dt, module='', subjectdn='', subject='', issuerdn='', issuer='', not_before=None, not_after=None, serial=None, certificate=None, memo='', verification_type=None, status=None)``
    ``doc``, ``pos``, ``page``, ``position``, ``size``, ``dt`` は、
    BaseSignature の引数と同じです。
    ``module`` はセキュリティモジュールの名前 (``str``) です。
    ``subjectdn`` は SUBJECT DN (distinguished name) の内容 (最大 511
    バイト) です。
    ``subject`` は SUBJECT の内容です。これは電子証明書の CN, OU, O
    または E フィールドにこの順で対応します。
    ``issuerdn`` および ``issuer`` は ISSUER DN および ISSUER の内容で、
    ``subjectdn`` および ``subject`` と同様です。いずれも ``str`` です。
    ``not_before``, ``not_after`` は ``datetime.datetime`` オブジェクトで、
    それぞれ有効期間の始期と終期です。
    ``serial`` は署名者の証明書のシリアル番号を16進数で表した文字列
    (``str``) です。
    ``certificate`` は DER (RFC3280) フォーマットの ``str`` で表現された
    証明書です。
    ``memo`` は備考の文字列 (``str``) です。
    ``verification_type`` は署名の検証方法です。 ``'LOW'``, ``'MID_LOCAL'``,
    ``'MID_NETWORK'``, ``'HIGH_LOCAL'`` または ``'HIGH_NETWORK'`` です。
    ``status`` は署名の状態です。 ``'UNKNOWN'``, ``'OK'``,
    ``'NO_ROOT_CERTIFICATE'``, ``'NO_REVOCATION_CHECK'``,
    ``'OUT_OF_VALIDITY'``, ``'OUT_OF_VALIDITY_AT_SIGNED_TIME'``,
    ``'REVOKE_CERTIFICATE'``, ``'REVOKE_INTERMEDIATE_CERTIFICATE'``,
    ``'INVLIAD_SIGNATURE'``, ``'INVALID_USAGE'`` または
    ``'UNDEFINED_ERROR'`` です。

インスタンス属性
----------------

コンストラクタに与える引数と同等です。
