@echo off
setlocal

rem 指定要打包的 Python 脚本列表
set SCRIPTS=simulator_app.py

rem 指定打包选项
set OPTIONS=--onefile --windowed

rem 遍历每个脚本进行打包
for %%s in (%SCRIPTS%) do (
    echo 正在打包 %%s ...
    pyinstaller %OPTIONS% %%s
    echo %%s 打包完成.
)

echo 所有脚本打包完成.
pause
