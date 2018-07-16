Readme


1、
输入命令: ./ac.sh
窗口会列出一系列的命令，拷贝相应命令修改

如：
编译maincode正式版本命令：./ac.sh maincode -config config_pixi3_5.xml -clean all -sync current_version -build -sign -teleweb yx_test
编译perso正式版本的命令：./ac.sh perso -config config_pixi3_5.xml -clean all -sync current_version -build -sign -teleweb yx_test


2、
输入命令:./ac.sh  [maincode | perso]  [-option]

-option有如下几种：
-config	    指定配置文件，后面跟上某个项目的配置文件，如config_pixi3_5.xml
-clean	    清环境，后面参数可以是all或out，all：清整个工程环境；out：只清out目录
-sync	    同步代码，后面参数可以是current_version、latest、v2D32，current_version：同步当前manifest的代码；latest：同步当前项目配置文件中分支的最新代码；v2D32：同步某个版本的代码
-modify	    修改代码标志，在同步代码后，编译窗口会暂停，这时可以对代码进行修改，改完代码，把./autotools/ac/目录下的modification_flag_file文件删掉，脚本接着往下编译
-build	    编译软件
-sign	    签名
-teleweb	上传软件到teleweb上，后面跟的参数是你要在teleweb对应项目的black目录下建的文件夹命名，上传的软件就是存放在该文件夹下


例子：
当前工程为pixi3-5-v1.0-dint分支的最新代码，现在在pixi353g 的1A2E版本上修改代码验证，命令如下：
./ac.sh maincode -config config_pixi3_5.xml -clean all -sync v1A2E -modify -build -sign -teleweb yx_test
