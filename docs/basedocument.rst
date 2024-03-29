============
basedocument
============

``basedocument`` モジュールは、DocuWorks 文書およびバインダー内文書を
総合して扱います。

BaseDocument オブジェクト
=========================

BaseDocument クラスは、Document クラス (DocuWorks 文書) および
DocumentInBinder クラス (バインダー内文書) の基底クラスです。

BaseDocument オブジェクトに対してインデックス表記を用いると、(バインダー内)
文書に含まれるページを Page オブジェクトとして取得できます。
また、インデックスにスライスを指定すると、連続するページ群を
PageCollection オブジェクトとして取得できます。

BaseDocument クラスはイテレータプロトコルをサポートしており、
Page オブジェクトを順次取得できます。

インスタンスメソッド
--------------------

``annotation_text()``
    (バインダー内) 文書内にあるすべてのテキスト / リンク / 日付印
    アノテーションに含まれているテキストデータ (アノテーションテキスト)
    を返します。アノテーション間は ``'\v'`` (0x0b) で、ページ間は
    ``'\f'`` (0x0c) で、それぞれ区切られます。
    返されるテキストに含まれる部分は、テキストアノテーションの場合は
    設定された文字列の全部、リンクアノテーションの場合はキャプション
    文字列の全部、日付印アノテーションの場合は (上欄に設定された文字列) +
    ``' <DATE> '`` + (下欄に設定された文字列) となります。
    返されるテキストはページ順に並んでいます。ただし、アノテーションの
    順序は内部状態によっていて、制御できません。

``append(obj)``
    ``obj`` は Page オブジェクト、PageCollection オブジェクト、BaseDocument
    オブジェクトまたは DocuWorks 文書を示すパス名です。 ``obj`` を
    (バインダー内) 文書の末尾に追加します。 ``insert(self.pages, obj)``
    と同等です。 ``insert()`` を参照してください。

``append_image(input_path, **kw)``
    ``input_path`` で指定するファイルから画像を読み込んでページを生成し、
    (バインダー内) 文書の末尾に追加します。
    ``insert_image(self.pages, input_path, **kw)`` と同等です。
    ``insert_image()`` を参照してください。

``bitmap(pos)``
    (バインダー内) 文書の ``pos`` 番目 (0 から始まります。) のページを
    画像化して Bitmap オブジェクトで返します。アノテーションを表示する
    設定になっていれば、アノテーションも画像に含めます。Page オブジェクトの
    インスタンスメソッド ``bitmap()`` を参照してください。

``content_text(type=None)``
    (バインダー内) 文書内のページタイプが ``type`` (``'APPLICATION'``
    または ``'IMAGE'`` 。省略時は両方) であるすべてのページに含まれる
    ページテキスト (アプリケーションテキストまたは OCR テキスト) を
    返します。返されるテキストはページ順に並んでいて、ページ間は ``'\f'``
    (0x0c) で区切られます。ただし、OCR テキストについては、OCR 処理を
    行わないと得られません。

``delete(pos)``
    (バインダー内) 文書の ``pos`` 番目 (0 から始まります。) のページを
    削除します。 ``pos`` 番目よりも後ろのページのページ位置は、順次
    繰り上げられます。 ``del self[pos]`` としても同じです。

``dirname()``
    (バインダー内) 文書が存在するディレクトリのパス名を返します。

``export(pos, path=None)``
    ページを別ファイルに書き出します。
    ``pos`` はページ番号です (0 から始まります)。 ``path`` は書き出し先の
    パス名です。 ``path`` を設定しない場合は、 ``self.name`` に ``'_Pn'``
    (``n`` は ``pos + 1``) を付加したもの (
    ``os.path.join(self.dir, '%s_P%d.xdw' % (self.name, self.pos + 1))``
    ) となります。実際に書き出されたパス名を返します。

