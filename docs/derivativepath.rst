==============
派生したパス名
==============

派生したパス名 (derivative path) とは、DocuWorks Desk での挙動と同じように、
パス名の衝突を枝番号を付することで回避したものです。

たとえば、すでに ``your/favorite/dir/example.xdw`` が存在し、
新たに同じパス名のファイルを作ろうとすると、xdwlib は自動的に
``your/favorite/dir/example-2.xdw`` というパス名のファイルを生成し、
そのパス名を返します。
