====
page
====

page モジュールでは、Page クラスに関する機能を扱います。

Page オブジェクト
=================

Page クラスは、DocuWorks 文書に含まれる個別のページを扱います。

Page クラスは、その基底クラスである Annotatable クラスに多くを負っています。
``annotatable`` モジュールを参照してください。

コンストラクタ
--------------

クラス ``Page(doc, pos)``
    ``doc`` は、ページが属する DocuWorks 文書またはバインダー内文書
    (Document オブジェクトまたは DocumentInBinder オブジェクト) です。
    ``pos`` は ``doc`` 内でのページ番号です (0 から始まります)。

インスタンス属性
----------------

``annotations``
    ページに直接付加されているアノテーションの個数です。

``bpp``
    ページの色深度 (ピクセルあたりのビット数) です。

``compress_type``
    ページの圧縮方法です。 ``'NORMAL'``, ``'LOSSLESS'``, ``'HIGHQUALITY'``,
    ``'HIGHCOMPRESS'``, ``'NOCOMPRESS'``, ``'JPEG'``, ``'PACKBITS'``,
    ``'G4'``, ``'MRC_NORMAL'``, ``'MRC_HIGHQUALITY'``,
    ``'MRC_HIGHCOMPRESS'``, ``'MRC'`` または ``'JPEG_TTN2'`` です。

``degree``
    ページの回転角です。90 の倍数です。

``doc``
    ページが属する DocuWorks 文書またはバインダー内文書 (Document
    オブジェクトまたは DocumentInBinder オブジェクト) です。
    (注) ページがバインダー内文書に含まれている場合であっても、
    そのバインダーをページから直接指し示す手段はありません。
    バインダー内文書 (DocumentInBinder オブジェクト) を取得した上で、
    その DocumentInBinder オブジェクトの属性 ``binder`` を参照して、
    バインダーにアクセスしてください。

``image_size``
    ページの元データの大きさを表す Point オブジェクトです。
    単位はピクセルです。

``is_color``
    ページがカラーの場合は ``True`` になります。
    モノクロまたはグレイスケールの場合は ``False`` になります。

``original_size``
    ページの元データの大きさを表す Point オブジェクトです。
    単位はミリメートルです。

``original_resolution``
    ページの元データの横・縦の解像度を表す Point オブジェクトです。
    単位は DPI です。

``pos``
    ``self.doc`` の中でのページ位置 (0 から始まります)。

``resolution``
    ページの横・縦の解像度を表す Point オブジェクトです。
    単位は DPI です。

``size``
    ページの横・縦の大きさを表す Point オブジェクトです。
    単位はミリメートルです。

``type``
    ページの種類です。 ``'IMAGE'``, ``'APPLICATION'`` または ``'NULL'``
    です。

インスタンスメソッド
--------------------

``bitmap()``
    ページを画像化して Bitmap オブジェクトで返します。アノテーションを
    表示する設定になっていれば、アノテーションも画像に含めます。
    (注) Bitmap オブジェクトは、属性として ``width``, ``height``,
    ``planes``, ``depth``, ``compression``, ``data_size``, ``color_used``,
    ``color_important``, ``resolution``, ``header`` および ``data``
    を持ちます。 BMP/DIB フォーマットの (ヘッダを含めた)
    オクテットストリーム (バイト列) は、Bitmap オブジェクトの
    インスタンスメソッド ``octet_stream()`` で取得できます。

``clear_ocr_text()``
    ページ内の OCR テキストをすべて消去します。

``color_scheme()``
    ``self.is_color`` および ``self.bpp`` から、ページのカラースキームを
    ``'COLOR'``, ``'MONO_HIGHQUALITY'`` (グレースケール) または
    ``'MONO'`` で返します。

``content_text(type=None)``
    ページに含まれるアプリケーションテキストまたは OCR テキストを返します。
    (注) アノテーションに含まれるテキストを取得するには、Annotatable
    クラスのインスタンスメソッド ``annotation_text()`` または
    ``fulltext()`` を利用してください。

``export(path=None)``
    ページを別ファイルに書き出します。 ``path`` は書き出し先のパス名です。
    ``path`` を設定しない場合は、 ``self.doc`` のファイル名の拡張子を除く
    部分に ``'_Pn'`` (n はページ番号) を付加したもの (
    ``os.path.join(self.dir, '%s_P%d.xdw' % (self.doc.name, self.pos))``)
    となります。実際に書き出されたファイルのパス名を返します。

