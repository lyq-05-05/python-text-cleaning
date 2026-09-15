from pathlib import Path
import json


def clean_text(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            lines.append(line)
    cleaned_text = "\n".join(lines)
    return cleaned_text


def collect_documents(base_dir: Path, input_dir: Path) -> tuple:
    documents = []
    skipped = []
    seen = set()

    try:
      items = sorted(input_dir.iterdir(), key= lambda path: path.name)
    except OSError:
      print("读取目录失败！")
      return documents, skipped
    
    for item in items:
      if not item.is_file():
        continue

      if item.suffix.lower() != ".txt":
        continue

      if "草稿" in item.name:
        skipped.append({
          "filename": item.name,
          "reason": "draft"
        })
        continue

      try:
        with item.open(encoding= "utf-8") as f:
          text = f.read()
        
      except UnicodeDecodeError:
        skipped.append({
          "filename": item.name,
          "reason": "decode_error"
        })
        continue

      except OSError:
        skipped.append({
          "filename": item.name,
          "reason": "read_error"
        })

      cleaned_text = clean_text(text)

      if not cleaned_text:
        skipped.append({
          "filename": item.name,
          "reason": "empty"
        })
        continue
      
      if len(cleaned_text) < 99:
        skipped.append({
          "filename": item.name,
          "reason": "too_sort"
        })
        continue

      if cleaned_text in seen:
        skipped.append({
          "filename": item.name,
          "reason": "duplicate"
        })
        continue
      
      seen.add(cleaned_text)
      documents.append({
        "filename": item.name,
        "source": item.relative_to(base_dir).as_posix(),
        "text": cleaned_text
      })

    return documents, skipped

def main():
  base_dir = Path(__file__).resolve().parent
  input_dir = base_dir / "sample_docs"
  output_path = base_dir / "output.json"

  if not input_dir.is_dir():
    print("输入目录不存在或不是目录")
    return

  documents, skipped = collect_documents(base_dir, input_dir)
  data = {
    "documents": documents,
    "skipped": skipped
  }

  try:
    with output_path.open("w", encoding= "utf-8") as f:
      json.dump(data, f, ensure_ascii= False, indent= 2)
  except OSError:
    print("json写入失败")
    return

  print(f"完成：导入 {len(documents)} 个，跳过 {len(skipped)} 个。")

if __name__ == "__main__":
  main()