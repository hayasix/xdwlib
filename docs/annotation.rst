==========
annotation
==========

``annotation`` モジュールは、アノテーションを取り扱います。

Annotation オブジェクト
=======================

Annotation クラスは、アノテーションを表します。

Annotation クラスは、その基底クラスである Annotatable クラスに多くを
負っています。 ``annotatable`` モジュールを参照してください。

コンストラクタ
--------------

クラス ``Annotation(pg, pos, parent=None)``
    ``pg`` は Page オブジェクト、 ``pos`` はページ内でのアノテーションの
    (内部的な) 位置です。アノテーションがページに直接付加されている場合は
    ``parent=None`` とします。アノテーションが他のアノテーションの子要素と
    なっている場合は、 ``parent`` には親となる Annotation オブジェクトを
    指定します。この場合、 ``pos`` はページ内ではなく親アノテーションから
    見た時の位置となります。

    アノテーションの (内部的な) 位置は、表示される位置 (座標) とは無関係
    です。表示位置からアノテーションを特定する方法については、Annotatable
    オブジェクトの ``find_annotations()`` メソッドを参照してください。

インスタンス属性
----------------

Annotation オブジェクトには、次の属性があります。

全アノテーション共通
''''''''''''''''''''

``handle``
    アノテーションハンドル。DocuWorks バインダーまたは文書の中で
    アノテーションを一意に指す値です。

``position``
    アノテーション領域の左上隅の位置。アノテーション領域とは、
    アノテーションの目に見える図形の周囲に DocuWorks が自動的に確保する
    マージンを含んだ領域のことです。

``size``
    アノテーション領域の幅と高さ。

``type``
    アノテーションタイプ。 ``'ARC'`` (楕円), ``'BITMAP'`` (ビットマップ),
    ``'CUSTOM'`` (カスタム), ``'GROUP'`` (グループ), ``'LINK'`` (リンク),
    ``'MARKER'`` (マーカー), ``'OLE'`` (OLE), ``'PAGEFORM'`` (見出し),
    ``'POLYGON'`` (多角形), ``'RECTANGLE'`` (矩形), ``'RECEIVEDSTAMP'``,
    ``'STAMP'`` (日付印), ``'STRAIGHTLINE'`` (直線), ``'STICKEY'`` (付箋),
    ``'TEXT'`` (テキスト), ``'TITLE'`` (タイトル) のいずれかです。

    Docuworks Viewer を利用してアノテーションをグループ化した場合は、
    それら (既存のアノテーション) を子アノテーションとして持つアノテーション
    (親アノテーション) が作られます (アノテーションタイプは 'GROUP')。
    この場合でも、属性 ``position`` および ``size`` は意味を持ちます。
    ``pos`` 番目の子アノテーションを取得するには、 ``self.annotation(pos)``
    または ``self[pos]`` とします。なお、xdwlib でグループアノテーションを
    追加することはできません。DocuWorks™ 7.x の XDWAPI がサポートしていない
    ためです。

    アノテーションには、子アノテーションを付けることができます。このとき、
    ``position`` は親アノテーションの ``position`` からの相対位置となります。
    DocuWorks Viewer の初期状態で利用できるテキスト付き付箋は、親となる
    付箋アノテーション (アノテーションタイプ ``'STICKEY'``) に
    子となるテキストアノテーション (アノテーションタイプ ``'TEXT'``) を
    追加して作られています。

    アノテーションタイプ ``'RECEIVEDSTAMP'`` は互換性のために存在するもの
    です。

``position``, ``size`` はいずれも擬似属性で、その子要素への直接代入は
できません。たとえば、 ``ann.position = Point(100, 150)`` とすることは
可能ですが、 ``ann.position.x = 100`` とすることはできません。

