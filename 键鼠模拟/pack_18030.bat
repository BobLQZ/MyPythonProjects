@echo off
setlocal

rem ָ��Ҫ����� Python �ű��б�
set SCRIPTS=simulator_app.py

rem ���ö����ֶΣ����������޸ģ�
set ADDITIONAL_FIELD=_v1.3.1

rem ָ�����ѡ��
set OPTIONS=--onefile --windowed

rem ָ���Զ���ͼ���ļ���ʹ�����·����
set ICON=.\ico\logo.ico

rem ����ÿ���ű����д��
for %%s in (%SCRIPTS%) do (
    echo ���ڴ�� %%s ...
    python313.exe -m PyInstaller %OPTIONS% --icon=%ICON% %%s --name=%%~ns%ADDITIONAL_FIELD%
    echo %%s �����ɣ�����ļ�Ϊ %%~ns%ADDITIONAL_FIELD%.
)

pause
