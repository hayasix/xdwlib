======
binder
======

``binder`` モジュールは、DocuWorks バインダー (拡張子 ``.xbd``)
を取り扱います。

モジュール関数
==============

``create_binder(path, color='RED', size='FREE')``
    与えられたパス名 ``path`` を持つ新しい DocuWorks バインダーを
    ファイルシステム上に生成します。

Binder オブジェクト
===================

Binder オブジェクトは、DocuWorks バインダーを表します。
これはファイルシステムに実在するファイルです。

Binder オブジェクトは、イテレータプロトコルをサポートしており、
DocumentInBinder オブジェクトを順次取得できます。

Binder クラスは、その基底クラスである XDWFile クラスに多くを負っています。
``xdwfile`` モジュールを参照してください。

コンストラクタ
--------------

クラス ``Binder(path)``
    ``path`` は Windows ファイルシステム上のパス名です。

インスタンスメソッド
--------------------

``annotation_text()``
    バインダー内のすべてのテキスト / リンク / 日付印アノテーションに
    含まれているテキストデータ (アノテーションテキスト) を返します。
    アノテーション間は ``'\v'`` (0x0b) で、ページ間は ``'\f'`` (0x0c)
    で区切られます。返されるテキストに含まれる部分は、
    テキストアノテーションの場合は設定された文字列の全部、
    リンクアノテーションの場合はキャプション文字列の全部、
    日付印アノテーションの場合は (上欄に設定された文字列) + ``' <DATE> '``
    + (下欄に設定された文字列) となります。返されるテキストはページ順に
    並んでいます。ただし、アノテーションの順序は内部状態によっていて、
    制御できません。

``append(path)``
    パス名 ``path`` で示される DocuWorks 文書を、バインダーの最後尾に
    追加します。 ``insert(-1, path)`` と同じです。

``content_text(type=None)``
    バインダー内のページタイプが ``type`` (``'APPLICATION'`` または
    ``'IMAGE'`` 。省略時は両方) であるすべてのページに含まれるページテキスト
    (アプリケーションテキストまたは OCR テキスト) を返します。
    返される文字列はページ順に並んでいて、ページ間は ``'\f'`` (0x0c)
    で区切られます。ただし、OCR テキストについては、OCR 処理を行わないと
    得られません。

``delete(pos)``
    バインダー内の ``pos`` 番目 (0 から開始します) にあるバインダー内文書を
    削除します。 ``pos`` よりも後にあるバインダー内文書の位置はひとつずつ
    繰り上げられます。 ``del self[pos]`` としても同じです。

``document(pos)``
    バインダー内の ``pos`` 番目 (0 から開始します) にあるバインダー内文書
    (DocumentInBinder オブジェクト) を返します。

``document_and_page(pos)``
    バインダー内の通しページで ``pos`` ページ目 (0 から開始します)
    にあるページが属するバインダー内文書と、そのページ自体 (Page
    オブジェクト) からなる、2 要素のタプルを返します。得られるページ
    (第 2 要素) の属性 ``pos`` は、バインダー内文書の中での相対的なページ
    (0 から開始します) であることに注意してください。

``document_pages()``
    バインダー内文書のページ数を列挙したリストを返します。

``find_fulltext(pattern)``
    バインダー内のすべてのページのページテキストおよびアノテーションテキスト
    について ``pattern`` を検索し、マッチしたページを集めた PageCollection
    オブジェクトを返します。 ``pattern`` には単純なテキストまたは ``re``
    モジュールでサポートされる正規表現を指定できます。

``fulltext()``
    バインダー内のすべてのページテキストおよびテキスト / リンク / 日付印
    アノテーションに含まれているアノテーションテキストを返します。
    返されるテキストはページ順に並んでいて、ページごとに ``'\f'`` (0x0c)
    で区切られ、ページ内では最初にページテキストが置かれ、以後は ``'\v'``
    (0x0b) で区切られながらアノテーションテキストが続きます。
    アノテーションの順序は内部状態によっていて、制御できません。

``insert(pos, path)``
    パス名 ``path`` で示される DocuWorks 文書を、バインダー内の ``pos``
    番目 (0 から開始します) にします。末尾に挿入する場合は ``pos`` に
    -1 を指定します。pos 以降のバインダー内文書の位置はひとつずつ
    繰り下げられます。

``page(pos)``
    バインダー内の通しページ番号が ``pos`` であるページ (Page オブジェクト)
    を返します。

``view(light=False, wait=True)``
    バインダーの内容を DocuWorks Viewer または DocuWorks Viewer Light
    のいずれかで閲覧します。 ``light`` が真である場合は、DocuWorks Viewer
    Light を優先して利用します。 ``wait`` が真である場合は、DocuWorks
    Viewer (Light) が終了するのを待ちます。 ``wait`` が偽である場合は、
    DocuWorks Viewer (Light) を起動したらすぐに制御が戻り、
    ``(proc, temp)`` という 2 要素からなるタプルを返します。この場合、
    ``proc`` は ``subprocess`` モジュールが提供する Popen オブジェクト
    であり、 ``temp`` は DocuWorks Viewer (Light) で閲覧中の一時ファイルの
    パス名です。
