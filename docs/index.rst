.. xdwlib documentation master file, created by
   sphinx-quickstart on Mon Jul  8 16:45:53 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================
xdwlib - Python DocuWorks Library
=================================

これは何?
=========

富士フイルムビジネスイノベーション株式会社 (FFBI) から発売されているロングセラー
DocuWorks™ は、オフィスワーカーにやさしい電子ファイリングシステムです。
蓄積した電子文書を有効に活用するには、単にアプリケーションを使うだけでなく、
外部プログラムから操作できた方がいいと思いませんか?
できれば、C++ や Java ではなくて、もっとフレンドリーな Python (日本語) で
使いたいものですね。
そこで、Python DocuWorks Library (xdwlib) を作ってみました!

私にも役に立つの?
=================

DocuWorks™ は、役に立ちます。;-)

xdwlib は、いまのところは Python プログラマにとって有用です。
Python は学びやすいプログラミング言語ですが、まったくのプログラミング初心者が
自由に使えるようになるには、相応の時間がかかるでしょう。そういう方は、
Python プログラマが素敵なアプリケーションを作ってくれるのを待ちましょう。

何ができるの?
=============

製造元である FFBI が提供している開発ツール (DocuWorks™ Development Tool Kit)
に含まれる DocuWorks API (XDWAPI) の機能は API のレベルでは網羅しているので、
基本的な作業はだいたいすべてできます。
DocuWorks Desk は XDWAPI 以上の機能を持っているので、特殊な作業は手作業で
行う必要があるでしょう。しかし、日常の基本的な作業を自動化 (バッチ処理化)
するには、xdwlib で十分です。

現時点での主な機能は、次のとおりです [1]_ 。

.. [1] いずれも DocuWorks™ をインストールした状態で使えるものです。

-   ドキュメント / バインダーの読み込みと分解。ドキュメント / バインダー、
    バインダー内ドキュメント、ページ、アノテーション、複数ページの
    コレクションを、それぞれ Python オブジェクトとして取り扱えます。
    「ドキュメントとページ」のように親子関係があるものは親をイテレータに
    していますので、すっきりと処理できます。
-   テキストの抜き出し。ドキュメント / バインダー、ページ、アノテーションに
    含まれるテキストデータ (アプリケーションテキスト、OCR テキスト、
    アノテーションテキスト) を抽出できます。
-   テキストの検索。ドキュメントから指定した文字列または正規表現にマッチする
    ページを検索・抽出できます。検索結果は別ファイルへ書き出すことも
    できますし、ページ群としてさらに追加処理を行うこともできます。
    ページ内で検索対象テキストが表示されている位置をとることもできますから、
    「検索してマーク」するのも簡単です。
-   テキストの置き換え。OCR テキストを入れ替えることができます。
-   ドキュメントの一部 (ページ) を画像 (BMP/JPEG/TIFF/PDF) で書き出せます。
    画像だけでよければ、PDF は手軽に作成できます。
-   ページ操作。ドキュメントにページ (群) やドキュメントを挿入したり、
    ページを削除したりできます。ページの画像化や OCR 処理も簡単です。
-   アノテーション操作。アノテーションの追加などができます。
-   ページフォーム (ヘッダ・フッタ) の管理ができます。
-   オリジナルデータ (添付ファイル) の管理ができます。
-   ドキュメントの保護とその解除ができます。
-   電子印鑑および電子証明書による署名の読み取りと、署名以降のドキュメントの
    更新の有無の検出ができます。
-   ドキュメントから自己解凍形式を生成すること、また逆に自己解凍形式から
    ドキュメントを取り出すことができます。
-   ドキュメントやページ、アノテーションのさまざまな属性を読み書きできます。
-   XDWAPI 互換モジュールを用意しました。製造元が提供するものは C 言語用です
    が、そのすべての API について Python から使うためのラッパーを用意して
    あります。

動作条件は?
===========

DocuWorks™ 7.0 以上の 32/64 bit 日本語版および Python 3.7 以上 [2]_ がインストールされている環境で動作します (Windows 限定) 。

.. [2] Python 2 で利用するには、xdwlib-2.29.6 以前が必要です。
    xdwlib-2.29.6 は Launchpad https://launchpad.net/xdwlib に
    保存されています。

また、Python Imaging Library (PIL) がインストールされていると、ページの任意角度 (90/180/270度以外) での回転が可能になります。

どこにあるの?
=============

``pip install xdwlib`` または ``easy_install xdwlib`` でインストールできます。
easy_install を利用するには setuptools をインストールしてください。

開発版は、GitHub https://github.com/hayasix/xdwlib にあります。

::

    git clone https://github.com/hayasix/xdwlib.git master

でコードを入手できます。

作者は中の人?
=============

いいえ。作者は FFBI やその前身の富士ゼロックス株式会社とは関係がありません。
xdwlib に関するご意見・ご要望は作者 (`林秀樹 <mailto:hideki@hayasix.com>`_)
へお寄せください。

各ページへのリンク
==================

.. toctree::
    :maxdepth: 2

    overview
    xdwfile
    binder
    document
    documentinbinder
    basedocument
    page
    annotation
    annotatable
    struct
    xdwtemp
    derivativepath
    halfopenregion
    colors
    fonts
    howto
    samples
    faq

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
