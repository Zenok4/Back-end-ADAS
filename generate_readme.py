#!/usr/bin/env python3
# generate_readme.py
# Sinh API.md tự động: quét cấu trúc thư mục + phát hiện endpoints (route + phương thức)

import ast
import datetime
import argparse
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

ROOT = Path(__file__).resolve().parent  # thư mục backend
OUT = ROOT / "REAdME.md"

HTTP_DECORATOR_METHODS = {
    "get": ["GET"],
    "post": ["POST"],
    "put": ["PUT"],
    "patch": ["PATCH"],
    "delete": ["DELETE"],
    "options": ["OPTIONS"],
    "head": ["HEAD"],
    "route": None,  # route sẽ đọc kwargs 'methods'
}


def get_literal_str(node) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if hasattr(ast, "Str") and isinstance(node, ast.Str):
        return node.s
    return None


def extract_methods_from_value(node) -> List[str]:
    if node is None:
        return []
    methods = []
    if isinstance(node, (ast.List, ast.Tuple)):
        for elt in node.elts:
            s = get_literal_str(elt)
            if s:
                methods.append(s.upper())
    else:
        s = get_literal_str(node)
        if s:
            methods.append(s.upper())
    return methods


def parse_decorator(dec: ast.AST) -> Optional[Tuple[Optional[str], List[str], Optional[str]]]:
    if not isinstance(dec, ast.Call):
        return None
    func = dec.func
    if isinstance(func, ast.Attribute):
        attr = func.attr.lower()
        owner = func.value.id if isinstance(func.value, ast.Name) else None
        if attr in HTTP_DECORATOR_METHODS:
            path = None
            for a in dec.args:
                s = get_literal_str(a)
                if s:
                    path = s
                    break
            methods = []
            if attr == "route":
                for kw in dec.keywords:
                    if kw.arg == "methods":
                        methods = extract_methods_from_value(kw.value)
                        break
            else:
                methods = HTTP_DECORATOR_METHODS.get(attr) or []
            return path, methods, owner
    return None


def parse_file_for_endpoints(pyfile: Path) -> List[Dict[str, Any]]:
    endpoints = []
    try:
        src = pyfile.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except Exception:
        return endpoints

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            found_routes = []
            for dec in node.decorator_list:
                res = parse_decorator(dec)
                if res:
                    path, methods, owner = res
                    if not methods:
                        methods = ["GET"]
                    found_routes.append({
                        "path": path or "(unknown)",
                        "methods": methods,
                        "owner": owner or "",
                    })
            if found_routes:
                doc = ast.get_docstring(node) or ""
                short_doc = doc.splitlines()[0].strip() if doc else ""
                endpoints.append({
                    "function": node.name,
                    "doc": short_doc,
                    "routes": found_routes,
                    "file": str(pyfile.relative_to(ROOT)),
                })
    return endpoints


def build_tree(folder: Path) -> List[str]:
    lines = []
    try:
        items = sorted(folder.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except Exception:
        return lines

    count = len(items)
    for idx, p in enumerate(items):
        connector = "└── " if idx == count - 1 else "├── "
        if p.is_dir():
            lines.append(f"{connector}📂 {p.name}/")
        else:
            lines.append(f"{connector}📄 {p.name}")
    return lines


def generate_readme(structure_only=False, endpoints_only=False):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Phần hướng dẫn setup
    setup_md = """# Backend API Documentation

## 🚀 Hướng dẫn cài đặt môi trường

1. Tạo môi trường ảo trong thư mục `backend/libs`
   ```bash
   cd backend
   python -m venv libs
   ```

2. Kích hoạt môi trường ảo  
   - Gõ lệnh dưới đây:
     ```bash
     libs\\Scripts\\activate
     ```
   - Nếu lệnh trên không được thì dùng lệnh này:
     ```bash
     source libs\\Scripts\\activate
     ```

3. Cài đặt thư viện cần thiết
   ```bash
   pip install -r requirements.txt
   ```

4. Chạy project
   ```bash
   python app.py
   ```

5. Nếu cần cài thêm thư viện
   - Gõ lệnh dưới đây:
   ```bash
   pip install <tên_thư_viện>
   pip freeze > requirements.txt
   ```
"""

    # Cấu trúc thư mục
    tree_lines = build_tree(ROOT)
    tree_md = "## 📂 Cấu trúc thư mục\n\n```\n" + f"{ROOT.name}/\n" + "\n".join(tree_lines) + "\n```"

    # Quét endpoints
    endpoints_all = []
    if not structure_only:
        for py in ROOT.rglob("*.py"):
            rel = py.relative_to(ROOT)
            if any(x in str(rel) for x in ["site-packages", "libs", ".venv"]):
                continue
            endpoints_all.extend(parse_file_for_endpoints(py))

    if endpoints_all:
        table_lines = [
            "| Method(s) | Path | Function | File | Description |",
            "|-----------|------|----------|------|-------------|"
        ]
        for ep in endpoints_all:
            for r in ep["routes"]:
                methods = ", ".join(r["methods"])
                path = r["path"]
                func = ep["function"]
                file = ep["file"]
                desc = ep["doc"] or ""
                desc = desc.replace("|", "\\|")
                table_lines.append(f"| {methods} | `{path}` | `{func}()` | `{file}` | {desc} |")
        endpoints_md = "\n".join(table_lines)
    else:
        endpoints_md = "_No endpoints discovered automatically._"

    # Kết hợp
    readme_parts = [setup_md, f"\n**Generated:** {now}\n"]

    if not endpoints_only:
        readme_parts.append(tree_md)

    if not structure_only:
        readme_parts.append(f"\n## 🌐 API Endpoints\n\n_{len(endpoints_all)} endpoint(s) found._\n\n{endpoints_md}\n")

    readme_parts.append("---\n\n> File này được tạo tự động bởi `generate_readme.py`. Đừng chỉnh sửa thủ công!")

    OUT.write_text("\n".join(readme_parts), encoding="utf-8")
    print(f"✅ API.md created/updated at {OUT}")
    print(f" - Endpoints found: {len(endpoints_all)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate API.md with structure + endpoints")
    parser.add_argument("--structure-only", action="store_true", help="Chỉ xuất cấu trúc thư mục")
    parser.add_argument("--endpoints-only", action="store_true", help="Chỉ xuất endpoints")
    args = parser.parse_args()

    generate_readme(structure_only=args.structure_only, endpoints_only=args.endpoints_only)
