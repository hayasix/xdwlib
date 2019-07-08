================
documentinbinder
================

``documentinbinder`` モジュールは、DocuWorks バインダーに含まれる個々の
DocuWorks 文書 (バインダー内文書) を扱います。

DocumentInBinder オブジェクト
=============================

DocumentInBinder オブジェクトは、 DocuWorks バインダーに含まれる個々の
DocuWorks 文書 (バインダー内文書) を表します。これはファイルシステムに
実在するファイルではありません。

DocumentInBinder クラスは、その基底クラスである BaseDocument クラスに
多くを負っています。 ``basedocument`` モジュールを参照してください。

コンストラクタ
--------------

クラス ``DocumentInBinder(bdoc, pos)``
    ``bdoc`` は Binder オブジェクト、 ``pos`` は bdoc 内での格納位置
    (0 から始まる整数) です。

インスタンス属性
----------------

``binder``
    バインダー内文書の格納先となっているバインダーです。

``handle``
    ``self.binder.handle`` と同じです。

``name``
    バインダー内文書のバインダー内文書名です。

``pages``
    バインダー内文書のページ数です。

``pos``
    バインダー内文書のバインダー内での位置です。0 から始まります。
