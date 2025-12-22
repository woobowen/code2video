@echo off
setlocal

REM =============================================================
REM 0) Environment Configuration (编码与日志优化)
REM =============================================================

REM 1. 将命令行代码页切换为 UTF-8，防止批处理自身的 echo 输出乱码
chcp 65001 >nul

REM 2. 强制 Python 标准输入输出使用 UTF-8 编码，防止 Python 日志乱码
set PYTHONIOENCODING=utf-8

REM 3. 禁用 Python 输出缓存，确保日志实时写入文件（像 tail -f 一样流畅）
set PYTHONUNBUFFERED=1

REM =============================================================
REM 1) Default values and constants
REM =============================================================

REM Python command (Windows下通常是 python 而不是 python3)
set "PY=python"
set "ENTRY=agent.py"

REM Common defaults
set "API=claude"
set "FOLDER_PREFIX=TEST-single"

REM Hyperparameters
set "MAX_CODE_TOKEN_LENGTH=10000"
set "MAX_FIX_BUG_TRIES=10"
set "MAX_REGENERATE_TRIES=10"
set "MAX_FEEDBACK_GEN_CODE_TRIES=3"
set "MAX_MLLM_FIX_BUGS_TRIES=3"
set "FEEDBACK_ROUNDS=2"

REM =============================================================
REM 2) KNOWLEDGE_POINT Logic
REM =============================================================

set "DEFAULT_KNOWLEDGE_POINT=Linear transformations and matrices"
set "USER_ARGS=%*"
set "KNOWLEDGE_POINT_ARGS="

REM 检测用户参数中是否包含 --knowledge_point
REM 如果没有找到，则使用默认知识点
echo %USER_ARGS% | findstr /C:"--knowledge_point" >nul
if %errorlevel% neq 0 (
    set "KNOWLEDGE_POINT_ARGS=--knowledge_point "%DEFAULT_KNOWLEDGE_POINT%""
    echo INFO: Using default knowledge point: %DEFAULT_KNOWLEDGE_POINT%
)

REM =============================================================
REM 3) Execute
REM =============================================================

REM 使用 ^ 符号进行换行
%PY% %ENTRY% ^
  --API "%API%" ^
  --folder_prefix "%FOLDER_PREFIX%" ^
  --use_feedback ^
  --use_assets ^
  --max_code_token_length %MAX_CODE_TOKEN_LENGTH% ^
  --max_fix_bug_tries %MAX_FIX_BUG_TRIES% ^
  --max_regenerate_tries %MAX_REGENERATE_TRIES% ^
  --max_feedback_gen_code_tries %MAX_FEEDBACK_GEN_CODE_TRIES% ^
  --max_mllm_fix_bugs_tries %MAX_MLLM_FIX_BUGS_TRIES% ^
  --feedback_rounds %FEEDBACK_ROUNDS% ^
  --parallel ^
  %KNOWLEDGE_POINT_ARGS% ^
  %*

endlocal