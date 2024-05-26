# Readme

## 踩坑记录

- 2024-05-26：若运行`uvicorn`出现如下报错，尝试删除pipfile中的`psycopg`依赖，然后重新安装：`pipenv install --dev psycopg[binary]` (上一次就是删除了dev package中的`psycopg`依赖再重装解决的，即使原来就已经是二进制包，可能和在Windows环境和mac环境之间切换有关系)。

  ``` sh
  PS D:\Projects\lc-render-backend> uvicorn main:app --reload
  INFO:     Will watch for changes in these directories: ['D:\\Projects\\lc-render-backend']
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  INFO:     Started reloader process [23852] using WatchFiles
  Process SpawnProcess-1:
  Traceback (most recent call last):
    File "C:\Python39\lib\multiprocessing\process.py", line 315, in _bootstrap
      self.run()
    File "C:\Python39\lib\multiprocessing\process.py", line 108, in run
      self._target(*self._args, **self._kwargs)
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\_subprocess.py", line 78, in subprocess_started
      target(sockets=sockets)
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\server.py", line 65, in run
      return asyncio.run(self.serve(sockets=sockets))
    File "C:\Python39\lib\asyncio\runners.py", line 44, in run
      return loop.run_until_complete(main)
    File "C:\Python39\lib\asyncio\base_events.py", line 647, in run_until_complete
      return future.result()
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\server.py", line 69, in serve
      await self._serve(sockets)
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\server.py", line 76, in _serve
      config.load()
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\config.py", line 433, in load
      self.loaded_app = import_from_string(self.app)
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\uvicorn\importer.py", line 19, in import_from_string
      module = importlib.import_module(module_str)
    File "C:\Python39\lib\importlib\__init__.py", line 127, in import_module
      return _bootstrap._gcd_import(name[level:], package, level)
    File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
    File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
    File "<frozen importlib._bootstrap>", line 986, in _find_and_load_unlocked
    File "<frozen importlib._bootstrap>", line 680, in _load_unlocked
    File "<frozen importlib._bootstrap_external>", line 850, in exec_module
    File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
    File "D:\Projects\lc-render-backend\main.py", line 10, in <module>
      from db import DbEngine, Todo
    File "D:\Projects\lc-render-backend\db\__init__.py", line 1, in <module>
      from .engine import DbEngine as DbEngine
      from psycopg import Connection as PsycopgConnection
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\psycopg\__init__.py", line 9, in <module>
      from . import pq  # noqa: F401 import early to stabilize side effects
      import_from_libpq()
    File "D:\Projects\lc-render-backend\PIPENV_VENV_IN_PROJECT\lc-render-backend-BehqWtBA\lib\site-packages\psycopg\pq\__init__.py", line 106, in import_from_libpq
      raise ImportError(
  ImportError: no pq wrapper available.
  Attempts made:
  - couldn't import psycopg 'c' implementation: No module named 'psycopg_c'
  - couldn't import psycopg 'binary' implementation: No module named 'psycopg_binary'
  - couldn't import psycopg 'python' implementation: libpq library not found
  ```

- 对于与数据库的通信（使用SQLModel），函数不需要`async`，否则有奇怪的报错。
- 