テキストアノテーション
''''''''''''''''''''''

※フォントの指定を参照してください。

``text``
    内容文字列。初期値は ``'TEXT'`` です。

``font_name``
    フォント名。TrueType フォントのみが有効です。 ``font_char_set`` も
    あわせて指定してください。初期値は ``u'ＭＳ 明朝'`` です。

``font_style``
    ``'ITALIC'``, ``'BOLD'``, ``'UNDERLINE'``, ``'STRIKEOUT'`` または
    これらの組み合わせ (``','`` で ``join`` します) で指定します。
    初期値は空文字列 (指定なし) です。

``font_size``
    フォントサイズです。ポイント数で指定します。1/10 ポイント未満は
    無視されます。初期値は 12 です。

``fore_color``
    文字色。色の指定を参照してください。初期値は ``'BLACK'`` です。

``font_pitch_and_family``
    フォントのピッチとファミリ。ピッチ (``'FIXED_PITCH'``,
    ``'VARIABLE_PITCH'``, ``'MONO_FONT'``) およびファミリ (``'ROMAN'``,
    ``'SWISS'``, ``'MODERN'``, ``'SCRIPT'``, ``'DECORATIVE'``) の
    組み合わせ  (``','`` で ``join`` します) で指定します (小文字でも
    かまいません)。ピッチ・ファミリの片方だけを指定することもでき、
    その場合は指定していない方はシステム既定値となります。初期値は
    ``'FIXED_PITCH,ROMAN'`` です。

``font_char_set``
    フォントの文字セット。 ``'DEFAULT'``, ``'ANSI'``, ``'SYMBOL'``,
    ``'MAC'``, ``'SHIFTJIS'``, ``'HANGEUL'``, ``'CHINESEBIG5'``,
    ``'GREEK'``, ``'TURKISH'``, ``'BALTIC'``, ``'RUSSIAN'``,
    ``'EASTEUROPE'``, ``'OEM'`` のいずれかで指定します (小文字でも
    かまいません)。初期値は ``'SHIFTJIS'`` です。

``back_color``
    背景色。色の指定を参照してください。初期値は ``'WHITE'`` です。

``word_wrap``
    ``True`` ならば、文字列を折り返します。初期値は ``False`` です。

``text_direction``
    ``True`` ならば、縦書きとします。初期値は ``False`` です。

``text_orientation``
    文字列の回転角度。0～359 の整数で指定します。初期値は 0 です。

``line_space``
    行間。行の高さの倍率で指定します。1/100 行未満は無視されます。
    初期値は 1 です。

``text_spacing``
    文字間隔。ポイント数で指定します。1/10 ポイント未満は無視されます。
    初期値は 0 です。

``margin``
    テキストアノテーションの上下左右の枠とテキスト領域の上下左右の辺との
    間の距離。mm 単位で指定します。それぞれ 0～200 が有効です。1/100 mm
    未満は無視されます。初期値はそれぞれ 1.7 です。

    これは擬似属性で、実際の値は以下の ``top_margin``, ``right_margin``,
    ``bottom_margin``, ``left_margin`` に格納されています。値を取得する
    ときは常に タプル (``top_margin``, ``right_margin``, ``bottom_margin``,
    ``left_margin``) を返しますが、値を設定するときは単一の数値または
    4 個までの数値のシーケンスを指定します。このシーケンスの構成は CSS と
    同じで、単一の値を指定したときは、上下左右すべてを同一の値とします。
    2 要素のシーケンスを指定したときは、最初の値を上下の、2 番目の値を
    左右の値とします。3 要素のシーケンスを指定したときは、最初の値を上辺の、
    2 番目の値を左右の、3 番目の値を下辺の値とします。4 個以上の要素を持つ
    シーケンスを指定したときは、最初の値を上辺の、2 番目の値を右辺の、
    3 番目の値を下辺の、4 番目の値を左辺の値とし、5 番目以降の要素が
    あっても無視します。

``top_margin``
    テキストアノテーションの上枠とテキスト領域の上辺との間の距離。
    mm 単位で指定します。0～200 が有効です。1/100 mm 未満は無視されます。
    初期値は 1.7 です。

``right_margin``
    テキストアノテーションの右枠とテキスト領域の右辺との間の距離。
    mm 単位で指定します。0～200 が有効です。1/100 mm 未満は無視されます。
    初期値は 1.7 です。

``bottom_margin``
    テキストアノテーションの下枠とテキスト領域の下辺との間の距離。
    mm 単位で指定します。0～200 が有効です。1/100 mm 未満は無視されます。
    初期値は 1.7 です。

``left_margin``
    テキストアノテーションの左枠とテキスト領域の左辺との間の距離。
    mm 単位で指定します。0～200 が有効です。1/100 mm 未満は無視されます。
    初期値は 1.7 です。

``auto_resize_height``
    ``True`` ならば、高さを自動調整します。 ``word_wrap`` が ``True`` の
    ときのみ有効です。初期値は ``False`` です。

リンクアノテーション
''''''''''''''''''''

``caption``
    リンクボタンのタイトル文字列。初期値は空文字列です。

``show_icon``
    ``True`` ならば、リンクボタンを表示します。初期値は ``True`` です。

``invisible``
    ``True`` ならば、リンクボタンを透明にします。初期値は ``False`` です。

``auto_resize``
    ``True`` ならば、リンクボタンの大きさをタイトルに合わせて自動調整
    します。初期値は ``True`` です。

``tooltip``
    ``True`` ならば、ツールチップを設定します。初期値は ``False`` です。

``tooltip_string``
    ツールチップ文字列。255 バイト以内で指定します。初期値は空文字列です。

``link_type``
    リンクの種類。 ``'ME'``, ``'XDW'``, ``'URL'``, ``'OTHERFILE'``,
    ``'MAILADDR'`` のいずれかで指定します (小文字でもかまいません)。
    初期値は ``'ME'`` です。

``url``
    リンク先 URL 文字列。255 バイト以内で指定します。 ``link_type`` が
    ``'URL'`` のとき有効です。初期値は空文字列です。

``xdw_path``
    リンク先 DocuWorks ファイルのパス名。絶対パス名に変換して 255 バイト
    以内で指定します。link_type が ``'XDW'`` のとき有効です。
    初期値は空文字列です。

``xdw_path_relative``
    ``True`` ならば、相対パス名でパス指定を行います。初期値は ``False``
    です。

``xdw_link``
    ``True`` ならば、リンク先をリンクアノテーションで指定します。
    ``False`` ならば、ページで指定します。初期値は ``False`` です。

``page_from``
    リンク先ページの指定方法を指定します。 ``'XDW'``, ``'XBD'``,
    ``'XDW_IN_XBD'`` のいずれかで指定します (小文字でもかまいません)。
    初期値は ``'XDW'`` です。

``xdw_name_in_xbd``
    リンク先の内部ドキュメントの文書名。 ``link_type `` が ``'XDW_IN_XBD'``
    のとき有効です。初期値は空文字列です。

``xdw_page``
    リンク先 DocuWorks ファイルのページ番号。バインダーの場合は通し番号です。
    プロファイル表示の場合は -1 になります。初期値は 0 です。

``link_atn_title``
    リンクアノテーションのタイトル。255 バイト以内の文字列です。
    初期値は空文字列です。

``other_file_path``
    リンク先ファイルのパス名。 ``link_type`` が ``'OTHERFILE'``
    のとき有効です。初期値は空文字列です。

``other_file_path_relative``
    ``True`` ならば、リンク先ファイルを相対パス名で指定します。
    初期値は False です。

``mail_address``
    リンク先のメールアドレス。255 バイト以内の文字列です。 ``link_type``
    が ``'MAILADDR'`` のとき有効です。初期値は空文字列です。

``font_name``, ``font_style``, ``font_size``, ``fore_color``,
``font_pitch_and_family``, ``font_char_set`` については、
テキストアノテーションと同様です。

付箋アノテーション
''''''''''''''''''

``fill_color``
    付箋内部の色。色の指定を参照してください。初期値は ``'WHITE'`` です。

``auto_resize`` については、リンクアノテーションと同様です。ただし、初期値は ``False`` です。

直線アノテーション
''''''''''''''''''

``border_width``
    線の太さ。ポイント数で指定します。1 ポイント未満は無視されます。
    初期値は 1 です。

``border_color``
    線の色。色の指定を参照してください。初期値は ``'BLACK'`` です。

``border_transparent``
    ``True`` ならば、線を半透明にします。初期値は ``False`` です。
``arrowhead_type``
    線端に付ける矢印の種類。 ``'NONE'``, ``'BEGINNING'``, ``'ENDING'``,
    ``'BOTH'`` のいずれかで指定します (小文字でもかまいません)。
    初期値は ``'NONE'`` です。

``arrowhead_style``
    線端に付ける矢印の形状。 ``'WIDE_POLYLINE'``, ``'POLYLINE'``,
    ``'POLYGON'`` のいずれかで指定します (小文字でもかまいません)。
    初期値は ``'WIDE_POLYLINE'`` です。

``points``
    始点・終点の座標データ。Point オブジェクトのシーケンスで指定します。

``border_type``
    線の種類。 ``'SOLID'``, ``'DOT'``, ``'DASH'``, ``'DASHDOT'``,
    ``'DOUBLE'`` のいずれかで指定します (小文字でもかまいません)。
    ``'DOT'``, ``'DOUBLE'`` は、``border_width < 3`` のときは実線で
    描画されます。 ``'DASH'``, ``'DASHDOT'`` を指定すると、
    ``border_transparent`` が無効になります。

矩形アノテーション・楕円アノテーション
''''''''''''''''''''''''''''''''''''''

``border_style``
     ``True`` ならば、枠線を表示します。初期値は ``True`` です。

``fill_style``
     ``'True'`` ならば、内部を塗りつぶします。初期値は ``'True'`` です。

``fill_transparent``
     ``'True'`` ならば、内部を半透明にします。初期値は ``'False'`` です。

``border_width``, ``border_color`` については、直線アノテーションと同様です。
``fill_color`` については、付箋アノテーションと同様です。

日付印アノテーション
''''''''''''''''''''

``top_field``
    上段の文字列。行あたり 12 バイト以内で、2 行まで指定できます。
    長さに改行文字は含めません。初期値は空文字列です。

``bottom_field``
    下段の文字列。行あたり 12 バイト以内で、2 行まで指定できます。
    長さに改行文字は含めません。初期値は空文字列です。

``date_style``
    ``True`` ならば、自動で日付を設定しません (つまり、手動で指定します)。
    ``False`` ならば、日付は自動設定されます。初期値は ``False`` です。

``basis_year_style``
    ``True`` ならば、日付印の基準年を設定します。 ``date_style`` が
    ``False`` のとき有効です。初期値は ``False`` です。

``basis_year``
    日付設定の基準年。1～9999 の整数で指定します。 ``basis_year_style`` が
    ``True`` のとき有効です。初期値は 1 です。

``date_field_first_char``
    日付欄の先頭文字 (1 文字)。初期値は ``"'"`` (アポストロフィ) です。

``year_field``
    日付欄の年部分。いわゆる半角英数字と  ``'-'`` から 4 文字までを
    指定できます。初期値は現在の年です。

``month_field``
    日付欄の月部分。いわゆる半角英数字と ``'-'`` から 4 文字までを
    指定できます。初期値は現在の月です。

``day_field``
    日付欄の日部分。いわゆる半角英数字と ``'-'`` から 4 文字までを
    指定できます。初期値は現在の日です。

``date_format``
    日付の書式設定。 ``'yy.mm.dd'``, ``'yy.m.d'``, ``'dd.mmm.yy'``,
    ``'dd.mmm.yyyy'`` のいずれかを指定できます (小文字で指定してください)。
    ``date_style`` が ``False`` のとき有効です。初期値は ``'yy.mm.dd'``
    です。

``date_order``
    ``True`` ならば、年月日を 日・月・年の順で表示します。 ``False``
    ならば、年・月・日の順で表示します。 ``date_style`` が ``False``
    のとき有効です。初期値は ``False`` です。

``border_color`` については、直線アノテーションと同様です。

マーカーアノテーション
''''''''''''''''''''''

