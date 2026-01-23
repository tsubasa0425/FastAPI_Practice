from fastapi import APIRouter

app08 = APIRouter()



''' ************** 1. 【见run.py】Middleware 中间件 ************** '''



''' ************** 2. 【见run.py】CORS (Cross-Origin Resource Sharing) 跨源资源共享 ************** '''



''' ************** 3. Background Tasks 后台任务 ************** '''

from fastapi import BackgroundTasks, Depends
from typing import Optional

def bg_task(framework:str):
    with open('Chapter08.md', 'a') as f:
        f.write(f'## {framework} 框架精讲')

@app08.post('/background_tasks')
async def run_bg_task(framework:str, bg_tasks:BackgroundTasks):
    """
    后台任务示例：将框架名称写入Chapter08.md文件。

    :param framework: 框架名称，作为任务参数。
    :param bg_tasks: 后台任务对象，用于添加后台任务。
    :return: 包含任务状态的字典。
    """
    bg_tasks.add_task(bg_task, framework)
    return {'message': '任务已在后台运行'}



def continue_write_readme(background_tasks: BackgroundTasks, q: Optional[str] = None):
    if q:
        background_tasks.add_task(bg_task, "\n> 整体的介绍 FastAPI，快速上手开发，结合 API 交互文档逐个讲解核心模块的使用\n")
    return q


@app08.post("/dependency/background_tasks")
async def dependency_run_bg_task(q: str = Depends(continue_write_readme)):
    if q:
        return {"message": "Chapter08.md更新成功"}




''' ************** 4. 【见test_chapter08.py】Testing 测试用例  ************** '''