``export_image(path=None, dpi=600, color='COLOR', format=None, compress='NORMAL', direct=False)``
    (バインダー内) 文書のページ (単独または連続する複数ページ) を
    画像ファイルへ書き出します。

    ``path`` は書き出し先のパス名です。すでに存在する場合は
    派生したパス名が書き出し先になります。

    ``dpi`` は書き出される画像の解像度です。単位は DPI です。
    10～600 が有効です。

    ``color`` は書き出される画像の色数の指定です。 ``'COLOR'``,
    ``'MONO'`` または ``'MONO_HIGHQUALITY'`` (グレースケール) で指定します
    (小文字でもかまいません)。

    ``format`` は書き出される画像のデータ形式です。 ``'BMP'``, ``'TIFF'``,
    ``'JPEG'`` または ``'PDF'`` で指定します (小文字でもかまいません)。

    ``compress`` は書き出される画像の圧縮形式です。 ``format`` が
    ``'BMP'`` である場合は、指定は無視されます。 ``format`` が ``'TIFF'``
    である場合は、 ``'NOCOMPRESS'``, ``'PACKBITS'``, ``'JPEG'``,
    ``'JPEG_TTN2'`` または ``'G4'`` を指定します。 ``format`` が
    ``'JPEG'`` である場合は、 ``'NORMAL'``, ``'HIGHQUALITY'`` または
    ``'HIGHCOMPRESS'`` を指定します。 ``format`` が ``'PDF'`` である場合は、
    ``'NORMAL'``, ``'HIGHQUALITY'``, ``'HIGHCOMPRESS'``, ``'MRC_NORMAL'``,
    ``'MRC_HIGHQUALITY'`` または ``'MRC_HIGHCOMPRESS'`` を指定します。

    ``direct`` が ``True`` である場合は、ページの画像 (アノテーションや
    ページフォームは含みません) を内部の圧縮イメージのまま書き出します。
    このため、処理が高速です。生成される画像の形式は内部状態に依存して
    TIFF, JPEG または PDF となり、生成される画像ファイルの拡張子はそれぞれ
    ``'.tiff'``, ``'.jpeg'`` または ``'.pdf'`` となります。画像の向きも
    内部状態に依存し、DocuWorks Viewer (Lite) で見たときとは異なる場合が
    あります。画像の向きは、 ``self.degree`` で取得できます。
    実際に書き出されたファイルのパス名を返します。

``get_userattr(name, default=None)``
    ページのユーザー定義属性 ``name`` の値を取得します。 ``str``
    を返します。 ユーザー定義属性 ``name`` がない場合は、 ``default``
    の値を返します。
    (注) ページのユーザー定義属性は、DocuWorks Desk/Viewer の GUI で
    アクセスすることはできません。

``ocr(engine='DEFAULT', strategy='SPEED', preprocessing='SPEED', noise_reduction='NONE', deskew=True, form='AUTO', column='AUTO', rects=None, language='AUTO', main_language='BALANCED', use_ascii=True, insert_space=False, verbose=False)``
    ページを OCR 処理します。結果として得られるテキストは、別途
    ``self.content_text()`` で取り出す必要があります。

    ``engine`` は ``'DEFAULT'`` または ``'WINREADER PRO'`` です
    (小文字でもかまいません)。

    ``strategy`` は ``'STANDARD'``, ``'SPEED'`` または ``'ACCURACY'``
    です (小文字でもかまいません)。

    ``preprocessing`` は ``'SPEED'`` または ``'ACCURACY'`` です
    (小文字でもかまいません)。

    ``noise_reduction`` は ``'NONE'``, ``'NORMAL'``, ``'WEAK'`` または
    ``'STRONG'`` です (小文字でもかまいません)。

    ``deskew`` が ``True`` の場合は、OCR 処理の前に傾き補正を自動的に
    行います。ただし、補正結果がページに反映されることはありません。

    ``form`` は ``'AUTO'``, ``'TABLE'`` または ``'WRITING'`` です
    (小文字でもかまいません)。

    ``column`` は ``'AUTO'``, ``'HORIZONTAL_SINGLE'``,
    ``'HORIZONTAL_MULTI'``, ``'VERTICAL_SINGLE'`` または
    ``'VERTICAL_MULTI'`` です (小文字でもかまいません)。

    ``rects`` は OCR 処理対象範囲となる領域 (Rect オブジェクト)
    のシーケンスです。

    ``language`` は ``'AUTO'``, ``'JAPANESE'`` または ``'ENGLISH'``
    です (小文字でもかまいません)。

    ``main_language`` は ``'BALANCED'``, ``'JAPANESE'`` または
    ``'ENGLISH'`` です (小文字でもかまいません)。

    ``use_ascii`` が ``True`` である場合は、ASCII コードで該当する文字が
    ある場合は ASCII コード (いわゆる半角英数) を採用します。

    ``insert_space`` が ``True`` である場合は、空白部分に空白文字を
    挿入します。

    ``verbose`` が ``True`` である場合は、認識作業中の様子を画面に
    表示します。ただし、 ``verbose`` を ``False`` にしても、
    「認識中…」と表示されるダイアログは表示されます。

