======
HOW-TO
======

インストール
============

xdwlib は DocuWorks 7 がインストールされた Windows 上の Python 3.3+
で利用できます。

Zip 形式のアーカイブを入手した場合は、それを展開してセットアップ
スクリプトを実行します。

::

    unzip xdwlib-VERSION.zip
    cd xdwlib
    python setup.py install

Git をお使いの方は、直接リポジトリから取得することもできます。

::

    git clone https://github.com/hayasix/xdwlib.git master
    cd xdwlib
    python setup.py install

ドキュメントを開く
==================

DocuWorks ドキュメントを開くには、次のようにします。

::

    from xdwlib import xdwopen

    doc = xdwopen(PATHNAME)

``doc`` は Document オブジェクトになります。

ここで利用している ``xdwopen()`` は、ユーティリティ関数です。
与えられたパス名の拡張子を見てオープンすべきファイルのタイプ (ドキュメントか
バインダーか) を判断し、適切なクラスのオブジェクトを返します。
``xdwopen()`` を利用しないでドキュメントを開く場合は、次のようにします。

::

    from xdwlib.document import Document

    doc = Document(PATHNAME)
    doc.open()

開いたドキュメントは、使い終わったら閉じなければなりません。
途中で内容を変更した場合は、必要に応じて保存も行ってください。
自動的に保存されるわけではありません。

::

    doc.save()  # 変更後のドキュメントを上書き保存します。
    doc.close()

ドキュメントの属性
==================

ドキュメントには、次の属性があります。show_annotations を除いて、いずれも
読み取り専用属性です。値を設定しても、ドキュメントには反映されません。

``version``
    DocuWorks のバージョン。

``type``
    ドキュメントタイプ。 ドキュメントの場合は ``'DOCUMENT'`` です。
    バインダーを開いたときは ``'BINDER'`` になります。

``dir``
    ファイル (``.xdw``) が存在するディレクトリ。

``name``
    ファイル (``.xdw``) のファイル名 (拡張子を含みません)。
    これを DocuWorks では文書名と呼んでいます。

``pages``
    ドキュメントのページ数。

``attachments``
    オリジナルデータ (添付ファイル) のリスト (ただし、AttachmentList
    クラスのインスタンスです)。

``editable``
    ``True`` ならば、ドキュメントは編集できます。

``annotatable``
    ``True`` ならば、ドキュメントのアノテーションを編集できます。

``printable``
    ``True`` ならば、ドキュメントは印刷できます。

``copyable``
    ``True`` ならば、ドキュメントをコピーできます。

``show_annotations``
    ``True`` ならば、アノテーションを表示します。

``properties``
    文書属性の個数。

``signatures``
    署名の個数。

``status``
    署名後の変更等の状態。
    電子印鑑の場合、 ``'NONE'`` =未検証, ``'NOEDIT'`` =変更なし, 
    ``'EDIT'`` =変更あり, ``'BAD'`` =異常 を意味します。
    電子証明書の場合、 ``'UNKNOWN'`` =未検証, ``'GOOD'``
    =変更なし/証明書の信頼なし, 'MODIFIED'`` =変更あり/証明書の信頼なし,
    ``'BAD'`` =異常, ``'GOOD_TRUSTED'`` =変更なし/証明書の信頼あり,
    ``'MODIFIED_TRUSTED'`` =変更あり/証明書の信頼あり,
    をそれぞれ意味します。

以下の属性は、バインダーの場合のみ有効です。こちらも読み取り専用属性です。

``documents``
    バインダーに格納されているドキュメントの数。

``binder_color``
    バインダーの色。

``binder_size``
    バインダーのサイズ。

ページにアクセスする
====================

Document オブジェクトに含まれるページにアクセスするには、 ``page()``
メソッドを使用します。このメソッドは Page オブジェクトを返します。

``page()`` メソッドの代わりに、インデックスでのアクセスもできます。
いずれの場合も、ページ番号は Python 風に 0 から始まり、また負数を指定すると
末尾からのページ数を指定したことになります。

