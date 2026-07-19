# Local Transcript Segment Quality Checker

## 解决的痛点
Local transcription tools produce timestamped text, but creators still need to spot too-long, empty, overlapping, or suspicious segments before publishing.

## 为什么现在值得做
Transcribe.cpp was a top HN item today; local transcription workflows need lightweight QA around generated segments.

## 安装与运行
无需第三方依赖，Python 3.9+ 即可运行。

```bash
python -m src.main --help
python -m src.main examples/transcript.txt --max-seconds 10
```

## 示例
```bash
python -m src.main examples/transcript.txt --max-seconds 10
```

命令会输出简洁报告，可用于本地自动化或 CI。

## 自检
```bash
python tests/test_main.py
```

## 路线图
- 增加更丰富的输入模板。
- 增加适合 CI 的 JSON / SARIF 等导出。
- 基于社区反馈补充真实案例。

## 许可证
MIT
