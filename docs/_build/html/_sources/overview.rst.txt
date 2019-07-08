==============
モジュール概観
==============

※このモジュール・リファレンスの適用対象は、xdwlib-2.29.3 以上 です。

Python DocuWorks Library は、DocuWorks 7 (7.0 以上) がインストール
されていることを前提に動作します。

DocuWorks が扱うファイルは、DocuWorks 文書と DocuWorks バインダーの 2
種類です。

-   バインダーは、複数の文書を格納するコンテナです。
-   文書は、ページ、ページフォーム、オリジナルデータ、署名を格納しています。
    ファイルとして存在する DocuWorks 文書と、バインダー内に格納されている
    バインダー内文書の 2 種類がありますが、おおむね同じ操作が可能です。
-   ページは、ページイメージ (画像)、テキスト (アプリケーションテキスト
    または OCR テキスト)、アノテーションを格納しています。
-   アノテーションは、他のアノテーション (子アノテーション) を格納できます。
    GUI (DocuWorks Viewer) でアノテーションをグループ化した場合、
    アノテーションを束ねる親アノテーションとなる専用のアノテーションが
    生成されています。

これらを扱うためのモジュールが、それぞれ次のように用意されています。

-   :doc:`binder`
-   :doc:`document` および :doc:`documentinbinder`
-   :doc:`page`
-   :doc:`annotation`

次のモジュールは、主に基底クラスとそれに関連するモジュール関数を用意して
いるものです。

-   :doc:`xdwfile`
-   :doc:`basedocument`
-   :doc:`annotatable`

次のモジュールでは、xdwlib が使用するデータを定義しています。

-   :doc:`bitmap`
-   :doc:`struct`
-   :doc:`timezone`

次のモジュールは、XDWAPI からの使用に適した一時ファイルの生成を支援します。

-   :doc:`xdwtemp`

次のモジュールでは、xdwlib の内部で使用するユーティリティ関数などを
定義しています。

-   :doc:`common`
-   :doc:`observer`

次のモジュールでは、xdwlib の下位層で働く API を定義しています。

.. automodule:: xdwlib.xdwapi

すでにある DocuWorks 文書を操作するときは、

::

    import xdwlib
    doc = xdwlib.xdwopen(pathname)

とした上で、 ``doc`` が持つメソッドを利用するのが一般的です。

::

    from xdwlib import *

とすると、次の各行を実行するのと同等の効果が得られます。

::

    from xdwlib.struct import Point, Rect
    from xdwlib.common import environ
    from xdwlib.xdwtemp import XDWTemp
    from xdwlib.xdwfile import xdwopen, optimize, copy, create_sfx, extract_sfx
    from xdwlib.xdwfile import protection_info, protect, unprotect, sign
    from xdwlib.document import Document, create, merge
    from xdwlib.binder import Binder, create_binder
    from xdwlib.documentinbinder import DocumentInBinder
    from xdwlib.page import Page, PageCollection
    from xdwlib.annotation import Annotation, AnnotationCache

エラーコードを利用したい場合などは、

::

    from xdwlib.xdwapi import InvalidArgError

などとする必要があるかもしれません。 