::
 
    firstpage = doc.page(0)  # doc[0] と書いても同じです。
    lastpage = doc[-1]

Document クラスは、イテレータプロトコルをサポートしています。
そこで、すべてのページにアクセスしたいときは、次のように書けます。

::

    # 全ページを OCR 処理します。
    for pg in doc:
        pg.ocr()

ページコレクション
==================

PageCollection クラスを利用すると、ページ群をひとまとめにして取り扱うことが
できます。PageCollection オブジェクトを生成するには、 ``PageCollection()``
とするか、あるいは Document オブジェクトにスライス表記を用いてページ群を
切り出します。

::

    # 3-5 ページ目を取り出します。
    pc = doc[2:5]
    # 次のようにしても同じです。
    pc = PageCollection()  # インスタンスの生成のみ行います。
    pc += doc.page(2)  # Page オブジェクトを追加できます。
    pc += doc[3:5]  # PageCollection オブジェクトも追加できます。

PageCollection クラスは、Python が標準で持つ ``list`` を拡張したものです。
ページの順序を入れ替えるような処理には、 ``list`` クラスのメソッドや
``list`` を扱う関数を利用できます。ただし、関数を利用する場合は、
戻り値が ``list`` インスタンスとなるため、再度 PageCollection インスタンスへ
変換しておいた方がよいでしょう。

::

    # doc1 は奇数ページだけのドキュメント、doc2 は偶数ページだけのドキュメントとします。
    pc = PageCollection(zip(doc1, doc2))  # 奇数ページ・偶数ページを交互に並べてひとつにまとめます。
    pc.reverse()  # ページ順を逆順に並べ替えます。なお、reversed(pc) では結果は PageCollection ではなく list になります。
    pc.export(PATH, flat=True)  # 新たなドキュメントとして保存します。バインダーとして保存するには pc.export(PATH, flat=False) とします。

アノテーションにアクセスする
============================

アノテーションは、ページに格納されています。Page オブジェクトから
``annotation()`` メソッドを利用して、アノテーションへアクセスできます。
ここでもまた、配列風の表現も使用できます。

::

    ann = pg.annotation(0)  # pg[0] と書いても同じです。

``ann`` は Annotation オブジェクトになります。

Page クラスも、Document クラスと同様に、イテレータプロトコルをサポート
しています。

::

    # ページ内のすべてのアノテーションの貼り付け位置を表示します。
    for ann in pg:
        print ann.position()

ただしこの例では、他のアノテーションの上に貼り付けられている
アノテーション (子アノテーション) については扱っていません。

DocuWorks では、アノテーションにアノテーションを貼り付けることもできます。
テキスト付きの付箋などがこれにあたります。
また、グループ化されたアノテーションでは、全体をまとめるアノテーションが
ひとつ作られ、元のアノテーション群はその子アノテーションとなっています。
そこで、アノテーションから子アノテーションへ、まったく同様にアクセスする
ことができます。
Annotation クラスもまた、イテレータプロトコルをサポートしています。

::

    child_ann = ann.annotation(2)  # ann[2] でも同じです。

    # すべての子アノテーションについて、アノテーションタイプを表示します。
    for child_ann in ann:
        print child_ann.type

    # ドキュメント 2 ページ目の 4 番目のアノテーションの 3 番目の子アノテーションのアノテーションタイプを表示します。
    print doc.page(1).annotation(3).annotation(2).type
    print doc[1][3][2].type  # こう書いても同じです。

アノテーションを追加するには、Page オブジェクトまたは Annotation
オブジェクトの ``add_*()`` メソッドを利用します (* には、 ``text``,
``stickey``, ``line/straightline``, ``rectangle``, ``arc``, ``bitmap``,
``stamp``, ``receivedstamp``, ``custom``, ``marker``, ``polygon``
のいずれかが入ります)。

アノテーションの属性
====================

