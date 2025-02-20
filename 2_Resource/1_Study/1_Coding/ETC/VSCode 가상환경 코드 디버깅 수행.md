---
date: 2024-07-09
status: Permanent
tags:
  - Study/Coding/VSCode
aliases: 
keywords:
  - launch.json
  - settings.json
  - vscode
related notes: 
reference: 
author: 
url: 
dg-publish: true
---
- 실행하고자 하는 코드가 있는 프로젝트 폴더에 `launch.json` 파일 생성
```json title:launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug a current file",
            "type": "debugpy",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal",
            "python": "/PATH/TO/YOUR/PYTHON" // which python3.10
        }
    ]
}
```