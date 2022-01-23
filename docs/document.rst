========
document
========

document モジュールでは、DocuWorks 文書 (拡張子 ``.xdw``) および DocuWorks
入れ物 (拡張子 ``.xct``) を取り扱います。

モジュール関数
==============

``create(input_path=None, output_path=None, **kw)``
    これはラッパー関数で、 ``input_path`` で示すファイルから DocuWorks
    文書を生成します。実際の生成作業は以下の ``create_from_image()``,
    ``create_from_pdf()``, ``create_from_app()`` の各関数によりますが、
    ``input_path`` が ``None`` である場合は、白紙のページを 1 ページだけ持つ
    DocuWorks 文書を生成します。 ``output_path`` は生成結果を書き出す先の
    パス名です。指定しない場合は、 ``input_path`` から派生したパス名
    となります。 ``input_path`` も指定されていない (または ``None``
    が指定されている) 場合は、 ``'blank.xdw'`` となります。実際に生成された
    DocuWorks 文書のパス名を返します。

    ``**kw`` には、 ``create_from_image()``, ``create_from_pdf()``
    または ``create_from_app()`` が要求するパラメータを指定します。

``create_from_image(input_path, output_path=None, fitimage='FITDEF', compress='NORMAL', zoom=0, size=Point(0, 0), align=('CENTER', 'CENTER'), maxpapersize='DEFAULT')``
    ``input_path`` で示すイメージデータ (画像ファイル) から DocuWorks
    文書を生成します。 ``output_path`` は生成結果を書き出す先のパス名です。
    指定しない場合は、 ``input_path`` から派生したパス名となります。
    実際に生成された DocuWorks 文書のパス名を返します。

    ``fitimage`` は ``'FITDEF'``, ``'FIT'``, ``'FITDEF_DIVIDEBMP'``,
    ``'USERDEF'`` または ``'USERDEF_FIT'`` で指定します。
    小文字で指定してもかまいません。

    ``compress`` は ``'NORMAL'``, ``'LOSSLESS'``, ``'NOCOMPRESS'``,
    ``'HIGHQUALITY'``, ``'HIGHCOMPRESS'``, ``'JPEG'``, ``'JPEG_TTN2'``,
    ``'PACKBITS'``, ``'G4'``, ``'MRC_NORMAL'``, ``'MRC_HIGHQUALITY'``
    または ``'MRC_HIGHCOMPRESS'`` で指定します。
    小文字で指定してもかまいません。

    ``zoom`` には変換時の拡大率を % で指定します。通常は 0 以上の数値で
    指定しますが、特に 0 を指定すると 100 を指定したのと同様に実寸大指定に
    なります。小数点以下 3 桁までが有効です。

    ``size`` には変換後のページサイズを指定します。Point オブジェクト
    または既定サイズで与えることができますが、Point オブジェクトで与える
    ことができるのは ``fitimage`` が ``'USERDEF'`` または ``'USERDEF_FIT'``
    の場合だけです。この場合は横幅・縦幅をそれぞれミリメートル単位で
    指定します。既定サイズで与える場合は、 ``'A3R'``, ``'A3'``, ``'A4R'``,
    ``'A4'``, ``'A5R'``, ``'A5'``, ``'B4R'``, ``'B4'``, ``'B5R'`` または
    ``'B5'`` で指定します。

    ``align`` には変換時にページサイズと画像サイズが異なった場合
    どの方向を揃えるかを 2 要素のシーケンスで指定します。最初の要素が
    水平方向の揃え方で、 ``'LEFT'``, ``'CENTER'`` または ``'RIGHT'``
    で指定します。次の要素が垂直方向の揃え方で、 ``'TOP'``, ``'CENTER'``
    または ``'BOTTOM'`` で指定します。
    いずれも、小文字で指定してもかまいません。

    ``maxpapersize`` には変換後の最大ページサイズを指定します。
    ``'DEFAULT'``, ``'A3'`` または ``'2A0'`` を指定できます。

``create_from_pdf(input_path, output_path=None)``
    ``input_path`` で示す PDF ファイルから DocuWorks 文書を生成します。
    ``output_path`` は生成結果を書き出す先のパス名です。指定しない場合は、
    ``input_path`` から派生したパス名となります。実際に生成された
    DocuWorks 文書のパス名を返します。

    PDF から DocuWorks 文書への変換は、DocuWorks 内で行える場合は
    そちらで処理しますが、処理できない場合は ``create_from_app()``
    で行いますので、Adobe Reader 等がインストールされていることが望ましい
    といえます。

``create_from_app(input_path, output_path=None, attachment=False, timeout=0)``
    ``input_path`` で示すファイルを OS で関連づけられたアプリケーション
    プログラムで開き、DocuWorks Printer 経由で DocuWorks 文書を生成します。
    ``output_path`` は生成結果を書き出す先のパス名です。指定しない場合は、
    ``input_path`` から派生したパス名となります。実際に生成された
    DocuWorks 文書のパス名を返します。

    元のファイルをオリジナルデータとして添付したい場合は、 ``attachment``
    を ``True`` とします。

    アプリケーションプログラムの起動後にプログラムのハングアップを回避
    したい場合は、 ``timeout`` にタイムアウトとなるまでの時間を秒単位で
    指定します。

``merge(input_paths, output_path=None)``
    複数の DocuWorks 文書を結合して、新たな DocuWorks 文書を生成します。

    ``input_paths`` はマージ元となる DocuWorks 文書のパス名を列挙した
    シーケンスです。 ``output_path`` はマージ結果を書き出す先のパス名です。
    指定しない場合は、 ``input_paths`` の先頭の要素から派生したパス名と
    なります。実際に生成された DocuWorks 文書のパス名を返します。

Document クラス
===============

Document クラスは、DocuWorks 文書を表します。これはファイルシステムに
実在するファイルです。

Document クラスは、その基底クラスである BaseDocument および XDWFile
クラスに多くを負っています。 ``basedocument`` モジュールおよび
``xdwfile`` モジュールを参照してください。

コンストラクタ
--------------

クラス ``Document(path)``
    ``path`` は Windows ファイルシステム上のパス名です。

Container クラス
================

Container クラスは、DocuWorks 入れ物 (封筒またはクリアフォルダー) を表します。
これはファイルシステムに実在するファイルです。

Container クラスは、 Document クラスから派生したクラスです。
Container オブジェクトは、ただ 1 ページの Page と AttachmentList を有しています。

現時点では、 Container クラス固有の機能はありません。また、入れ物のファイルを
xdwlib を利用して新たに作成することはできません。

コンストラクタ
--------------

クラス ``Container(path)``
    ``path`` は Windows ファイルシステム上のパス名です。

インスタンスメソッド
--------------------

次のメソッドは利用できません:
``'append()'``, ``'insert()'``, ``'append_image()'``, ``'insert_image()'``,
``'export()'``, ``'delete()'``, ``'rasterize()'``.

``rotate(pos, degree=0)``
    ページを回転します。 ``pos`` には 0 を指定してください。
    ``degree`` は ページの中央を中心とした時計回りの回転角で、単位は度です。
    0, 90, 180, 270 のみ指定できます。