各アノテーションには、位置やサイズ、テキスト、色など、
アノテーションタイプに合わせてさまざまな属性 (アトリビュート) があります。
それらは、Annotation オブジェクトの属性として読み取ることができます。

アノテーションの属性を変更するには、単に値を Annotation オブジェクトの属性へ
設定してください。

::

    from xdwlib.struct import Point
    : (中略)
    pg = doc.page(0)
    ann = pg.add_text(u"変更前の文字列") # 既定の位置にテキストアノテーションを貼り付けます。
    ann.text = u"変更後の文字列"
    ann.font_size = 10.5 # ポイント
    ann.font_style = "bold,italic"
    ann.fore_color = "red"
    ann.back_color = "none"
    ann.position = Point(pg.size.x - 200, 75) # 右から 200mm, 上から 75mm の位置へ移動します。

ただし、最終的に ``doc.save()`` を行わなければファイルの内容は変更されない
ことに注意してください。

バインダーを開く
================

バインダーを開くには、ドキュメントと同様に ``xdwopen()`` を利用します。

::

    from xdwlib import xdwopen

    xbd = xdwopen(PATHNAME)

``xdwopen()`` はユーティリティ関数でした。与えるパス名の拡張子が ``'.xdw'``
だとドキュメントを開くことになり、 ``'.xbd'`` だとバインダーを開くことに
なります。
バインダーを開いた場合は、戻り値が Binder オブジェクトになります。
``xdwopen()`` を利用せずにバインダーを開くには、次のようにします。

::

    from xdwlib.binder import Binder

    xbd = Binder(PATHNAME)
    xbd.open()

Binder オブジェクトは、0 個以上のドキュメントを含むことができます。
ただし、ここでいうドキュメントは「バインダー内のドキュメント」ですので、
Document オブジェクトとは別の DocumentInBinder オブジェクトになります。
DocumentInBinder オブジェクトにアクセスするには、Binder オブジェクトから
``document()`` メソッドを用います。インデックスでのアクセスもできます。

::

    inner_doc = xbd.document(3)  # xbd[3] と書いても同じです。

Binder オブジェクトもまたイテレータプロトコルをサポートしています。

::

    # すべてのバインダー内ドキュメントについて、文書名を表示します。
    for inner_doc in xbd:
        print inner_doc.name

バインダーの中でページを直接指定する (DocumentInBinder オブジェクトを
経由しない) ときは、Binder オブジェクトから直接 ``page()`` メソッドを
用いることもできます。

::

    # バインダーの30ページ目 (4 つ目のドキュメントの 5 ページ目) を指定します。
    pg = xbd.page(29)
    equiv_pg = xbd.document(3).page(4)  # xbd[3][4] とも書けます。

新たにバインダーを作成するには、 ``create_binder()`` 関数を利用します。
これは作成だけ行いますので、続けてそのバインダーを利用する場合は、
``xdwopen()`` で開く必要があります。

::

    from xdwlib import xdwopen
    from xdwlib.binder import Binder, create_binder

    create_binder(PATHNAME, color="red", size="free")
    xbd = xdwopen(PATHNAME)

開いたバインダーは、使い終わったら閉じなければなりません。
途中で内容を変更した場合は、必要に応じて保存も行ってください。
自動的に保存されるわけではありません。

::

    xbd.save()  # 変更後のバインダーを上書き保存します。
    xbd.close()

いくつかの便利なメソッド
========================

view()
------

Document/DocumentInBinder/Binder/Page オブジェクトには
``view()`` メソッドが用意されています。Document/Binder オブジェクトを
``save()`` していなくても、ページを DocuWorks Viewer (Light) で見ることが
できます。デバッグ時など、Python の対話モードで利用するのに便利です。
いじってみた結果を ``view()`` で確認し、気に入らなければ ``save()``
しなければよいからです。

::

    doc_or_pg.view(light=False, wait=True)

