========
色の指定
========

アノテーションの色指定
======================

アノテーションでの色には、 ``'NONE'``, ``'BLACK'``, ``'MAROON'``,
``'GREEN'``, ``'OLIVE'``, ``'NAVY'``, ``'PURPLE'``, ``'TEAL'``, ``'GRAY'``,
``'SILVER'``, ``'RED'``, ``'LIME'``, ``'YELLOW'``, ``'BLUE'``,
``'FUCHSIA'``, ``'AQUA'``, ``'WHITE'`` を指定できます
(小文字でもかまいません)。

指定できる色の名前の一覧を確認するには、 Annotation クラスの
``all_colors()`` メソッドを利用してください。

付箋の色指定
============

付箋の色は、 ``'WHITE'``, ``'RED'``, ``'BLUE'``, ``'YELLOW'``, ``'LIME'``,
``'PALE_RED'``, ``'PALE_BLUE'``, ``'PALE_YELLOW'``, ``'PALE_LIME'``
を指定できます (小文字でもかまいません)。

付箋に指定できる色の名前の一覧を確認するには、 Annotation クラスの
``all_colors(stickey=True)`` メソッドを利用してください。

バインダーの色指定
==================

バインダーの色は、 ``'NAVY'``, ``'GREEN'``, ``'BLUE'``, ``'YELLOW'``,
``'ORANGE'``, ``'RED'``, ``'FUCHSIA'``, ``'PINK'``, ``'PURPLE'``,
``'BROWN'``, ``'OLIVE'``, ``'LIME'``, ``'AQUA'``, ``'CREAM'``,
``'SILVER'``, ``'WHITE'`` を指定できます (小文字でもかまいません)。

バインダーに指定できる色の名前の一覧を確認するには、 Binder クラスの
``all_colors()`` メソッドを利用してください。