``rasterize()``
    ページがアプリケーションページである場合は、イメージページに
    置き換えます。アプリケーションページでない場合は、何もしません。

``reduce_noise(level='NORMAL')``
    ページイメージのノイズを除去します。 ``level`` は ``'NORMAL'``,
    ``'WEAK'`` または ``'STRONG'`` です (小文字でもかまいません)。
    (注) モノクロイメージのページについてのみ利用可能です。
    アプリケーションページやカラー/グレイスケールのイメージページで
    利用するとエラーとなります。

``re_regions(pattern)``
    指定のパターンに適合する文字列がページ上で占める半開矩形領域を求めます。
    ``pattern`` は ``re`` モジュールで利用できる正規表現文字列または
    正規表現オブジェクトです。
    Rect (ただし、適合する文字列が存在していても
    対応するページ上の表示領域が得られない場合は None) のリストを返します。
    (注) ``set_ocr_text()`` で OCR テキストが設定されていた場合は、
    このメソッドで AccessDeniedError を発生することがあります。
    これは XDWAPI の制限です。

``rotate(degree=0, auto=False)``
    ページを回転します。 ``degree`` は時計回りの回転角で、単位は度です。
    ``auto`` が ``True`` である場合は、OCR 処理用に自動正立処理を行います。
    ``degree`` に指定できる値は、PIL (Python Imaging Library) が利用できる
    場合は任意の整数です。PIL が利用できない場合は、90 の倍数のみ指定
    できます。
    (注) ``degree`` が 90 の倍数でない場合、ページを画像にして処理を
    進めます。この結果、アノテーションは画像の一部となり、アプリケーション
    テキストや OCR テキストも失われます。

``set_ocr_text(rtlist, charset='SHIFTJIS', half_open=True)``
    ページの OCR テキストを置き換えます。

    ``rtlist`` は 2 要素のシーケンス ``(rect, text)`` のシーケンスです。
    rect は 文字列 ``text`` がページ上で占める半開矩形領域です。
    単位はミリメートルです。
    たとえば、

    ::

        [(Rect(10, 10, 30, 18), "とある文字列"),
         (Rect(10, 30, 200, 32), "A long char string")]

    などのようになります。

    ``charset`` は ``text`` の文字セットで、 ``'DEFAULT'``, ``'OEM'``,
    ``'ANSI'``, ``'SYMBOL'``, ``'MAC'``, ``'SHIFHTJIS'``, ``'HANGEUL'``,
    ``'CHINESEBIG5'``, ``'GREEK'``, ``'TURKISH'``, ``'BALTIC'``,
    ``'RUSSIAN'`` または ``'EASTEUROPE'`` で指定します
    (小文字でもかまいません)。

    ``half_open`` に ``False`` を指定した場合は、 ``rect`` を
    閉鎖矩形領域として扱います。
    (注) このメソッドで OCR テキストを設定した場合、 ``text_regions()``
    や ``re_regions()`` で文字列の位置を取得しようとすると
    AccessDeniedError が発生します。これは XDWAPI の制限です。

