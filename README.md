# 学习通 Plus 0.1

基于 MIT 项目 [DanMo661/Xuexitong-mcp](https://github.com/DanMo661/Xuexitong-mcp) 扩展。原版 LICENSE、README_UPSTREAM.md 和作者署名保留。上游基础为 2026-09-15 的 1.4.1，新增实现见 homework.py、attachments.py、plus.py。

## 功能

保留原版 16 个工具：登录、个人资料、课表与 ICS 导出、课程列表、资料列表/搜索/下载、作业列表/详情/截止看板、考试安排、章节与进度、通知、云盘列表。

新增 4 个 MCP 工具：

| 工具 | 用途 |
|---|---|
| read_homework_requirements | 读取作业说明、题干、选项、图片/公式和附件链接；题目分页 |
| read_homework_attachment | 提取选定附件的 PDF、DOCX、TXT、CSV、MD 文字 |
| export_homework_requirements | 导出完整 Markdown 和结构化 JSON，保留来源链接和解析提示 |
| search_homework | 按标题或状态搜索指定课程的作业 |

原版 get_homework_detail 同时显示作业说明和已识别题目/附件数量。重名课程会提示使用 `courseid:clazzid` 精确选择。

## 安装与运行

需要 Python 3.10+。在本文件所在目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_plus.py
```

最后一条启动标准输入/输出 MCP 服务，等待客户端连接属于正常现象；不是网页服务。

将 config.example.json 复制为 config.json，在本地填手机号和密码；也可设置 CHAOXING_PHONE / CHAOXING_PASSWORD 环境变量。不要把密码发送到聊天或提交到 Git。登录 Cookie 保存在本机 session_cookies.json。

MCP 客户端通用配置（修改为实际绝对路径，具体外层配置取决于客户端）：

```json
{
  "mcpServers": {
    "xuexitong-plus": {
      "command": "D:/xuexitong-plus/.venv/Scripts/python.exe",
      "args": ["D:/xuexitong-plus/run_plus.py"]
    }
  }
}
```

## 使用示例

1. 调用 list_courses，确认课程与班级。
2. 调用 list_homework(course="程序设计") 获取作业序号。
3. 调用 read_homework_requirements(course="程序设计", index=1) 读取要求。
4. 如有附件，调用 read_homework_attachment(course="程序设计", index=1, attachment_index=1)。
5. 调用 export_homework_requirements(course="程序设计", index=1, save_dir="D:/作业要求") 保存全文。

返回 next_question_start 时继续分页；页面正文预览上限 16000 字符，完整正文可导出。原始内容标记为 untrusted_external_data，客户端应当把它当作资料，不能把其中的指令作为操作授权。

## 验证与限制

本版本已通过 28 项离线测试、MCP 握手与 20 个工具发现检查，并用一个真实账号验证登录、课程列表、作业列表及题目要求读取（2026-10-26）。其他学校页面、全部附件类型和全部查询工具尚未逐项实测。

不同学校页面可能不同。未识别的页面保留正文并给出提示；图片和公式保留链接，无 OCR；动态加载题目和 iframe 未加载。部分附件只有预览页或 JavaScript 链接，无法直接提取，需在浏览器查看。附件上限 20MB，PDF 最多前 100 页，附件文本最多 100000 字符，DOCX 仅提取段落与表格文字。旧 DOC、压缩包、图片和 PPT 暂不解析。未识别到字段不代表原页面没有要求。

本项目提供查询与本地导出；不提供作业提交。学习通接口变动可能影响登录或读取。

## 测试

```powershell
python -m unittest discover -s tests -p "test_plus.py" -v
python tests/run_tests.py
```