``border_color``, ``border_width``, ``border_transparent``, ``points``
については、直線アノテーションと同様です。

多角形アノテーション
''''''''''''''''''''

``border_color``, ``border_width``, ``points``
については、直線アノテーションと同様です。
``border_style``, ``fill_style``, ``fill_color``, ``fill_transparent``
については、矩形アノテーションと同様です。

その他のアノテーション
''''''''''''''''''''''

固有の属性はありません。

インスタンスメソッド
--------------------

``attributes()``
    アノテーションが持つすべての属性名と属性値を持つ辞書を返します。

``content_text()``
    アノテーションに設定されているテキストを返します。
    テキストアノテーションの場合は ``self.text`` が、
    リンクアノテーションの場合は ``self.caption`` が、
    日付印アノテーションの場合は
    ``self.top_field + ' <DATE> ' + self.bottom.field`` が、
    それぞれ返ります。
    その他のアノテーションである場合は ``None`` が返ります。

``del_property(name)``
    ユーザ定義のプロパティ ``name`` を削除します。

``delprop(name)``
    ``del_property(name)`` と同じです。

``get_property(name, default=None)``
    ユーザ定義のプロパティ ``name`` の値を取得します。結果は ``str``,
    ``int``, ``bool`` または ``datetime.date`` オブジェクトです。
    プロパティ ``name`` が存在しない場合は、 ``default`` に
    指定した値を返します。

``getprop(name, default=None)``
    ``get_property(name)`` と同じです。

``get_userattr(name, default=None)``
    ユーザ定義属性 ``name`` の値を ``str`` で返します。
    ユーザ定義属性 ``name`` がない場合は ``default`` の値を返します。
    (注) 「ユーザ定義属性」と「ユーザ定義のプロパティ」は別物です。
    ユーザ定義属性に DocuWorks Viewer の GUI でアクセスする方法は
    現状ではありません。

``has_property(name)``
    ユーザ定義のプロパティ ``name`` が存在すれば ``True`` を、
    存在しなければ ``False`` を返します。

``hasprop(name)``
    ``has_property(name)`` と同じです。

``inside(rect)``
    ``rect`` は Rect オブジェクトです。 ``rect`` で指定する半開矩形領域に
    アノテーションが完全に収まっている場合は ``True`` を、そうでない場合は
    ``False`` を返します。

``lock()``
    アノテーションを固定します。

``unlock()``
    アノテーションの固定を解除します。

``rotate(degree, origin=None, orientation=False)``
    ``degree`` は時計回りでの角度 (単位は度です。)、 ``origin`` は Point
    オブジェクトです。 ``origin`` で示すページ上の位置を中心として
    アノテーションを ``degree`` 度だけ時計回りに回転します。 ``origin``
    が ``None`` である場合はアノテーションの現在位置 (多くの場合は左上)
    を回転の中心とします。 ``orientation`` が真である場合は、
    回転角に合わせてアノテーション自体の角度も変えます。 ``orientation``
    の指定は、テキストアノテーション、直線アノテーション、
    マーカーアノテーションおよび多角形アノテーションについてのみ有効です。
    (注) 直線アノテーション、マーカーアノテーションおよび
    多角形アノテーションの場合、 ``orientation`` に真を指定すると
    元のアノテーションは削除されて新たに適切な位置に同様のアノテーションが
    生成されます。

``set_property(name, value)``
    ユーザ定義のプロパティ ``name`` を設定します。 ``value`` は ``str``,
    ``int``, ``bool`` または ``datetime.date`` オブジェクトです。

``setprop(name, value)``
    ``set_property(name, value)`` と同じです。

``set_userattr(name, value)``
    ユーザ定義属性 ``name`` を設定します。 ``value`` は ``str`` で与えます。
    ``value`` に型を持たせたい場合は ``set_property()`` を用いてください。
    (注) 「ユーザ定義属性」と「ユーザ定義のプロパティ」は別物です。
    ユーザ定義属性に DocuWorks Viewer の GUI でアクセスする方法は
    現状ではありません。

``shift(*args)``
    ``*args`` は 2 個の数値からなるシーケンスです。 ``shift(x, y)``
    という形式でも、 ``shift([x, y])`` あるいは ``shift(Point(x, y))``
    という形式でもかまいません。アノテーションの位置を右へ ``x``
    ミリメートル, 下へ ``y`` ミリメートルだけ移動します。
    1/100 ミリメートル未満は無視されます。

AnnotationCache オブジェクト
============================

AnnotationCache クラスは、アノテーションの属性を (そのアノテーションが
消去された後であっても) 保持するために利用されます。

AnnotationCache オブジェクトは、元となった Annotation オブジェクトと
同等の属性を持ちます。オブジェクトの初期化後はすべての属性が読み出し専用と
なり、値の設定はできません。

コンストラクタ
--------------

クラス ``AnnotationCache(ann_or_type, **kw)``
    ``ann_or_type`` に Annotation オブジェクトを指定した場合は、Annotation
    オブジェクト ``ann`` の全属性 (ユーザ定義属性やプロパティは含みません。)
    を ``self`` の属性へコピーします。 ``kw`` の内容は参照されません。
    ``ann_or_type`` に文字列 (``'ARC'`` (楕円), ``'BITMAP'`` (ビットマップ),
    ``'CUSTOM'`` (カスタム), ``'GROUP'`` (グループ), ``'LINK'`` (リンク),
    ``'MARKER'`` (マーカー), ``'OLE'`` (OLE), ``'PAGEFORM'`` (見出し),
    ``'POLYGON'`` (多角形), ``'RECTANGLE'`` (矩形), ``'RECEIVEDSTAMP'``,
    ``'STAMP'`` (日付印), ``'STRAIGHTLINE'`` (直線), ``'STICKEY'`` (付箋),
    ``'TEXT'`` (テキスト), ``'TITLE'`` (タイトル) のいずれか) を
    指定した場合は、 ``kw`` の内容を ``self`` の属性へコピーします。

インスタンス属性
----------------

AnnotationCache オブジェクトのインスタンス属性は、コンストラクタに
与えられたアノテーションまたはアノテーションタイプによって異なります。

インスタンスメソッド
--------------------

``attributes()``
    インスタンス属性をまとめた ``dict`` を返します。

``content_text()``
    ``self.type()`` が ``'TEXT'``, ``'LINK'`` または ``'STAMP'``
    である場合は、アノテーションが保持しているテキストを返します。
    ``self.type()`` がそれ以外の値である場合は、 ``None`` を返します。

``type()``
    アノテーションタイプを返します。
