@echo off
setlocal

rem 指定要打包的 Python 脚本列表
set SCRIPTS=simulator_app.py

rem 设置额外字段（可以根据需求修改）
set ADDITIONAL_FIELD=_v1.1.0

rem 组合成最终的输出文件名
set OUTPUT_NAME=%BASENAME%%ADDITIONAL_FIELD%

rem 指定打包选项
set OPTIONS=--onefile --windowed

rem 遍历每个脚本进行打包
for %%s in (%SCRIPTS%) do (
    echo 正在打包 %%s ...
    pyinstaller %OPTIONS% %%s --name=%%~ns%ADDITIONAL_FIELD% 
    echo %%s 打包完成，输出文件名为 %OUTPUT_NAME%.
)

pause
