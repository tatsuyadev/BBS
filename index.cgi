#!/usr/bin/perl

use strict;
use CGI::Carp qw(fatalsToBrowser);
use warnings;
use v5.16.3;
use utf8;
use Encode;
use Image::Magick;
#use encoding "utf8";
use open ':encoding(UTF-8)';
binmode(STDOUT, ':encoding(UTF-8)');

print "Content-type: text/html; charset=UTF-8\n\n";

my %in;
my $alldata;

# フォーム処理
&form_processing();

my $tno;

# ----- 設定始まり -----
# 画像サイズ
my $IMGMAX = 5000000;
# 画像保存ディレクトリ
my $DIR = './img/';
# 管理パスワード
my $password = '';
# 投稿パスワード
my $post_password = '';
my $br_max =500;
my $br_max2 =0;
my $br_count = 0;
my $br_count2 = 0;
my $name_max = 60;
my $title_max = 60;
my $message_max = 1000;
my $res_max = 1000;
# 連続投稿制限時間(スレッド)
my $restrict_thread = 360;
# 連続投稿制限時間(レス)
my $restrict_res = 210;
# 禁止ワードリスト
my $no_wdList = "fuck,Fuck,hentai,エルメス偽物,死ね";
my $deny_IP;
my $deny_host;
# Defalutの1はurlリンク出来る
my $urllinkflag = 1;
my $maillinkflag = 1;
# 名前が空っぽの場合設定される名前
my $name_empty = '名無し';
# 1が投稿パスワード必須 0が必要なし
my $post_passwordflag = 1;
# 上下の枠の色
my $bgcolor = "#202070";
my $background_color = "#b0c4de";
my $solid_color = "#778899";

my $Version = "v2.1.0";
my $announce = "4枚までの複数画像アップロード対応";
my $r_vw = 10;
my $t_vw = 10;
# ----- 設定終わり -----

if($in{mode} eq 'admin'){ &admin(); }
if($in{mode} eq 'delete'){ &dele_data(); }
if($in{mode} eq 'form'){ &form(); }
if($in{mode} eq 'search'){ &search(); }

my @log;
my @log2;
my @log3;
my @disp;
my @disp_th;

my $title = $in{"title"};
my $name = $in{"name"};
my $message = $in{"message"};
my $pass = $in{"pass"};
my (@FileData, @FileNameList, @FileNameList_Time);

if(@FileData){
	writeImg();
	@FileData = ();
	@FileNameList = ();
}
$title = decode_utf8($title);
$name = decode_utf8($name);
$message = decode_utf8($message);

my $no_wd;
my $code;