``export_image(pos, path=None, pages=1, dpi=600, color='COLOR', format=None, compress='NORMAL', direct=False)``
    (バインダー内) 文書のページ (単独または連続する複数ページ) を
    画像ファイルへ書き出します。
    ``pos`` はページ番号です (0 から始まります)。 ``int`` の場合は
    単独ページを指定したことになります。連続する複数ページを指定するには、
    2 要素のタプル ``(start, stop)`` またはリストを指定します。この場合、
    ``start`` ページから ``stop - 1`` ページまでが書き出されます。さらに、
    ``pages`` が指定されていたとしても無視されます。
    ``path`` は書き出し先のパス名です。すでに存在する場合は、
    `派生したパス名`_ が書き出し先になります。
    ``pages`` は書き出すページ数です。 ``pos`` が ``int`` である場合、
    第 ``pos`` ページ (0 から始まります) から ``pos + pages - 1`` ページ
    までが書き出されます。
    ``dpi`` は書き出される画像の解像度です。単位は DPI です。10～600 が
    有効です。
    ``color`` は書き出される画像の色数の指定です。 ``'COLOR'``, ``'MONO'``
    または ``'MONO_HIGHQUALITY'`` (グレースケール) で指定します
    (小文字でもかまいません)。
    ``format`` は書き出される画像のデータ形式です。 ``'BMP'``, ``'TIFF'``,
    ``'JPEG'`` または ``'PDF'`` で指定します (小文字でもかまいません)。
    ``compress`` は書き出される画像の圧縮形式です。 ``format`` が ``'BMP'``
    である場合は、指定は無視されます。 ``format`` が ``'TIFF'`` である
    場合は、 ``'NOCOMPRESS'``, ``'PACKBITS'``, ``'JPEG'``, ``'JPEG_TTN2'``
    または ``'G4'`` を指定します。 ``format`` が ``'JPEG'`` である場合は、
    ``'NORMAL'``, ``'HIGHQUALITY'`` または ``'HIGHCOMPRESS'`` を指定します。
    ``format`` が ``'PDF'`` である場合は、 ``'NORMAL'``, ``'HIGHQUALITY'``,
    ``'HIGHCOMPRESS'``, ``'MRC_NORMAL'``, ``'MRC_HIGHQUALITY'`` または
    ``'MRC_HIGHCOMPRESS'`` を指定します。
    ``direct`` が真である場合は、ページの画像 (アノテーションや
    ページフォームは含みません) を内部の圧縮イメージのまま書き出します。
    このため、処理が高速です。生成される画像の形式は内部状態に依存して
    TIFF, JPEG または PDF となり、生成される画像ファイルの拡張子はそれぞれ
    ``'.tiff'``, ``'.jpeg'`` または ``'.pdf'`` となります。画像の向きも
    内部状態に依存し、DocuWorks Viewer (Lite) で見たときとは異なる場合が
    あります。画像の向きは、 ``self.page(pos).degree`` で取得できます。
    実際に書き出しを行ったファイルのパス名を返します。

.. _派生したパス名: derivativepath.rst

``find(pattern, func=None)``
    (バインダー内) 文書のすべてのページについて、ページを引数にとる関数
    ``func`` の戻り値が ``pattern`` にマッチするかどうかを調べ、
    マッチしたページだけを集めた PageCollection オブジェクトを返します。
    ``pattern`` は ``str`` または ``re`` モジュールで使用できる
    正規表現オブジェクトです。 ``func`` は 1 引数の関数で、引数は Page
    オブジェクト、戻り値は引数に対応した文字列であることが必要です。
    指定しないときは、 ``self.fulltext`` と同じです。

``find_annotation_text(pattern)``
    (バインダー内) 文書のすべてのページについて、各ページのアノテーション
    テキスト (全体) が ``pattern`` にマッチするかどうかを調べ、マッチした
    ページだけを集めた PageCollection オブジェクトを返します。

``find_content_text(pattern, type=None)``
    (バインダー内) 文書のすべてのページについて、各ページの
    アプリケーションテキストまたは OCR テキスト (全体) が ``pattern``
    にマッチするかどうかを調べ、マッチしたページだけを集めた
    PageCollection オブジェクトを返します。  ``type`` を指定すると、
    対象となるページの種類 (``'APPLICATION'``, ``'IMAGE'``, ``'NONE'``)
    を限定します。

