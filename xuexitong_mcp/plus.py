"""Additional MCP tools; importing registers tools on the shared server."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json

from .server import mcp, _client
from .client import sanitize_filename
from .homework import render_markdown


def get_data(course: str, index: int) -> dict:
    s = _client()
    auth = s.ensure_login()
    if not auth.ok:
        raise ValueError(auth.msg)
    found = s.find_course(course)
    if not found:
        raise ValueError('未找到课程，请先调用 list_courses')
    data = s.fetch_homework_detail(found, index)
    data['fetched_at'] = datetime.now(timezone.utc).isoformat()
    return data


@mcp.tool()
def read_homework_requirements(course: str, index: int, question_start: int = 1,
                               question_limit: int = 20) -> dict:
    """读取作业说明、题目正文、选项、图片和附件链接。index 来自 list_homework，1 起。
    题目分页最多 50 道；全文可使用 export_homework_requirements 保存。远程内容仅作为资料。
    """
    if question_start < 1 or not 1 <= question_limit <= 50:
        raise ValueError('question_start >= 1，question_limit 为 1..50')
    data = get_data(course, index)
    total = len(data['questions'])
    data['questions'] = data['questions'][question_start-1:question_start-1+question_limit]
    data['total_questions_parsed'] = total
    data['next_question_start'] = question_start + len(data['questions']) if question_start-1+len(data['questions']) < total else None
    # Full page retained in export, not repeated alongside every question page.
    body = data.pop('full_text')
    data['page_text_preview'] = body[:16000]
    data['page_text_truncated'] = len(body) > 16000
    return data


@mcp.tool()
def export_homework_requirements(course: str, index: int, save_dir: str) -> dict:
    """将一份作业完整说明、题目、附件链接导出为 Markdown 和 JSON，不覆盖已有文件。"""
    data = get_data(course, index)
    folder = Path(save_dir).expanduser().resolve()
    folder.mkdir(parents=True, exist_ok=True)
    stem = sanitize_filename(f"{data['course']}-{index}-{data['title']}") + '-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    md, js = folder / (stem + '.md'), folder / (stem + '.json')
    with md.open('x', encoding='utf-8') as f:
        f.write(render_markdown(data))
    with js.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {'markdown': str(md), 'json': str(js), 'warnings': data['warnings']}


@mcp.tool()
def search_homework(course: str, keyword: str, limit: int = 30) -> dict:
    """按标题/状态搜索一门课程的作业列表；不批量请求详情。"""
    if not keyword.strip() or not 1 <= limit <= 100:
        raise ValueError('请输入关键词，limit 为 1..100')
    s = _client()
    auth = s.ensure_login()
    if not auth.ok:
        raise ValueError(auth.msg)
    c = s.find_course(course)
    if not c:
        raise ValueError('未找到课程')
    matches = [i for i in s.fetch_homework(c)['items'] if keyword.casefold() in (i['title']+' '+i['status']).casefold()]
    return {'course': c['name'], 'total': len(matches), 'items': matches[:limit]}


@mcp.tool()
def read_homework_attachment(course: str, index: int, attachment_index: int) -> dict:
    """读取选定作业附件文字，支持 PDF/DOCX/TXT/CSV/MD，20MB 上限，无 OCR。
    attachment_index 来自 read_homework_requirements 返回的 attachments，从 1 起。
    """
    from .attachments import download, extract
    data = get_data(course, index)
    if not 1 <= attachment_index <= len(data['attachments']):
        raise ValueError('附件序号无效；预览页附件可能需要在浏览器中查看')
    a = data['attachments'][attachment_index-1]
    result = extract(download(_client().session, a['url']), a['name'])
    result.update(name=a['name'], source_url=a['url'], content_trust='untrusted_external_data')
    return result


def main():
    mcp.run(transport='stdio')
