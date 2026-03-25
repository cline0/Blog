---
title: "UNIX 时间"
type: "docs"
weight: 150
markmap: true
xmindSource: "UNIX 时间.xmind"
---

```markmap
---
markmap:
  initialExpandLevel: 2
  spacingVertical: 30
  spacingHorizontal: 180
---

# UNIX 时间
- 日历时间
  - 1970年1月1日00:00:00这个时刻所经过的秒数的累计值
- 进程时间（CPU时间）
  - 进程时间以时钟滴答计算。每秒中曾取为50、60或100个时钟滴答
  - 系统基本数据类型 clock_t 保存这种时间值
  - 为度量一个进程的执行时间，UNIX 为一个进程维护了 3 个进程时间值
    - 时钟时间
      - 又称（墙上时钟时间 wall clock time），是进程运行的时间总量
    - 用户CPU时间
      - 执行用户指令所用的时间
    - 系统CPU时间
      - 为该进程执行内核程序所经历的时间
```