``set_userattr(name, value)``
    ページのユーザー定義属性 ``name`` を値 ``value`` で設定します。
    ``value`` は ``str`` で与えます。
    (注) ページのユーザー定義属性は、DocuWorks Desk/Viewer の GUI で
    アクセスすることはできません。

``text_regions(text, ignore_case=False, ignore_width=False, ignore_hirakata=False)``
    指定のテキストに適合する文字列がページ上で占める半開矩形領域を求めます。
    ``text`` は対象文字列です。
    ``ignore_case`` が ``True`` である場合は、大文字と小文字を区別しません。
    ``ignore_width`` が ``True`` である場合は、いわゆる全角文字と
    いわゆる半角文字を区別しません。 ``ignore_hirakata`` が ``True``
    である場合は、平仮名と片仮名を区別しません。
    Rect (ただし、適合する文字列が存在していても対応するページ上の
    表示領域が得られない場合は ``None``) のリストを返します。
    単位はミリメートルです。
    (注) ``set_ocr_text()`` で OCR テキストが設定されていた場合は、
    このメソッドで AccessDeniedError を発生することがあります。
    これは XDWAPI の制限です。

``view(light=False, wait=True)``
    ページの内容を複製した閲覧用一時ファイルを DocuWorks Viewer または
    DocuWorks Viewer Light のいずれかで閲覧します。
    ``light`` が ``True`` である場合は、DocuWorks Viewer Light
    を優先して利用します。
    ``wait`` が ``True`` である場合は、DocuWorks Viewer (Light) が
    終了するのを待ちます。終了後、更新された一時ファイルを読み込み、
    ページの全アノテーションについての (1) 表示領域 (半開矩形領域)、
    (2) アノテーションタイプ名、(3) アノテーションが含む文字列、
    の 3 要素を持つタプル ``(Rect, str, str)`` のリストを返します。
    アノテーションが存在しない場合は、空リストを返します。
    アノテーションが含む文字列は、アノテーションタイプが ``'TEXT'``,
    ``'LINK'`` または ``'STAMP'`` である場合に与えられ、その他の場合は
    ``None`` になります。
    ``wait`` が ``False`` である場合は、DocuWorks Viewer (Light)
    を起動したらすぐに制御が戻り、 ``(proc, path)`` という
    2 要素からなるタプルを返します。この場合、 ``proc`` は
    ``subprocess`` モジュールが提供する Popen オブジェクトであり、
    ``path`` は閲覧中用一時ファイルのパス名です。
    (注) ``wait`` を ``False`` とした場合は、閲覧用一時ファイルは、
    このメソッドを呼び出した側が必要がなくなった時点で、
    その親ディレクトリと共に消去してください。 ``wait`` を ``True``
    とした場合は、閲覧用一時ファイルは自動的に消去されます。

    ::

        pg = Page(...)
        proc, temp = pg.view(wailt=False)
        # ... wait for proc.poll() != None ...
        os.remove(temp)
        os.rmdir(os.path.dirname(temp))  # shutil.rmtree() を利用してもよい

PageCollection オブジェクト
===========================

PageCollection クラスは、Page オブジェクトの集合 (シーケンス) を扱います。
DocuWorks には対応する概念はありませんが、おおむね、DocuWorks 文書を開いて
一覧表示した状態で Ctrl + クリックして複数のページを選択した状態に
相当します。

PageCollection クラスは、 ``list`` を拡張したものです。 ``list``
で利用できるメソッド等が使えますが、その場合は結果も ``list``
になることがある点に注意してください。

コンストラクタ
--------------

クラス ``PageCollection(seq)``
    ``seq`` は Page オブジェクトからなるシーケンスです。

インスタンスメソッド
--------------------

``__add__(obj)``
    ``obj`` は Page オブジェクトまたは PageCollection オブジェクトです。
    ``obj`` をページのシーケンスに追加 (``append`` または ``extend``)
    して得られる PageCollection オブジェクトを返します。

``__iadd__(obj)``
    ``self += obj`` は ``self = self + obj`` と同じです。

