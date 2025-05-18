@echo off
setlocal

rem 指定要打包的 Python 脚本列表
set SCRIPTS=simulator_app.py

rem 设置额外字段（根据需求修改）
set ADDITIONAL_FIELD=_v1.3.1

rem 指定打包选项
set OPTIONS=--onefile --windowed

rem 指定自定义图标文件（使用相对路径）
set ICON=.\ico\logo.ico

rem 遍历每个脚本进行打包
for %%s in (%SCRIPTS%) do (
    echo %%s ...
    python313.exe -m PyInstaller %OPTIONS% %%s --name=%%~ns%ADDITIONAL_FIELD%
    echo %%s %%~ns%ADDITIONAL_FIELD%.
)

pause