``find_fulltext(pattern)``
    (バインダー内) 文書のすべてのページについて、各ページの
    アプリケーションテキストまたは OCR テキスト (全体) および
    アノテーションテキストが ``pattern`` にマッチするかどうかを調べ、
    マッチしたページだけを集めた PageCollection オブジェクトを返します。

``fulltext()``
    (バインダー内) 文書のすべてのページテキストおよび テキスト / リンク /
    日付印アノテーションに含まれているアノテーションテキストを返します。
    返されるテキストはページ順に並んでいて、ページごとに ``'\f'`` (0x0c)
    で区切られ、ページ内では最初にページテキストが置かれ、以後は
    ``'\v'`` (0x0b) で区切られながらアノテーションテキストが続きます。
    アノテーションの順序は内部状態によっていて、制御できません。

``insert(pos, obj)``
    ``obj`` は Page オブジェクト、PageCollection オブジェクト、
    BaseDocument オブジェクトまたは DocuWorks 文書を示すパス名です。
    ``obj`` を (バインダー内) 文書の ``pos`` 番目 (0 から始まります。)
    に挿入します。 ``obj`` に Binder オブジェクトや DocuWorks バインダーを
    示すパス名を指定することはできません。挿入位置以降にあったページの
    ページ位置は、順次繰り下げられます。

``insert_image(pos, input_path, fitimage='FITDEF', compress='NORMAL', zoom=0, size=Point(0, 0), align=('CENTER', 'CENTER'), maxpapersize='DEFAULT')``
    画像ファイルを読み込み、(バインダー内) 文書の指定位置に
    イメージページとして挿入します。
    ``pos`` はページ番号です (0 から始まります)。挿入位置以降にあった
    ページのページ位置は、順次繰り下げられます。
    ``input_path`` は読み込むべき画像ファイルです。TIFF, BMP, JPEG が
    読み込み可能ですが、形式によっては読み込めないことがあります。
    ``fitimage`` はページサイズの指定です。 ``'FITDEF'`` (イメージが
    収まる定型サイズ), ``'FIT'`` (イメージサイズそのもの),
    ``'FITDEF_DIVIDEBMP'`` (``'FITDEF'`` と同様ですが、BMP 形式の画像が
    入力されそれが最大ページサイズ (2A0 または A3) を超過している場合は
    分割して複数ページにします), ``'USERDEF'`` (ユーザー指定サイズ)
    または ``'USERDEF_FIT'`` (ユーザー指定サイズですが、画像がこれより
    大きい場合は指定サイズに収まるよう縮小されます) です (小文字でも
    かまいません)。
    ``compress`` はカラーイメージの圧縮方式です。 ``'NORMAL'`` (JPEG標準),
    ``'LOSSLESS'`` (劣化なし), ``'HIGHQUALITY'`` (JPEG高画質),
    ``'HIGHCOMPRESS'`` (JPEG高圧縮), ``'MRC_NORMAL'`` (MRC圧縮標準),
    ``'MRC_HIGHQUALITY'`` (MRC圧縮高画質) または
    ``'MRC_HIGHCOMPRESS'`` (MRC圧縮高圧縮) で指定します (小文字でも
    かまいません)。
    ``zoom`` は読み込み時の拡大 (・縮小) 率です。単位はパーセントです。
    1/1000 % 未満は無視されます。0 を指定すると、100% (等倍) と同じ意味に
    なります。
    ``size`` は 生成されるページの大きさです。 ``fitimage`` が
    ``'USERDEF'`` または ``'USERDEF_FIT'`` の場合に有効です。Point
    オブジェクト (単位はミリメートル)、 ``int`` または ``str`` で指定します。
    ``int`` の場合は、1=A3R, 2=A3, 3=A4R, 4=A4, 5=A5R, 6=A5, 7=B4R, 8=B4,
    9=B5R, 10=B5 になります。 ``str`` の場合は、 ``'A3R'``, ``'A3'``,
    ``'A4R'``, ``'A4'``, ``'A5R'``, ``'A5'``, ``'B4R'``, ``'B4'``,
    ``'B5R'`` または ``'B5'`` で指定します。
    ``align`` は 2 要素のタプル ``(horiz, vert)`` でページ内の画像配置を
    指定します。 ``horiz`` は ``'CENTER'``, ``'LEFT'`` または ``'RIGHT'``
    です。 ``vert`` は ``'CENTER'``, ``'TOP'`` または ``'BOTTOM'`` です。
    いずれも小文字でもかまいません。
    ``maxpapersize`` は 最大ページサイズで、 ``'DEFAULT'``, ``'A3'``
    または ``'2A0'`` です。DocuWorks 7.0 以上では、 ``'DEFAULT'`` と
    ``'2A0'`` は同じ結果となります。

