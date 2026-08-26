@echo off
setlocal
cd /d "%~dp0"
echo ========================================================
echo  TalentLens AI - Push to GitHub Repository
echo ========================================================
echo.
echo Remote repository: https://github.com/Kumarshiv16/talentlens-ai.git
echo Branch: main
echo.
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/Kumarshiv16/talentlens-ai.git
echo Adding files and committing...
git add .
git commit -m "feat: complete TalentLens AI enterprise platform" 2>nul
echo Pushing to GitHub...
git push -u origin main
if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS: Code pushed to GitHub!
    echo  Repository: https://github.com/Kumarshiv16/talentlens-ai
    echo ========================================================
) else (
    echo.
    echo ========================================================
    echo  Push failed or authorization required.
    echo ========================================================
)
echo.
pause