if (length($title) >= $title_max){
	&error("件名が長すぎます。${title_max}より少なくして下さい。");
}
if (length($name) >= $name_max){
	&error("名前が長すぎます。${name_max}より少なくして下さい。");
}
if (length($message) >= $message_max){
	&error("メッセージが長すぎます。${message_max}より少なくして下さい。");
}
if ($title ne ""){
	$title =~ s/"/&quot;/g;
	$title =~ s/</&lt;/ig;
	$title =~ s/>/&gt;/ig;
	$title =~ s/&/&amp;/g;
	$title =~ s/\r\n/\n/g;
	$title =~ s/\r/\n/g;
	$title =~ s/\n\n*/\n/g;
}
while ($title =~ /<br>/ig){
	$br_count2++;
}
if ($br_max2 ne "" and $br_max2 < $br_count2){
	&error("改行は${br_max2}までです");
}
if ($message ne ""){
	$message =~ s/"/&quot;/g;
	$message =~ s/</&lt;/ig;
	#$message =~ s/>/&gt;/ig;
	$message =~ s/&/&amp;/g;
	
	# スレッドリンク機能
	$message =~ s*>>>(\d+)(?!\d+\.|\.)*<a href=\"$ENV{SCRIPT_NAME}?read=$1\">>>>$1<\/a>*g;
	# スレッドレスリンク機能 (通常)
	$message =~ s*>>>(\d+)\.(\d+)(?!\d+\-\d+|\-\d+)*<a href=\"$ENV{SCRIPT_NAME}?read=$1&num=$2\">>>>$1.$2<\/a>*g;
	# スレッドレスリンク機能 (範囲)
	$message =~ s*>>>(\d+)\.(\d+\-\d+)*<a href=\"$ENV{SCRIPT_NAME}?read=$1&num=$2\">>>>$1.$2<\/a>*g;
	# レスリンク機能 (通常)
	$message =~ s*(?=<br>|\s|^|)(?<!>)>>(\d+)(?!\d+\-\d+|\-\d+)*<a href=\"$ENV{SCRIPT_NAME}?read=$in{"tno"}&num=$1\">>>$1</a>*g;
	# レスリンク機能 (範囲)
	$message =~ s*>>(\d+\-\d+)*<a href=\"$ENV{SCRIPT_NAME}?read=$in{"tno"}&num=$1\">>>$1</a>*g;
	
	$message =~ s/\{赤\}([\s|\S]+?)\{\/赤\}/<font color ="red">$1<\/font>/g;
	$message =~ s/\{緑\}([\s|\S]+?)\{\/緑\}/<font color ="green">$1<\/font>/g;
	$message =~ s/\{青\}([\s|\S]+?)\{\/青\}/<font color ="blue">$1<\/font>/g;
	$message =~ s/\{黄\}([\s|\S]+?)\{\/黄\}/<font color ="yellow">$1<\/font>/g;
	$message =~ s/\{大\}([\s|\S]+?)\{\/大\}/<font size ="6">$1<\/font>/g;
	$message =~ s/\{小\}([\s|\S]+?)\{\/小\}/<font size ="1">$1<\/font>/g;
	$message =~ s/\{茶\}([\s|\S]+?)\{\/茶\}/<font color ="Brown">$1<\/font>/g;
	$message =~ s/\{紫\}([\s|\S]+?)\{\/紫\}/<font color ="Purple">$1<\/font>/g;
	#$message =~ s/\{深空\}([\s|\S]+?)\{\/深空\}/<font color ="DeepSkyBlue">$1<\/font>/g;
	$message =~ s/\{空\}([\s|\S]+?)\{\/空\}/<font color ="SkyBlue">$1<\/font>/g;
	$message =~ s/\{桃\}([\s|\S]+?)\{\/桃\}/<font color ="Pink">$1<\/font>/g;
	$message =~ s/\{流\}([\s|\S]+?)\{\/流\}/<marquee behavior="scroll">$1<\/marquee>/g;
	$message =~ s/\{往\}([\s|\S]+?)\{\/往\}/<marquee behavior="alternate">$1<\/marquee>/g;
	$message =~ s/\{太\}([\s|\S]+?)\{\/太\}/<b>$1<\/b>/g;
	#Perl
	while ($message =~ /\{perl\}([\s|\S]+?)\{\/perl\}/g){
		$code = $1;
		$code =~ s/&amp;/&/g;
		$code =~ s/&lt;/</g;
		$code =~ s/&gt;/>/g;
		$code =~ s/&quot;/"/g;
		$code =~ s/<script/javascriptは使えません/gi;
		$message =~ s/\{perl\}([\s|\S]+?)\{\/perl\}/<pre class="brush:perl;">$code<\/pre>/;
	}
	#css
	while ($message =~ /\{css\}([\s|\S]+?)\{\/css\}/g){
		$code = $1;
		$code =~ s/&amp;/&/g;
		$code =~ s/&lt;/</g;
		$code =~ s/&gt;/>/g;
		$code =~ s/&quot;/"/g;
		$code =~ s/<script/javascriptは使えません/gi;
		$message =~ s/\{css\}([\s|\S]+?)\{\/css\}/<pre class="brush:css;">$code<\/pre>/;
	}
=pod
	#Javascript
	while ($message =~ /\{javascript\}([\s|\S]+?)\{\/javascript\}/g){
		$code = $1;
		$code =~ s/&amp;/&/g;
		$code =~ s/&lt;/</g;
		$code =~ s/&gt;/>/g;
		$code =~ s/&quot;/"/g;
		$message =~ s/\{javascript\}([\s|\S]+?)\{\/javascript\}/<pre class="brush:js;">$code<\/pre>/;
	}
=cut
	#Delphi
	while ($message =~ /\{delphi\}([\s|\S]+?)\{\/delphi\}/g){
		$code = $1;
		$code =~ s/&amp;/&/g;
		$code =~ s/&lt;/</g;
		$code =~ s/&gt;/>/g;
		$code =~ s/&quot;/"/g;
		$code =~ s/<script/javascriptは使えません/gi;
		$message =~ s/\{delphi\}([\s|\S]+?)\{\/delphi\}/<pre class="brush:delphi;">$code<\/pre>/;
	}
	if ($urllinkflag == 1){
		$message =~ s*(https?://[\S]+)(?=<br>|\s|$)*<a href=\"$1" target=\"_blank\">$1<\/a>*ig;
	}
	$message =~ s/\r\n/<br>/g;
	$message =~ s/\r/<br>/g;
	$message =~ s/\n\n*/<br>/g;
	#multipart対策
	$message =~ s/\x0D\x0A/<br>/g;
=pod
	if ($maillinkflag == 1){
		$message =~ s/\b([-\w.]+@[-\w.]+\.[-\w]+)\b/<a href="mailto:$1">メールリンク<＼/a>/g;
	}
=cut
}
if ($name ne ""){
	$name =~ s/\r\n/\n/g;
	$name =~ s/\r/\n/g;
	$name =~ s/\n\n*/\n/g;
	$name =~ s/"/&quot;/g;
	$name =~ s/</&lt;/ig;
	$name =~ s/>/&gt;/ig;
	$name =~ s/&/&amp;/g;
}
while ($message =~ /<br>/ig){
	$br_count++;
}
if ($br_max ne "" and $br_max < $br_count){
	&error("改行は${br_max}までです");
}

if ($name =~ /#/){
	my $tmp = $`;
	my $tripkey = $';
	
	$tripkey =~ s/&r//g;
	$tripkey =~ s/＃/#/g;
	$tripkey =~ s/◆/◇/g;
	$tripkey = decode_utf8($tripkey);
	$tripkey = encode('Shift_JIS', $tripkey);
	my $salt = substr($tripkey.'H.',1,2);
	$salt =~ s/[^\.-z]/\./go;
	$salt =~ tr/:;<=>?@[\\]^_`/ABCDEFGabcdef/;
	my $trip = crypt($tripkey,$salt);
	$trip =substr($trip,-10);
	$trip = decode('Shift_JIS', $trip, );
	$trip = encode_utf8($trip);
	$trip = '◆'.$trip;
	$name = "$tmp$trip";
}

my @youbi = ('日','月','火','水','木','金','土');
my $time = time;
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime($time);
$year += 1900;
$mon++;
$mon = sprintf("%02d", $mon);
$mday = sprintf("%02d", $mday);
$hour = sprintf("%02d", $hour);
$min = sprintf("%02d", $min);
$sec = sprintf("%02d", $sec);

my $date = "$year/$mon/$mday(@youbi[$wday]) $hour:$min:$sec";

# レス表示部分
if($in{read} >= 1){
	open(IN, "data/$in{read}.cgi") or &error("open err: $in{read}.cgi");
	@log = <IN>;
	close(IN);
	my $size = @log;
	my $r_begin;
	my $r_end;
	my $r_num1;
	my $r_num2;
	if ($in{num} eq 'all'){
		$r_begin =0;
		$r_end =$size;
		$r_num1 = 1;
		$r_num2 = $size;
	}
	if (($in{num} >= 1) or ($in{num} =~ /([\d]+)\-([\d]+)/)){
		if ($in{num} =~ /([\d]+)\-([\d]+)/){
			if (($1 < $2) and ($1 >= 1) and ($2 <= $size)){
				$r_num1 = $1;
				$r_num2 = $2;
				$r_begin = $size - $r_num2;
				$r_end = $size - $r_num1 + 1;
			} else {
				error("正しい数字の範囲を入力して下さい。");
			}
		} else {
			$r_begin = $size - $in{num};
			$r_end = $r_begin + 1;
		}
	} elsif ($in{num} ne 'all'){
		if ($size < $r_vw){
			$r_num1 =1;
		} else {
			$r_num1 =$size - $r_vw + 1;
		}
		$r_num2 =$size;
		if ($r_num2 < $r_vw){
			$r_end = $r_num2;
		} else {
			$r_end = $r_vw;
		}
		$r_begin = 0;
	}
	
	for(my $i = $r_begin; $i < $r_end; ++$i){
		my @img_p = ();
		my ($tno,$no_p,$name_p,$message_p,$date_p,$id_p,$img1,$img2,$img3,$img4) = (split(/<>/,$log[$i]))[0,2,3,4,5,9,10,11,12,13];
		$img_p[0] = $img1;
		$img_p[1] = $img2;
		$img_p[2] = $img3;
		$img_p[3] = $img4;
		my @File = ();
		my $ii = 0;
		while($img_p[$ii] =~ /\./){
			$File[$ii] = "<a href = \"https://$ENV{SERVER_NAME}/bbs/img/$img_p[$ii]\"><img src=\"$DIR$img_p[$ii]\" align=\"right\" alt=\"画像\" width=\"48\" height=\"48\"></a>";
			++$ii;
			if(4 == $ii){ last; }
		}
		#Perl
		if ($message_p =~ /<pre class="brush:perl;">[\s|\S]+?<\/pre>/){
			
			#改行を変換　ループから抜ける為にわざと誤変換
			while ($message_p =~ /<pre class="brush:perl;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:perl;">([\s|\S]+?)<\/pre>/<pre class="brush:perl;">$code<pre>/;
			}
			#ループから抜ける為に誤変換したものを直す処理。番兵法or他に簡潔な方法があったら変える予定
			while ($message_p =~ /<pre class="brush:perl;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:perl;">([\s|\S]+?)<pre>/<pre class="brush:perl;">$code<\/pre>/;
			}
		}
		#CSS
		if ($message_p =~ /<pre class="brush:css;">[\s|\S]+?<\/pre>/){
			
			#改行を変換　ループから抜ける為にわざと誤変換
			while ($message_p =~ /<pre class="brush:css;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:css;">([\s|\S]+?)<\/pre>/<pre class="brush:css;">$code<pre>/;
			}
			#ループから抜ける為に誤変換したものを直す処理。番兵法or他に簡潔な方法があったら変える予定
			while ($message_p =~ /<pre class="brush:css;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:css;">([\s|\S]+?)<pre>/<pre class="brush:css;">$code<\/pre>/;
			}
		}
=pod
		#Javascript
		if ($message_p =~ /<pre class="brush:js;">[\s|\S]+?<\/pre>/){
			
			#改行を変換　ループから抜ける為にわざと誤変換
			while ($message_p =~ /<pre class="brush:js;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:js;">([\s|\S]+?)<\/pre>/<pre class="brush:js;">$code<pre>/;
			}
			#ループから抜ける為に誤変換したものを直す処理。番兵法or他に簡潔な方法があったら変える予定
			while ($message_p =~ /<pre class="brush:js;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:js;">([\s|\S]+?)<pre>/<pre class="brush:js;">$code<\/pre>/;
			}
		}
=cut
		#Delphi
		if ($message_p =~ /<pre class="brush:delphi;">[\s|\S]+?<\/pre>/){
			
			#改行を変換　ループから抜ける為にわざと誤変換
			while ($message_p =~ /<pre class="brush:delphi;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:delphi;">([\s|\S]+?)<\/pre>/<pre class="brush:delphi;">$code<pre>/;
			}
			#ループから抜ける為に誤変換したものを直す処理。番兵法or他に簡潔な方法があったら変える予定
			while ($message_p =~ /<pre class="brush:delphi;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:delphi;">([\s|\S]+?)<pre>/<pre class="brush:delphi;">$code<\/pre>/;
			}
		}
		$disp[$i] = "<hr color=#3377bb>[$no_p]$name_p<br><font color=#ff3399>ID:$id_p</font><br>$message_p<br>@File<br><font  color=#dddd33>$date_p</font>";
		
	}
	my ($tno,$title) = (split(/<>/,$log[$#log]))[0,1];
	print <<"EOF";
	<html>
	<head>
	<meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
	<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\" />
	<meta http-equiv=\"Content-Script-Type\" content=\"text/javascript\">
	<meta http-equiv=\"Content-Style-Type\" content=\"text/css\">
	<link type=\"text/css\" rel=\"stylesheet\" href=\"https://developer-world.net/sh/styles/shCore.css\" />
	<link type=\"text/css\" rel=\"stylesheet\" href=\"https://developer-world.net/sh/styles/shCoreDefault.css\" />
	<link type=\"text/css\" rel=\"stylesheet\" href=\"https://developer-world.net/sh/styles/shThemeDefault.css\" />
	<link type=\"text/css\" rel=\"stylesheet\" href=\"https://developer-world.net/bbs/main.css\" />
	<script src=\"../jquery-3.5.1.min.js\"></script>
	<script src=\"main.js\"></script>
	<script src="mojicount.js"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/XRegExp.js\"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/shCore.js\"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/shBrushPerl.js\"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/shBrushCss.js\"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/shBrushJScript.js\"></script>
	<script type=\"text/javascript\" src=\"https://developer-world.net/sh/scripts/shBrushDelphi.js\"></script>
	
	<script type=\"text/javascript\">
	SyntaxHighlighter.defaults['auto-links'] = false;
	SyntaxHighlighter.defaults['toolbar'] = false;
	SyntaxHighlighter.defaults['gutter'] = true;
	SyntaxHighlighter.all();
	</script>
	
	<Script Language=\"JavaScript\">
<!--
	function show() {
	var objID=document.getElementById( \"change\" );
	if(objID.className=='close') {
		objID.style.display='block';
		objID.className='open';
	}else{
		objID.style.display='none';
		objID.className='close';
		}
	}
//-->
	</script>
	<title>$title</title>
	</head>
	<body>
	<h2>$title</h2>
	<form action="$ENV{SCRIPT_NAME}" method="post">
	<table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
	<a href="#bottom" name="top" accesskey="8">▼</a> <a href="$ENV{SCRIPT_NAME}?read=$tno" accesskey="5">更新</a>
	<a href="$ENV{SCRIPT_NAME}">掲示板トップ</a></td></tr></table>
EOF

	@disp = reverse(@disp);
	print "@disp";
	print <<"EOF";
		<hr color="#3377bb">
<table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
<a href="#top" name="bottom" accesskey="2">▲</a> <a href="$ENV{SCRIPT_NAME}">掲示板トップ</a>
EOF
	
	if (($size > $r_num2) and (($r_vw - 1) == ($r_num2 - $r_num1))){
		my $range1;
		my $range2;
		$range1 =  $r_num1 + $r_vw;
		$range2 = $r_num2 + $r_vw;
		if ($size < $range2){
			$range1 = $size - $r_vw + 1;
			$range2 = $size;
		}
		printf qq(<a href="$ENV{'SCRIPT_NAME'}?read=$tno&num=%d-%d"><<前ページ</a>\n),$range1,$range2;
	}
	if((1 < $r_num1) and (($r_vw - 1) == ($r_num2 - $r_num1))){
		my $range1;
		my $range2;
		$range1 =  $r_num1 - $r_vw;
		$range2 = $r_num2 - $r_vw;
		if ($r_vw  > $range2){
			$range1 = 1;
			$range2 = $r_vw;
		}
		printf qq(<a href ="$ENV{SCRIPT_NAME}?read=$tno&num=%d-%d">次ページ>></a>\n),$range1,$range2;
	}
	printf qq(<a href ="$ENV{SCRIPT_NAME}?read=$tno&num=all">全部</a></td></tr></table>\n);
	print qq(<input type="hidden" name="num" value="$in{'num'}"></form>);
	print <<"EOF";
		<form action="$ENV{SCRIPT_NAME}"method="post" enctype="multipart/form-data">
		<table><tr><th>名前:</th><td><input type=\"text\" name=\"name\" placeholder=\"お名前を入力(省略化)\" id=\"name\"></td></tr>
		<tr><th><a href=\"javascript:void(0)\" onClick=show();>独自タグ</a></th><td><div id=\"change\" style=\"display: none;position:relative;\" class=\"close\">
		<input type=\"button\" value=\"赤\" class=\"tag\"> <input type=\"button\" value=\"緑\" class=\"tag\"> <input type=\"button\" value=\"青\" class=\"tag\"> 
		<input type=\"button\" value=\"黄\" class=\"tag\"> <input type=\"button\" value=\"茶\" class=\"tag\"> <input type=\"button\" value=\"紫\" class=\"tag\"> 
		<input type=\"button\" value=\"空\" class=\"tag\"> <input type=\"button\" value=\"桃\" class=\"tag\"> <input type=\"button\" value=\"大\" class=\"tag\"> 
		<input type=\"button\" value=\"小\" class=\"tag\"> <input type=\"button\" value=\"流\" class=\"tag\"> <input type=\"button\" value=\"往\" class=\"tag\"> 
		<input type="button" value="太" class="tag"> 
		<input type=\"button\" value=\"perl\" class=\"tag\"> <input type=\"button\" value=\"delphi\" class=\"tag\"> <input type=\"button\" value=\"css\" class=\"tag\"></div></td></tr>
		<tr><th>メッセージ:</th><td><textarea name="message" rows="5" cols= "45" id="message" class="message" placeholder="メッセージを入力" onKeyUp="checkText();"></textarea></td></tr>
		<tr><th align=right><font color=#757575><div id="result_mojicount" class="result_mojicount"></div></font></th><td align=left>/$message_max</font></td></tr>
		<tr><th>画像:</th><td><input type="file" name="img" value="" size="50" multiple="multiple"></td></tr>
		<tr><th><td>※JPG・JPEG・GIF・PNGのみ（${IMGMAX}バイト以内で4枚まで）</th></td></tr>
EOF

	if($post_passwordflag == 1){
		print <<"EOF";
			<tr><th>投稿パス:</th><td><input type=\"password\" name=\"pass\" value=\"\" size=\"20\" placeholder=\"投稿パスを入力\" id=\"pass\"></td></tr>
EOF

	}
	print <<"EOF";
		</table><input type=\"hidden\" name=\"tno\" value=\"$tno\"><input type=\"button\" onclick=\"submit();save();\" value =\"投稿\"></form>
		<a href="https://px.a8.net/svt/ejp?a8mat=3H83LP+4EYRAQ+50+2HZO35" rel="nofollow">
		<img border="0" width="468" height="60" alt="" src="https://www21.a8.net/svt/bgt?aid=210329917267&wid=001&eno=01&mid=s00000000018015115000&mc=1"></a>
		<img border="0" width="1" height="1" src="https://www19.a8.net/0.gif?a8mat=3H83LP+4EYRAQ+50+2HZO35" alt="">
		<div id="page-top"><a href="#down" name="up">PAGE BOTTOM</a></div><a href="#up" name="down"></a></body>
EOF

exit;
}
# メッセージが入力されているときは書き込み処理を行なう
if($in{tno} >= 1){
	open(IN, "data/$in{tno}.cgi") or $!;
	@log2 = <IN>;
	close(IN);
	if ($name eq ""){$name =$name_empty;}
	if ($message ne "") {
		if($post_passwordflag == 1 and $pass ne $post_password){
			error("投稿パスワードが間違っています");
		}
		# メッセージに何か入ってるならhost取得
		my ($host,$ip) = &get_host();
		open(DAT,"+< data/$in{tno}.cgi") or $!;
		my $top = <DAT>;
		my($tno,$title,$no,$hos,$tim)= (split(/<>/,$top))[0,1,2,6,7];
		if($no == $res_max){
			error("レス投稿最大数は${res_max}です");
		}
		my $flg;
		if($host eq  $hos && $time - $tim < $restrict_res){ $flg =1;}
		if($flg){
			close(DAT);
			error("現在投稿制限中(${restrict_res}秒規制)");
		}
		close(DAT);
		
		# 禁止ワードチェック
		no_wd();
		
# $noはレス投稿からは2から始まる
		++$no;
		my $salt = substr($ip.'H.',1,2);
		$salt =~ s/[^\.-z]/\./go;
		$salt =~ tr/:;<=>?@[\\]^_`/ABCDEFGabcdef/;
		my $id = crypt($ip,$salt);
		$id =substr($id,-8);
# レスログファイルに書き込み
		unshift @log2,"$tno<>$title<>$no<>$name<>$message<>$date<>$host<>$time<>$ip<>$id<>$FileNameList_Time[0]<>$FileNameList_Time[1]<>$FileNameList_Time[2]<>$FileNameList_Time[3]<>\n";
		open(OUT,"> data/$in{tno}.cgi");
		flock(OUT,2);
		truncate(OUT,0);
		seek(OUT,0,0);
		print OUT @log2;
		close(OUT);

		@FileNameList_Time = ();
		my($img1,$img2,$img3,$img4);
# スレログファイル上書き
		my $flg1;
		open(DAT2,"+< data/index.log") or $!;
		#eval "flock(DAT2,2);";
		while(<DAT2>){
			my($tno,$title,$no,$name,$message,$date,$host,$time,$ip,$id,$img1,$img2,$img3,$img4) = split(/<>/);
			if($in{tno} == $tno){
				next;
			}
			push(@log3,$_);
		}
		seek(DAT2,0,0);
		print DAT2 @log3;
		truncate(DAT2,tell(DAT2));
		close(DAT2);

		
		unshift @log3,"$tno<>$title<>$no<>$name<>$message<>$date<>$host<>$time<>$ip<>$id<>$img1<>$img2<>$img3<>$img4<>\n";
		open(OUT2,"> data/index.log");
		#flock(OUT2,2);
		truncate(OUT2,0);
		seek(OUT2,0,0);
		print OUT2 @log3;
		close(OUT2);
	}
}

my $ip_address;

# 掲示板トップページ
print <<"EOF";
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta http-equiv="Content-Style-Type" content="text/css">
<title>交流掲示板$Version</title>
</head>
<body>
<h2>交流掲示板$Version</h2>
$announce<br>
<form action="$ENV{SCRIPT_NAME}" method="post">
<table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
<a href="#bottom" name="top" accesskey="8">▼</a> <a href = "$ENV{SCRIPT_NAME}?mode=form">投稿</a> <a href="https://developer-world.net$ENV{SCRIPT_NAME}" accesskey="5">更新</a> <a href = "$ENV{SCRIPT_NAME}?mode=search">検索</a>
EOF

#能が文字化けしてしまう為の対策
print '<a href="https://developer-world.net/aboutbbs.html">機能</a> <a href="https://developer-world.net/">ホームページ</a></td></tr></table><hr color=#3377bb>';


# スレッド表示部分
# スレッド読み込み
open(IN, "data/index.log") or $!;
@log3 = <IN>;
close(IN);
# スレッドの1番目のレス表示部分
if ($name eq ""){$name =$name_empty;}
if ($title ne "" and $message ne ""){
	if($post_passwordflag == 1 and $pass ne $post_password){
		error("投稿パスワードが間違っています");
	}
# メッセージに何か入ってるならhost取得
	my ($host,$ip) = &get_host();
	open(DAT,"+< data/index.log") or $!;
	my $top = <DAT>;
	my($hos,$tim)= (split(/<>/,$top))[6,7];
	my $flg;
	if($host eq  $hos && $time - $tim < $restrict_thread){ $flg =1;}
	if($flg){
		close(DAT);
		error("現在投稿制限中(${restrict_thread}秒規制)");
	}
	close(DAT); 

	# 禁止ワードチェック
	no_wd();

	my $tno;
	my $no=1;
	my $i=0;
	while($i < $#log3 + 1){
		my $tmp =(split(/<>/,$log3[$i]))[0];
		if($tno < $tmp){
			$tno = $tmp;
		}
		$i++;
	}

	$tno++;
	my $salt = substr($ip.'H.',1,2);
	$salt =~ s/[^\.-z]/\./go;
	$salt =~ tr/:;<=>?@[\\]^_`/ABCDEFGabcdef/;
	my $id = crypt($ip,$salt);
	$id =substr($id,-8);
	#print "$tno,$title<br>";

# スレログファイルに書き込み
	unshift(@log3,"$tno<>$title<>$no<>$name<>$message<>$date<>$host<>$time<>$ip<>$id<>$FileNameList_Time[0]<>$FileNameList_Time[1]<>$FileNameList_Time[2]<>$FileNameList_Time[3]<>\n");
	open(OUT1,"> data/index.log");
	#flock(OUT1,2);
	truncate(OUT1,0);
	seek(OUT1,0,0);
	print OUT1 @log3;
	close(OUT1);

# レス一番目の投稿に書き込み	
	unshift(@log,"$tno<>$title<>$no<>$name<>$message<>$date<>$host<>$time<>$ip<>$id<>$FileNameList_Time[0]<>$FileNameList_Time[1]<>$FileNameList_Time[2]<>$FileNameList_Time[3]<>\n");
	open(OUT2,"> data/$tno.cgi");
	#flock(OUT2,2);
	truncate(OUT2,0);
	seek(OUT2,0,0);
	print OUT2 @log;
	close(OUT2);
	@FileNameList_Time = ();
}

if($in{pg}<=-1){
	error("そんなページ無いよ");
}
my $vw = 10;
my $begin = $in{'pg'};
my $back = $in{'pg'} - $vw;
my $next = $begin +$vw;
if($next > @log3){
	$next = @log3;
}
#print "@log3";
# スレッド一覧表示
for(my $i = $begin; $i < $next; ++$i){
	my ($tno,$title,$no) = (split(/<>/,$log3[$i]))[0,1,2];
	$disp_th[$i] = "・<a href=$ENV{SCRIPT_NAME}?read=$tno>$title</a> #$no<br>";
	chomp $disp_th[$i];
}
print "<form action=$ENV{SCRIPT_NAME}>";
print "@disp_th";
print "</form>";
print <<EOF;
	<hr color=#3377bb><table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;"><a href="#top" name="bottom" accesskey="2">▲</a><br>
EOF

if(1 <= $in{'pg'}){
	print qq(<a href="$ENV{'SCRIPT_NAME'}?pg=$back"><<前ページ</a>\n);
}
if($next < @log3){
	print qq(<a href ="$ENV{SCRIPT_NAME}?pg=$next">次ページ>></a>\n);
}
print qq(</td></tr></table>);
printf qq(ページ数[%d]),$in{'pg'} / $vw + 1;
print qq(<input type="hidden" name="pg" value="$in{'pg'}"></form>);
print qq(<form action="$ENV{SCRIPT_NAME}"><a href = "$ENV{SCRIPT_NAME}?mode=admin">管理</a></form>);



=pod
printf qq(<form action=http://perlman.s601.xrea.com/cgi-bin/test1.cgi><input type="number" name="pg">);
printf qq(<input type="submit" value="レス番号Jump"></form>);
=cut

print <<EOF;
	<form id="homepage_query_box_form" action="https://www.google.co.jp/m?"><div>
	<input type="hidden" name="ie" value="UTF-8"/> <input class="c4" id="homepage_query_box_textbox" type="text" name="q" size="8"/>
	<input class="c0" id="homepage_query_box_submit" type="submit" value="Google"/></div></form></body></html>
EOF
#---------------------------------------------------------------------------------------------------
# サブルーチン
#---------------------------------------------------------------------------------------------------
# IP&ホスト取得
sub get_host {
	my $host = $ENV{REMOTE_HOST};
	my $ip = $ENV{REMOTE_ADDR};
	if ($host eq "" || $host eq $ip) {
		$host = gethostbyaddr(pack("C4", split(/\./, $ip)), 2);
	}
	
	# IPチェック
	my $flg;
	foreach ( split(/\s+/,$deny_IP) ) {
		s/\./\\\./g;
		s/\*/\.\*/g;
		
		if ($ip =~ /^$_/i) { $flg = 1; last; }
	}
	if ($flg) {
		error("このIPは書き込みを許可されていません");
	
	# ホストチェック
	foreach ( split(/\s+/,$deny_host) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;
			
			if ($host =~ /$_$/i) { $flg = 1; last; }
		}
		if ($flg) {
			error("このHostは書き込みを許可されていません");
		}
	}
	
	if ($host eq "") { $host = $ip; }
	return ($host,$ip);
}
# error処理
sub error{
	my $error_message =$_[0];
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
	<title>エラー</title></head><body>
EOF

	print "<hr color=#3377bb>$error_message";
	print "<hr color=#3377bb>";
	print <<EOF;
	</body>
	</html>
EOF
	
	exit;
}

sub form{
	print <<"EOF";
	<html>
	<head>
	<meta name="viewport" content="width=device-width,initial-scale=1.0">
	<script src="../jquery-3.5.1.min.js"></script>
	<script src="main.js"></script>
	<script src="mojicount.js"></script>
	<title>投稿画面</title>
	<Script Language="JavaScript">
<!--
function show() {
var objID=document.getElementById( "change" );
if(objID.className=='close') {
objID.style.display='block';
objID.className='open';
}else{
objID.style.display='none';
objID.className='close';
}
}

//-->
</script>
	</head>
	<body><form action="$ENV{SCRIPT_NAME}"method="post" enctype="multipart/form-data">
	<table>
	<tr><th>件名:</th><td><input type="text" name="title" placeholder=\"件名を入力\"></td></tr>
	<tr><th>名前:</th><td><input type="text" name="name" placeholder=\"お名前を入力(省略化)\" id=\"name\"></td></tr>
	<tr><th><a href="javascript:void(0)" onClick=show();>独自タグ</a></th><td><div id="change" style="display: none;position:relative;" class="close"><input type="button" value="赤" class="tag"> <input type="button" value="緑" class="tag"> <input type="button" value="青" class="tag"> <input type="button" value="黄" class="tag"> <input type="button" value="茶" class="tag"> <input type="button" value="紫" class="tag"> <input type="button" value="空" class="tag"> <input type="button" value="桃" class="tag"> <input type="button" value="大" class="tag"> <input type="button" value="小" class="tag"> <input type="button" value="流" class="tag"> <input type="button" value="往" class="tag"> <input type="button" value="太" class="tag"> <input type="button" value="perl" class="tag"> <input type="button" value="delphi" class="tag"> <input type="button" value="css" class="tag"></div></td></tr>
	<tr><th>メッセージ:</th><td><textarea name="message" rows="5" cols= "45" id="message" class="message" placeholder=\"メッセージを入力\" onKeyUp="checkText();"></textarea></td></tr>
	<tr><th align=right><font color=#757575><div id="result_mojicount" class="result_mojicount"></div></font></th><td align=left>/$message_max</font></td></tr>
	<tr><th>画像:</th><td><input type="file" name="img" value="" size="50" multiple="multiple"></td></tr>
EOF

	if($post_passwordflag == 1){
		print <<"EOF";
			<tr><th>投稿パス:</th><td><input type="password" name="pass" value="" size="20" placeholder=\"投稿パスを入力\" id=\"pass\"></td></tr>
EOF

	}

print "<tr><th><td>※JPG・JPEG・GIF・PNGのみ（${IMGMAX}バイト以内で4枚まで）</th></td></tr>";
print "</table><input type=\"button\" onclick=\"submit();save();\" value =\"投稿\"></form></body>";
	print <<"EOF";
	<a href="https://px.a8.net/svt/ejp?a8mat=3H855Y+EU1UEQ+1JUK+ZQV5T" rel="nofollow">
<img border="0" width="468" height="60" alt="" src="https://www25.a8.net/svt/bgt?aid=210331942897&wid=001&eno=01&mid=s00000007238006004000&mc=1"></a>
<img border="0" width="1" height="1" src="https://www10.a8.net/0.gif?a8mat=3H855Y+EU1UEQ+1JUK+ZQV5T" alt="">
EOF

	exit;
}

# form処理
sub form_processing{
	if($ENV{'REQUEST_METHOD'} eq 'POST'){
		read(STDIN,$alldata,$ENV{'CONTENT_LENGTH'});
	} else {
		$alldata = $ENV{'QUERY_STRING'};
	}
	#$test = $alldata;
	if (defined($ENV{'CONTENT_TYPE'}) && $ENV{'CONTENT_TYPE'}=~m|^multipart/form-data|){
		my ($split) = split(/\x0D\x0A/, $alldata);
		my $ii = 0;
		foreach my $pair (split(/$split/, $alldata)) {
			my @alldata = split(/\x0D\x0A/, $pair);
			if($alldata[1] =~ /(filename)="(.+\.\w+)"/) {
				$FileNameList[$ii] = $2;
				if($alldata[1] =~ /name="(\w+)"/) {
					for(my $i = 3 ; $i < @alldata ; $i++) {
						if(4 <= $ii){
							error("投稿できる画像の数は4枚までです。");
						}
						if($FileData[$ii]) {
							$FileData[$ii] .= "\x0D\x0A";
						}
						$FileData[$ii] .= $alldata[$i];
					}
				}
				++$ii;
			}
			else {
				$in{$1} =~ tr/\t/ /;
				if($alldata[1] =~ /name="(\w+)"/) {
					for(my $i = 3 ; $i < @alldata ; $i++) {
						if($in{$1}) {
							$in{$1} .= "\x0D\x0A";
						}
						$in{$1} .= $alldata[$i];
					}
				}
			}
		}
	}
	else {
		foreach my $data (split(/&/,$alldata)){
		my ($key,$value) = split(/=/,$data);
		$value =~ s/\+/ /g;
		$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack('C',hex($1))/eg;
		$value =~ s/\t//g;
		$in{"$key"} = $value;
		}
	}
}
# 画像処理部分
sub writeImg{
	my @Extension;
	for(my $i = 0; $i < $#FileData + 1; ++$i){
		my @filename = split(/\./, $FileNameList[$i]);
		$filename[@filename - 1] =~ tr/A-Z/a-z/;
		$Extension[$i] = $filename[@filename - 1];
		
		if(length($FileData[$i]) > $IMGMAX) {
			error("$FileNameList[$i]の画像はサイズオーバーです。（" . length($FileData[$i]) . "バイト）");
		}
		elsif(!($Extension[$i] eq "jpg" or $Extension[$i] eq "jpeg" or $Extension[$i] eq "gif"
			or $Extension[$i] eq "png")) {
			error("$FileNameList[$i]の拡張子ではアップロードできません。");
		}
	}
	my @Path;
	for(my $i = 0; $i < $#FileData + 1; ++$i){
		my $timeImg = time;
		$FileNameList_Time[$i] = $timeImg . $i + 1 . "." . $Extension[$i];
		$Path[$i] = $DIR . $FileNameList_Time[$i];
		open(IMG1, ">$Path[$i]") or error("ファイル作成に失敗しました。");
		binmode(IMG1);
		print IMG1 $FileData[$i];
		close(IMG1);
		system("/usr/bin/convert $Path[$i] -sampling-factor 4:2:0 -auto-orient -interlace $Extension[$i] -quality 85 -strip $Path[$i]");
	}
}

# 禁止ワードチェック
sub no_wd{
	my $flg;
	foreach(split(/,/,$no_wdList)){
		if(index("$message",$_) >= 0){
			$no_wd =$_;
			$flg = 1;
			last;
		}
	}
	if ($flg) { error("禁止ワード($no_wd)が含まれています"); }
}

# admin
sub admin{
	form_processing();
	check_passwd();

	# 条件分岐
	if ($in{data_mente}) { data_mente(); }
	if ($in{act} eq "del") { th_dele(); }
	if ($in{act} eq "art") { data_mente_res(); }

	if ($in{act} eq "menu_html") { menu_html(); }
	if ($in{res_dele}) { res_dele(); }
	menu_html();
	
	exit;
}

# パスワード認証
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		enter_form();
	
	# パスワード認証
	} elsif ($in{pass} ne "$password") {
	
		#print "$password";
		error("認証できません");
	}
}

# 入室画面
sub enter_form {
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
	<title>入室画面</title></head><body>
	<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
	<div id="login">
	<fieldset><legend> password </legend>
		<input type="hidden" name="mode" value=admin>
		<input type="password" name="pass">
		<input type="submit" value="ログイン">
	</fieldset>
	</div>
	</form>
	</body>
	</html>
EOF
	exit;
}

sub menu_html {
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>管理画面</title></head><body>
	<center><h2>管理画面</h2></center>
	<hr color=#3377bb><center><a href="$ENV{SCRIPT_NAME}" target="_blank">スレッド掲示板確認</a></center><hr color=#3377bb>
	<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
	<input type="hidden" name="mode" value=admin>
	<input type="hidden" name="pass" value=$password>
	<center><input type="submit" name="data_mente" value="スレッド管理"></center>
	</form>
	</body>
	</html>
EOF
	exit;
}
# スレッド管理
sub data_mente {
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
	<title>スレッド管理</title><meta http-equiv="Content-Style-Type" content="text/css"></head><body>
	<h2>スレッド管理</h2>
	<table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;"><a href="#bottom" name="top" accesskey="8">▼</a>
	</td></tr></table>
	<hr color=#3377bb>
	<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
	<input type="hidden" name="mode" value=admin>
	<input type="hidden" name="pass" value=$password>
EOF


	open(IN, "data/index.log") or $!;
	my @logmente_th = <IN>;
	close(IN);

	if($in{pg}<=-1){
		error("そんなページ無いよ");
	}

	my $vw_th = 1000;
	my $begin_th = 0;
	my $next_th = 1000;
	if($next_th > @logmente_th){
		$next_th = @logmente_th;
	}

	# スレッド一覧表示
	my $ii = 0;
	for(my $i = $begin_th; $i < $next_th; ++$i){
		my ($tno,$title,$no) = (split(/<>/,$logmente_th[$i]))[0,1,2];
		++$ii;
		$disp_th[$i] = "<input type=checkbox name=selectedth$ii value=$tno>$title #$no<br>";
		chomp $disp_th[$i];
	}
	print "@disp_th";
	
	print <<EOF;
		<br><select name="act">
		<option value="menu_html">メニューに戻る
		<option value="art">スレッド内移動
		<option value="del">スレッド削除
		</select><input type="submit" value="送信する">
		<hr color=#3377bb><table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
		<a href="#top" name="bottom" accesskey="2">▲</a></td></tr></table>
EOF

	print qq(</form></body></html>);
	exit;
}
# スレッド削除
sub th_dele {
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\">
	<title>スレッド削除</title></head><body>
	<h2>スレッド削除</h2>
	<hr color=#3377bb>
	<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
	<input type="hidden" name="mode" value=admin>
	<input type="hidden" name="pass" value=$password>
	<input type="submit" name="data_mente" value="スレッド管理に戻る">
EOF
	# チェック機能付ける予定
	my @deletelist;
	
	for (my $i=1; $i <= 1000; ++$i){
		if (defined($in{"selectedth$i"})){
			push(@deletelist,$in{"selectedth$i"});
		}
	}
	my $length = @deletelist;
	my @array;
	for (my $i=1; $i <= $length; ++$i){
		my $num = pop(@deletelist);
		if (unlink "data/$num.cgi"){
			print "$num.cgiファイルは削除されました。<br>";
		}
		open IN, "+<data/index.log" or die;
		while(<IN>){
		        if(/^$num<>/){ next; }
		        push @array, $_;
		}
		seek IN, 0, 0;
		foreach(@array){ print IN $_; }
		truncate IN, (tell IN) or die;
		close IN;
		@array = ();
	}
	print <<EOF;
	<body><html>
EOF

	exit;

}
# レス管理
sub data_mente_res {
	
	my @selectedth;
	for (my $i=1; $i <= 1000; ++$i){
		if (defined($in{"selectedth$i"})){
			push(@selectedth,$in{"selectedth$i"});
		}
	}

	if( 1  != $#selectedth +1){
		error("スレッドを一つだけ選択して下さい");
	}

	# レス表示部分
	if($in{mode} = "admin" and @selectedth >= 1){
		open(IN, "data/@selectedth.cgi") or &error("open err: @selectedth.cgi");
		@log = <IN>;
		close(IN);
		my $vw;
		my $begin;
		my $end;
		$begin =0;
		$end =1000;
		if($end > @log){
			$end = @log;
		}
		my $ii = 0;
		for(my $i = $begin; $i < $end; ++$i){
			my ($tno,$no_p,$name_p,$message_p,$date_p,$ip_p,$id_p,$img_p) = (split(/<>/,$log[$i]))[0,2,3,4,5,8,9,10];
			my $tmp = "";
			if($img_p =~ /\./){
				$tmp = "<a href = \"https://" + $ENV{HTTP_HOST}  + "/bbs/img/$img_p\"><img src=\"$DIR$img_p\" align=\"right\" alt=\"画像\" width=\"48\" height=\"48\"></a><br>"
			}
			#Perl
			if ($message_p =~ /<pre class="brush:perl;">[\s|\S]+?<\/pre>/){
				
				while ($message_p =~ /<pre class="brush:perl;">([\s|\S]+?)<\/pre>/g){
					$code = $1;
					$code =~ s/<br>/\r\n/g;
					$message_p =~ s/<pre class="brush:perl;">([\s|\S]+?)<\/pre>/<pre class="brush:perl;">$code<pre>/;
				}
				
				while ($message_p =~ /<pre class="brush:perl;">([\s|\S]+?)<pre>/g){
					$code = $1;
					$message_p =~ s/<pre class="brush:perl;">([\s|\S]+?)<pre>/<pre class="brush:perl;">$code<\/pre>/;
				}
			}
			#CSS
		if ($message_p =~ /<pre class="brush:css;">[\s|\S]+?<\/pre>/){
			
			while ($message_p =~ /<pre class="brush:css;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:css;">([\s|\S]+?)<\/pre>/<pre class="brush:css;">$code<pre>/;
			}
			
			while ($message_p =~ /<pre class="brush:css;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:css;">([\s|\S]+?)<pre>/<pre class="brush:css;">$code<\/pre>/;
			}
		}
		#Javascript
		if ($message_p =~ /<pre class="brush:js;">[\s|\S]+?<\/pre>/){
			
			while ($message_p =~ /<pre class="brush:js;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:js;">([\s|\S]+?)<\/pre>/<pre class="brush:js;">$code<pre>/;
			}
			
			while ($message_p =~ /<pre class="brush:js;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:js;">([\s|\S]+?)<pre>/<pre class="brush:js;">$code<\/pre>/;
			}
		}
		#Delphi
		if ($message_p =~ /<pre class="brush:delphi;">[\s|\S]+?<\/pre>/){
			
			while ($message_p =~ /<pre class="brush:delphi;">([\s|\S]+?)<\/pre>/g){
				$code = $1;
				$code =~ s/<br>/\r\n/g;
				$message_p =~ s/<pre class="brush:delphi;">([\s|\S]+?)<\/pre>/<pre class="brush:delphi;">$code<pre>/;
			}
			
			while ($message_p =~ /<pre class="brush:delphi;">([\s|\S]+?)<pre>/g){
				$code = $1;
				$message_p =~ s/<pre class="brush:delphi;">([\s|\S]+?)<pre>/<pre class="brush:delphi;">$code<\/pre>/;
			}
		}
			++$ii;
			$disp[$i] = "<hr color=#3377bb><input type=checkbox name=selectedres$ii value=$no_p>[$no_p]$name_p<br><font color=#ff3399>ID:$id_p</font><br>$message_p<br><font color=#4169e1>$ip_p</font><br>$tmp<font  color=#dddd33>$date_p</font>";
			
		}
		my ($tno,$title) = (split(/<>/,$log[$#log]))[0,1];
		print <<"EOF";
		<html>
		<head>
		<meta name="viewport" content="width=device-width,initial-scale=1.0">
		<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
		<meta http-equiv="Content-Script-Type" content="text/javascript">
		<meta http-equiv="Content-Style-Type" content="text/css">
		<link type="text/css" rel="stylesheet" href="https://developer-world.net/sh/styles/shCore.css" />
		<link type="text/css" rel="stylesheet" href="https://developer-world.net/sh/styles/shCoreDefault.css" />
		<link type="text/css" rel="stylesheet" href="https://developer-world.net/sh/styles/shThemeDefault.css" />
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/XRegExp.js"></script>
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/shCore.js"></script>
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/shBrushPerl.js"></script>
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/shBrushCss.js"></script>
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/shBrushJScript.js"></script>
		<script type="text/javascript" src="https://developer-world.net/sh/scripts/shBrushDelphi.js"></script>
		<script type="text/javascript">
		SyntaxHighlighter.defaults['auto-links'] = false;
		SyntaxHighlighter.defaults['toolbar'] = false;
		SyntaxHighlighter.defaults['gutter'] = true;
		SyntaxHighlighter.all();
		</script>
		<title>$title</title>
		</head>
		<body>
		<h2>$title</h2>
		<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
		<input type="hidden" name="mode" value=admin>
		<input type="hidden" name="pass" value=$password>
		<table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
		<a href="#bottom" name="top" accesskey="8">▼</a> <input type="submit" name="data_mente" value=">>スレッド管理に戻る"></td></tr></table>
EOF

		@disp = reverse(@disp);
		print "@disp";
		print <<"EOF";
			<hr color="#3377bb"><table border="0" width="100%" bgcolor="$bgcolor"><tr><td colspan="2" style="background-color:$background_color; border:1px solid $solid_color;">
			<a href="#top" name="bottom" accesskey="2">▲</a> <input type="submit" name="data_mente" value=">>スレッド管理に戻る"> <input type=hidden name=thnum value=@selectedth><input type="submit" name="res_dele" value="レス削除">
			</td></tr></table>
EOF

		print qq(</form>);

	exit;
	}
}

# レス削除
sub res_dele {
	print <<EOF;
	<html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1.0\"><title>レス削除</title></head><body>
	<h2>レス削除</h2>
	<hr color=#3377bb>
	<form action="$ENV{SCRIPT_NAME}?mode=admin" method="post">
	<input type="hidden" name="mode" value=admin>
	<input type="hidden" name="pass" value=$password>
	<input type="submit" name="data_mente" value="スレッド管理に戻る"><br>
EOF
	# チェック機能付ける予定
	my @deletelist;
	
	for (my $i=1; $i <= 1000; ++$i){
		if (defined($in{"selectedres$i"})){
			push(@deletelist,$in{"selectedres$i"});
		}
	}
	#print "$#deletelist";
	# $#deletelistは使わない事！バグがある。
	my $length = @deletelist;
	if ($length == 0){
		error("レスを削除する場合は、選択してからボタンを押して下さい。");
	}
	my @array;
	my $num=0;
	while ( $num <= $length ){
		open IN, "+<data/$in{thnum}.cgi" or die;
		while(<IN>){
			if(/^$in{thnum}<>[\s|\S]+?<>$deletelist[$num]<>[\s|\S]+?$/){
				$_ =~ s/(^$in{thnum}<>[\s|\S]+?<>$deletelist[$num]<>)[\s|\S]+/$1<font color=red><b>レス削除済み<\/b><\/font><>\n/;
				++$num;
			}
			push @array, $_;
		}
		seek IN, 0, 0;
		foreach(@array){ print IN $_; }
		truncate IN, (tell IN) or die;
		close IN;
		++$num;
	}
	$num = 0;
	while ( $num < $length ){
		print "$in{thnum}の$deletelist[$num]レスは削除されました。<br>";
		++$num;
	}
	print <<EOF;
	<body><html>
EOF

	exit;
}

sub search {
	form_processing();
	
	print <<"EOF";
	<html>
	<head>
	<meta name="viewport" content="width=device-width,initial-scale=1.0">
	<title>検索</title>
	</head>
	<body><form action="$ENV{SCRIPT_NAME}?mode=search" method="post" enctype=\"multipart/form-data\">
	<tr><th>検索ワード:</th><td><input type="text" name="searchwd" placeholder=\"検索ワードを入力\"></td></tr>
	<input type="hidden" name="mode" value=search>
	<input type=\"button\" onclick=\"submit();\" value =\"検索\"></form></body>
EOF

	if (defined($in{"searchwd"})){
		open(IN, "data/index.log") or $!;
		my @search = <IN>;
		close(IN);
		
		my @searchresult;
		my @searchhit;
		# スレッドタイトル検索
		my $searchcount = 0;
		foreach (@search){
			my $searchtitle = (split(/<>/,$_))[1];
			if ($searchtitle =~ /$in{"searchwd"}/){
				$searchhit[$searchcount] = $_;
				++$searchcount;
			}
		}
		for(my $i = 0; $i < $searchcount; ++$i){
			my ($tno,$title,$no) = (split(/<>/,$searchhit[$i]))[0,1,2];
			$searchresult[$i] = "・<a href=\"$ENV{SCRIPT_NAME}?read=$tno\">$title</a> #$no<br>";
			chomp $searchresult[$i];
		}
		print "<hr color=#3377bb>";
		print "@searchresult";
	}
	exit;
}