``export(path=None, flat=False, group=True)``
    ``self`` が持つページをすべてまとめた内容の新たな DocuWorks
    文書またはバインダーを生成します。
    ``path`` は生成先のパス名です。指定しなかった場合は、
    最初のページが属する文書またはバインダーのパス名から
    派生したパス名となります。
    ``flat`` が ``True`` である場合は、DocuWorks 文書が生成されます。
    ``flat`` が ``False`` である場合は、DocuWorks バインダーが生成されます。
    ``group`` の指定は、 ``flat`` が ``False`` の場合のみ有効です。
    ``group`` が ``True`` である場合は、各ページが属する DocuWorks
    文書またはバインダー内文書が同一の連続するページは、
    バインダー内文書にまとめられます。 ``group`` が ``False``
    である場合は、各ページはすべて別々のバインダー内文書となります。
    実際に生成された DocuWorks 文書またはバインダーのパス名を返します。
    拡張子は DocuWorks 文書の場合は ``.xdw`` となり、DocuWorks
    バインダーの場合は ``.xbd`` となります。

``group()``
    ``self`` を分解して、PageCollection オブジェクトのリストにして返します。
    分解に際して、連続する Page オブジェクトの属する BaseDocument
    オブジェクトが同一であれば、同じ PageCollection オブジェクトに
    格納されるようにします。
    たとえば、 ``self`` が
    ``PageCollection([A[0], A[1], B[2], C[2], C[5], C[7], A[3], B[4], B[6]])``
    であれば、 ``self.group()`` は
    ``[PageCollection([A[0], A[1]]), PageCollection([B[2]]), PageCollection([C[2], C[5], C[7]]), PageCollection([A[3]]), PageCollection([B[4], B[6]])]``
    となります。

``view(light=False, wait=True, flat=False, group=True)``
    ``self`` の内容を複製した閲覧用一時ファイルを DocuWorks Viewer または
    DocuWorks Viewer Light のいずれかで閲覧します。
    パスワード、DocuWorks 電子印鑑または電子証明書によるセキュリティーの設定が
    されている文書では、エラーとなります。
    ``light`` が ``True`` である場合は、DocuWorks Viewer Light
    を優先して利用します。
    ``wait`` が ``True`` である場合は、DocuWorks Viewer (Light)
    が終了するのを待ちます。終了後、更新された一時ファイルを読み込み、
    キーをページ番号 (0 から始まります)、値をそのページの全アノテーションに
    ついての (1) 表示領域 (半開矩形領域)、(2) アノテーションタイプ名、
    (3) アノテーションが含む文字列、の 3 要素を持つタプル (Rect, str, str)
    のリストとする辞書 (
    ``{0: [(Rect(...), 'TEXT', 'Sample Text'), (Rect(...), 'RECTANGLE', None), ...], 1: [...], ...}``
    のような形式) を返します。アノテーションが存在しないページについては、
    辞書にエントリを作りません。アノテーションが含む文字列は、
    アノテーションタイプが ``'TEXT'``, ``'LINK'`` または ``'STAMP'``
    である場合に与えられ、その他の場合は ``None`` になります。
    ``wait`` が ``False`` である場合は、DocuWorks Viewer (Light)
    を起動したらすぐに制御が戻り、 ``(proc, path)`` という
    2 要素からなるタプルを返します。この場合、 ``proc`` は ``subprocess``
    モジュールが提供する Popen オブジェクトであり、 ``path`` は
    閲覧用一時ファイルのパス名です。
    ``flat`` が ``True`` である場合は、DocuWorks 文書として閲覧します。
    ``flat`` が ``False`` である場合は、DocuWorks バインダーとして
    閲覧します。
    ``group`` の指定は、 ``flat`` が ``False`` である場合に有効です。
    ``group`` が ``True`` である場合は、連続して同一の文書に属するページは
    バインダー内文書としてまとめて閲覧します。 ``group`` が ``False``
    である場合は、各ページがそれぞれ 1 ページのバインダー内文書となります。
    (注) ``wait`` を ``False`` とした場合は、閲覧用一時ファイルは、
    このメソッドを呼び出した側が必要がなくなった時点で、
    その親ディレクトリと共に消去してください。 ``wait`` を ``True``
    とした場合は、閲覧用一時ファイルは自動的に消去されます。

    ::

        pc = PageCollection(...)
        proc, temp = pc.view(wailt=False)
        # ... wait for proc.poll() != None ...
        os.remove(temp)
        os.rmdir(os.path.dirname(temp))  # shutil.rmtree() を利用してもよい