``light``
    ``True`` ならば DocuWorks Viewer Light を使用してページを表示します
    (DocuWorks Viewer Light が使用できなければ、DocuWorks Viewer を
    使用します)。 ``False`` ならば DocuWorks Viewer を使用してページを
    表示します (DocuWorks Viewer が使用できなければ、DocuWorks Viewer
    Light を使用します)。

``wait``
    ``True`` ならば DocuWorks Viewer (Light) が終了されるまで処理を停止
    します。 ``False`` ならば DocuWorks Viewer (Light) を起動後すぐに
    処理を続行します。

rasterize()
-----------

Document/DocumentInBinder オブジェクトには、 ``rasterize()`` メソッドが
用意されています。アプリケーションページを強制的にイメージページへ
変換します。
このメソッドを使用すると、そのページの元のデータ (アプリケーションテキストや
アノテーションのデータ) は失われることに注意してください (アノテーションは
画像としては反映されます)。

::

    doc.rasterize(pos, dpi=600, color="COLOR")

``pos``
    ページ位置 (0 から始まります) を指定します。

``dpi``
    イメージページの解像度を 10 以上 600 以下で指定します。

``color``
    イメージページの色を ``'MONO'``, ``'MONO_HIGHQUALITY'``, ``'COLOR'``
    で指定します (小文字でもかまいません)。

re_regions()
------------

Page オブジェクトには、 ``re_regions()`` メソッドが用意されています。
ページ内で正規表現に従ってテキストを検索し、発見した箇所の矩形領域 (Rect)
のリストを返します。

::

    pg.re_regions(pattern)

``pattern``
    正規表現 (Python 標準ライブラリの re モジュールで使用できるもの)。

正規表現でなく文字列を検索する ``text_regions()`` メソッドもあります。

::

    pg.text_regions(pattern, ignore_case=False, ignore_width=False, ignore_hirakata=False)

``pattern``
    検索するテキスト。

``ignore_case``
    ``True`` ならば大文字・小文字を区別しません。
    ``False`` ならば区別します。

``ignore_width``
    ``True`` ならば全角・半角を区別しません。
    ``False`` ならば区別します。

``ignore_hirakata``
    ``True`` ならばひらがなとカタカナを区別しません。
    ``False`` ならば区別します。

実際の利用例については、サンプルプログラムの「検索してマーク」をご覧ください。

find_annotations()
------------------

Page オブジェクトおよび Annotation オブジェクトには、
``find_annotations()`` メソッドが用意されています。
ページ内で指定した条件に従ってアノテーションを検索し、
発見したアノテーションのリストを返します。

::

    pg_or_ann.find_annotations(handles=None, types=None, rect=None, half_open=True, recursive=False)

``handles``
    検索対象とするアノテーションハンドルのシーケンス。 ``None`` ならば
    限定しません。

``types``
    検索対象とするアノテーションタイプのシーケンス。 
    ``None`` ならば限定しません。
    アノテーションタイプは、 ``'STICKEY'``, ``'TEXT'``, ``'STAMP'``,
    ``'STRAIGHTLINE'``, ``'RECTANGLE'``, ``'ARC'``, ``'POLYGON'``,
    ``'MARKER'``, ``'LINK'``, ``'PAGEFORM'``, ``'OLE'``, ``'BITMAP'``,
    ``'RECEIVEDSTAMP'``, ``'CUSTOM'``, ``'TITLE'``, ``'GROUP'`` から
    指定します (小文字でもかまいません)。

``rect``
    この矩形範囲内に収まっているアノテーションを検索対象とします。
    Annotation オブジェクトに対して使用する場合は、ページに直接
    貼り付けられたアノテーションならばページ左上が、他のアノテーションに
    貼り付けられたアノテーションならば貼り付け先 (親アノテーション) の
    左上が、それぞれ原点となります。単位は mm です。

``half_open``
    ``True`` ならば ``rect`` が半開矩形領域であるものと解釈します。 

``recursive``
    ``True`` ならばアノテーションに貼り付けられたアノテーション
    (子アノテーション) も検索対象とします。