``page(pos)``
    (バインダー内) 文書の ``pos`` 番目 (0 から始まります。) のページを表す
    Page オブジェクトを返します。

``rasterize(pos)``
    ``pos`` はページ番号です (0 から始まります)。ページがアプリケーション
    ページである場合は、イメージページに置き換えます。アプリケーション
    ページでない場合は、何もしません。

``rotate(pos, degree=0, auto=False)``
    ページを回転します。 ``pos`` はページ番号です (0 から始まります)。
    ``degree`` はページの中央を中心とした時計回りの回転角で、単位は度です。
    ``auto`` が真である場合は、OCR 処理用に自動正立処理を行います。
    ``degree`` に指定できる値は、PIL (Python Imaging Library) が利用できる
    場合は任意の整数です。PIL が利用できない場合は、90 の倍数のみ指定
    できます。
    (注) ``degree`` が 90 の倍数でない場合、ページを画像にして処理を
    進めます。この結果、アノテーションは画像の一部となり、アプリケーション
    テキストや OCR テキストも失われます。

``view(light=False, wait=True, page=0, fullscreen=False, zoom=0)``
    (バインダー内) 文書の内容を複製した閲覧用一時ファイル DocuWorks Viewer
    または DocuWorks Viewer Light のいずれかで閲覧します。
    ``light`` が真である場合は、DocuWorks Viewer Light を優先して利用します。
    パスワード、DocuWorks 電子印鑑または電子証明書によるセキュリティーの
    設定がされている文書では、エラーとなります。
    ``wait`` が真である場合は、DocuWorks Viewer (Light) が終了するのを待ち、
    閲覧中に追加されたものも含めて、ページ番号 (0 から開始します) をキー、
    各ページのアノテーションの情報 (``AnnotationCache`` オブジェクト)
    を列挙したリストを値とする辞書を返します。アノテーションが存在しない
    ページは含まれません。閲覧用一時ファイルは自動的に消去されます。
    ``wait`` が偽である場合は、DocuWorks Viewer (Light) を起動したら
    すぐに制御が戻り、``(proc, temp)`` という 2 要素からなるタプルを
    返します。この場合、``proc`` は ``subprocess`` モジュールが提供する
    ``Popen`` オブジェクトであり、 ``temp`` は DocuWorks Viewer (Light)
    で閲覧中の一時ファイルのパス名です。
    ``temp`` およびその親ディレクトリは、このメソッドを呼び出した側が
    必要がなくなった時点で消去してください。

    ::

        proc, temp = doc.view(wailt=False)
        # ... wait for proc.poll() != None ...
        os.remove(temp)
        os.rmdir(os.path.dirname(temp))  # shutil.rmtree() を利用してもよい

    ``page`` が指定されている場合は、最初からそのページ (0 から開始します)
    を表示します。
    ``fullscreen`` が真である場合は、フルスクリーン (プレゼンテーション
    モード) で表示します。
    ``zoom`` には表示倍率を % で表示します。ただし、0 は 100% を意味します。
    また ``'WIDTH'``, ``'HEIGHT'``, ``'PAGE'`` を指定すると、それぞれ
    幅 / 高さ / ページ全体で表示します。
