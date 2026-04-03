@echo off
echo ========================================
echo  Building Lumina Cricket 2D...
echo ========================================
pyinstaller cricket_2d.spec --clean
if %errorlevel% neq 0 (
    echo [ERROR] 2D build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Building Lumina Cricket 3D Pro...
echo ========================================
pyinstaller cricket_3d_pro.spec --clean
if %errorlevel% neq 0 (
    echo [ERROR] 3D build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Both builds complete!
echo  Executables are in the dist\ folder.
echo ========================================
pause
