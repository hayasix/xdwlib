============
半開矩形領域
============

矩形領域を指定する場合、 ``xdwlib`` では半開矩形領域 (half-open rectangular)
を用います。

半開矩形領域とは、横 (x) 座標範囲および縦 (y) 座標範囲がそれぞれ半開区間
``[left, right), [top, bottom)`` となっているような矩形領域を指します。
このとき、

-   ``left`` は指定矩形領域内の左端
-   ``top`` は指定矩形領域内の上端
-   ``right`` は指定矩形領域外の左端 (指定矩形領域内の右端の右隣)
-   ``bottom`` は指定矩形領域外の上端 (指定矩形領域内の下端の下隣)

です [1]_ 。

.. [1] DocuWorks で扱う座標は (1/100 ミリメートル単位の)
       離散値からなるため、「隣」が定義できます。

半開矩形領域 ``r`` = ``Rect(left, top, right, bottom)`` の大きさ
(横幅および高さ) を求める関数 ``size`` は、次のように書けます。

::

    def size(r):
        width = r.right - r.left
        height = r.bottom - r.top
        return Point(width, height)

横幅は ``right - left``, 縦幅 (高さ) は ``bottom - top`` で求められます。
また、ある座標 ``p`` = ``Point(x, y)`` が 半開矩形領域 ``r`` =
``Rect(left, top, right, bottom)`` に含まれるか否かを判定する関数
``inside`` は、次のように書けます。

::

    def inside(p, r):
        return r.left <= p.x < r.right and r.top <= p.y < r.bottom

矩形領域を指定するメソッドでオプション引数 ``half_open``
が用意されている場合は、それに ``False`` を指定することで、
半開矩形領域でなく閉鎖矩形領域 (横・縦座標範囲がいずれも閉鎖区間であるもの)
を与えることもできます。
